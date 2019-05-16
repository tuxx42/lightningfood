import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
import grpc
import os
import codecs
import qrcode

CERT_PATH = '~/.config/lightning-app/lnd/tls.cert'
MACAROON_PATH = '~/.config/lightning-app/lnd/data/chain/bitcoin/mainnet/admin.macaroon'  # noqa


class LndClient:
    def __init__(self, host='localhost',
                 port=10009,
                 cert_path='~/.lnd/tls.cert',
                 macaroons_path='~/.lnd/chain/bitcoin/mainnet/admin.macaroon'):

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


if __name__ == '__main__':
    client = LndClient('localhost', 10006, CERT_PATH, MACAROON_PATH)
    req = client.AddInvoice(4000, 'chicken food').payment_request
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2
    )
    qr.add_data(req)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img.save('test.png', quality=100)
