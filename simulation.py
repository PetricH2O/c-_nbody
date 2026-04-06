
import argparse
import os
import time
from vpython import*
import traceback
import record
import numpy as np

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('dt', type=float)
    parser.add_argument('file_path', type=str)
    parser.add_argument('rate', type=float)
    parser.add_argument('scene_center', type=int)
    parser.add_argument('max_day', type=float)
    parser.add_argument('integration_method', type=str)
    parser.add_argument('collision_option', type=str)
    parser.add_argument('cuda_option', type=str)
    args = parser.parse_args()


    if args.cuda_option.lower() == 'yes':
        try:
            import cupy as cp
            xp = cp
            using_cuda = True
            print("使用 CUDA（CuPy）")
        except ImportError:
            print("CuPy 無 CUDA，使用 NumPy。")
            xp = np
            using_cuda = False
    else:
        xp = np
        using_cuda = False
        print("不使用 CUDA，使用 NumPy")

    dt = args.dt
    dtime = 0.0
    day = 0.0
    max_day = args.max_day
    G = 6.67430e-11
    softening = 5
    scene_center = args.scene_center
    integration_method = args.integration_method.lower()
    collision_option = args.collision_option.lower()


    mass, position, velocity, acceleration = read_initial_data(args.file_path, xp)


    scene = canvas(width=1800, height=600)
    running = True
    def handle_keydown(evt):
        nonlocal running
        s = evt.key
        if s == ' ':
            running = not running
        elif s == 'esc':
            running = False

    scene.bind('keydown', handle_keydown)

    def toggle_simulation():
        nonlocal running
        running = not running
        print("Simulation resumed" if running else "Simulation paused")

    toggle_button = button(text='PAUSE', bind=lambda:toggle_simulation())


    momentum_graph = graph(title="總動量隨時間變化", xtitle="時間 (秒)",
                           ytitle="總動量 (kg·m/s)", width=400, height=300,
                           align='left',
                           background=color.white, foreground=color.black)
    momentum_curve = gcurve(color=color.red, label="總動量")
    
    energy_graph = graph(title="總能量隨時間變化", xtitle="時間 (秒)",
                         ytitle="總能量 (J)", width=400, height=300,
                         align='left',
                         background=color.white, foreground=color.black)
    energy_curve = gcurve(color=color.blue, label="總能量")

    spheres = create_spheres(mass, position)

    initial_conditions = {
        'dt': dt,
        'rate': args.rate,
        'max_day': args.max_day,
        'integration_method': args.integration_method,
        'collision_option': args.collision_option,
        'cuda_option': args.cuda_option,
    }

    data_filename_base = os.path.basename(args.file_path)
    data_filename = record.create_simulation_folder(
        folder_path='simulation_data',
        data_filename=data_filename_base,
        script_filename=__file__,
        initial_conditions=initial_conditions
    )


    if integration_method == 'euler':
        integrate = lambda m, p, v, dt: euler_integration(m, p, v, dt, xp, softening)
    elif integration_method == 'runge-kutta':
        integrate = lambda m, p, v, dt: runge_kutta_integration(m, p, v, dt, xp, softening)
    else:
        integrate = lambda m, p, v, dt: euler_integration(m, p, v, dt, xp, softening)
    start_time = time.time()
    while day < max_day:
        if not running:
            time.sleep(0.1)
            continue

        rate(args.rate)
        scene.center = spheres[scene_center].pos


        record.write_pos_to_file(mass, position, velocity, acceleration, data_filename, dtime)

        acceleration, dx, dy, dz, inv_r3 = getAcc(mass, position, softening, xp, G, return_intermediates=True)

        mv = mass[:, xp.newaxis] * velocity
        total_momentum = xp.linalg.norm(xp.sum(mv, axis=0))
        
        # 動能 (ke)
        ke = 0.5 * xp.sum(mass * xp.sum(velocity**2, axis=1))

        dr2 = dx**2 + dy**2 + dz**2

        mask = xp.triu(xp.ones_like(dr2, dtype=bool), k=1)

        r_ij = xp.sqrt(dr2[mask])

        mm = (mass[:, xp.newaxis] * mass[xp.newaxis, :])[mask]
        potential_energy = -G * xp.sum(mm / r_ij)
        total_energy = ke + potential_energy
# ///////////////////////////////////////////////////////////////////////////////////////
        momentum_curve.plot(pos=(dtime, float(total_momentum)))
        energy_curve.plot(pos=(dtime, float(total_energy)))
# ///////////////////////////////////////////////////////////////////////////////////////

        dtime += dt
        day += dt / 86400.0


        if collision_option == 'yes':
            from collision import check_collision
            distance = xp.sqrt(dr2)
            velocity, position = check_collision(distance, 0.5, mass, position, velocity, using_cuda)


        velocity, position = integrate(mass, position, velocity, dt)


        for i in range(len(spheres)):
            spheres[i].pos = vector(
                float(position[i, 0]),
                float(position[i, 1]),
                float(position[i, 2])
            )

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("模擬結束python")
    print(f"模擬時間: {day:.2f} 天")
    print(f"實際運行時間: {elapsed_time:.2f} 秒")

    # 保持畫面
    while True:
        rate(30)

def read_initial_data(file_path, xp):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")

    data_list = []
    with open(file_path, 'r') as f:
        for line in f:
            values = line.strip().split(',')
            if len(values) >= 10:
                data_list.append([float(v) for v in values[:10]])

    data = xp.array(data_list)
    mass = data[:, 0]
    position = data[:, 1:4]
    velocity = data[:, 4:7]
    acceleration = data[:, 7:10]
    return mass, position, velocity, acceleration

def getAcc(mass, position, softening, xp, G, return_intermediates=False):
    x = position[:,0]
    y = position[:,1]
    z = position[:,2]

    dx = x[xp.newaxis,:] - x[:, xp.newaxis]
    dy = y[xp.newaxis,:] - y[:, xp.newaxis]
    dz = z[xp.newaxis,:] - z[:, xp.newaxis]

    dr2 = dx**2 + dy**2 + dz**2 + softening**2
    inv_r3 = dr2 ** (-1.5)
    xp.fill_diagonal(inv_r3, 0.0)

    ax = G * xp.sum((dx * inv_r3) * mass[xp.newaxis,:], axis=1)
    ay = G * xp.sum((dy * inv_r3) * mass[xp.newaxis,:], axis=1)
    az = G * xp.sum((dz * inv_r3) * mass[xp.newaxis,:], axis=1)

    a = xp.stack((ax, ay, az), axis=1)

    if return_intermediates:
        return a, dx, dy, dz, inv_r3
    else:
        return a

def euler_integration(mass, position, velocity, dt, xp, softening):
    a = getAcc(mass, position, softening, xp, 6.67430e-11)
    velocity += a * dt
    position += velocity * dt
    return velocity, position

def runge_kutta_integration(mass, position, velocity, dt, xp, softening):
    G = 6.67430e-11
    a1 = getAcc(mass, position, softening, xp, G)
    k1_v = a1 * dt
    k1_x = velocity * dt

    a2 = getAcc(mass, position + 0.5*k1_x, softening, xp, G)
    k2_v = a2 * dt
    k2_x = (velocity + 0.5*k1_v)*dt

    a3 = getAcc(mass, position + 0.5*k2_x, softening, xp, G)
    k3_v = a3 * dt
    k3_x = (velocity + 0.5*k2_v)*dt

    a4 = getAcc(mass, position + k3_x, softening, xp, G)
    k4_v = a4 * dt
    k4_x = (velocity + k3_v)*dt

    velocity += (k1_v + 2*k2_v + 2*k3_v + k4_v)/6
    position += (k1_x + 2*k2_x + 2*k3_x + k4_x)/6
    return velocity, position

def create_spheres(mass, position):
    spheres = []
    rainbow_colors = [color.red, color.orange, color.yellow, color.green, color.blue, color.cyan, color.white]
    for i in range(len(mass)):
        new_sphere = sphere(
            m=mass[i],
            pos=vector(float(position[i,0]), float(position[i,1]), float(position[i,2])),
            color=rainbow_colors[i % len(rainbow_colors)],
            radius=0.5,
            make_trail=True,
            retain=150
        )
        spheres.append(new_sphere)
    return spheres

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_log_path = os.path.join(os.getcwd(), 'error_log.txt')
        with open(error_log_path, 'w', encoding='utf-8') as f:
            f.write("An error occurred during the simulation:\n")
            traceback.print_exc(file=f)
        print("error_log.txt")
