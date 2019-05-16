# lightningfood
lightning network enabled food dispenser

## Building

```bash
git clone git@github.com:tuxx42/lightningfood.git
python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto
```
