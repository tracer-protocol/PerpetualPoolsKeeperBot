#!/bin/python3
import sys
import re
import collections
from typing import List, Tuple
from web3 import Web3
from erc20 import ERC20

from leveraged_pool import LeveragedPool
from pool_committer import PoolCommitter
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

    COMMITTER = True

    def get_next_9_UIs(committer, update_interval):
        UIs = []

        for i in range(update_interval, update_interval + 9):
            commitment = committer.total_pool_commitments(i)
            UIs.append(commitment)
        return UIs

    pools = []
    committers = []
    for pool in pool_list:
        pools.append(LeveragedPool(web3, pool))
        if COMMITTER:
            pool = pools[len(pools) - 1]
            # if "ETH" not in pool.pool_name():
                # continue
            short_token = ERC20(web3, pool.short_token())
            long_token = ERC20(web3, pool.long_token())

            committer = PoolCommitter(web3, pool.pool_committer())
            id = committer.update_interval_id()

            ####### GET PENDING BURNS -> ADD TO TOTAL SUPPLY

            UIs = get_next_9_UIs(committer, id)

            pending_long_burns = committer.pending_long_burn_pool_tokens()
            pending_short_burns = committer.pending_short_burn_pool_tokens()
            print(pending_long_burns)

            long_price = pool.long_balance() / (long_token.total_supply() + pending_long_burns)
            short_price = pool.short_balance() / (short_token.total_supply() + pending_short_burns)
            # short_price = pool.short_balance() / (short_token.total_supply() + 0)
            print(f"long balance: {pool.long_balance()}")
            print(f"long total_supply: {long_token.total_supply()}")
            print("SHORT PRICE")
            print(short_price)
            print("LONG PRICE")
            print(long_price)
            print(pool.pool_name())
            print(committer.address)
            new_long_settlement = 0
            new_short_settlement = 0
            short_burns = 0
            long_burns = 0
            for i in range(id, id + 9):
                print("")
                print("---------------")
                print(f"{i - id + 1} hours away")
                print(i)
                # commitment = committer.total_pool_commitments(i)
                commitment = UIs[i - id]
                print(f"longMintSettlement: {(commitment[0] / (10**6)):,}")
                new_long_settlement += (commitment[0] / (10**6))
                print(f"longBurnPoolTokens: {(commitment[1] / (10**6)):,}")
                new_long_settlement -= (commitment[1] / (10**6)) * (long_price / 10 ** 6)
                print(f"shortMintSettlement: {(commitment[2] / (10**6)):,}")
                new_short_settlement += (commitment[2] / (10**6))
                print(f"shortBurnPoolTokens: {(commitment[3] / (10**6)):,}")
                new_short_settlement -= (commitment[3] / (10**6)) * (short_price / 10 ** 6)
                print(f"shortBurnLongMintPoolTokens: {(commitment[4] / (10**6)):,}")
                new_short_settlement -= (commitment[4] / (10**6)) * (short_price / 10 ** 6)
                new_long_settlement += (commitment[4] / (10**6)) * (short_price / 10 ** 6)
                print(f"longBurnShortMintPoolTokens: {(commitment[5] / (10**6)):,}")
                new_short_settlement += (commitment[5] / (10**6)) * (long_price / 10 ** 6)
                new_long_settlement -= (commitment[5] / (10**6)) * (long_price / 10 ** 6)
                print("---------------")
                print("")
            print(f"new_long_settlement {(pool.long_balance() / 10**6 + new_long_settlement):,}")
            print(f"new_short_settlement {(pool.short_balance() / 10**6 + new_short_settlement):,}")
            # sys.exit()


    sys.exit()

    keeper = PoolKeeper(web3, keeper_address, key)
    executioner = Executioner(web3, pools, keeper)
    executioner.run()
