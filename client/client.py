import time
import pandas as pd
import hashlib
import json
import requests
import sys
import gc
import threading
import os
from web3 import Web3
from model import LocalModel  # your ML model class

# --------- Optional Client ID for Multi-Client Setup -----------
client_id = sys.argv[1] if len(sys.argv) > 1 else "main"
print(f"[Client {client_id}] Initializing...")

# --------- Setup -----------
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
assert w3.is_connected(), f"[Client {client_id}] Web3 not connected"

private_key = "0xYOUR_PRIVATE_KEY_HERE"  # Replace with your private key
account = "0xYOUR_ACCOUNT_ADDRESS_HERE"  # Replace with your account address
contract_address = "0xYOUR_CONTRACT_ADDRESS_HERE"  # Replace with your contract address

with open("artifacts/contracts/DataVerification.sol/DataVerification.json") as f:
    abi = json.load(f)["abi"]
contract = w3.eth.contract(address=contract_address, abi=abi)

model = LocalModel()
max_training_rounds = 2
training_counter = 0
MAX_ROWS_PER_LOOP = 20
ROW_BATCH_FOR_UPDATE = 20
data_buffer = []

# -------- Shared Hash File ------------
hash_file = ".seen_hashes.json"
hash_lock = threading.Lock()

def load_seen_hashes():
    if not os.path.exists(hash_file):
        return set()
    with open(hash_file, "r") as f:
        return set(json.load(f))

def save_seen_hashes(seen):
    with open(hash_file, "w") as f:
        json.dump(list(seen), f)

def hash_row(row):
    return hashlib.sha256(",".join(map(str, row)).encode()).hexdigest()

def store_hash_on_chain(row_hash_hex):
    row_hash_bytes = bytes.fromhex(row_hash_hex)
    try:
        already_whitelisted = contract.functions.verifyDataHash(row_hash_bytes).call()
    except Exception as e:
        print(f"[Client {client_id}] [Error] verifyDataHash call failed: {e}")
        return False

    if already_whitelisted:
        print(f"[Client {client_id}] Hash already whitelisted.")
        return False

    nonce = w3.eth.get_transaction_count(account)
    tx = contract.functions.addToWhitelist(row_hash_bytes).build_transaction({
        "from": account,
        "nonce": nonce,
        "gas": 2000000,
        "gasPrice": w3.to_wei("50", "gwei")
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"[Client {client_id}] Stored hash | Tx: {tx_hash.hex()}")
    return True

def send_model_to_server():
    weights = model.get_weights()
    res = requests.post("http://127.0.0.1:5000/upload_model", json=weights)
    print(f"[Client {client_id}] Sent model weights. Server said:", res.text)

def receive_model_from_server():
    res = requests.get("http://127.0.0.1:5000/get_global_model")
    if res.status_code == 200:
        model.load_weights(res.json())
        print(f"[Client {client_id}] Updated model from server.")
    else:
        print(f"[Client {client_id}] Failed to get global model")

# ---------- Main Loop -----------
try:
    while True:
        df = pd.read_csv("data/aursad.csv")
        new_rows = 0

        with hash_lock:
            seen_hashes = load_seen_hashes()

        for _, row in df.iterrows():
            if new_rows >= MAX_ROWS_PER_LOOP:
                break

            row_hash_hex = hash_row(row)

            with hash_lock:
                if row_hash_hex in seen_hashes:
                    continue
                seen_hashes.add(row_hash_hex)
                save_seen_hashes(seen_hashes)

            print(f"[Client {client_id}] Received new data, hashing and storing...")
            success = store_hash_on_chain(row_hash_hex)
            if success:
                data_buffer.append(row)
                new_rows += 1

        if len(data_buffer) >= ROW_BATCH_FOR_UPDATE:
            print(f"[Client {client_id}] Training model on {len(data_buffer)} new rows")
            batch_df = pd.DataFrame(data_buffer)
            X = batch_df.iloc[:, :-1]
            y = batch_df.iloc[:, -1]

            if len(set(y)) < 2:
                print(f"[Client {client_id}] Skipping training — only one class in batch: {set(y)}")
            else:
                model.train(X, y)
                send_model_to_server()
                receive_model_from_server()
                training_counter += 1
                print(f"[Client {client_id}] ✅ Training round {training_counter} completed.")
                if training_counter >= max_training_rounds:
                    print(f"[Client {client_id}] Max training reached ({max_training_rounds}). Exiting.")
                    break

            data_buffer = []

        if new_rows == 0 and len(data_buffer) < ROW_BATCH_FOR_UPDATE:
            print(f"[Client {client_id}] No new data. Nothing to train. Exiting.")
            break

        time.sleep(5)
        gc.collect()

except KeyboardInterrupt:
    print(f"\n[Client {client_id}] Exiting gracefully.")
except Exception as e:
    print(f"\n[Client {client_id}] Unhandled error: {e}")
