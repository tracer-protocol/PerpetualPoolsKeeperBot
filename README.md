# Perpetual Pools Keeper Bot

## Running
- Create a file called `pool_addresses` in the root branch, following the structure described below.
- Start the virtual environment with `source env/bin/activate`
- Run with `./src/run_keeper.py [-u | --url] <RPC_URL> [-k | --keeper] <POOL_KEEPER_ADDRESS> [-p | --private_key] <PRIVATE_KEY>`

### pool_addresses
The pool address file should be of the format `ADDRESS,ADDRESS,...`.
For example, `0xF83A19C95a5B64DAb4f6DBf54f2466D3BFE247B8,0xAb7Afa3570725dff5ef865Ec348b56dDCb6f3332,0xc63a4e13057bc8259f0b30c1cde1ae199f935ca9`
