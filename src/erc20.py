import time
from contract_utilities import fetch_build
from web3 import Web3
from eth_account import Account

ABI_FILE = "./artifacts/ERC20.json"

class ERC20(object):
	def __init__(self, w3, address):
		self.w3 = w3
		json = fetch_build(ABI_FILE)
		self.abi = json[0]
		self.contract = w3.eth.contract(address=address, abi=self.abi)
		self.address = address

	def total_supply(self):
		return self.contract.functions.totalSupply().call()

	def balance_of(self, address):
		return self.contract.functions.balanceOf(address).call()


