#!/bin/python3
import sys
import re
import collections
from typing import List, Tuple
from web3 import Web3

from leveraged_pool import LeveragedPool
from pool_keeper import PoolKeeper
from executioner import Executioner

USAGE = (f"Usage: {sys.argv[0]} "
         "[--help] | [-u <url>] | [-k <keeper] | [-p <private_key>]") 
def parse(args: List[str]) -> Tuple[str, List[int]]:
    arguments = collections.deque(args)
    separator = "\n"
    operands: List[int] = []
    args = {}
    if len(arguments) != 1 + 3 * 2:
        raise SystemExit(USAGE)
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
            args["k"] = keeper_address
            continue
        try:
            operands.append(arg)
        except ValueError:
            raise SystemExit(USAGE)
    return args

if __name__ == "__main__":
    args = parse(sys.argv)

    url = args["u"]
    key = args["p"]
    keeper_address = args["k"]

    # TODO add all pool addresses
    f = open("pool_addresses", "r")
    pool_list = f.read().split(",")
    pool_list = list(map(lambda x: x.strip(), pool_list))

    web3 = Web3(Web3.HTTPProvider(url))

    pools = []
    for pool in pool_list:
        pools.append(LeveragedPool(web3, pool))

    keeper = PoolKeeper(web3, keeper_address, key)
    executioner = Executioner(web3, pools, keeper)
    executioner.run()
