
import numpy as np
import os
from vpython import *
import time
import argparse


scene = canvas(width=1800, height=600)
gdv = graph(title="v-t plot", width=300, height=300, x=0, y=0, xtitle="t(s)", ytitle="v(m/s)")
gda = graph(title="a-t plot", width=300, height=300, x=0, y=0, xtitle="t(s)", ytitle="a(m/s^2)")

def toggle_simulation():
    global running
    running = not running
    if running:
        print("Simulation resumed")
    else:
        print("Simulation paused")

toggle_button = button(text='PAUSE', bind=toggle_simulation)

def read_data_generator(file_path):
    full_path = os.path.join('simulation_data', file_path)
    with open(full_path, 'r') as file:
        current_data = []
        current_time = None
        for line in file:
            line = line.strip()
            if "Simulation started at" in line:
                simulation_start = line.split(" at ")[1]
            elif line.startswith("time"):
                if current_data:
                    yield current_time, current_data
                current_time = float(line.split(":")[1])
                current_data = []
            else:
                data_values = tuple(map(float, line.split(',')))
                current_data.append(data_values)
        if current_data:
            yield current_time, current_data

parser = argparse.ArgumentParser()
parser.add_argument('file_path', type=str)
parser.add_argument('rate', type=float)
parser.add_argument('scene_center', type=int)
args = parser.parse_args()


fps_graph = graph(title="FPS-t plot", width=300, height=300, x=0, y=0, xtitle="t(s)", ytitle="FPS")
fps_curve = gcurve(graph=fps_graph, color=color.blue)
fps_label = label(pos=vector(20, 20, 0), text='FPS: ', height=16, color=color.white, align='left', box=False)
start_time = time.time()
last_time = start_time
frame_count = 0
fps_update_interval = 1

scene_center = args.scene_center
file_path = os.path.relpath(args.file_path)
data_generator = read_data_generator(file_path)
running = True
spheres = []
rainbow_colors = [color.red, color.orange, color.yellow, color.green, color.blue, color.cyan, color.white]

try:
    current_time, data = next(data_generator)
    for i, obj_data in enumerate(data):
        mass = obj_data[0]
        pos = vec(obj_data[1], obj_data[2], obj_data[3])
        vel = vec(obj_data[4], obj_data[5], obj_data[6])
        acc = vec(obj_data[7], obj_data[8], obj_data[9])
        new_sphere = sphere(pos=pos, color=rainbow_colors[i % len(rainbow_colors)], radius=0.5, make_trail=True, retain=10)
        new_sphere.m = mass
        new_sphere.v = vel
        new_sphere.a = acc
        spheres.append(new_sphere)
except StopIteration:
    pass

v_curve = gcurve(graph=gdv, color=color.red)
a_curve = gcurve(graph=gda, color=color.red)

while True:
    rate(args.rate)
    scene.center = spheres[scene_center].pos

    if not running:
        time.sleep(0.1)
        continue

    current_time_fps = time.time()
    frame_count += 1

    if current_time_fps - last_time >= fps_update_interval:
        fps = frame_count / fps_update_interval
        fps_label.text = 'FPS: {:.2f}'.format(fps)
        fps_curve.plot(current_time_fps - start_time, fps)
        frame_count = 0
        last_time = current_time_fps

    try:
        current_time, data = next(data_generator)
        for i, obj_data in enumerate(data):
            mass = obj_data[0]
            pos = vec(obj_data[1], obj_data[2], obj_data[3])
            vel = vec(obj_data[4], obj_data[5], obj_data[6])
            acc = vec(obj_data[7], obj_data[8], obj_data[9])

            spheres[i].pos = pos
            spheres[i].v = vel
            spheres[i].a = acc
            spheres[i].m = mass

        v_mag = mag(spheres[scene_center].v)
        a_mag = mag(spheres[scene_center].a)
        v_curve.plot(pos=(current_time, v_mag))
        a_curve.plot(pos=(current_time, a_mag))

    except StopIteration:
        print("No more data to read.")
        break
