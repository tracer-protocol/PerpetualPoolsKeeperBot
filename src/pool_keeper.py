from contract_utilities import fetch_build
from web3 import Web3
from eth_account import Account
import hexbytes

ABI_FILE = "./artifacts/PoolKeeper.json"
POOL_ABI_FILE = "./artifacts/LeveragedPool.json"

class PoolKeeper(object):
    def __init__(self, w3, address, private_key):
        self.w3 = w3
        json = fetch_build(ABI_FILE)
        self.abi = json[0]
        self.contract = w3.eth.contract(address=address, abi=self.abi)
        self.private_key = private_key
        self.wallet_address = Account.privateKeyToAccount(self.private_key).address


    def check_upkeep(self, address):
        return self.contract.functions.checkUpkeepSinglePool(address).call()

    def tx_skeleton(self):
        nonce = self.w3.eth.getTransactionCount(self.wallet_address)
        tx_data = {
            'nonce': nonce,
            'gas': 12500000,
        }
        return tx_data

    def send_and_process_tx(self, tx):
        signed_tx = self.w3.eth.account.signTransaction(tx, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(f"Transaction hash: {signed_tx.hash.hex()}")
        print(f"Waiting for receipt")
        self.w3.eth.wait_for_transaction_receipt(signed_tx.hash, timeout=45)

    def perform_upkeep_single_pool(self, address):
        tx_data = self.tx_skeleton()

        tx = self.contract.functions.performUpkeepSinglePool(address).buildTransaction(tx_data)
        self.send_and_process_tx(tx)


    def perform_upkeep_multiple_pools(self, addresses):
        tx_data = self.tx_skeleton()

        tx = self.contract.functions.performUpkeepMultiplePools(addresses).buildTransaction(tx_data)
        self.send_and_process_tx(tx)

