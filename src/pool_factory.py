import time
from contract_utilities import fetch_build
from web3 import Web3
from eth_account import Account

ABI_FILE = "./artifacts/PoolFactory.json"

class PoolFactory(object):
	def __init__(self, w3, address):
		self.w3 = w3
		json = fetch_build(ABI_FILE)
		self.abi = json[0]  		
		self.contract = w3.eth.contract(address=address, abi=self.abi)
		self.address = address

	def numPools(self):
		return self.contract.functions.numPools().call()
	
	def pools(self,index):
		return self.contract.functions.pools(index).call()
	
	def getPools(self):
		pools = []
		for i in range(self.numPools()):
			pools.append(self.pools(i))
		return pools
 


