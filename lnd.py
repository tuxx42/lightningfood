import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
import grpc
import os
import codecs
# import time


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

    def LookupInvoices(self):
        return self.stub.LookupInvoice(ln.LookupInvoiceRequest())

    def ListInvoices(self):
        return self.stub.ListInvoices(ln.ListInvoiceRequest(reversed=True))

    def AddInvoice(self, amt=0, memo=''):
        p = ln.Invoice(value=amt, memo=memo)
        return self.stub.AddInvoice(p)

    def SubscribeInvoices(self):
        p = ln.InvoiceSubscription()
        for invoice in self.stub.SubscribeInvoices(p):
            yield invoice


if __name__ == '__main__':
    client = LndClient(host='archie')
    client.AddInvoice(200, "chicken food")
