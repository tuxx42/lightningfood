from lnd import LndClient
from flask import (
    Flask, render_template, make_response, send_from_directory, request
)
from flask_socketio import SocketIO, join_room, emit
# from RPi import GPIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')
client = LndClient(host='archie')
clients = {}


def wait_for_invoice():
    pass


@socketio.on('register_invoice')
def handle_invoice(invoice):
    clients[invoice['invoice']] = request.sid
    join_room(request.sid)

    for i in client.SubscribeInvoices():
        if i.settled is True:
            print('paying', i.payment_request)
            room = clients.get(i.payment_request)
            emit('settled', {'invoice': i.payment_request}, room=room)


@app.route('/')
def index():
    return render_template('static.html')


@app.route('/invoice')
def invoice():
    data = client.AddInvoice(200, "chicken food").payment_request
    r = make_response(data)
    r.mimetype = 'text/plain'
    return r


@app.route('/js/<path>')
def send_js(path):
    return send_from_directory('js', path)


if __name__ == '__main__':
    socketio.run(app, debug=True)
