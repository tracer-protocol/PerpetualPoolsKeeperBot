from web3 import Web3
import json

# Should we use geth or just use the raw private key?
def fetch_build(json_file):
    with open(json_file) as f:
        build_json = json.load(f)
        
        return build_json["abi"], build_json["bytecode"]