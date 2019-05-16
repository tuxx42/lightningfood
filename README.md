# lightningfood
lightning network enabled food dispenser

## Setup
```
$ pip install -r requirements.txt
$ FLASK_APP=main.py flask run -h 0.0.0.0
```

Running the above, will start a flask service which allows you to generate an invoice.
Invoice generation will trigger the PWM to move the servo motor

![example_qr](test.png)

## Building the gRPC/protobuf bindings (optional)

```bash
$ git clone https://github.com/googleapis/googleapis.git
$ python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto
$ rm -rf googleapis
```
