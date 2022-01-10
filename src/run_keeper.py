#---!/bin/python3
import sys
import re
import collections
from typing import List, Tuple
from web3 import Web3

from leveraged_pool import LeveragedPool
from pool_keeper import PoolKeeper
from pool_factory import PoolFactory
from executioner import Executioner

USAGE = (f"Usage: {sys.argv[0]} "
         "[--help] | [-u <url>] | [-k <keeper] | [-p <private_key>]") 
def parse(args: List[str]) -> Tuple[str, List[int]]:
    arguments = collections.deque(args)
    separator = "\n"
    operands: List[int] = []
    args = {}
    while arguments:
        arg = arguments.popleft()
        if arg == "--help":
            print(USAGE)
            sys.exit(0)
        if arg in ("-u", "--url"):
            url = arguments.popleft()
            args["u"] = url
            continue
        if arg in ("-p", "--private_key"):
            private_key = arguments.popleft()
            args["p"] = private_key
            continue
        if arg in ("-k", "--keeper"):
            keeper_address = arguments.popleft()
            args["k"] = Web3.toChecksumAddress(keeper_address)
            continue
        if arg in ("-f", "--factory"):
            factory_address = arguments.popleft()
            args["f"] = Web3.toChecksumAddress(factory_address)
            continue        
        try:
            operands.append(arg)
        except ValueError:
            raise SystemExit(USAGE)
    
    for req in ["u", "p", "k"]:
        if req not in args:
            raise SystemExit(USAGE)    
           
    return args

if __name__ == "__main__":
    args = parse(sys.argv)

    url = args["u"]
    key = args["p"]
    keeper_address = args["k"]

    web3 = Web3(Web3.HTTPProvider(url))   

    pool_list = []
    if "f" in args:
        f = open("skip_pool_addresses", "r")
        skip_pool_list = f.read().split(",")
        skip_pool_list = list(map(lambda x: x.strip(), skip_pool_list))
        
        factory_address = args["f"]
        factory = PoolFactory(web3, factory_address)
        pool_list = factory.getPools()
        pool_list=[pool for pool in pool_list if pool not in skip_pool_list]                
    else:
        f = open("pool_addresses", "r")
        pool_list = f.read().split(",")
        pool_list = list(map(lambda x: x.strip(), pool_list))



    pools = []
    for pool in pool_list:
        pools.append(LeveragedPool(web3, pool))

    keeper = PoolKeeper(web3, keeper_address, key)
    executioner = Executioner(web3, pools, keeper)
    executioner.run()
