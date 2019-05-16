import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
from flask import Flask, render_template, make_response
from RPi import GPIO
import time
import grpc
import os
import codecs
import threading
import qrcode
import io

app = Flask(__name__)


class LndClient:
    def __init__(self, host='localhost',
                 port=10009,
                 cert_path='~/.lnd/tls.cert',
                 macaroons_path='~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon'):

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

client = LndClient()

def wait_for_invoice():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    p = GPIO.PWM(18, 50)

    for i in client.SubscribeInvoices():
        p.start(1)
        p.ChangeDutyCycle(1)
        time.sleep(0.3)
        p.ChangeDutyCycle(11)
        time.sleep(0.3)
        p.ChangeDutyCycle(1)



x = threading.Thread(target=wait_for_invoice)
x.start()


@app.route('/')
def index():
    return render_template('static.html')


@app.route('/invoice')
def invoice():
    data = client.AddInvoice(4000, "chicken food").payment_request
    r = make_response(data)
    r.mimetype = 'text/plain'
    return r


@app.route('/qr/<invoice>')
def qr(invoice):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2
    )
    qr.add_data(invoice)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bytesio = io.BytesIO()
    img.save(bytesio, quality=100)
    data = bytesio.getvalue()

    r = make_response(data)
    r.mimetype = 'image/png'
    return r


if __name__ == '__main__':
    pass
