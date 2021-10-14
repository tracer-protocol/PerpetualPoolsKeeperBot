import time
from contract_utilities import fetch_build
from web3 import Web3
from eth_account import Account

ABI_FILE = "./artifacts/LeveragedPool.json"

class LeveragedPool(object):
	def __init__(self, w3, address):
		self.w3 = w3
		json = fetch_build(ABI_FILE)
		self.abi = json[0]
		self.contract = w3.eth.contract(address=address, abi=self.abi)
		self.address = address

	def interval_passed(self):
		return self.contract.functions.intervalPassed().call()

	def update_interval(self):
		return self.contract.functions.updateInterval().call()

	def last_price_timestamp(self):
		return self.contract.functions.lastPriceTimestamp().call()

	def time_till_next_upkeep(self):
		return_result = self.update_interval() + self.last_price_timestamp() - time.time()
		return max(return_result, 0)


