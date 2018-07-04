import web3

from web3 import Web3, HTTPProvider, TestRPCProvider
from web3.contract import ConciseContract

from solc import compile_source, compile_standard
from solc import compile_source, compile_files, link_code

w3 = Web3(HTTPProvider("http://localhost:8545"));

def compile():
    Mixward = "./contracts/Mixward.sol"
    SafeMath = "./contracts/SafeMath.sol"  
    Queue =  "./contracts/Queue.sol"
    compiled_sol =  compile_files([Queue, SafeMath, Mixward], allow_paths="./contracts")
    mixward_interface = compiled_sol[Mixward + ':Mixward']
    return mixward_interface
   
def deploy():
    mixward_interface = compile()
    mixward = w3.eth.contract(abi=mixward_interface['abi'], bytecode=mixward_interface['bin'])
    tx_hash = mixward.deploy(transaction={'from': w3.eth.accounts[0], 'gas': 4000000}, args=[])
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, 10000)
    mixward_address = tx_receipt['contractAddress']
    print("[INFO] Mixward address: ", mixward_address)
    abi = mixward_interface['abi']
    mixward = w3.eth.contract(address=mixward_address, abi=abi, ContractFactoryClass=ConciseContract)
    return(mixward)

def deposit_call(mixward, callingAddress, recipient, rewardInWei):
    denomination = 1000000000000000000 # The contract supports payments of 1 ether = 1000000000000000000 wei
    value = rewardInWei + denomination
    tx_hash = mixward.deposit(recipient, transact={'from': callingAddress, 'gas': 4000000, "value": w3.toWei(value, "wei")})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, 10000)
    return tx_receipt

def unlock_call(mixward, callingAddress):
    tx_hash = mixward.unlock(transact={'from': callingAddress, 'gas': 4000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, 10000)
    return tx_receipt

def printBalances(sender, recipient, unlocker, mixward):
    print("Sender balance --> ", w3.eth.getBalance(sender))
    print("Recipient balance --> ", w3.eth.getBalance(recipient))
    print("Unlocker balance --> ", w3.eth.getBalance(unlocker))
    print("Mixward contract balance --> ", w3.eth.getBalance(mixward))

def main():
    senderAddress = w3.eth.accounts[0]
    recipientAddress = w3.eth.accounts[1]
    unlockerAddress = w3.eth.accounts[2]
    reward = 12000000000000000 # 12000000000000000 wei = 0.012finney = 0.012 ether

    print("Deploying contracts...")
    mixward = deploy()

    print(" ----------- BALANCES BEFORE DEPOSIT ---------- ")
    printBalances(senderAddress, recipientAddress, unlockerAddress, mixward.address)

    receipt = deposit_call(mixward, senderAddress, recipientAddress, reward)
    print("Receipt of deposit ", receipt)

    print(" ----------- BALANCES AFTER DEPOSIT ---------- ")
    printBalances(senderAddress, recipientAddress, unlockerAddress, mixward.address)

    print("Unlocking payment")
    receipt = unlock_call(mixward, unlockerAddress)
    print("Receipt of unlock ", receipt)

    print(" ----------- BALANCES AFTER WITHDRAW ---------- ")
    printBalances(senderAddress, recipientAddress, unlockerAddress, mixward.address)

if __name__== "__main__":
     main()
