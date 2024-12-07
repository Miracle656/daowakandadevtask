from algosdk import account, encoding, mnemonic
from algosdk import transaction
from algosdk.v2client import algod
from typing import Dict, Any

# Create a new algod client, configured to connect to our local sandbox
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

#utility funtions
def create_account():
    private_key, address = account.generate_account()
    print(f"Created account: {address}")
    print(f"Mnemonic: {mnemonic.from_private_key(private_key)}")
    
    return private_key, address

def wait_for_confirmation(txid):
    while True:
        try:
            tx_info = algod_client.pending_transaction_info(txid)
            if tx_info.get("confirmed-round"):
                print(f"Transaction confirmed in round {tx_info['confirmed-round']}.")
                return tx_info
        except Exception:
            pass


# create an ASA
def create_asa(creator_key, creator_address):
    params = algod_client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=creator_address,
        sp=params,
        total=1000,
        default_frozen=False,
        unit_name="TESTASA",
        asset_name="Test Algorand Standard Asset",
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address,
        decimals=0,
    )
    stxn = txn.sign(creator_key)
    txid = algod_client.send_transaction(stxn)
    print(f"Asset creation transaction sent with txID: {txid}")
    tx_info = wait_for_confirmation(txid)
    asset_id = tx_info["asset-index"]
    print(f"Created ASA with ID: {asset_id}")
    return asset_id

# opt account B into the ASA
def opt_in_asset(account_key, account_address, asset_id):
    params = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=account_address,
        sp=params,
        receiver=account_address,
        amt=0,
        index=asset_id,
    )
    stxn = txn.sign(account_key)
    txid = algod_client.send_transaction(stxn)
    print(f"Opt-in transaction sent with txID: {txid}")
    wait_for_confirmation(txid)

# Transfer 1 unit of the ASA from A to B
def transfer_asset(sender_key, sender_address, receiver_address, asset_id, amount):
    params = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        amt=amount,
        index=asset_id
    )
    stxn = txn.sign(sender_key)
    txid = algod_client.send_transaction(stxn)
    print(f"Transfer transaction sent with txID: {txid}")
    wait_for_confirmation(txid)

# Freeze the ASA in account B
def freeze_asset(freeze_account_key, freeze_account_address, target_account, asset_id, freeze_state):
    params = algod_client.suggested_params()
    txn = transaction.AssetFreezeTxn(
        sender=freeze_account_address,
        sp=params,
        index=asset_id,
        target=target_account,
        new_freeze_state=freeze_state,
    )
    stxn = txn.sign(freeze_account_key)
    txid = algod_client.send_transaction(stxn)
    print(f"Freeze transaction sent with txID: {txid}")
    wait_for_confirmation(txid)

# generate 2 accounts
acct1pk, acct1addr = create_account()
acct2pk, acct2addr = create_account()

print("Fund accounts A and B with 10 ALGOs each before proceeding")

asset_id = None

print("Freeze ASA solution")
# choice = input("what will you? \n1. create asa\n2. opt acct b into asa\n3. transfer 1 unit\n4. freeze asa\nchoose an option: ")

continue_operation = 'y'

while continue_operation == 'y':
    choice = input("what will you? \n1. create asa\n2. opt acct b into asa\n3. transfer 1 unit\n4. freeze asa\nchoose an option: ")
    if choice == '1':
        asset_id = create_asa(acct1pk, acct1addr)
    elif choice == '2':
        opt_in_asset(acct2pk, acct2addr, asset_id)
    elif choice == '3':
        transfer_asset(acct1pk, acct1addr, acct2addr, asset_id, 1)
    elif choice == '4':
        freeze_asset(acct1pk, acct1addr, acct2addr, asset_id, True)
    else:
        print("invalid option")
        
    continue_operation = input("Would you like to do anything else[y/n]: ")

print("Script completed successfully!")