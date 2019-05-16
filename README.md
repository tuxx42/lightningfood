# lightningfood
lightning network enabled food dispenser

## Setup
```
pip install -r requirements.txt
```

## Building the gRPC/protobuf bindings (optional)

```bash
git clone https://github.com/googleapis/googleapis.git
python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto
rm -rf googleapis
```
