from flask import Flask, request, jsonify, abort
import mysql.connector
import os
import bcrypt 
import zipfile
import requests 
import json      
import datetime 
#testgit
app = Flask(__name__)

# MySQL 資料庫配置
db_config = {
    'user': 'root',            
    'password': '550327wu',     
    'host': 'localhost',        
    'database': 'nbody',        
    'raise_on_warnings': True
}


@app.route('/api/login', methods=['POST'])
def login():
    """
    使用者登入認證
    """
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': '缺少使用者名稱或密碼'}), 400

    username = data['username']
    password = data['password']

    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)

        # 查詢使用者
        query = "SELECT user_id, username, password, role FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        cursor.close()
        cnx.close()

        if user:
            stored_password = user['password']

            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):

                user_info = {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'role': user['role']
                }
                return jsonify(user_info), 200
            else:

                return jsonify({'error': '使用者名稱或密碼錯誤'}), 401
        else:

            return jsonify({'error': '使用者名稱或密碼錯誤'}), 401

    except mysql.connector.Error as err:
        print(f"資料庫連接錯誤: {err}")
        return jsonify({'error': '資料庫連接錯誤'}), 500
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")
        return jsonify({'error': '內部伺服器錯誤'}), 500


@app.route('/api/register', methods=['POST'])
def register():
    """
    使用者註冊
    """
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': '缺少使用者名稱或密碼'}), 400

    username = data['username']
    password = data['password']


    if len(username) < 3 or len(password) < 6:
        return jsonify({'error': '使用者名稱至少3個字元，密碼至少6個字元'}), 400

    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)


        query = "SELECT user_id FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            cnx.close()
            return jsonify({'error': '使用者名稱已存在'}), 409  # 409 Conflict


        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


        insert_query = "INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, NOW())"
        cursor.execute(insert_query, (username, hashed_password.decode('utf-8'), 'user'))  # 預設角色為 'user'
        cnx.commit()

        cursor.close()
        cnx.close()

        return jsonify({'message': '註冊成功'}), 201  # 201 Created

    except mysql.connector.Error as err:
        print(f"資料庫連接錯誤: {err}")
        return jsonify({'error': '資料庫連接錯誤'}), 500
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")
        return jsonify({'error': '內部伺服器錯誤'}), 500


@app.route('/api/files', methods=['GET'])
def get_file_list():
    print("收到獲取文件列表的請求")
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        print("已連接到資料庫")

        query = """
            SELECT 
                simulation_id, 
                simulation_name, 
                COALESCE(dt, 0) AS dt, 
                COALESCE(description, '無') AS description, 
                COALESCE(integration_method, 'Euler') AS integration_method, 
                COALESCE(collision_option, '禁用') AS collision_option, 
                COALESCE(cuda_option, '不使用') AS cuda_option, 
                COALESCE(created_at, NOW()) AS created_at 
            FROM simulation_data
        """
        cursor.execute(query)
        result = cursor.fetchall()
        print(f"獲取到 {len(result)} 條記錄")
        formatted_result = []
        for record in result:

            if isinstance(record['created_at'], datetime.datetime):
                record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            formatted_result.append(record)
            print(record)  
        cursor.close()
        cnx.close()
        return jsonify(formatted_result)
    except mysql.connector.Error as err:
        print(f"資料庫連接錯誤: {err}")
        return jsonify([]), 500
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")
        return jsonify([]), 500




@app.route('/api/files/<int:simulation_id>', methods=['GET'])
def get_file_url(simulation_id):
    print(f"收到獲取 simulation_id: {simulation_id} 的文件 URL 請求")
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        print("已連接到資料庫")

        query = "SELECT file_id FROM hfs_files WHERE simulation_id = %s"
        cursor.execute(query, (simulation_id,))
        result = cursor.fetchone()
        cursor.close()
        cnx.close()
        if result:
            file_id = result[0]
            print(f"找到 simulation_id: {simulation_id} 對應的 file_id: {file_id}")

            download_url = f"http://petricho.ddns.net/{file_id}/?get=zip"

            return jsonify({'download_url': download_url})
        else:
            print(f"找不到 simulation_id: {simulation_id} 對應的 file_id")
            return jsonify({'error': '找不到對應的文件 ID'}), 404
    except mysql.connector.Error as err:
        print(f"資料庫連接錯誤: {err}")
        return jsonify({'error': '資料庫連接錯誤'}), 500
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")
        return jsonify({'error': '內部伺服器錯誤'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_simulation():
    """
    上傳模擬資料
    """
    data = request.get_json()
    if not data or 'folder_name' not in data or 'user_id' not in data:
        return jsonify({'error': '缺少資料夾名稱或使用者 ID'}), 400

    folder_name = data['folder_name']
    user_id = data['user_id']


    simulation_folder_path = os.path.join('simulation_data', folder_name)


    if not os.path.exists(simulation_folder_path):
        return jsonify({'error': '指定的資料夾不存在'}), 404


    initial_conditions_file = os.path.join(simulation_folder_path, 'initial_conditions.txt')
    if not os.path.exists(initial_conditions_file):
        return jsonify({'error': '資料夾中缺少 initial_conditions.txt'}), 404

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
                start_time_str = lines[7].strip()
                script_filename_base = lines[8].strip()

                # 調試訊息
                print(f"Received start_time_str: {start_time_str}")
                print("Datetime module:", datetime)
                print("Has strptime:", hasattr(datetime.datetime, 'strptime'))
                print("Available attributes:", dir(datetime.datetime))


                try:

                    created_at = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                    print(f"Parsed created_at: {created_at}")
                except ValueError as ve:
                    print(f"ValueError: {ve}")
                    return jsonify({'error': '無效的時間格式'}), 400

            else:
                return jsonify({'error': 'initial_conditions.txt 格式錯誤'}), 400
    except Exception as e:
        return jsonify({'error': f'讀取 initial_conditions.txt 時發生錯誤: {e}'}), 500


    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()


        insert_simulation_query = """
            INSERT INTO simulation_data (
                user_id,
                simulation_name,
                dt,
                rate,
                max_day,
                description,
                integration_method,
                collision_option,
                cuda_option,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_simulation_query, (
            user_id,
            folder_name,
            dt,
            rate,
            max_day,
            data_filename_base,
            integration_method,
            collision_option,
            cuda_option,
            created_at
        ))
        cnx.commit()
        simulation_id = cursor.lastrowid  


        insert_hfs_query = """
            INSERT INTO hfs_files (simulation_id)
            VALUES (%s)
        """
        cursor.execute(insert_hfs_query, (simulation_id,))
        cnx.commit()
        file_id = cursor.lastrowid  

        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"資料庫連接錯誤: {err}")
        return jsonify({'error': '資料庫連接錯誤'}), 500
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")
        return jsonify({'error': '內部伺服器錯誤'}), 500


    try:

        hfs_host = "petricho.ddns.net"
        hfs_port = 80  # HTTP 端口
        new_folder_name = str(file_id) 


        create_folder_response = create_folder(hfs_host, hfs_port, new_folder_name)
        if create_folder_response is None or create_folder_response.status_code not in [200, 201]:
            print(f"在 HFS 伺服器上創建資料夾失敗: {create_folder_response.text}")
            return jsonify({'error': '在 HFS 伺服器上創建資料夾失敗'}), 500


        upload_files_response = upload_files(hfs_host, hfs_port, new_folder_name, simulation_folder_path)
        if not upload_files_response:
            return jsonify({'error': '上傳文件到 HFS 伺服器失敗'}), 500

        return jsonify({'message': '上傳成功', 'simulation_id': simulation_id}), 200

    except Exception as e:
        print(f"上傳檔案時發生錯誤: {e}")
        return jsonify({'error': f'上傳檔案時發生錯誤: {e}'}), 500

def create_folder(host, port, folder_name):
    """
    使用 HFS 的 API 創建一個新資料夾。

    :param host: HFS 伺服器的主機地址
    :param port: HFS 伺服器的端口號
    :param folder_name: 要創建的資料夾名稱
    :return: 伺服器的回應對象
    """
    url = f"http://{host}:{port}/~/api/create_folder"


    payload = json.dumps({
        "uri": "/",               
        "name": folder_name       
    })


    headers = {
        'x-hfs-anti-csrf': '1',
        'Content-Type': 'application/json'
    }

    try:

        response = requests.post(url, headers=headers, data=payload)
        return response
    except requests.exceptions.RequestException as e:
        print(f"創建資料夾時發生錯誤: {e}")
        return None

def upload_files(host, port, target_folder, local_folder):


    upload_url = f"http://{host}:{port}/{target_folder}/"


    if not os.path.isdir(local_folder):
        print(f"指定的本地資料夾不存在: {local_folder}")
        return False


    for root, dirs, files in os.walk(local_folder):
        for file_name in files:

            file_path = os.path.join(root, file_name)
            print(f"正在上傳文件: {file_path}")


            relative_path = os.path.relpath(root, local_folder)

            if relative_path != '.':
                target_url = upload_url + relative_path.replace('\\', '/') + '/'
            else:
                target_url = upload_url


            try:
                with open(file_path, 'rb') as file:
                    files_payload = {
                        'upload': (file_name, file, 'application/octet-stream')
                    }

                    response = requests.post(target_url, files=files_payload)


                    if response.status_code in [200, 201]:
                        print(f"文件上傳成功: {file_name}")
                    else:
                        print(f"上傳失敗 ({response.status_code}): {file_name}")
                        print("伺服器回應:", response.text)
                        return False
            except FileNotFoundError:
                print(f"文件不存在: {file_path}")
                return False
            except requests.exceptions.RequestException as e:
                print(f"上傳文件時發生錯誤: {e}")
                return False

    print("所有文件上傳完成。")
    return True

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
