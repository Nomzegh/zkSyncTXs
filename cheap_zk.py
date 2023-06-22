from web3 import Web3
from abi import contract_abi
import random
import time


#--CONFIG--#
#Insert Private keys in keys.txt; One key per line | Приватные ключи в созданный файл keys.txt. По 1 в строку, не должны начинаться с 0x
from_sec = 1      #|Wait from N seconds between transactions | Минимальное значение "ждать от N sec между транзакиями". Для рандомного выбора 
to_sec = 100	    #|Wait to N seconds between transactions | Максиимальное значение "спать до N sec между транзакциями". Для рандомного выбора 
eth_min = 0.00001 #|Min ETH quantity for deposit | Значение ETH минимального депозита. Для рандомного выбора
eth_max = 0.0001   #|Max ETH quantity for deposit | Значение ETH максимального депозита. Для рандомного выбора
contract_address = "0x7442E417C0B53d622d93F5D7BbD84eEd808F26C5" #|Contract address. DO NOT CHANGE if own contract is not deployed | Адрес контракта. НЕ МЕНЯТЬ если не свой не деплоили
RPC = "https://mainnet.era.zksync.io" #|RPC for web3 provider. DO NOT CHANGE if you dont have own RPC | RPC web3 провайдера. НЕ МЕНЯТЬ если нет своей
#----------#



eth_min = float(eth_min)
eth_max = float(eth_max)
private_keys = []
failed_keys = []
web3 = Web3(Web3.HTTPProvider(RPC))
contract_address = web3.to_checksum_address(contract_address)
contract = web3.eth.contract(contract_address, abi=contract_abi)

def random_sleep():
    sleep_duration = random.randint(from_sec, to_sec)
    print(f"Sleeping for {sleep_duration} seconds")
    time.sleep(sleep_duration)


def deposit(min_val, max_val, pvt_key):
	address = web3.eth.account.from_key(pvt_key).address
	value_eth = "{:.8f}".format(random.uniform(min_val, max_val))
	value_wei = web3.to_wei(value_eth, 'ether')
	transaction = contract.functions.deposit().build_transaction({
		'from': web3.to_checksum_address(address),
		'value': value_wei,
		'gasPrice': web3.to_wei(0.25, 'gwei'),
		'nonce': web3.eth.get_transaction_count(web3.to_checksum_address(address))
	})

	transaction['gas'] = int(web3.eth.estimate_gas(transaction))

	signed_txn = web3.eth.account.sign_transaction(transaction, pvt_key)
	transaction_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
	print(f"Deposited {value_eth} ETH | Hash: {transaction_hash}")
	random_sleep()


def withdraw(pvt_key):
	address = web3.eth.account.from_key(pvt_key).address
	balance = contract.functions.getBalance().call({'from': address})
	transaction = contract.functions.withdraw(
		balance
	).build_transaction({
		'from': web3.to_checksum_address(address),
		'value': 0,
		'gasPrice': web3.to_wei(0.25, 'gwei'),
		'nonce': web3.eth.get_transaction_count(web3.to_checksum_address(address))
	})
	transaction['gas'] = int(web3.eth.estimate_gas(transaction))
	signed_txn = web3.eth.account.sign_transaction(transaction, pvt_key)
	transaction_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
	print(f"Withdrawing {web3.from_wei(balance, 'ether')} ETH for {address}\nHash: {transaction_hash}\nPrivate key: {pvt_key}")
	random_sleep()

def check_balance(pvt_key):
	address = web3.eth.account.from_key(pvt_key).address
	balance = contract.functions.getBalance().call({'from': address})
	print(f"Address: {address}\nPrivate key: {pvt_key}\nBalance: {web3.from_wei(balance, 'ether')} ETH\n")

with open('keys.txt', 'r') as f:
    for line in f:
        line = line.strip()
        private_keys.append(line)

choice = int(input("\n----------------------\n1: deposit\n2: withdraw\n3: check balance\nChoice: "))
for key in private_keys:
    try:
        if choice == 1:
              deposit(eth_min, eth_max, key)
        elif choice == 2:
              withdraw(key)
        elif choice == 3:
              check_balance(key)
        else:
              print(f"Wrong choice number. 1 | 2 | 3")
    except Exception as e:
        print(f"Transaction failed for private key: {key} | Error: {e}")
        failed_keys.append(key)
    
print("\n\nFailed keys: ")
for failed in failed_keys:
    print(failed)
