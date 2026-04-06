
import datetime  
import os
import numpy as np
import cupy as cp

def ensure_directory_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def create_simulation_folder(folder_path, data_filename, script_filename, initial_conditions):

    full_path = ensure_directory_exists(folder_path)
    

    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time_2 = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    data_filename_base, _ = os.path.splitext(os.path.basename(data_filename))
    script_filename_base, _ = os.path.splitext(os.path.basename(script_filename))
    folder_name = f"{start_time_2}-{data_filename_base}-{script_filename_base}"
    full_folder_path = os.path.join(full_path, folder_name)
    

    os.makedirs(full_folder_path, exist_ok=True)
    

    data_file_name = f"{folder_name}.txt"
    data_file_path = os.path.join(full_folder_path, data_file_name)
    with open(data_file_path, 'w', encoding='utf-8') as file:
        file.write(f"Simulation started at {start_time}\n")
    

    introduction_file_path = os.path.join(full_folder_path, 'Introduction.txt')
    with open(introduction_file_path, 'w', encoding='utf-8') as intro_file:
        intro_file.write(f"數據名稱：{folder_name}\n")
        intro_file.write(f"模擬開始時間：{start_time}\n")
    

    dt = initial_conditions.get('dt')
    rate = initial_conditions.get('rate')
    max_day = initial_conditions.get('max_day')
    integration_method = initial_conditions.get('integration_method')
    collision_option = initial_conditions.get('collision_option')
    cuda_option = initial_conditions.get('cuda_option')
    

    initial_conditions_file_path = os.path.join(full_folder_path, 'initial_conditions.txt')
    with open(initial_conditions_file_path, 'w', encoding='utf-8') as ic_file:
        ic_file.write(f"{dt}\n")
        ic_file.write(f"{rate}\n")
        ic_file.write(f"{max_day}\n")
        ic_file.write(f"{data_filename_base}\n") 
        ic_file.write(f"{integration_method}\n")
        ic_file.write(f"{collision_option}\n")
        ic_file.write(f"{cuda_option}\n")
        ic_file.write(f"{start_time}\n") 
        ic_file.write(f"{script_filename_base}\n") 
    
    return data_file_path



def write_pos_to_file(mass_array, position_array, velocity_array, acceleration_array, filename, time):

    if isinstance(mass_array, cp.ndarray):
        mass_array = cp.asnumpy(mass_array)
    if isinstance(position_array, cp.ndarray):
        position_array = cp.asnumpy(position_array)
    if isinstance(velocity_array, cp.ndarray):
        velocity_array = cp.asnumpy(velocity_array)
    if isinstance(acceleration_array, cp.ndarray):
        acceleration_array = cp.asnumpy(acceleration_array)
    
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"time:{time}\n")
        number_of_elements = len(mass_array)
        for i in range(number_of_elements):
            mass = mass_array[i]
            pos = position_array[i]
            vel = velocity_array[i]
            acc = acceleration_array[i]

            mass_value = float(mass)
            pos_values = [float(v) for v in pos]
            vel_values = [float(v) for v in vel]
            acc_values = [float(v) for v in acc]
            file.write(f"{mass_value},{pos_values[0]},{pos_values[1]},{pos_values[2]},"
                       f"{vel_values[0]},{vel_values[1]},{vel_values[2]},"
                       f"{acc_values[0]},{acc_values[1]},{acc_values[2]}\n")
