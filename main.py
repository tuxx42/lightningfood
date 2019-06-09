from threading import Lock
from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO, emit, join_room
from lnd import LndClient


async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
client = LndClient(host='archie')
clients = {}
thread = None
thread_lock = Lock()


def get_invoices(data):
    return [i.payment_request for i in data if i.settled is True]


invoices = get_invoices(client.ListInvoices().invoices)


def background_thread():
    global invoices

    while True:
        i = client.ListInvoices()
        for invoice in i.invoices:
            if invoice.payment_request in invoices:
                continue

            if invoice.settled is True:
                room = clients.get(invoice.payment_request)
                socketio.emit(
                    'settled', {'data': 'Server generated event', 'count': 0},
                    room=room, namespace='/test'
                )
        invoices = get_invoices(i.invoices)
        socketio.sleep(2)


@app.route('/')
def index():
    return render_template('static.html', async_mode=socketio.async_mode)


@app.route('/js/<path>')
def send_js(path):
    return send_from_directory('js', path)


@socketio.on('invoice', namespace='/test')
def invoice():
    data = client.AddInvoice(200, "chicken food").payment_request
    clients[data] = request.sid
    join_room(request.sid)
    emit('invoice', data)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    global clients

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
        emit('my_response', {'data': 'hi', 'count': 0}, namespace='/test')


if __name__ == '__main__':
    socketio.run(app, debug=True)
