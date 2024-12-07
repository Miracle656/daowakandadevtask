from algosdk import account, encoding, mnemonic
from algosdk import transaction
from algosdk.v2client import algod
from typing import Dict, Any

# Create a new algod client, configured to connect to our local sandbox
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)