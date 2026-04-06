import argparse
import os
import time
import traceback

from vpython import *
import numpy as np

import record
import nbody_cpp  #pybind11
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

    #CPU/NumPy
    if args.cuda_option.lower() == 'yes':
        print("C++  目前不支援 CuPy，將改用 NumPy。")
    xp = np
    using_cuda = False

    dt = args.dt
    dtime = 0.0
    day = 0.0
    max_day = args.max_day
    G = 6.67430e-11
    softening = 5.0
    scene_center = args.scene_center
    integration_method = args.integration_method.lower()
    collision_option = args.collision_option.lower()

    mass, position, velocity, acceleration = read_initial_data(args.file_path)

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

    toggle_button = button(text='PAUSE', bind=lambda: toggle_simulation())

    momentum_graph = graph(
        title="總動量隨時間變化",
        xtitle="時間 (秒)",
        ytitle="總動量 (kg·m/s)",
        width=400,
        height=300,
        align='left',
        background=color.white,
        foreground=color.black
    )
    momentum_curve = gcurve(color=color.red, label="總動量")

    energy_graph = graph(
        title="總能量隨時間變化",
        xtitle="時間 (秒)",
        ytitle="總能量 (J)",
        width=400,
        height=300,
        align='left',
        background=color.white,
        foreground=color.black
    )
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
    start_time = time.time()
    while day < max_day:
        if not running:
            time.sleep(0.1)
            continue

        rate(args.rate)
        scene.center = spheres[scene_center].pos

        record.write_pos_to_file(mass, position, velocity, acceleration, data_filename, dtime)

        # -------------------------
        #C++ : 加速度
        # -------------------------
        acceleration = getAcc_cpp(mass, position, softening, G)

        x = position[:, 0]
        y = position[:, 1]
        z = position[:, 2]

        dx = x[np.newaxis, :] - x[:, np.newaxis]
        dy = y[np.newaxis, :] - y[:, np.newaxis]
        dz = z[np.newaxis, :] - z[:, np.newaxis]

        dr2 = dx**2 + dy**2 + dz**2
        dr2_soft = dr2 + softening**2

        with np.errstate(divide='ignore', invalid='ignore'):
            inv_r3 = dr2_soft ** (-1.5)
        np.fill_diagonal(inv_r3, 0.0)

        mv = mass[:, np.newaxis] * velocity
        total_momentum = np.linalg.norm(np.sum(mv, axis=0))

        ke = 0.5 * np.sum(mass * np.sum(velocity**2, axis=1))

        mask = np.triu(np.ones_like(dr2, dtype=bool), k=1)
        r_ij = np.sqrt(dr2[mask])

        mm = (mass[:, np.newaxis] * mass[np.newaxis, :])[mask]
        with np.errstate(divide='ignore', invalid='ignore'):
            potential_energy = -G * np.sum(mm / r_ij)
        total_energy = ke + potential_energy

        momentum_curve.plot(pos=(dtime, float(total_momentum)))
        energy_curve.plot(pos=(dtime, float(total_energy)))

        dtime += dt
        day += dt / 86400.0


        #碰撞：


        position = np.ascontiguousarray(position, dtype=np.float64)
        velocity = np.ascontiguousarray(velocity, dtype=np.float64)
        mass = np.ascontiguousarray(mass, dtype=np.float64)

        nbody_cpp.check_collision_inplace(mass, position, velocity, 0.5, 0.7)


        #積分Python

        if integration_method == 'euler':
            velocity, position = euler_integration_cpp_acc(
                mass, position, velocity, dt, softening, G
            )
        elif integration_method == 'runge-kutta':
            velocity, position = runge_kutta_integration_cpp_acc(
                mass, position, velocity, dt, softening, G
            )
        else:
            velocity, position = euler_integration_cpp_acc(
                mass, position, velocity, dt, softening, G
            )

        for i in range(len(spheres)):
            spheres[i].pos = vector(
                float(position[i, 0]),
                float(position[i, 1]),
                float(position[i, 2])
            )

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("模擬結束c++")
    print(f"模擬時間: {day:.2f} 天")
    print(f"實際運行時間: {elapsed_time:.2f} 秒")

    # 保持畫面
    while True:
        rate(30)


def read_initial_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")

    data_list = []
    with open(file_path, 'r') as f:
        for line in f:
            values = line.strip().split(',')
            if len(values) >= 10:
                data_list.append([float(v) for v in values[:10]])

    data = np.array(data_list, dtype=np.float64)
    mass = data[:, 0]
    position = data[:, 1:4]
    velocity = data[:, 4:7]
    acceleration = data[:, 7:10]
    return mass, position, velocity, acceleration


def getAcc_cpp(mass, position, softening, G):
    position = np.ascontiguousarray(position, dtype=np.float64)
    mass = np.ascontiguousarray(mass, dtype=np.float64)
    return nbody_cpp.get_acc(position, mass, G, softening)


def euler_integration_cpp_acc(mass, position, velocity, dt, softening, G):
    a = getAcc_cpp(mass, position, softening, G)
    velocity = velocity + a * dt
    position = position + velocity * dt
    return velocity, position


def runge_kutta_integration_cpp_acc(mass, position, velocity, dt, softening, G):
    a1 = getAcc_cpp(mass, position, softening, G)
    k1_v = a1 * dt
    k1_x = velocity * dt

    a2 = getAcc_cpp(mass, position + 0.5 * k1_x, softening, G)
    k2_v = a2 * dt
    k2_x = (velocity + 0.5 * k1_v) * dt

    a3 = getAcc_cpp(mass, position + 0.5 * k2_x, softening, G)
    k3_v = a3 * dt
    k3_x = (velocity + 0.5 * k2_v) * dt

    a4 = getAcc_cpp(mass, position + k3_x, softening, G)
    k4_v = a4 * dt
    k4_x = (velocity + k3_v) * dt

    velocity = velocity + (k1_v + 2 * k2_v + 2 * k3_v + k4_v) / 6
    position = position + (k1_x + 2 * k2_x + 2 * k3_x + k4_x) / 6
    return velocity, position


def create_spheres(mass, position):
    spheres = []
    rainbow_colors = [
        color.red, color.orange, color.yellow,
        color.green, color.blue, color.cyan, color.white
    ]
    for i in range(len(mass)):
        new_sphere = sphere(
            m=mass[i],
            pos=vector(float(position[i, 0]), float(position[i, 1]), float(position[i, 2])),
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
    except Exception:
        error_log_path = os.path.join(os.getcwd(), 'error_log.txt')
        with open(error_log_path, 'w', encoding='utf-8') as f:
            f.write("An error occurred during the simulation:\n")
            traceback.print_exc(file=f)
        print("error_log.txt")