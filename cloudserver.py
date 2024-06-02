from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import requests
import sqlite3
import json
import threading
import time

#urlserver = "http://46.101.71.117:5000"
urlserver = "http://127.0.0.1:5000"
urlrpi = "http://127.0.0.1:5001"

app = Flask(__name__)
api = Api(app)

motor_activate = False

def get_add_bowl():
	while True:
		r = requests.get(url = urlserver + '/send_bowl')
		data = json.loads(r.text)
		if data:
			bowl_name = data['bowl_name']
			daily_goal = data['daily_goal']
			user_id = data['user_id']
			conn = sqlite3.connect('database.db',  check_same_thread=False)
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM UserBowls WHERE user_id=? AND animal_name=?", (user_id, bowl_name))
			user = cursor.fetchone()
			if not user:
				r = requests.post(url = urlrpi + '/add_bowl', json=data)
			conn.close
		time.sleep(2)
		

def send_bowls_list():
	while True:
		r = requests.get(url = urlserver + '/send_bowls_list')
		data = r.json()
		is_get = data['message']
		if is_get:
			bowls = requests.get(url = urlrpi + '/get_bowls_list').json()
			requests.post(url = urlserver + '/send_bowls_list', json=bowls)
		time.sleep(2)

def send_ard_num():
	while True:
		r = requests.get(url = urlserver + '/send_arduinos_count')
		data = json.loads(r.text)
		is_get = data['message']
		if is_get:
			count_arduinos = requests.get(url = urlrpi + '/get_arduino_count').json()
			requests.post(url = urlserver + '/send_arduinos_count', json=count_arduinos)
		time.sleep(2)
        

def send_daily_goal():
	while True:
		r = requests.get(url = urlserver + '/send_daily_goal')
		data = json.loads(r.text)
		is_get = data['message']
		if is_get:
			print(data)
			payload = {'bowl_name': data['bowl_name']}
			daily_goal = requests.get(url = urlrpi + '/get_daily_goal', params=payload).json()
			requests.post(url = urlserver + '/send_daily_goal', json=daily_goal)
		time.sleep(2)
    
        
def send_food_amount():
	while True:
		r = requests.get(url = urlserver + '/send_food_amount')
		data = json.loads(r.text)
		is_get = data['message']
		if is_get:
			payload = {'bowl_name': data['bowl_name']}
			food = requests.get(url = urlrpi + '/get_food_amount', params=payload).json()
			requests.post(url = urlserver + '/send_food_amount', json=food)
		time.sleep(2)


def send_feeding_time():
	while True:
		r = requests.get(url = urlserver + '/send_last_feeding_time')
		data = json.loads(r.text)
		is_get = data['message']
		if is_get:
			payload = {'bowl_name': data['bowl_name']}
			feeding_time = requests.get(url = urlrpi + '/get_last_feeding_time', params=payload).json()
			requests.post(url = urlserver + '/send_last_feeding_time', json=feeding_time)
		time.sleep(2)


def get_set_daily_goal():
	while True:
		r = requests.get(url = urlserver + '/rpi_set_daily_goal')
		data = json.loads(r.text)
		is_get = data['message']
		if is_get:
			bowl_name = data['bowl_name']
			daily_goal = data['daily_goal']
			payload = {'bowl_name': bowl_name, 'daily_goal': daily_goal }
			requests.post(url = urlrpi + '/set_daily_goal', json=payload)
			requests.post(url = urlserver + '/rpi_set_daily_goal', json={'message':'DONE'})
		time.sleep(2)
		
		
def get_set_feeding_time():
	while True:
		r = requests.get(url = urlserver + '/rpi_set_feeding_time')
		data = json.loads(r.text)
		is_get = data['message']
		if is_get:
			bowl_name = data['bowl_name']
			feeding_time = data['feeding_time']
			payload = {'bowl_name': bowl_name, 'feeding_time': feeding_time }
			requests.post(url = urlrpi + '/set_feeding_time', json=payload)
			requests.post(url = urlserver + '/rpi_set_feeding_time', json={'message':'DONE'})
		time.sleep(2)
		
		
def send_weight():
	while True:
		r = requests.get(url = urlserver + '/send_weight')
		data = json.loads(r.text)
		is_get = data['message']
		if is_get:
			bowl_name = data['bowl_name']
			payload = {'bowl_name': bowl_name}
			weight = requests.get(url = urlrpi + '/get_weight', params=payload).json()
			requests.post(url = urlserver + '/send_weight', json=weight)
		time.sleep(2)


@app.route('/get_bowls_list', methods=['GET'])
def get_bowls_list():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Bowls")
    bowls = cursor.fetchall()
    lst = []
    for bowl in bowls:
        lst = lst + [bowl[0]]
    conn.close()
    return jsonify({'bowls' : lst})
    
    
# testar
@app.route('/get_arduino_count', methods=['GET'])
def ard_count():
	try:
		conn = sqlite3.connect('database.db', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("SELECT COUNT(*) FROM arduinos_animal WHERE animal_name = to_be_def")
		nard = cursor.fetchall()
		conn.close()
	except:
		nard = [0]
	return jsonify({'number_arduinos' : int(nard[0])})
    
        

#testar    
@app.route('/get_daily_goal', methods=['GET'])
def get_daily_goal():
    data = request.args
    bowl_name = data.get('bowl_name')
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT daily_dose FROM Bowls WHERE animal_name=?", (bowl_name,))
    dose = cursor.fetchone()
    conn.close()
    return jsonify({'daily_goal': float(dose[0])})


#testar
@app.route('/get_food_amount', methods=['GET'])
def get_food_amount():
    data = request.args
    bowl_name = data.get('bowl_name')
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT food_dispensed FROM Bowls WHERE animal_name=?", (bowl_name,))
    food = cursor.fetchone()
    conn.close()
    return jsonify({'food_amount': float(food[0])})


# testar
@app.route('/get_last_feeding_time', methods=['GET'])
def get_last_feeding_time():
    data = request.args
    bowl_name = data.get('bowl_name')
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT last_food FROM Bowls WHERE animal_name=?", (bowl_name,))
    food = cursor.fetchone()
    conn.close()
    return jsonify({'last_feeding_time': food})


#testar
@app.route('/set_daily_goal', methods=['POST'])
def set_daily_goal():
    data = request.get_json()
    bowl_name = data['bowl_name']
    daily_goal = data['daily_goal']
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("UPDATE Bowls SET daily_dose=? WHERE animal_name=?", (daily_goal, bowl_name))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Daily goal of {bowl_name} was successfully changed to {daily_goal}'})


#testar
@app.route('/set_feeding_time', methods=['POST'])
def set_feeding_time():
   data = request.get_json()
   bowl_name = data['bowl_name']
   feeding_time = data['feeding_time']
   conn = sqlite3.connect('database.db', check_same_thread=False)
   cursor = conn.cursor()
   cursor.execute("UPDATE Bowls SET last_food=? WHERE animal_name=?", (feeding_time, bowl_name))
   conn.commit()
   conn.close()
   return {'message': f'Last feeding time set to {feeding_time}'}
   

@app.route('/add_bowl', methods=['POST'])
def add_bowl():
    data = request.get_json()
    bowl_name = data['bowl_name']
    daily_goal = data['daily_goal']
    user_id = data['user_id']
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM arduinos_animal")
    arduino = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO Users (user_id) VALUES (?)", (user_id,))
    cursor.execute("INSERT INTO UserBowls (user_id, animal_name) VALUES (?, ?)", (user_id, bowl_name))    
    cursor.execute("UPDATE arduinos_animal SET animal_name=? WHERE arduino_id=?", (bowl_name, arduino[0]))
    cursor.execute("INSERT INTO Bowls (animal_name, daily_dose, bowl_weight, food_dispensed, last_food) VALUES (?, ?, null, null, null)", (bowl_name, daily_goal))    
    conn.commit()
    conn.close()
    return jsonify({'message': f'Bowl {bowl_name} added successfully with daily goal of {daily_goal}'})


@app.route('/control_motor', methods=['POST', 'GET'])
def control_motor():
	global motor_activate
	data = json.loads(request.data.decode('utf-8'))
	
	if request.method == 'POST':
		if data['message']== 'on':
			motor_activate = True
		elif data['message']== 'off':
			motor_activate = False
		return jsonify({'message': 'DONE'})

	if request.method == 'GET':
		return jsonify({'start_motor': motor_activate })


@app.route('/connect', methods=['POST'])
def connect_arduino():
    conn = sqlite3.connect('database.db',  check_same_thread=False)
    cursor = conn.cursor()
    data = json.loads(request.data.decode('utf-8'))
    cursor.execute("INSERT INTO arduinos_animal (arduino_id, animal_name) VALUES (?, ?)", (data['mac'], "to_be_def"))
    conn.commit()
    conn.close()
    return jsonify({'message': 'DONE'})
 

#testar    
@app.route('/post_weight', methods=['POST'])
def get_weight_from_arduino():
	data = json.loads(request.data.decode('utf-8'))
	conn = sqlite3.connect('database.db',  check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT animal_name FROM arduinos_animal WHERE arduino_id=?", (data['mac'], ))
	arduino = cursor.fetchone()
	cursor.execute("UPDATE Bowls SET bowl_weight=? WHERE animal_name=?", (data['weight'], arduino[0]))
	conn.commit()
	conn.close()
	return jsonify({'message': 'DONE'})


#testar
@app.route('/get_weight', methods=['GET'])
def get_weight():
    data = request.args
    bowl_name = data.get('bowl_name')
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT bowl_weight FROM Bowls WHERE animal_name=?", (bowl_name,))
    weight = cursor.fetchone()
    conn.close()
    return jsonify({'weight': float(weight[0])})

'''
@app.route('/reset_bowl', methods=['POST'])
def reset_bowl():
   bowl_name = request.form['bowl_name']
   return {'message': f'Bowl {bowl_name}\'s weight has been updated'}
'''


if __name__ == '__main__':
    thread_add_bowl = threading.Thread(target=get_add_bowl)
    thread_add_bowl.start()
    thread_bowls_lst = threading.Thread(target=send_bowls_list)
    thread_bowls_lst.start()
    thread_bowls_lst = threading.Thread(target=send_daily_goal)
    thread_bowls_lst.start()
    thread_bowls_lst = threading.Thread(target=send_ard_num)
    thread_bowls_lst.start()
    thread_bowls_lst = threading.Thread(target=send_food_amount)
    thread_bowls_lst.start()
    thread_bowls_lst = threading.Thread(target=send_feeding_time)
    thread_bowls_lst.start()
    thread_bowls_lst = threading.Thread(target=get_set_daily_goal)
    thread_bowls_lst.start()
    thread_bowls_lst = threading.Thread(target=get_set_feeding_time)
    thread_bowls_lst.start()
    thread_bowls_lst = threading.Thread(target=send_weight)
    thread_bowls_lst.start()
    app.run(threaded=True, host='0.0.0.0', port=5001)
