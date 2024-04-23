from flask import Flask, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Conectado:', request.sid)

@socketio.on('message')
def handle_message(message):
    print('Mensagem recebida:', message)
    # adicionar processamento de mensagens

@socketio.on('disconnect')
def handle_disconnect():
    print('Desconectado:', request.sid)

# pedir peso
def get_bowl_weight(arduino_sid, bowl_name):
    socketio.emit('get_bowl_weight', {'bowl_name': bowl_name}, room=arduino_sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000)
