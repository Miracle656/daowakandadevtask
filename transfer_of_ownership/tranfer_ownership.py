from algosdk import account, encoding, mnemonic
from algosdk import transaction
from algosdk.v2client import algod
from typing import Dict, Any

# Constants
# Create a new algod client, configured to connect to our local sandbox
algod_address = "http://localhost:4001"
algod_token = "a" * 64
algod_client = algod.AlgodClient(algod_token, algod_address)

# Utility functions
def create_account():
    private_key, address = account.generate_account()
    print(f"Created account: {address}")
    print(f"Mnemonic: {mnemonic.from_private_key(private_key)}")
    return private_key, address

def fund_account(funder_key, funder_address, recipient_address, amount):
    params = algod_client.suggested_params()
    txn = transaction.PaymentTxn(
        sender=funder_address,
        sp=params,
        receiver=recipient_address,
        amt=int(amount * 1e6),
    )
    signed_txn = txn.sign(funder_key)
    txid = algod_client.send_transaction(signed_txn)
    print(f"Funding transaction sent with txID: {txid}")
    wait_for_confirmation(txid)

def wait_for_confirmation(txid):
    while True:
        try:
            tx_info = algod_client.pending_transaction_info(txid)
            if tx_info.get("confirmed-round"):
                print(f"Transaction confirmed in round {tx_info['confirmed-round']}.")
                return tx_info
        except Exception as e:
            print(f"Waiting for confirmation... {e}")

# Create accounts
private_key_A, account_A = create_account()
private_key_B, account_B = create_account()

print("\nFund these accounts using your sandbox 'dispenser' before proceeding.")

# Step 1: Rekey Account A to Account B
def rekey_account(from_key, from_address, rekey_to):
    params = algod_client.suggested_params()
    txn = transaction.PaymentTxn(
        sender=from_address,
        sp=params,
        receiver=from_address,  # Self-transaction for rekeying
        amt=0,
        rekey_to=rekey_to
    )
    signed_txn = txn.sign(from_key)
    txid = algod_client.send_transaction(signed_txn)
    print(f"Rekey transaction sent with txID: {txid}")
    wait_for_confirmation(txid)

rekey_account(private_key_A, account_A, account_B)

# Step 2: Transfer all funds from Account A to Account B
def transfer_funds(sender_key, sender_address, receiver_address):
    params = algod_client.suggested_params()
    account_info = algod_client.account_info(sender_address)
    balance = account_info["amount"]
    txn = transaction.PaymentTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        amt=balance - 1000,  # Leave minimum balance
    )
    # Sign with the rekeyed account's private key
    signed_txn = txn.sign(sender_key)
    txid = algod_client.send_transaction(signed_txn)
    print(f"Transfer transaction sent with txID: {txid}")
    wait_for_confirmation(txid)

transfer_funds(private_key_B, account_A, account_B)

print("Script completed successfully!")
