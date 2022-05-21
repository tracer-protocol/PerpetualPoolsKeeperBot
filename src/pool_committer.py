import time
from contract_utilities import fetch_build
from web3 import Web3
from eth_account import Account

ABI_FILE = "./artifacts/PoolCommitter.json"

class PoolCommitter(object):
	def __init__(self, w3, address):
		self.w3 = w3
		json = fetch_build(ABI_FILE)
		self.abi = json[0]
		self.contract = w3.eth.contract(address=address, abi=self.abi)
		self.address = address

	def interval_passed(self):
		return self.contract.functions.intervalPassed().call()

	def pool_name(self):
		return self.contract.functions.poolName().call()

	def update_interval_id(self):
		return self.contract.functions.updateIntervalId().call()

	def total_pool_commitments(self, update_interval):
		# return self.contract.functions.userCommitments("0xA79AA23603823E9A968d0F0029cc6CdAcbebaFAa", update_interval).call()
		return self.contract.functions.totalPoolCommitments(update_interval).call()

	def pending_long_burn_pool_tokens(self):
		return self.contract.functions.pendingLongBurnPoolTokens().call()

	def pending_short_burn_pool_tokens(self):
		return self.contract.functions.pendingShortBurnPoolTokens().call()


