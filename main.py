#main.py
#testgit
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import os
import subprocess
import zipfile
import shutil
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  
import numpy as np

extract_file_display_map = {}


current_user = {}

def authenticate_user(username, password):

    url = "http://petricho.ddns.net:5000/api/login" 
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:

            user_data = response.json()
            current_user.update(user_data)  # 確保 user_data 包含 user_id
            return True
        elif response.status_code == 401:
            return False
        else:
            messagebox.showerror("錯誤", f"登入失敗，狀態碼：{response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        messagebox.showerror("錯誤", f"請求後端時出現錯誤：{e}")
        return False

def register_user(username, password, confirm_password):

    if password != confirm_password:
        messagebox.showerror("錯誤", "密碼與確認密碼不符")
        return False

    if len(username) < 3 or len(password) < 6:
        messagebox.showerror("錯誤", "使用者名稱至少3個字元，密碼至少6個字元")
        return False

    url = "http://petricho.ddns.net:5000/api/register"  # 更新為您的後端 API 地址
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 201:
            messagebox.showinfo("成功", "註冊成功，請登入")
            return True
        elif response.status_code == 409:
            messagebox.showerror("錯誤", "使用者名稱已存在")
            return False
        else:
            error_msg = response.json().get('error', '註冊失敗')
            messagebox.showerror("錯誤", f"註冊失敗：{error_msg}")
            return False
    except requests.exceptions.RequestException as e:
        messagebox.showerror("錯誤", f"請求後端時出現錯誤：{e}")
        return False

def logout(root_window):

    root_window.destroy()

    current_user.clear()

    show_login_window()

def show_register_window():

    register_window = tk.Toplevel()
    register_window.title("註冊")
    register_window.geometry("300x250")


    tk.Label(register_window, text="使用者名稱:").pack(pady=10)
    username_entry = tk.Entry(register_window)
    username_entry.pack()


    tk.Label(register_window, text="密碼:").pack(pady=10)
    password_entry = tk.Entry(register_window, show='*')
    password_entry.pack()


    tk.Label(register_window, text="確認密碼:").pack(pady=10)
    confirm_password_entry = tk.Entry(register_window, show='*')
    confirm_password_entry.pack()

    def register():
        """
        註冊按鈕的回調函數，進行使用者註冊
        """
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()
        if username and password and confirm_password:
            if register_user(username, password, confirm_password):
                register_window.destroy()
        else:
            messagebox.showwarning("輸入錯誤", "請填寫所有欄位")


    tk.Button(register_window, text="註冊", command=register).pack(pady=20)

def show_login_window():

    login_window = tk.Tk()
    login_window.title("登入")
    login_window.geometry("300x250")


    tk.Label(login_window, text="使用者名稱:").pack(pady=10)
    username_entry = tk.Entry(login_window)
    username_entry.pack()
    username_entry.insert(0, "test2")  # 在此處輸入您想要的預設使用者名稱


    tk.Label(login_window, text="密碼:").pack(pady=10)
    password_entry = tk.Entry(login_window, show='*')
    password_entry.pack()
    password_entry.insert(0, "000000")  # 在此處輸入您想要的預設密碼

    def login():

        username = username_entry.get()
        password = password_entry.get()
        if username and password:

            if authenticate_user(username, password):

                login_window.destroy()
                show_main_window()
            else:
                messagebox.showerror("登入失敗", "使用者名稱或密碼錯誤")
        else:
            messagebox.showwarning("輸入錯誤", "請輸入使用者名稱和密碼")


    tk.Button(login_window, text="登入", command=login).pack(pady=10)


    tk.Button(login_window, text="註冊", command=show_register_window).pack(pady=10)

    login_window.mainloop()

def show_main_window():

    root = tk.Tk()
    root.geometry("1000x700") 
    root.title("模擬器")


    logout_button = tk.Button(root, text="登出", command=lambda: logout(root))
    logout_button.place(x=750, y=10)


    user_info_label = tk.Label(root, text=f"當前使用者：{current_user.get('username', '')}")
    user_info_label.place(x=650, y=10)


    style = ttk.Style()


    style.configure('TNotebook.Tab', font=('Arial', 14), padding=[10, 0])


    notebook = ttk.Notebook(root, style='TNotebook')
    notebook.pack(expand=True, fill='both')


    tab1 = tk.Frame(notebook)
    tab2 = tk.Frame(notebook)
    tab3 = tk.Frame(notebook)


    notebook.add(tab1, text="模擬")
    notebook.add(tab2, text="回放")

    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\    
    ### 分頁一內容（模擬） ###
    def set_axes_equal(ax):

        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()
    
        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)
    

        plot_radius = 0.5 * max([x_range, y_range, z_range])
    
        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])    
    def run_program(
        dt_value,
        rate_value,
        max_day_value,
        integration_method,
        collision_option,
        cuda_option,
        backend_option
    ):

        # 獲取當前選擇的資料集名稱
        folder_name = selected_data_variable.get()
        if not folder_name:
            messagebox.showerror("錯誤", "請選擇一個資料集")
            return
    
        # 建立 dt 參數的對應字典
        dt_map = {
            "1": "1",
            "30": "30",
            "60": "60",
            "60*30": "1800",
            "60*60": "3600",
            "60*60*2": "7200",
            "60*60*24": "86400",
            "60*60*24*365": "31536000",
        }
        dt = dt_map.get(dt_value, "1800")
    

        rate_map = {"1": "1", "10": "10", "30": "30", "60": "60", "120": "120", "無限制": "1000"}
        rate = rate_map.get(rate_value, "120")  # 預設值為 "120"
    

        max_day_map = {"1": "1", "30": "30", "365": "365", "5y": "1825"}
        max_day = max_day_map.get(max_day_value, "365")  # 預設值為 "365"
    

        scene_center = scene_center_entry.get()
        if not scene_center.isdigit():
            messagebox.showerror("錯誤", "場景中心應為整數")
            return
    

        folder_path = os.path.join('data', folder_name)
        folder_txt_file = os.path.join(folder_path, f"{folder_name}.txt")
    
        if not os.path.exists(folder_txt_file):
            messagebox.showerror("錯誤", f"文件 {folder_txt_file} 不存在")
            return
    

        if backend_option == "Python":
            script_name = "simulation.py"
        else:
            script_name = "simulation_cpp.py"
    
        integration_methods_map = {
            "Euler": "euler",
            "Runge-Kutta": "runge-kutta",
        }
        integration_arg = integration_methods_map.get(integration_method, "euler")
    
        collision_arg = "yes" if collision_option == "啟用" else "no"
        cuda_arg = "yes" if cuda_option == "使用" else "no"
    

        cmd = [
            "python",  # 使用當前 Python 解釋器
            script_name,
            dt,               # dt
            folder_txt_file,  # file_path
            rate,             # rate
            scene_center,     # scene_center
            max_day,          # max_day
            integration_arg,  # integration_method
            collision_arg,    # collision_option
            cuda_arg,         # cuda_option
        ]
    

        print("Command to execute:")
        print(' '.join(map(str, cmd)))
    
        try:
            p = subprocess.Popen(cmd)
            return p
        except Exception as e:
            messagebox.showerror("錯誤", f"執行程式時發生錯誤：{e}")
    
    def update_data_tree():

        folder_path = 'data'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    

        for item in data_tree.get_children():
            data_tree.delete(item)
    

        for folder in folders:
            introduction_file = os.path.join(folder_path, folder, 'Introduction.txt')
            description = ""
            if os.path.exists(introduction_file):
                with open(introduction_file, 'r', encoding='utf-8') as f:
                    description = f.read().strip()
            else:
                description = "無"
            data_tree.insert('', 'end', values=(folder, description))
    
    def on_data_tree_select(event):

        selected_item = data_tree.selection()
        if selected_item:
            item = data_tree.item(selected_item)
            folder_name = item['values'][0]  # 資料集名稱

            selected_data_variable.set(folder_name)

            introduction_text_widget.config(state='normal')
            introduction_text_widget.delete(1.0, tk.END)
            introduction_text_widget.insert(tk.END, item['values'][1])
            introduction_text_widget.config(state='disabled')
            

            plot_file_path = os.path.join('data', folder_name, f"{folder_name}.txt")
            if os.path.exists(plot_file_path):
                try:

                    ax.cla()
                    ax.set_title("3D")
                    ax.set_xlabel("X")
                    ax.set_ylabel("Y")
                    ax.set_zlabel("Z")
                    
                    masses = []
                    pos_xs = []
                    pos_ys = []
                    pos_zs = []

                    with open(plot_file_path, 'r') as f:
                        for line in f:
                            parts = line.strip().split(',')
                            if len(parts) >= 4:
                                try:
                                    mass = float(parts[0])
                                    pos_x = float(parts[1])
                                    pos_y = float(parts[2])
                                    pos_z = float(parts[3])
                                    masses.append(mass * 5) 
                                    pos_xs.append(pos_x)
                                    pos_ys.append(pos_y)
                                    pos_zs.append(pos_z)
                                except ValueError:
                                    continue
                    

                    scatter = ax.scatter(pos_xs, pos_ys, pos_zs, s=5, c='b', marker='.', alpha=0.6)
                    

                    set_axes_equal(ax)
                    

                    canvas.draw()
                except Exception as e:
                    messagebox.showerror("錯誤", f"更新 3D 座標圖時發生錯誤：{e}")
            else:

                ax.cla()
                ax.set_title("3D")
                ax.set_xlabel("X")
                ax.set_ylabel("Y")
                ax.set_zlabel("Z")
                canvas.draw()
                messagebox.showwarning("警告", f"找不到資料集的數據檔案：{plot_file_path}")

    
    def show_add_data_window():
        add_window = tk.Toplevel()
        add_window.title("新增資料")
        add_window.geometry("1100x650")
    

        sphere_number = tk.IntVar(value=1)  

        sphere_data = {
            'mass': np.array([]),
            'x': np.array([]),
            'y': np.array([]),
            'z': np.array([]),
            'vx': np.array([]),
            'vy': np.array([]),
            'vz': np.array([]),
            'ax': np.array([]),
            'ay': np.array([]),
            'az': np.array([])
        }
        

        fig_add = plt.Figure(figsize=(5, 5))
        
        ax_add = fig_add.add_subplot(111, projection='3d')
        ax_add.set_title("3D")
        ax_add.set_xlabel("X")
        ax_add.set_ylabel("Y")
        ax_add.set_zlabel("Z")


        scatter = ax_add.scatter([], [], [], s=5, c='b', marker='o', alpha=0.6)  

    

        canvas_add = FigureCanvasTkAgg(fig_add, master=add_window)
        canvas_add.draw()
        canvas_add.get_tk_widget().place(x=10, y=40, width=500, height=400)
    

        tk.Label(add_window, text="球體數量:").place(x=520, y=10)
        sphere_label = tk.Label(add_window, textvariable=sphere_number)
        sphere_label.place(x=600, y=10)
    

        input_frame = tk.LabelFrame(add_window, text="單球體生成")
        input_frame.place(x=520, y=40, width=550, height=200)
    

        tk.Label(input_frame, text="Mass:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        mass_entry = tk.Entry(input_frame)
        mass_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        mass_entry.insert(0, "1")  # 設置Mass的預設值為1
    

    

        position_frame = tk.LabelFrame(input_frame, text="Position")
        position_frame.grid(row=1, column=0, padx=5, pady=5, sticky='w')
    
        tk.Label(position_frame, text="X:").grid(row=0, column=0, padx=2, pady=2, sticky='e')
        pos_x_entry = tk.Entry(position_frame, width=20)
        pos_x_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        pos_x_entry.insert(0, "0")  # 設置Position X的預設值為0
    
        tk.Label(position_frame, text="Y:").grid(row=1, column=0, padx=2, pady=2, sticky='e')
        pos_y_entry = tk.Entry(position_frame, width=20)
        pos_y_entry.grid(row=1, column=1, padx=2, pady=2, sticky='w')
        pos_y_entry.insert(0, "0")  # 設置Position Y的預設值為0
    
        tk.Label(position_frame, text="Z:").grid(row=2, column=0, padx=2, pady=2, sticky='e')
        pos_z_entry = tk.Entry(position_frame, width=20)
        pos_z_entry.grid(row=2, column=1, padx=2, pady=2, sticky='w')
        pos_z_entry.insert(0, "0")  # 設置Position Z的預設值為0
    

        velocity_frame = tk.LabelFrame(input_frame, text="Velocity")
        velocity_frame.grid(row=1, column=1, padx=5, pady=5, sticky='w')
    
        tk.Label(velocity_frame, text="X:").grid(row=0, column=0, padx=2, pady=2, sticky='e')
        vel_x_entry = tk.Entry(velocity_frame, width=20)
        vel_x_entry.grid(row=0, column=1, padx=2, pady=2, sticky='w')
        vel_x_entry.insert(0, "0")  # 設置Velocity X的預設值為0
    
        tk.Label(velocity_frame, text="Y:").grid(row=1, column=0, padx=2, pady=2, sticky='e')
        vel_y_entry = tk.Entry(velocity_frame, width=20)
        vel_y_entry.grid(row=1, column=1, padx=2, pady=2, sticky='w')
        vel_y_entry.insert(0, "0")  # 設置Velocity Y的預設值為0
    
        tk.Label(velocity_frame, text="Z:").grid(row=2, column=0, padx=2, pady=2, sticky='e')
        vel_z_entry = tk.Entry(velocity_frame, width=20)
        vel_z_entry.grid(row=2, column=1, padx=2, pady=2, sticky='w')
        vel_z_entry.insert(0, "0")  # 設置Velocity Z的預設值為0
    

        acceleration_frame = tk.LabelFrame(input_frame, text="Acceleration")
        acceleration_frame.grid(row=1, column=2, padx=5, pady=5, sticky='w')
    
        tk.Label(acceleration_frame, text="X:").grid(row=0, column=0, padx=2, pady=2, sticky='e')
        acc_x_entry = tk.Entry(acceleration_frame, width=20)
        acc_x_entry.grid(row=0, column=1, padx=2, pady=2, sticky='w')
        acc_x_entry.insert(0, "0")  # 設置Acceleration X的預設值為0
    
        tk.Label(acceleration_frame, text="Y:").grid(row=1, column=0, padx=2, pady=2, sticky='e')
        acc_y_entry = tk.Entry(acceleration_frame, width=20)
        acc_y_entry.grid(row=1, column=1, padx=2, pady=2, sticky='w')
        acc_y_entry.insert(0, "0")  # 設置Acceleration Y的預設值為0
    
        tk.Label(acceleration_frame, text="Z:").grid(row=2, column=0, padx=2, pady=2, sticky='e')
        acc_z_entry = tk.Entry(acceleration_frame, width=20)
        acc_z_entry.grid(row=2, column=1, padx=2, pady=2, sticky='w')
        acc_z_entry.insert(0, "0")  
    

        for col in range(4):
            input_frame.grid_columnconfigure(col, weight=1)
    

        multiple_spheres_frame = tk.LabelFrame(add_window, text="多球體生成")
        multiple_spheres_frame.place(x=520, y=250, width=550, height=200)
    

        tk.Label(multiple_spheres_frame, text="Mass:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        multi_mass_entry = tk.Entry(multiple_spheres_frame)
        multi_mass_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        multi_mass_entry.insert(0, "1") 
    
        tk.Label(multiple_spheres_frame, text="球體集半徑:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        multi_main_radius_entry = tk.Entry(multiple_spheres_frame)
        multi_main_radius_entry.grid(row=0, column=3, padx=10, pady=10, sticky='w')
        multi_main_radius_entry.insert(0, "5")  
    

        multi_position_frame = tk.LabelFrame(multiple_spheres_frame, text="Position")
        multi_position_frame.grid(row=1, column=0, padx=5, pady=5, sticky='w')
    
        tk.Label(multi_position_frame, text="X:").grid(row=0, column=0, padx=2, pady=2, sticky='e')
        multi_pos_x_entry = tk.Entry(multi_position_frame, width=20)
        multi_pos_x_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        multi_pos_x_entry.insert(0, "0")  
    
        tk.Label(multi_position_frame, text="Y:").grid(row=1, column=0, padx=2, pady=2, sticky='e')
        multi_pos_y_entry = tk.Entry(multi_position_frame, width=20)
        multi_pos_y_entry.grid(row=1, column=1, padx=2, pady=2, sticky='w')
        multi_pos_y_entry.insert(0, "0") 
    
        tk.Label(multi_position_frame, text="Z:").grid(row=2, column=0, padx=2, pady=2, sticky='e')
        multi_pos_z_entry = tk.Entry(multi_position_frame, width=20)
        multi_pos_z_entry.grid(row=2, column=1, padx=2, pady=2, sticky='w')
        multi_pos_z_entry.insert(0, "0")
    

        multi_velocity_frame = tk.LabelFrame(multiple_spheres_frame, text="Velocity")
        multi_velocity_frame.grid(row=1, column=1, padx=5, pady=5, sticky='w')
    
        tk.Label(multi_velocity_frame, text="X:").grid(row=0, column=0, padx=2, pady=2, sticky='e')
        multi_vel_x_entry = tk.Entry(multi_velocity_frame, width=20)
        multi_vel_x_entry.grid(row=0, column=1, padx=2, pady=2, sticky='w')
        multi_vel_x_entry.insert(0, "0")  
    
        tk.Label(multi_velocity_frame, text="Y:").grid(row=1, column=0, padx=2, pady=2, sticky='e')
        multi_vel_y_entry = tk.Entry(multi_velocity_frame, width=20)
        multi_vel_y_entry.grid(row=1, column=1, padx=2, pady=2, sticky='w')
        multi_vel_y_entry.insert(0, "0")  
    
        tk.Label(multi_velocity_frame, text="Z:").grid(row=2, column=0, padx=2, pady=2, sticky='e')
        multi_vel_z_entry = tk.Entry(multi_velocity_frame, width=20)
        multi_vel_z_entry.grid(row=2, column=1, padx=2, pady=2, sticky='w')
        multi_vel_z_entry.insert(0, "0")  
    

        multi_acceleration_frame = tk.LabelFrame(multiple_spheres_frame, text="Acceleration")
        multi_acceleration_frame.grid(row=1, column=2, padx=5, pady=5, sticky='w')
    
        tk.Label(multi_acceleration_frame, text="X:").grid(row=0, column=0, padx=2, pady=2, sticky='e')
        multi_acc_x_entry = tk.Entry(multi_acceleration_frame, width=20)
        multi_acc_x_entry.grid(row=0, column=1, padx=2, pady=2, sticky='w')
        multi_acc_x_entry.insert(0, "0")  
    
        tk.Label(multi_acceleration_frame, text="Y:").grid(row=1, column=0, padx=2, pady=2, sticky='e')
        multi_acc_y_entry = tk.Entry(multi_acceleration_frame, width=20)
        multi_acc_y_entry.grid(row=1, column=1, padx=2, pady=2, sticky='w')
        multi_acc_y_entry.insert(0, "0") 
    
        tk.Label(multi_acceleration_frame, text="Z:").grid(row=2, column=0, padx=2, pady=2, sticky='e')
        multi_acc_z_entry = tk.Entry(multi_acceleration_frame, width=20)
        multi_acc_z_entry.grid(row=2, column=1, padx=2, pady=2, sticky='w')
        multi_acc_z_entry.insert(0, "0")  
    
 
        for col in range(4):
            multiple_spheres_frame.grid_columnconfigure(col, weight=1)
    
        def add_sphere():

            try:

                mass = float(mass_entry.get())
                pos_x = float(pos_x_entry.get())
                pos_y = float(pos_y_entry.get())
                pos_z = float(pos_z_entry.get())
                vel_x_val = float(vel_x_entry.get())
                vel_y_val = float(vel_y_entry.get())
                vel_z_val = float(vel_z_entry.get())
                acc_x_val = float(acc_x_entry.get())
                acc_y_val = float(acc_y_entry.get())
                acc_z_val = float(acc_z_entry.get())
    

                sphere_data['mass'] = np.append(sphere_data['mass'], mass)
                sphere_data['x'] = np.append(sphere_data['x'], pos_x)
                sphere_data['y'] = np.append(sphere_data['y'], pos_y)
                sphere_data['z'] = np.append(sphere_data['z'], pos_z)
                sphere_data['vx'] = np.append(sphere_data['vx'], vel_x_val)
                sphere_data['vy'] = np.append(sphere_data['vy'], vel_y_val)
                sphere_data['vz'] = np.append(sphere_data['vz'], vel_z_val)
                sphere_data['ax'] = np.append(sphere_data['ax'], acc_x_val)
                sphere_data['ay'] = np.append(sphere_data['ay'], acc_y_val)
                sphere_data['az'] = np.append(sphere_data['az'], acc_z_val)
    

                scatter._offsets3d = (sphere_data['x'], sphere_data['y'], sphere_data['z'])
                scatter.set_sizes(sphere_data['mass'] * 50)  # 調整大小
                canvas_add.draw_idle()
    

                mass_entry.delete(0, tk.END)
                pos_x_entry.delete(0, tk.END)
                pos_y_entry.delete(0, tk.END)
                pos_z_entry.delete(0, tk.END)
                vel_x_entry.delete(0, tk.END)
                vel_y_entry.delete(0, tk.END)
                vel_z_entry.delete(0, tk.END)
                acc_x_entry.delete(0, tk.END)
                acc_y_entry.delete(0, tk.END)
                acc_z_entry.delete(0, tk.END)
    

                sphere_number.set(sphere_number.get() + 1)
            except ValueError:
                messagebox.showerror("輸入錯誤", "請確保所有欄位都填寫為數字")
    
        def add_multiple_spheres():

            try:
                mass = float(multi_mass_entry.get())
                input_main_radius = float(multi_main_radius_entry.get())
                main_radius = input_main_radius
                pos_x = float(multi_pos_x_entry.get())
                pos_y = float(multi_pos_y_entry.get())
                pos_z = float(multi_pos_z_entry.get())
                vel_x_val = float(multi_vel_x_entry.get())
                vel_y_val = float(multi_vel_y_entry.get())
                vel_z_val = float(multi_vel_z_entry.get())
                acc_x_val = float(multi_acc_x_entry.get())
                acc_y_val = float(multi_acc_y_entry.get())
                acc_z_val = float(multi_acc_z_entry.get())
    
                spacing = 1  
                grid_x = np.arange(pos_x - main_radius, pos_x + main_radius + spacing, spacing)
                grid_y = np.arange(pos_y - main_radius, pos_y + main_radius + spacing, spacing)
                grid_z = np.arange(pos_z - main_radius, pos_z + main_radius + spacing, spacing)
                generated_spheres = 0
    
                for x in grid_x:
                    for y in grid_y:
                        for z in grid_z:

                            if (x - pos_x)**2 + (y - pos_y)**2 + (z - pos_z)**2 <= main_radius**2:
                                sphere_data['mass'] = np.append(sphere_data['mass'], mass)
                                sphere_data['x'] = np.append(sphere_data['x'], x)
                                sphere_data['y'] = np.append(sphere_data['y'], y)
                                sphere_data['z'] = np.append(sphere_data['z'], z)

                                sphere_data['vx'] = np.append(sphere_data['vx'], vel_x_val)
                                sphere_data['vy'] = np.append(sphere_data['vy'], vel_y_val)
                                sphere_data['vz'] = np.append(sphere_data['vz'], vel_z_val)
                                sphere_data['ax'] = np.append(sphere_data['ax'], acc_x_val)
                                sphere_data['ay'] = np.append(sphere_data['ay'], acc_y_val)
                                sphere_data['az'] = np.append(sphere_data['az'], acc_z_val)
    
                                generated_spheres += 1
    
                if generated_spheres > 0:
                    scatter._offsets3d = (sphere_data['x'], sphere_data['y'], sphere_data['z'])
                    scatter.set_sizes(np.full(len(sphere_data['mass']), 5.0))
                    canvas_add.draw_idle()
    

                multi_mass_entry.delete(0, tk.END)
                multi_main_radius_entry.delete(0, tk.END)
                multi_pos_x_entry.delete(0, tk.END)
                multi_pos_y_entry.delete(0, tk.END)
                multi_pos_z_entry.delete(0, tk.END)
                multi_vel_x_entry.delete(0, tk.END)
                multi_vel_y_entry.delete(0, tk.END)
                multi_vel_z_entry.delete(0, tk.END)
                multi_acc_x_entry.delete(0, tk.END)
                multi_acc_y_entry.delete(0, tk.END)
                multi_acc_z_entry.delete(0, tk.END)
    
                sphere_number.set(sphere_number.get() + generated_spheres)
            except ValueError:
                messagebox.showerror("輸入錯誤", "請確保所有欄位都填寫為數字")
    

        add_button = tk.Button(add_window, text="新增", command=add_sphere)
        add_button.place(x=950, y=200, width=50, height=30)
    

        add_multiple_button = tk.Button(add_window, text="新增多球體", command=add_multiple_spheres)
        add_multiple_button.place(x=950, y=400, width=100, height=30)
    

        bottom_frame = tk.LabelFrame(add_window, text="編輯詳細資料")
        bottom_frame.place(x=10, y=450, width=500, height=200)
    

        tk.Label(bottom_frame, text="命名:").place(x=10, y=10)
        name_entry = tk.Entry(bottom_frame, width=50)
        name_entry.place(x=70, y=10)
    

        tk.Label(bottom_frame, text="介紹:").place(x=10, y=50)
        intro_text = tk.Text(bottom_frame, height=4, width=50)
        intro_text.place(x=70, y=50)
    
        def confirm_add():

            dataset_name = name_entry.get().strip()
            introduction = intro_text.get("1.0", tk.END).strip()
    
            if not dataset_name:
                messagebox.showwarning("輸入錯誤", "請輸入資料集名稱")
                return
            if not sphere_data['mass'].size:
                messagebox.showwarning("輸入錯誤", "請至少新增一個球體資料")
                return
    
            target_folder = os.path.join('data', dataset_name)
            if os.path.exists(target_folder):
                messagebox.showerror("錯誤", f"資料集名稱 '{dataset_name}' 已存在")
                return
    
            try:
                os.makedirs(target_folder)
                txt_file_path = os.path.join(target_folder, f"{dataset_name}.txt")
    

                with open(txt_file_path, 'w') as f:
                    for idx in range(len(sphere_data['mass'])):
                        mass = sphere_data['mass'][idx]
                        pos_x = sphere_data['x'][idx]
                        pos_y = sphere_data['y'][idx]
                        pos_z = sphere_data['z'][idx]
                        vel_x_val = sphere_data['vx'][idx]
                        vel_y_val = sphere_data['vy'][idx]
                        vel_z_val = sphere_data['vz'][idx]
                        acc_x_val = sphere_data['ax'][idx]
                        acc_y_val = sphere_data['ay'][idx]
                        acc_z_val = sphere_data['az'][idx]
    
                        f.write(f"{mass},{pos_x},{pos_y},{pos_z},{vel_x_val},{vel_y_val},{vel_z_val},{acc_x_val},{acc_y_val},{acc_z_val}\n")
    

                intro_file_path = os.path.join(target_folder, 'Introduction.txt')
                with open(intro_file_path, 'w', encoding='utf-8') as f:
                    f.write(introduction)
    
                messagebox.showinfo("成功", f"資料集 '{dataset_name}' 已成功新增")
                add_window.destroy()

                update_data_tree()
            except Exception as e:
                messagebox.showerror("錯誤", f"保存資料時發生錯誤：{e}")
    

        confirm_button = tk.Button(bottom_frame, text="確定", command=confirm_add)
        confirm_button.place(x=400, y=120, width=80, height=30)
    
    
    

    selected_data_variable = tk.StringVar()
    selected_data_variable.set("") 
    

    data_frame = tk.LabelFrame(tab1, text="資料選擇")
    data_frame.place(x=10, y=10, width=960, height=440)
    

    data_tree = ttk.Treeview(data_frame, columns=('DataName'), show='headings')
    data_tree.heading('DataName', text='資料名稱')
    # data_tree.heading('Description', text='介紹')
    data_tree.column('DataName', width=200)
    # data_tree.column('Description', width=130)
    data_tree.place(x=520, y=10, width=340, height=180)
    

    data_tree.bind('<<TreeviewSelect>>', on_data_tree_select)
    

    tree_scrollbar = tk.Scrollbar(data_frame, orient='vertical', command=data_tree.yview)
    data_tree.configure(yscrollcommand=tree_scrollbar.set)
    tree_scrollbar.place(x=860, y=10, height=180)
    

    refresh_data_button = tk.Button(data_frame, text="刷新", command=update_data_tree)
    refresh_data_button.place(x=620, y=250)

    add_data_button = tk.Button(data_frame, text="新增資料", command=show_add_data_window)
    add_data_button.place(x=710, y=250)
    

    plot_frame = tk.Frame(data_frame, bg="white")
    plot_frame.place(x=10, y=10, width=500, height=400)
    

    fig = plt.Figure(figsize=(3.4, 1.8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title("3D ")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill='both')
    

    introduction_text_widget = tk.Text(
        data_frame, height=10, width=40, wrap='word')
    introduction_text_widget.place(x=520, y=200, width=340, height=50)
    introduction_text_widget.config(state='disabled')
    

    update_data_tree()
    

    param_frame = tk.LabelFrame(tab1, text="參數設定")
    param_frame.place(x=10, y=450, width=510, height=180)
    

    dt_label = tk.Label(param_frame, text="dt:", anchor="w")
    dt_label.place(x=10, y=10)
    dt_options = ["1", "30", "60", "60*30", "60*60",
                  "60*60*2", "60*60*24", "60*60*24*365"]
    dt_variable = tk.StringVar(param_frame)
    dt_variable.set(dt_options[3]) 
    dt_menu = tk.OptionMenu(param_frame, dt_variable, *dt_options)
    dt_menu.place(x=120, y=10)
    

    rate_label = tk.Label(param_frame, text="rate:", anchor="w")
    rate_label.place(x=10, y=50)
    rate_options = ["1", "10", "30", "60", "120", "無限制"]
    rate_variable = tk.StringVar(param_frame)
    rate_variable.set(rate_options[4]) 
    rate_menu = tk.OptionMenu(param_frame, rate_variable, *rate_options)
    rate_menu.place(x=120, y=50)
    

    max_day_label = tk.Label(param_frame, text="max_day:", anchor="w")
    max_day_label.place(x=10, y=90)
    max_day_options = ["1", "30", "365", "5y"]
    max_day_variable = tk.StringVar(param_frame)
    max_day_variable.set(max_day_options[1])  
    max_day_menu = tk.OptionMenu(param_frame, max_day_variable, *max_day_options)
    max_day_menu.place(x=120, y=90)
    

    scene_center_label = tk.Label(param_frame, text="scene_center:", anchor="w")
    scene_center_label.place(x=10, y=130)
    scene_center_entry = tk.Entry(param_frame,width=10)
    scene_center_entry.insert(0, "0")
    scene_center_entry.place(x=120, y=130)
    

    integration_label = tk.Label(param_frame, text="積分方法:", anchor="w")
    integration_label.place(x=200, y=10)
    integration_options = ["Euler", "Runge-Kutta"]
    integration_variable = tk.StringVar(param_frame)
    integration_variable.set(integration_options[0]) 
    integration_menu = tk.OptionMenu(param_frame, integration_variable, *integration_options)
    integration_menu.place(x=320, y=10)
    

    collision_label = tk.Label(param_frame, text="碰撞檢測:", anchor="w")
    collision_label.place(x=200, y=50)
    collision_options = ["啟用", "禁用"]
    collision_variable = tk.StringVar(param_frame)
    collision_variable.set(collision_options[0]) 
    collision_menu = tk.OptionMenu(param_frame, collision_variable, *collision_options)
    collision_menu.place(x=320, y=50)
    

    cuda_label = tk.Label(param_frame, text="CUDA:", anchor="w")
    cuda_label.place(x=200, y=90)
    cuda_options = ["使用", "不使用"]
    cuda_variable = tk.StringVar(param_frame)
    cuda_variable.set(cuda_options[0]) 
    cuda_menu = tk.OptionMenu(param_frame, cuda_variable, *cuda_options)
    cuda_menu.place(x=320, y=90)
    

    backend_label = tk.Label(param_frame, text="語言:", anchor="w")
    backend_label.place(x=200, y=130)

    backend_options = ["Python", "C++"]
    backend_variable = tk.StringVar(param_frame)
    backend_variable.set(backend_options[0])

    backend_menu = tk.OptionMenu(param_frame, backend_variable, *backend_options)
    backend_menu.place(x=320, y=130)

    run_button = tk.Button(
        tab1,
        text="執行",
        command=lambda: run_program(
            dt_value=dt_variable.get(),
            rate_value=rate_variable.get(),
            max_day_value=max_day_variable.get(),
            integration_method=integration_variable.get(),
            collision_option=collision_variable.get(),
            cuda_option=cuda_variable.get(),
            backend_option=backend_variable.get()
        ),
    )
    run_button.place(x=700, y=520, width=100, height=50)
    run_button.config(font=("Arial", 14,'bold'))



    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ### 分頁二內容（回放） ###
    def record_run_program(rate_value, selected_item):
        """
        執行回放程式，傳遞相對路徑給回放.py
        """

        rate_map = {"1": "1", "10": "10", "30": "30",
                    "60": "60", "120": "120", "240": "240", "無限制": "1000"}
        rate = rate_map.get(rate_value, "1000") 
        scene_center = record_scene_center_entry.get() 


        if not selected_item:
            messagebox.showwarning("警告", "請選擇一個記錄文件")
            return
        item = playback_tree.item(selected_item)
        folder_name = item['values'][0]


        data_file_name = f"{folder_name}.txt"
        file_path = os.path.join(folder_name, data_file_name)  


        full_file_path = os.path.join('simulation_data', file_path)
        if not os.path.exists(full_file_path):
            messagebox.showerror("錯誤", f"資料檔案 {full_file_path} 不存在")
            return


        try:
            p = subprocess.Popen(
                ["python", "playback.py", file_path, rate, scene_center])
            return p  
        except Exception as e:
            messagebox.showerror("錯誤", f"無法啟動回放腳本：{e}")

    def fetch_file_list_from_backend():
        """
        從後端獲取文件列表
        """
        url = "http://petricho.ddns.net:5000/api/files"  
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                file_list = response.json()  
                print(f"收到的文件列表：{file_list}")
                return file_list
            else:
                messagebox.showerror("錯誤", f"無法從後端獲取文件列表，狀態碼：{response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            messagebox.showerror("錯誤", f"請求後端時出現錯誤：{e}")
            return []

    def download_file_from_backend(simulation_id, simulation_name):
        """
        從後端下載指定的文件，並指定解壓後的文件夾名稱
        """
        url = f"http://petricho.ddns.net:5000/api/files/{simulation_id}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'download_url' in data:
                    download_url = data['download_url']
                    print(f"收到的下載 URL：{download_url}")

                    download_and_extract_zip(download_url, simulation_name)

                    update_playback_file_list()
                else:
                    messagebox.showerror("錯誤", f"後端未返回下載 URL，響應內容：{data}")
            else:
                messagebox.showerror("錯誤", f"無法從後端獲取下載 URL，狀態碼：{response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("錯誤", f"請求後端時出現錯誤：{e}")

    def download_and_extract_zip(url, folder_name):

        base_folder_path = 'simulation_data'
        if not os.path.exists(base_folder_path):
            os.makedirs(base_folder_path)


        extraction_path = os.path.join(base_folder_path, folder_name)
        if not os.path.exists(extraction_path):
            os.makedirs(extraction_path)

        zip_file_path = os.path.join(base_folder_path, 'temp_download.zip')

        try:
            print(f"正在下載 ZIP 文件：{url}")
            response = requests.get(url, stream=True)
            if response.status_code == 200:

                with open(zip_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"ZIP 文件已下載到：{zip_file_path}")


                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extraction_path)
                print(f"ZIP 文件已解壓縮到：{extraction_path}")


                os.remove(zip_file_path)
                print(f"已刪除 ZIP 文件：{zip_file_path}")

                messagebox.showinfo("成功", f"文件已下載並解壓縮到 {extraction_path}")
            else:
                messagebox.showerror("錯誤", f"無法下載 ZIP 文件，狀態碼：{response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("錯誤", f"下載 ZIP 文件時出現錯誤：{e}")
        except zipfile.BadZipFile:
            messagebox.showerror("錯誤", "下載的文件不是有效的 ZIP 文件")
        except Exception as e:
            messagebox.showerror("錯誤", f"解壓縮 ZIP 文件時出現錯誤：{e}")

    def update_playback_file_list():

        folder_path = 'simulation_data'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        folders = [f for f in os.listdir(folder_path)
                   if os.path.isdir(os.path.join(folder_path, f))]

        for item in playback_tree.get_children():
            playback_tree.delete(item)

        for folder in folders:
            initial_conditions_file = os.path.join(
                folder_path, folder, 'initial_conditions.txt')
            if not os.path.exists(initial_conditions_file):
                continue 
            try:
                with open(initial_conditions_file, 'r', encoding='utf-8') as f:
                    lines = f.read().splitlines()
                    if len(lines) >= 9:

                        dt = float(lines[0].strip())
                        rate = float(lines[1].strip())
                        max_day = float(lines[2].strip())
                        data_filename_base = lines[3].strip()
                        integration_method = lines[4].strip()
                        collision_option = lines[5].strip()
                        cuda_option = lines[6].strip()
                        start_time = lines[7].strip()
                        script_filename_base = lines[8].strip()
                        filename = folder
                        playback_tree.insert('', 'end', values=(
                            filename, dt, data_filename_base, integration_method, collision_option, cuda_option, start_time))
            except Exception as e:
                print(f"讀取 {initial_conditions_file} 時發生錯誤：{e}")

    def on_playback_tree_select(event):

        selected_item = playback_tree.selection()
        if selected_item:
            item = playback_tree.item(selected_item)
            folder_name = item['values'][0]
            folder_path_full = os.path.join('simulation_data', folder_name)
            introduction_file = os.path.join(folder_path_full, 'Introduction.txt')
            if os.path.exists(introduction_file):
                try:
                    with open(introduction_file, 'r', encoding='utf-8') as f:
                        intro_text = f.read()
                    record_introduction_text_widget.config(state='normal')
                    record_introduction_text_widget.delete(1.0, tk.END)
                    record_introduction_text_widget.insert(tk.END, intro_text)
                    record_introduction_text_widget.config(state='disabled')
                except Exception as e:
                    messagebox.showerror("錯誤", f"讀取 Introduction.txt 時發生錯誤：{e}")
            else:
                record_introduction_text_widget.config(state='normal')
                record_introduction_text_widget.delete(1.0, tk.END)
                record_introduction_text_widget.insert(tk.END, "無")
                record_introduction_text_widget.config(state='disabled')


    download_frame = tk.LabelFrame(tab2, text="下載")
    download_frame.place(x=10, y=10, width=900, height=200)


    file_tree = ttk.Treeview(download_frame, columns=(
        'simulation_id', 'simulation_name', 'dt', 'description', 'integration_method', 'collision_option', 'cuda_option', 'created_at'), show='headings')
    
    file_tree.heading('simulation_id', text='Simulation ID')
    file_tree.heading('simulation_name', text='文件名')
    file_tree.heading('dt', text='dt')
    file_tree.heading('description', text='初始資料')
    file_tree.heading('integration_method', text='積分方法')
    file_tree.heading('collision_option', text='碰撞檢測')
    file_tree.heading('cuda_option', text='CUDA')
    file_tree.heading('created_at', text='日期')
    
    file_tree.column('simulation_id', width=0, stretch=False) 
    file_tree.column('simulation_name', width=150)
    file_tree.column('dt', width=50)
    file_tree.column('description', width=80)
    file_tree.column('integration_method', width=80)
    file_tree.column('collision_option', width=50)
    file_tree.column('cuda_option', width=50)
    file_tree.column('created_at', width=100)

    
    file_tree.place(x=10, y=10, width=850, height=120)

 







    def load_file_list():
        print("正在加載文件列表...")
        file_list = fetch_file_list_from_backend()
        print(f"收到的文件列表：{file_list}")

        for item in file_tree.get_children():
            file_tree.delete(item)

        for file in file_list:
            simulation_id = file.get('simulation_id', 'N/A')
            simulation_name = file.get('simulation_name', 'N/A')
            dt = file.get('dt', 'N/A')
            description = file.get('description', 'N/A')
            integration_method = file.get('integration_method', 'N/A')
            collision_option = file.get('collision_option', 'N/A')
            cuda_option = file.get('cuda_option', 'N/A')
            created_at = file.get('created_at', 'N/A')
            
            file_tree.insert('', 'end', values=(
                simulation_id, simulation_name, dt,
                description,
                integration_method,
                collision_option,
                cuda_option,
                created_at))
            

                
                
    load_files_button = tk.Button(
        download_frame, text="加載文件列表", command=load_file_list)
    load_files_button.place(x=10, y=140)

    def download_selected_file():

        selected_item = file_tree.selection()
        if selected_item:
            item = file_tree.item(selected_item)
            simulation_id = item['values'][0]
            simulation_name = item['values'][1]
            download_file_from_backend(simulation_id, simulation_name)
        else:
            messagebox.showwarning("警告", "請選擇一個文件進行下載")

    def upload_selected_simulation(selected_item):

        if not selected_item:
            messagebox.showwarning("警告", "請選擇一個模擬資料進行上傳")
            return

        item = playback_tree.item(selected_item)
        folder_name = item['values'][0]


        simulation_folder_path = os.path.join('simulation_data', folder_name)
        print(f"準備上傳的資料夾路徑：{simulation_folder_path}")
        if not os.path.exists(simulation_folder_path):
            messagebox.showerror("錯誤", f"資料夾 {simulation_folder_path} 不存在")
            return


        initial_conditions_file = os.path.join(simulation_folder_path, 'initial_conditions.txt')
        print(f"檢查 initial_conditions.txt 的路徑：{initial_conditions_file}")
        if not os.path.exists(initial_conditions_file):
            messagebox.showerror("錯誤", f"未找到 initial_conditions.txt 檔案：{initial_conditions_file}")
            return

        try:
            with open(initial_conditions_file, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
                if len(lines) >= 9:
                    dt = float(lines[0])
                    rate = float(lines[1])
                    max_day = float(lines[2])
                    data_filename_base = lines[3].strip()
                    integration_method = lines[4].strip()
                    collision_option = lines[5].strip()
                    cuda_option = lines[6].strip()
                    start_time = lines[7].strip()
                    script_filename_base = lines[8].strip()
                else:
                    messagebox.showerror("錯誤", "initial_conditions.txt 檔案格式不正確")
                    return
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取 initial_conditions.txt 檔案時發生錯誤：{e}")
            return


        data = {
            'folder_name': folder_name,
            'user_id': current_user.get('user_id'), 

            'data_filename_base': data_filename_base,
            'integration_method': integration_method,
            'collision_option': collision_option,
            'cuda_option': cuda_option,
            'start_time': start_time
        }

        print(f"上傳資料：{data}") 

        url = "http://petricho.ddns.net:5000/api/upload" 

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                messagebox.showinfo("成功", f"上傳成功，模擬 ID：{result.get('simulation_id')}")
            else:
                error_msg = response.json().get('error', '上傳失敗')
                messagebox.showerror("錯誤", f"上傳失敗：{error_msg}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("錯誤", f"請求後端時出現錯誤：{e}")

    download_record_button = tk.Button(
        download_frame, text="下載", command=download_selected_file)
    download_record_button.place(x=100, y=140)


    playback_frame = tk.LabelFrame(tab2, text="回放設定")
    playback_frame.place(x=10, y=220, width=900, height=400)


    playback_tree = ttk.Treeview(playback_frame, columns=(
        'Filename', 'dt', 'data_filename_base', 'integration_method', 'collision_option', 'cuda_option', 'start_time'), show='headings')
    playback_tree.heading('Filename', text='文件名')
    playback_tree.heading('dt', text='dt')
    playback_tree.heading('data_filename_base', text='初始資料')
    playback_tree.heading('integration_method', text='積分')
    playback_tree.heading('collision_option', text='碰撞')
    playback_tree.heading('cuda_option', text='cuda')
    playback_tree.heading('start_time', text='日期')
    
    playback_tree.column('Filename', width=150)
    playback_tree.column('dt', width=50)
    playback_tree.column('data_filename_base', width=80)
    playback_tree.column('integration_method', width=80)
    playback_tree.column('collision_option', width=50)
    playback_tree.column('cuda_option', width=50)
    playback_tree.column('start_time', width=100)

    
    playback_tree.place(x=10, y=10, width=850, height=150)


    playback_tree.bind('<<TreeviewSelect>>', on_playback_tree_select)


    update_playback_file_list()


    record_rate_label = tk.Label(playback_frame, text="rate:")
    record_rate_label.place(x=10, y=300)
    record_rate_options = ["1", "10", "30", "60", "120", "240"]
    record_rate_variable = tk.StringVar(playback_frame)
    record_rate_variable.set(record_rate_options[4])
    record_rate_menu = tk.OptionMenu(
        playback_frame, record_rate_variable, *record_rate_options)
    record_rate_menu.place(x=60, y=300)


    record_scene_center_label = tk.Label(
        playback_frame, text="scene_center:")
    record_scene_center_label.place(x=150, y=300)
    record_scene_center_entry = tk.Entry(playback_frame)
    record_scene_center_entry.insert(0, "0")
    record_scene_center_entry.place(x=250, y=300)


    record_run_button = tk.Button(playback_frame, text="執行", command=lambda: record_run_program(
        record_rate_variable.get(), playback_tree.selection()))
    record_run_button.place(x=10, y=340)


    load_playback_files_button = tk.Button(
        playback_frame, text="更新文件列表", command=update_playback_file_list)
    load_playback_files_button.place(x=100, y=340)

    upload_button = tk.Button(playback_frame, text="上傳", command=lambda: upload_selected_simulation(
    playback_tree.selection()))
    upload_button.place(x=200, y=340)    


    record_introduction_label = tk.Label(
        playback_frame, text="介紹：", anchor="w")
    record_introduction_label.place(x=10, y=170)
    record_introduction_text_widget = tk.Text(
        playback_frame, height=5, width=90, wrap='word')
    record_introduction_text_widget.place(x=10, y=200)
    record_introduction_text_widget.config(state='disabled')


    root.mainloop()

if __name__ == "__main__":
    show_login_window()
