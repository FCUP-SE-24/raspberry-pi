from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import requests
import sqlite3
import json
import threading
import time
import socket

#urlserver = "http://46.101.71.117:5000"
urlrpi = "http://127.0.0.1:5001"
urlserver = "http://127.0.0.1:5002"


app = Flask(__name__)
api = Api(app)

lastMotorState = False
lastWeightState = False
motor_activate = False

# Configurações do servidor
HOST = '0.0.0.0'  # Escuta em todas as interfaces de rede disponíveis
PORT = 5000       # Porta para escutar conexões

# Cria o socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

def arduino_connection_handler():
	conn, addr = server_socket.accept()
	with sqlite3.connect('database.db', check_same_thread=False) as con:
		cursor = con.cursor()
		cursor.execute("SELECT arduino_id FROM arduinos_animal WHERE arduino_id=?", (addr[0],))
		arduino_info = cursor.fetchone()
		if not arduino_info:
			cursor.execute("INSERT INTO arduinos_animal (arduino_id, animal_name) VALUES (?, ?)", (addr[0], "to_be_def"))
			con.commit()
	# Start threads for Arduino communication
	thread_receive = threading.Thread(target=receive_data, args=(conn,))
	thread_receive.start()
	thread_receive.join()

def get_add_bowl():
    while True:
        r = requests.get(url=urlserver + '/send_bowl')
        data = json.loads(r.text)
        if data:
            bowl_name = data['bowl_name']
            daily_goal = data['daily_goal']
            user_id = data['user_id']
            with sqlite3.connect('database.db', check_same_thread=False) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM UserBowls WHERE user_id=? AND animal_name=?", (user_id, bowl_name))
                user = cursor.fetchone()
                if not user:
                    requests.post(url=urlrpi + '/add_bowl', json=data)
        time.sleep(2)

def send_bowls_list():
    while True:
        r = requests.get(url=urlserver + '/send_bowls_list')
        data = r.json()
        is_get = data['message']
        if is_get:
            bowls = requests.get(url=urlrpi + '/get_bowls_list').json()
            requests.post(url=urlserver + '/send_bowls_list', json=bowls)
        time.sleep(2)

def send_ard_num():
    while True:
        r = requests.get(url=urlserver + '/send_arduinos_count')
        data = json.loads(r.text)
        is_get = data['message']
        if is_get:
            count_arduinos = requests.get(url=urlrpi + '/get_arduino_count').json()
            requests.post(url=urlserver + '/send_arduinos_count', json=count_arduinos)
        time.sleep(2)

def send_daily_goal():
    while True:
        r = requests.get(url=urlserver + '/send_daily_goal')
        data = json.loads(r.text)
        is_get = data['message']
        if is_get:
            payload = {'bowl_name': data['bowl_name']}
            daily_goal = requests.get(url=urlrpi + '/get_daily_goal', params=payload).json()
            requests.post(url=urlserver + '/send_daily_goal', json=daily_goal)
        time.sleep(2)

def send_food_amount():
    while True:
        r = requests.get(url=urlserver + '/send_food_amount')
        data = json.loads(r.text)
        is_get = data['message']
        if is_get:
            payload = {'bowl_name': data['bowl_name']}
            food = requests.get(url=urlrpi + '/get_food_amount', params=payload).json()
            requests.post(url=urlserver + '/send_food_amount', json=food)
        time.sleep(2)

def send_feeding_time():
    while True:
        r = requests.get(url=urlserver + '/send_last_feeding_time')
        data = json.loads(r.text)
        is_get = data['message']
        if is_get:
            payload = {'bowl_name': data['bowl_name']}
            feeding_time = requests.get(url=urlrpi + '/get_last_feeding_time', params=payload).json()
            requests.post(url=urlserver + '/send_last_feeding_time', json=feeding_time)
        time.sleep(2)

def get_set_daily_goal():
    while True:
        r = requests.get(url=urlserver + '/rpi_set_daily_goal')
        data = json.loads(r.text)
        is_get = data['message']
        if is_get:
            bowl_name = data['bowl_name']
            daily_goal = data['daily_goal']
            payload = {'bowl_name': bowl_name, 'daily_goal': daily_goal}
            requests.post(url=urlrpi + '/set_daily_goal', json=payload)
            requests.post(url=urlserver + '/rpi_set_daily_goal', json={'message': 'DONE'})
        time.sleep(2)

def get_set_feeding_time():
    while True:
        r = requests.get(url=urlserver + '/rpi_set_feeding_time')
        data = json.loads(r.text)
        is_get = data['message']
        if is_get:
            bowl_name = data['bowl_name']
            feeding_time = data['feeding_time']
            payload = {'bowl_name': bowl_name, 'feeding_time': feeding_time}
            requests.post(url=urlrpi + '/set_feeding_time', json=payload)
            requests.post(url=urlserver + '/rpi_set_feeding_time', json={'message': 'DONE'})
        time.sleep(2)

def send_bowl_weight():
    while True:
        r = requests.get(url=urlserver + '/send_bowl_weight')
        data = json.loads(r.text)
        is_get = data['message']
        if is_get:
            bowl_name = data['bowl_name']
            payload = {'bowl_name': bowl_name}
            weight = requests.get(url=urlrpi + '/get_weight', params=payload).json()
            requests.post(url=urlserver + '/send_bowl_weight', json=weight)
        time.sleep(2)

def send_motor_info():
    while True:
        r = requests.get(url=urlserver + '/send_control_motor')
        data = json.loads(r.text)
        is_get = data['message']
        if is_get:
            bowl_name = data['bowl_name']
            motor_state = data['motor_state']
            
            with sqlite3.connect('database.db', check_same_thread=False) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT arduino_id FROM arduinos_animal WHERE animal_name=?", (bowl_name,))
                arduino_info = cursor.fetchone()
            
            if arduino_info:
                arduino_ip = arduino_info[0]
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect((arduino_ip, 5000))  # Adjust port if necessary
                        if motor_state == 'on':
                            command = 'activate_motor'
                        elif motor_state == 'off':
                            command = 'deactivate_motor'
                        else:
                            command = lastMotorState
                        
                        sock.sendall(command.encode())
                        print(f"Comando '{command}' enviado ao Arduino no IP {arduino_ip}.")
                except Exception as e:
                    print(f"Erro ao conectar ou enviar comando para o Arduino: {e}")
            
            requests.post(url=urlserver + '/send_control_motor', json={'message': 'DONE'})
        time.sleep(2)

# Função para receber dados do Arduino
def receive_data(conn):
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Dados recebidos: {data.decode()}")
    finally:
        conn.close()
        server_socket.close()
'''
# Função para enviar comandos ao Arduino
def send_motor_command(state, conn):
   if state == 'on':
      command = 'activate_motor'
   elif state == 'off':
      command = 'deactivate_motor'
   else:
      command = lastMotorState
  
   try:
     conn.sendall(command.encode())
     print(f"Comando '{command}' enviado ao Arduino.")
   except Exception as e:
     print(f"Erro ao enviar comando: {e}")'''

def get_weight(state, conn):
   if state == 'true':
      command = 'get_weight'
   elif state == 'false':
      command = 'stop_weighing'
   else: 
      command = lastWeightState

   try: 
      conn.sendall(command.encode())
      print(f"Comando '{command}' enviado ao Arduino.")
   except Exception as e:
        print(f"Erro ao enviar comando: {e}")

'''
# Função para enviar comandos ao Arduino com entrada do usuário
def user_input(conn):
	print(conn)
	try:
		while True:
			state = input("Digite o seu comando ['on','off,'true','false']: ").strip().lower()
			if state in ['on', 'off']:
				send_motor_command(state, conn)
			elif state in ['true','false']:
				get_weight(state, conn)
			else:
				print("Entrada inválida. Digite 'on' ou 'off'.")
	except Exception as e:
		print(f"Erro ao processar entrada do usuário: {e}")
	finally:
		conn.close()'''

@app.route('/get_bowls_list', methods=['GET'])
def get_bowls_list():
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Bowls")
        bowls = cursor.fetchall()
    lst = [bowl[0] for bowl in bowls]
    return jsonify({'bowls': lst})

@app.route('/get_arduino_count', methods=['GET'])
def ard_count():
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM arduinos_animal WHERE animal_name = ?", ("to_be_def",))
        nard = cursor.fetchone()
    return jsonify({'number_arduinos': int(nard[0])})

@app.route('/get_daily_goal', methods=['GET'])
def get_daily_goal():
    data = request.args
    bowl_name = data.get('bowl_name')
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT daily_dose FROM Bowls WHERE animal_name=?", (bowl_name,))
        dose = cursor.fetchone()
    return jsonify({'daily_goal': int(dose[0])})

@app.route('/get_food_amount', methods=['GET'])
def get_food_amount():
    data = request.args
    bowl_name = data.get('bowl_name')
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT food_dispensed FROM Bowls WHERE animal_name=?", (bowl_name,))
        food = cursor.fetchone()
    return jsonify({'food_amount': int(food[0])})

@app.route('/get_last_feeding_time', methods=['GET'])
def get_last_feeding_time():
    data = request.args
    bowl_name = data.get('bowl_name')
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_food FROM Bowls WHERE animal_name=?", (bowl_name,))
        food = cursor.fetchone()
    return jsonify({'last_feeding_time': food})

@app.route('/set_daily_goal', methods=['POST'])
def set_daily_goal():
    data = request.get_json()
    bowl_name = data['bowl_name']
    daily_goal = data['daily_goal']
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Bowls SET daily_dose=? WHERE animal_name=?", (daily_goal, bowl_name))
        conn.commit()
    return jsonify({'message': f'Daily goal of {bowl_name} was successfully changed to {daily_goal}'})

@app.route('/set_feeding_time', methods=['POST'])
def set_feeding_time():
    data = request.get_json()
    bowl_name = data['bowl_name']
    feeding_time = data['feeding_time']
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Bowls SET last_food=? WHERE animal_name=?", (feeding_time, bowl_name))
        conn.commit()
    return {'message': f'Last feeding time set to {feeding_time}'}

@app.route('/add_bowl', methods=['POST'])
def add_bowl():
    data = request.get_json()
    bowl_name = data['bowl_name']
    daily_goal = data['daily_goal']
    user_id = data['user_id']
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = cursor.fetchone()
        cursor.execute("SELECT * FROM arduinos_animal")
        arduino = cursor.fetchone()
        if not user:
            cursor.execute("INSERT INTO Users (user_id) VALUES (?)", (user_id,))
        cursor.execute("INSERT INTO UserBowls (user_id, animal_name) VALUES (?, ?)", (user_id, bowl_name))
        cursor.execute("UPDATE arduinos_animal SET animal_name=? WHERE arduino_id=?", (bowl_name, arduino[0]))
        cursor.execute("INSERT INTO Bowls (animal_name, daily_dose, bowl_weight, food_dispensed, last_food) VALUES (?, ?, null, 0, null)", (bowl_name, daily_goal))
        conn.commit()
    return jsonify({'message': f'Bowl {bowl_name} added successfully with daily goal of {daily_goal}'})

@app.route('/control_motor', methods=['POST', 'GET'])
def control_motor():
    global motor_activate
    data = json.loads(request.data.decode('utf-8'))

    if request.method == 'POST':
        if data['message'] == 'on':
            motor_activate = True
        elif data['message'] == 'off':
            motor_activate = False
        return jsonify({'message': 'DONE'})

    if request.method == 'GET':
        return jsonify({'start_motor': motor_activate})

'''
@app.route('/connect', methods=['POST'])
def connect_arduino():
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        data = json.loads(request.data.decode('utf-8'))
        cursor.execute("INSERT INTO arduinos_animal (arduino_id, animal_name) VALUES (?, ?)", (data['mac'], "to_be_def"))
        conn.commit()
    return jsonify({'message': 'DONE'})'''

#testar    
@app.route('/post_bowl_weight', methods=['POST'])
def get_bowl_weight_from_arduino():
    data = json.loads(request.data.decode('utf-8'))
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT animal_name FROM arduinos_animal WHERE arduino_id=?", (data['mac'], ))
        arduino = cursor.fetchone()
        cursor.execute("UPDATE Bowls SET bowl_weight=? WHERE animal_name=?", (data['weight'], arduino[0]))
        conn.commit()
    return jsonify({'message': 'DONE'})

@app.route('/get_bowl_weight', methods=['GET'])
def get_bowl_weight():
    data = request.args
    bowl_name = data.get('bowl_name')
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT bowl_weight FROM Bowls WHERE animal_name=?", (bowl_name,))
        weight = cursor.fetchone()
    weight = weight[0] if weight else None
    return jsonify({'bowl_weight': weight})

@app.route('/get_weight', methods=['GET'])
def get_food_weight():
    data = request.args
    bowl_name = data.get('bowl_name')
    with sqlite3.connect('database.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT bowl_weight FROM Bowls WHERE animal_name=?", (bowl_name,))
        bowl_weight = cursor.fetchone()
    bowl_weight = bowl_weight[0] if bowl_weight else None
    # pedir weight arduino ard_weight
    if bowl_weight:
        weight = ard_weight - bowl_weight
    else:
        weight = None
    return jsonify({'bowl_weight': weight})

if __name__ == '__main__':
    # rpi -> cloudserver
    thread_add_bowl = threading.Thread(target=get_add_bowl)
    thread_add_bowl.start()
    thread_bowls_lst = threading.Thread(target=send_bowls_list)
    thread_bowls_lst.start()
    thread_daily_goal = threading.Thread(target=send_daily_goal)
    thread_daily_goal.start()
    thread_ard_num = threading.Thread(target=send_ard_num)
    thread_ard_num.start()
    thread_food_amount = threading.Thread(target=send_food_amount)
    thread_food_amount.start()
    thread_feeding_time = threading.Thread(target=send_feeding_time)
    thread_feeding_time.start()
    thread_set_daily_goal = threading.Thread(target=get_set_daily_goal)
    thread_set_daily_goal.start()
    thread_set_feeding_time = threading.Thread(target=get_set_feeding_time)
    thread_set_feeding_time.start()
    thread_bowl_weight = threading.Thread(target=send_bowl_weight)
    thread_bowl_weight.start()
    thread_motor = threading.Thread(target=send_motor_info)
    thread_motor.start()
    
    # Start the Flask app in a separate thread
    threading.Thread(target=lambda: app.run(threaded=True, host='0.0.0.0', port=5001)).start()


    # Handle Arduino connections
    arduino_connection_handler()
