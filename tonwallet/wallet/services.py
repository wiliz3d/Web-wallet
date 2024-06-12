# wallet/services.py
from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.types import KeyPair, DeploySet, CallSet, Signer, Abi
from .models import Wallet
import json
import uuid 


client = TonClient(network={'server_address': DEVNET_BASE_URL})

def generate_wallet():
    keys = client.crypto.generate_random_sign_keys()
    address = create_wallet(keys)
    return address, keys

def create_wallet(keys):
    # Load the TVC and ABI files
    with open('path/to/wallet.tvc', 'rb') as f:
        tvc = f.read()

    with open('path/to/wallet.abi.json', 'r') as f:
        abi = json.load(f)

    # Prepare the deploy set
    deploy_set = DeploySet(
        tvc=tvc,
        initial_data={}
    )

    # Prepare the call set for constructor, if needed
    call_set = CallSet(
        function_name='constructor',
        input={}
    )

    # Prepare the signer
    signer = Signer.Keys(keys)

    # Prepare the ABI
    abi = Abi.Json(abi)

    # Deploy the wallet contract
    result = client.abi.encode_message(
        abi=abi,
        deploy_set=deploy_set,
        call_set=call_set,
        signer=signer
    )

    address = result['address']

    # Process the message to deploy the contract
    client.processing.process_message(
        message_encode_params={
            'abi': abi,
            'deploy_set': deploy_set,
            'call_set': call_set,
            'signer': signer,
        }
    )

    return address

def get_balance(address):
    result = client.net.query_collection(
        collection='accounts',
        filter={'id': {'eq': address}},
        result='balance'
    )
    return int(result[0]['balance'], 16) / 10**9  # Convert from nanotons

def send_transaction(from_wallet, to_address, amount):
    # Decrypt the seed phrase
    seed_phrase = from_wallet.decrypt_seed_phrase()
    
    # Generate keypair from the seed phrase
    keys = client.crypto.mnemonic_derive_sign_keys(phrase=seed_phrase)
    
    # Prepare the call set for the send transaction method
    call_set = CallSet(
        function_name='sendTransaction',
        input={
            'dest': to_address,
            'value': int(amount * 10**9),  # Convert to nanotons
            'bounce': False
        }
    )
    
    # Prepare the signer
    signer = Signer.Keys(keys)
    
    # Prepare the ABI
    abi = Abi.Json(json.loads('<abi_of_your_wallet>'))
    
    # Execute the transaction
    result = client.processing.process_message(
        message_encode_params={
            'abi': abi,
            'address': from_wallet.address,
            'call_set': call_set,
            'signer': signer
        }
    )
    
    return result

def generate_receive_code(wallet):
    wallet.receive_code = uuid.uuid4()
    wallet.save()
    return wallet.receive_code
