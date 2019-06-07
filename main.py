import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
from flask import Flask, render_template, make_response, send_from_directory
# from flask_socketio import SocketIO, emit
# from RPi import GPIO
import grpc
import os
import codecs
# import time

app = Flask(__name__)

MACAROONS_PATH = '/home/alarm/.lnd/data/chain/bitcoin/mainnet/admin.macaroon'
CERT_PATH = '/home/alarm/.lnd/tls.cert'


class LndClient:
    def __init__(self, host='localhost', port=10009,
                 cert_path='tls.cert', macaroons_path='admin.macaroon'):

        with open(os.path.expanduser(macaroons_path), 'rb') as f:
            macaroon = codecs.encode(f.read(), 'hex')

        with open(os.path.expanduser(cert_path), 'rb') as f:
            cert = f.read()

        creds = grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(cert),
            grpc.metadata_call_credentials(
                lambda a, b: b([('macaroon', macaroon)], None)
            )
        )

        uri = '{host}:{port}'.format(host=host, port=port)
        channel = grpc.secure_channel(uri, creds)

        self.stub = lnrpc.LightningStub(channel)

    def WalletBalance(self):
        return self.stub.WalletBalance(ln.WalletBalanceRequest())

    def ListPayments(self):
        return self.stub.ListPayments(ln.ListPaymentsRequest())

    def AddInvoice(self, amt=0, memo=''):
        p = ln.Invoice(value=amt, memo=memo)
        return self.stub.AddInvoice(p)

    def SubscribeInvoices(self):
        p = ln.InvoiceSubscription()
        for invoice in self.stub.SubscribeInvoices(p):
            yield invoice


client = LndClient(host='archie')


def wait_for_invoice():
    pass
    # for i in client.SubscribeInvoices():
    #     GPIO.setmode(GPIO.BCM)
    #     GPIO.setup(18, GPIO.OUT)
    #     p = GPIO.PWM(18, 50)
    #     p.start(1)
    #     p.ChangeDutyCycle(7.5)
    #     time.sleep(0.3)
    #     p.ChangeDutyCycle(12.5)
    #     time.sleep(0.8)
    #     p.ChangeDutyCycle(7.5)
    #     time.sleep(1)
    #     p.stop()
    #     GPIO.cleanup()


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
    pass
