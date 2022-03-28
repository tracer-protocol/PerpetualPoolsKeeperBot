import time
import sys

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
                min_pools = [pool.address]
                current_minimum = wait_time
            elif wait_time == current_minimum:
                min_pools.append(pool.address)
        return (current_minimum, min_pools)

    def run(self):
        while True:
            self.main_loop()

    def main_loop(self):
        """Main loop to wait for update interval to pass, then execute upkeep."""
        min_pools = self.prepare()
        if not min_pools:
            return

        while True:
            print("Checking upkeep")
            print(f"Pools that need upkeep: {min_pools}")
            start_time = time.time()
            if not self.loop_until_ready(min_pools[0]):
                pass
                break
            end_time = time.time()
            print(end_time - start_time)

            try:
                # There exists a function that allows you to pass in an array of pools,
                # which is unnecessary if you only want to upkeep one
                if len(min_pools) == 1:
                    self.keeper.perform_upkeep_single_pool(min_pools[0])
                else:
                    self.keeper.perform_upkeep_multiple_pools(min_pools)
                break
            except Exception as e:
                print(f"Performing upkeep failed with {e!r}")
                break

    def loop_until_ready(self, first_min_pool):
        """Once the update interval has passed according to off-chain time,
        iterate until the blockchain state says the upkeep will be successful.
        This exists because the off-chain time tends to be a bit later than the
        on-chain `block.timestamp`, causing premature upkeep calls (waste of gas)
        """
        for i in range(0, 10):
            try:
                if self.keeper.check_upkeep(first_min_pool):
                    print("Ready to upkeep")
                    return True
            except Exception as e:
                print(f"Checking upkeep failed with {e!r}")
            print("Not yet ready")
            time.sleep(1)
        return False
    
    def prepare(self):
        """Scan for the next pool to be upkept and sleep until it is ready
        """
        minimum_wait_time = None
        min_pools = None
        try:
            (minimum_wait_time, min_pools) = self.minimum_wait_time()
        except Exception as e:
            print(f"Scanning for upkeep times failed with {e!r}")
            return None

        # Add a small amount of buffer to the sleep, because I have noticed some weird stuff happening
        # with the timestamp where local time vs Arbitrum One timestamp gets offput by a small amount.
        print(min_pools[0])
        if minimum_wait_time > 0:
            print(f"sleeping for {minimum_wait_time + 300}")
            time.sleep(minimum_wait_time + 400)

        # Do it again in case more can be upkept
        try:
            (minimum_wait_time, min_pools) = self.minimum_wait_time()
        except Exception as e:
            print(f"Scanning for upkeep times failed with {e!r}")
            return None

        return min_pools
