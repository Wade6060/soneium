import time
from web3 import Web3
import random
from config import RPS, THREADS, RETRY, COUNT_TX, SLEEP_TRANSACTIONS, GAS, TIMEOUT, PERCENT, PROXY
from abi import ABI_WETH
import threading
from loguru import logger

proxies = {'http': f'http://{PROXY}', 'https': f'http://{PROXY}'}
web3 = Web3(Web3.HTTPProvider(RPS, request_kwargs={"proxies": proxies}))

def read_file():
    with open('accounts.txt', 'r') as file:
        lines = [line.rstrip() for line in file.readlines()]
    return lines

class Soneium():
    def __init__(self, accs):
        self.private = accs
        wallet = Web3().eth.account.from_key(self.private)
        self.address = wallet.address
        self.WETH = Web3.to_checksum_address('0x4200000000000000000000000000000000000006')
        self.contract_WETH = web3.eth.contract(address=self.WETH, abi=ABI_WETH)
        self.chainid = 1868
        self.timeout = TIMEOUT
        self.percent = PERCENT
        self.gas = GAS


    def wrap(self):
        for _ in range(RETRY):
            try:
                nonce = web3.eth.get_transaction_count(self.address)
                percent = random.uniform(*self.percent)
                amount_wrap = int(web3.eth.get_balance(self.address) * percent)
                gas = random.randint(90000, 120000)
                transaction = self.contract_WETH.functions.deposit().build_transaction({
                    'chainId': self.chainid,
                    'value': amount_wrap,
                    'nonce': nonce,
                    'gas': gas,
                    'gasPrice': int(web3.eth.gas_price * self.gas)

                })
                signed_transaction = web3.eth.account.sign_transaction(transaction, self.private)
                transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                time.sleep(5)
                tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=self.timeout,
                                                                   poll_latency=5)
                if tx_receipt['status'] == 1:
                    logger.success(f"WRAP | https://soneium.blockscout.com/tx/{transaction_hash.hex()}")
                    time.sleep(random.randint(*SLEEP_TRANSACTIONS))
                    return True
                else:
                    logger.error(f"ERROR WRAP, RETRY | https://soneium.blockscout.com/tx/{transaction_hash.hex()}")
                    time.sleep(random.randint(*SLEEP_TRANSACTIONS))

            except Exception as err:
                logger.error(f"ERROR :{err} | {self.address}")
                time.sleep(random.randint(*SLEEP_TRANSACTIONS))

    def unwrap(self):
        for _ in range(RETRY):
            try:
                nonce = web3.eth.get_transaction_count(self.address)
                amount_unwrap = self.contract_WETH.functions.balanceOf(self.address).call()
                gas = random.randint(90000, 120000)
                transaction = self.contract_WETH.functions.withdraw(amount_unwrap).build_transaction({
                    'chainId': self.chainid,
                    'value': 0,
                    'nonce': nonce,
                    'gas': gas,
                    'gasPrice': int(web3.eth.gas_price * self.gas)
                })
                signed_transaction = web3.eth.account.sign_transaction(transaction, self.private)
                transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                time.sleep(5)
                tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=self.timeout,
                                                                   poll_latency=5)
                if tx_receipt['status'] == 1:
                    logger.success(f"UNWRAP | https://soneium.blockscout.com/tx/{transaction_hash.hex()}")
                    time.sleep(random.randint(*SLEEP_TRANSACTIONS))
                    return True
                else:
                    logger.error(f"ERROR UNWRAP, RETRY | https://soneium.blockscout.com/tx/{transaction_hash.hex()}")
                    time.sleep(random.randint(*SLEEP_TRANSACTIONS))

            except Exception as err:
                logger.error(f"ERROR :{err} | {self.address}")
                time.sleep(random.randint(*SLEEP_TRANSACTIONS))

    def sign(self):
        for _ in range(RETRY):
            try:
                to_address = Web3.to_checksum_address('0xbb4904e033Ef5Af3fc5d3D72888f1cAd7944784D')
                nonce = web3.eth.get_transaction_count(self.address)
                gas = random.randint(90000, 120000)
                data = f'0xb5d7df97'
                transaction = {
                    'chainId': self.chainid,
                    'to': to_address,
                    'value': 0,
                    'nonce': nonce,
                    'gas': gas,
                    'data': data,
                    'gasPrice': int(web3.eth.gas_price * self.gas)
                }
                signed_transaction = web3.eth.account.sign_transaction(transaction, self.private)
                transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                time.sleep(5)
                tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=self.timeout,
                                                                   poll_latency=5)
                if tx_receipt['status'] == 1:
                    logger.success(f"SIGN | https://soneium.blockscout.com/tx/{transaction_hash.hex()}")
                    time.sleep(random.randint(*SLEEP_TRANSACTIONS))
                    return True
                else:
                    logger.error(f"ERROR SIGN, RETRY | https://soneium.blockscout.com/tx/{transaction_hash.hex()}")
                    time.sleep(random.randint(*SLEEP_TRANSACTIONS))

            except Exception as err:
                logger.error(f"ERROR :{err} | {self.address}")
                time.sleep(random.randint(*SLEEP_TRANSACTIONS))

    def farm(self):
        functions = [self.wrap, self.unwrap, self.sign]
        fixed_order = [self.wrap, self.unwrap]
        remaining = [func for func in functions if func not in fixed_order]
        insertion_point = random.randint(0, len(fixed_order))
        fixed_order.insert(insertion_point, remaining[0])
        for func in fixed_order:
            func()
def work(private, semaphore):
    with semaphore:
        worker = Soneium(private)
        for _ in range(random.randint(*COUNT_TX)):
            worker.farm()

threads = []
def main():
    semaphore = threading.Semaphore(THREADS)
    private_key = read_file()
    random.shuffle(private_key)
    for private in private_key:
        thread = threading.Thread(target=work, args=(private, semaphore))
        threads.append(thread)
        thread.start()
        time.sleep(random.randint(3, 5))


if __name__ == '__main__':
    print(f'Work {COUNT_TX} tx...')
    main()
    for t in threads:
        t.join()
    print(f"Done {COUNT_TX} tx.")