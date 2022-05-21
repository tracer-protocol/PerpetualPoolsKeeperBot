import time
import sys

from pool_factory import PoolFactory

class Executioner(object):
    def __init__(self, w3, pools, keeper):
        self.w3 = w3
        self.pools = pools
        self.keeper = keeper

    def scan_for_upkeep(self):
        pools_to_upkeep = []
        # TODO: Add async
        for pool in self.pools:
            if self.keeper.check_upkeep(pool.address) == True:
                pools_to_upkeep.append(pool.address)
        return pools_to_upkeep

    # Go through all pools and find one that requires least wait time
    def minimum_wait_time(self):
        current_minimum = sys.maxsize
        min_pools = []
        for pool in self.pools:
            wait_time = pool.time_till_next_upkeep()
            if wait_time < current_minimum:
                next_upkeep_time = pool.last_price_timestamp() + pool.update_interval()
                min_pools = [pool.address]
                current_minimum = wait_time
            elif wait_time == current_minimum:
                min_pools.append(pool.address)
            print(f"wait time: {wait_time}")
        print(min_pools)
        return (current_minimum, min_pools, next_upkeep_time)

    def get_latest_block_time(self):
        return self.w3.eth.get_block('latest').timestamp

    def run(self):
        while True:
            self.main_loop()

    def main_loop(self):
        """Main loop to wait for update interval to pass, then execute upkeep."""
        factory = PoolFactory(self.w3, "0xdabffa47e509659FEDE5deC5e22CFFb9Cb9040b4")
        print(factory.numPools())
            
        (min_pools, upkeep_time) = self.prepare()
        if not min_pools:
            return

        while True:
            print("Checking upkeep")
            print(f"Pools that need upkeep: {min_pools}")
            # start_time = time.time()
            function_called = 0
            param = 0
            # There exists a function that allows you to pass in an array of pools,
            # which is unnecessary if you only want to upkeep one
            if len(min_pools) == 1:
                print("1 pool")
                function_called = self.keeper.perform_upkeep_single_pool
                param = min_pools[0]
            elif len(min_pools) == 2:
                print("2 pools")
                function_called = self.keeper.perform_upkeep_multiple_pools
                param = min_pools
            else:
                print(f"{len(min_pools)} pools")
                function_called = self.keeper.perform_upkeep_multiple_pools_packed
                param = min_pools
            print(function_called)
            if not self.loop_until_ready(min_pools[0], upkeep_time):
                # It failed after 200+ seconds, so we'll re-query pending upkeeps
                break
            # end_time = time.time()
            # print(end_time - start_time)

            try:
                function_called(param)
                """
                if len(min_pools) == 1:
                    self.keeper.perform_upkeep_single_pool(min_pools[0])
                elif len(min_pools) == 2:
                    self.keeper.perform_upkeep_multiple_pools(min_pools)
                else:
                    self.keeper.perform_upkeep_multiple_pools_packed(min_pools)
                """
                break
            except Exception as e:
                print(f"Performing upkeep failed with {e!r}")
                break

    def loop_until_ready(self, first_min_pool, upkeep_time):
        """Once the update interval has passed according to off-chain time,
        iterate until the blockchain state says the upkeep will be successful.
        This exists because the off-chain time tends to be a bit later than the
        on-chain `block.timestamp`, causing premature upkeep calls (waste of gas)
        """
        for i in range(0, 400):
            try:
                first = time.time()
                time_difference = upkeep_time - self.w3.eth.get_block('latest').timestamp
                second = time.time()
                print(time_difference)
                print(f"took {second - first} seconds")
                if time_difference > 10:
                    time.sleep(max(0, time_difference - 5))
                    continue 
                elif time_difference > 5:
                    time.sleep(0.5)
                    continue 
                else:
                    time.sleep(max(0, time_difference - 4))
                    print("Ready to upkeep")
                    return True
            except Exception as e:
                print(f"Checking upkeep failed with {e!r}")
            print("Not yet ready")
            time.sleep(0.25)
        return False
    
    def prepare(self):
        """Scan for the next pool to be upkept and sleep until it is ready
        """
        minimum_wait_time = None
        min_pools = None
        try:
            (minimum_wait_time, min_pools, next_upkeep_time) = self.minimum_wait_time()
        except Exception as e:
            print(f"Scanning for upkeep times failed with {e!r}")
            return (None, None)

        # Add a small amount of buffer to the sleep, because I have noticed some weird stuff happening
        # with the timestamp where local time vs Arbitrum One timestamp gets offput by a small amount.
        if minimum_wait_time > 0:
            print(f"sleeping for {minimum_wait_time - 10}")
            time.sleep(max(0, minimum_wait_time - 10))

        # Do it again in case more can be upkept
        """
        try:
            (minimum_wait_time, min_pools) = self.minimum_wait_time()
        except Exception as e:
            print(f"Scanning for upkeep times failed with {e!r}")
            return None
        """

        return (min_pools, next_upkeep_time)
