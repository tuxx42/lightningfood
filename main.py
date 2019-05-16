import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
import grpc
import os
import codecs
import qrencode

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
    # print(client.AddInvoice(4000, 'chicken food').payment_request)
    req = 'lnbc40u1pwdexz5pp5n9vtm426hehtyyypkrqj9lup7eg8m8wr72xvh9yn807xw3pngemqdq5vd5xjcmtv4hzqen0dajqcqzpgf79jdmp2uuyx0hstnwxe7lgsh74mshlw3nlmgycllqcf4etzqk8kkaufmm67ehq4um8yqec3rxrlacxeeekgdu6r682f3hqltzne8gcq75x2ey'
    version, size, im = qrencode.encode_scaled(req.encode('utf-8'), size=200)
    im.save('foo.jpg', quality=100)
