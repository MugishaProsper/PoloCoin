from src.blockchain.blockchain import Blockchain
from src.blockchain.wallet import Wallet

def test_pos_enhanced():
    # Initialize blockchain and wallets
    my_blockchain = Blockchain()
    wallet1 = Wallet("Validator1")
    wallet2 = Wallet("Validator2")

    # Stake coins
    my_blockchain.add_stake(wallet1.address, wallet1.stake(50))
    my_blockchain.add_stake(wallet2.address, wallet2.stake(30))

    # Print staking pool
    print("Staking Pool:", my_blockchain.staking_pool)

    # Add blocks and simulate rewards/slashing
    my_blockchain.add_block(["Transaction 1", "Transaction 2"])
    my_blockchain.add_block(["Transaction 3", "Transaction 4"])

    # Validator1 withdraws some stake
    my_blockchain.withdraw_stake(wallet1.address, 20)

    # Print the final staking pool
    print("Final Staking Pool:", my_blockchain.staking_pool)

test_pos_enhanced()
