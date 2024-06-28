from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

data = {
    'title': 'Data Page',
    'header': 'Welcome to the Data Page',
    'data_items': [
        {'name': 'Item 1', 'value': 10},
        {'name': 'Item 2', 'value': 20},
        {'name': 'Item 3', 'value': 30}
    ]
}
import datetime
def update_data():
    global data
    i = 0
    time.sleep(1)
    while True:
        i += 1
        data = {
            'title': 'Data Page',
            'header': 'Welcome to the Data Page',
            'data_items': 0
        }
        socketio.emit('update_data', data, namespace='/')
        app.logger.warning('Data updated')
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/')
def handle_connect():
    emit('update_data', data)

if __name__ == '__main__':
    thread = threading.Thread(target=update_data)
    thread.daemon = True
    thread.start()
    socketio.run(app, debug=True)
