"""
Deploy D8 Economy to BSC Testnet

Steps:
1. Compile smart contracts
2. Deploy D8Token
3. Deploy FundamentalLaws
4. Create congress wallet
5. Initialize fundamental laws
6. Save deployment info
"""

import json
from pathlib import Path
from web3 import Web3
from solcx import compile_source, install_solc
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Install Solidity compiler
install_solc('0.8.0')


def compile_contract(contract_path: Path) -> dict:
    """Compile Solidity contract"""
    print(f"📦 Compiling {contract_path.name}...")
    
    with open(contract_path) as f:
        source = f.read()
    
    compiled = compile_source(source, output_values=['abi', 'bin'])
    
    # Get contract interface
    contract_id = list(compiled.keys())[0]
    return compiled[contract_id]


def deploy_contract(w3: Web3, contract_interface: dict, deployer_address: str, deployer_key: str, *args) -> tuple:
    """Deploy contract to blockchain"""
    
    contract = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )
    
    # Build transaction
    nonce = w3.eth.get_transaction_count(deployer_address)
    
    transaction = contract.constructor(*args).build_transaction({
        'from': deployer_address,
        'nonce': nonce,
        'gas': 3000000,
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign and send
    signed = w3.eth.account.sign_transaction(transaction, deployer_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    
    print(f"   TX sent: {tx_hash.hex()}")
    
    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] != 1:
        raise Exception("Contract deployment failed")
    
    print(f"   ✅ Deployed at: {receipt['contractAddress']}")
    
    return receipt['contractAddress'], contract_interface['abi']


def main():
    print("🚀 D8 Economy Deployment to BSC Testnet")
    print("=" * 60)
    
    # 1. Connect to BSC Testnet
    bsc_rpc = os.getenv("BSC_TESTNET_RPC", "https://data-seed-prebsc-1-s1.binance.org:8545/")
    w3 = Web3(Web3.HTTPProvider(bsc_rpc))
    
    if not w3.is_connected():
        print("❌ Failed to connect to BSC Testnet")
        return
    
    print(f"✅ Connected to BSC Testnet (Chain ID: {w3.eth.chain_id})")
    print()
    
    # 2. Get deployer account (Leo)
    leo_address = os.getenv("LEO_ADDRESS")
    leo_private_key = os.getenv("LEO_PRIVATE_KEY")
    
    if not leo_address or not leo_private_key:
        print("❌ LEO_ADDRESS and LEO_PRIVATE_KEY must be set in .env")
        return
    
    balance = w3.eth.get_balance(leo_address)
    balance_bnb = w3.from_wei(balance, 'ether')
    
    print(f"👤 Deployer (Leo): {leo_address}")
    print(f"   Balance: {balance_bnb:.4f} BNB")
    
    if balance_bnb < 0.1:
        print("⚠️  Warning: Low BNB balance. Get testnet BNB from faucet:")
        print("   https://testnet.binance.org/faucet-smart")
        return
    
    print()
    
    # 3. Compile contracts
    contracts_dir = Path(__file__).parent.parent / "app" / "economy" / "contracts"
    
    print("📦 Compiling smart contracts...")
    d8_token = compile_contract(contracts_dir / "D8Token.sol")
    fundamental_laws = compile_contract(contracts_dir / "FundamentalLaws.sol")
    print("✅ Contracts compiled")
    print()
    
    # 4. Deploy D8Token
    print("🪙 Deploying D8Token...")
    token_address, token_abi = deploy_contract(
        w3, d8_token, leo_address, leo_private_key
    )
    print()
    
    # 5. Deploy FundamentalLaws
    print("📜 Deploying FundamentalLaws...")
    laws_address, laws_abi = deploy_contract(
        w3, fundamental_laws, leo_address, leo_private_key
    )
    print()
    
    # 6. Create congress wallet
    print("🏛️  Creating congress wallet...")
    congress_account = w3.eth.account.create()
    congress_address = congress_account.address
    congress_private_key = congress_account.key.hex()
    
    print(f"   Address: {congress_address}")
    
    # Fund congress with some BNB for gas
    transfer_tx = {
        'from': leo_address,
        'to': congress_address,
        'value': w3.to_wei(0.01, 'ether'),
        'nonce': w3.eth.get_transaction_count(leo_address),
        'gas': 21000,
        'gasPrice': w3.eth.gas_price
    }
    
    signed = w3.eth.account.sign_transaction(transfer_tx, leo_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"   ✅ Funded with 0.01 BNB")
    print()
    
    # 7. Update congress in D8Token
    print("🔧 Configuring D8Token...")
    token_contract = w3.eth.contract(address=token_address, abi=token_abi)
    
    update_congress_tx = token_contract.functions.updateCongress(congress_address).build_transaction({
        'from': leo_address,
        'nonce': w3.eth.get_transaction_count(leo_address),
        'gas': 100000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed = w3.eth.account.sign_transaction(update_congress_tx, leo_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"   ✅ Congress set to {congress_address}")
    print()
    
    # 8. Initialize fundamental laws
    print("📜 Initializing fundamental laws...")
    
    from app.economy.security import FundamentalLawsSecurity, FUNDAMENTAL_LAWS
    
    laws_security = FundamentalLawsSecurity(
        bsc_client=None,  # We'll use direct web3
        contract_address=laws_address,
        encryption_key=os.getenv("LEO_ENCRYPTION_KEY", "default_key_change_this").encode()
    )
    
    laws_contract = w3.eth.contract(address=laws_address, abi=laws_abi)
    
    for law_id, law_content in FUNDAMENTAL_LAWS.items():
        # Encrypt law
        encrypted = laws_security.encryption.encrypt(law_content)
        data_hash = laws_security._hash_data(encrypted)
        
        # Create law on blockchain
        create_law_tx = laws_contract.functions.createLaw(
            law_id,
            encrypted,
            data_hash,
            law_content[:50]  # Short description
        ).build_transaction({
            'from': leo_address,
            'nonce': w3.eth.get_transaction_count(leo_address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed = w3.eth.account.sign_transaction(create_law_tx, leo_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"   ✅ Law {law_id} created")
    
    print()
    
    # 9. Save deployment info
    deployment_info = {
        'network': 'BSC Testnet',
        'chain_id': w3.eth.chain_id,
        'deployed_at': str(Path.cwd()),
        'contracts': {
            'd8_token': {
                'address': token_address,
                'abi': token_abi
            },
            'fundamental_laws': {
                'address': laws_address,
                'abi': laws_abi
            }
        },
        'wallets': {
            'leo': {
                'address': leo_address
                # Private key NOT saved
            },
            'congress': {
                'address': congress_address,
                'private_key': congress_private_key  # Save for system use
            }
        },
        'deployment_timestamp': w3.eth.get_block('latest')['timestamp']
    }
    
    deployment_file = Path.home() / "Documents" / "d8_data" / "deployment.json"
    deployment_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(deployment_file, 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"💾 Deployment info saved to {deployment_file}")
    print()
    
    # 10. Summary
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"D8Token:          {token_address}")
    print(f"FundamentalLaws:  {laws_address}")
    print(f"Congress:         {congress_address}")
    print()
    print("📋 Next steps:")
    print("1. Update .env with contract addresses")
    print("2. Run tests: pytest tests/economy/")
    print("3. Initialize economy in start_d8.py")
    print()
    print("🔍 View on BSCScan Testnet:")
    print(f"   https://testnet.bscscan.com/address/{token_address}")
    print(f"   https://testnet.bscscan.com/address/{laws_address}")


if __name__ == "__main__":
    main()
