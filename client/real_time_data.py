import time
import pandas as pd
from web3 import Web3
import hashlib
import json
from model import LocalModel

# Load full dataset initially
data = pd.read_csv("data/aursad.csv")
X = data.iloc[:, :-1]  # Features
y = data.iloc[:, -1]   # Labels

# Train local model once
model = LocalModel()
model.train(X, y)
model.save_model()
print("[Client] Trained local model and saved weights.")

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
assert w3.is_connected(), "Web3 not connected"

# Contract setup
contract_address = "0x192cE3eF4c21B972cbFd208Ea088B0fa9af63Bad"
with open("artifacts/contracts/DataVerification.sol/DataVerification.json") as f:
    abi = json.load(f)["abi"]

contract = w3.eth.contract(address=contract_address, abi=abi)

# Your private key and account address
private_key = "0x9afccdea74cfb70b3d756cec4ff7954e749f64e4b890c4886c263fe41af59d1b"
account = "0x03d154aaA29Caa484470f2c31D81a4f51b6f2267"

def hash_row(row):
    return hashlib.sha256(",".join(map(str, row)).encode()).hexdigest()

seen_hashes = set()
MAX_ROWS_PER_LOOP = 5  # limit how many new rows we process per iteration

while True:
    df = pd.read_csv("data/aursad.csv")
    new_rows_count = 0

    for _, row in df.iterrows():
        if new_rows_count >= MAX_ROWS_PER_LOOP:
            break

        row_hash = hash_row(row)
        if row_hash not in seen_hashes:
            seen_hashes.add(row_hash)
            new_rows_count += 1

            print("[Client] New data row found:", row.to_dict())

            nonce = w3.eth.get_transaction_count(account)
            tx = contract.functions.addToWhitelist(Web3.to_bytes(hexstr=row_hash)).build_transaction({
                "from": account,
                "nonce": nonce,
                "gas": 2000000,
                "gasPrice": w3.to_wei("50", "gwei")
            })

            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print("[Client] Hash stored on blockchain! TxHash:", tx_hash.hex())

            time.sleep(1)  # little pause between txs

    time.sleep(5)  # wait before next read to simulate real-time checking
