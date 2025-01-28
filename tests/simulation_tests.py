from src.utils.Database import Database as db
from src.network.node import Node
from src.staking.staking_pool import StakingPool
from src.blockchain.blockchain import Blockchain
from src.blockchain.transaction import Transaction
import time

# Initialize the database connection
db.initialize(
    host="localhost",
    database="plc_db",
    user="blockchain_user",
    password="pass",
    port=5432
)

# Initialize blockchain and staking pool
blockchain = Blockchain()
staking_pool = StakingPool()

def menu():
    """Display the menu options."""
    print("\n==== PoloCoin App ====")
    print("1. Register a Node")
    print("2. Stake Coins")
    print("3. Unstake Coins")
    print("4. Create Transaction")
    print("5. View Blockchain")
    print("6. Exit")

def register_node():
    """Register a new node."""
    public_key = input("Enter node public key: ")
    Node.register_node(public_key)
    print(f"Node with public key {public_key} registered.")

def stake_coins():
    """Stake coins for a node."""
    public_key = input("Enter node public key: ")
    amount = float(input("Enter amount to stake: "))
    staking_pool.add_stake(public_key, amount)
    print(f"{amount} coins staked for node {public_key}.")

def unstake_coins():
    """Unstake coins from a node."""
    public_key = input("Enter node public key: ")
    amount = float(input("Enter amount to unstake: "))
    staking_pool.remove_stake(public_key, amount)
    print(f"{amount} coins unstaked for node {public_key}.")

def create_transaction():
    """Create a new transaction."""
    sender = input("Enter sender public key: ")
    receiver = input("Enter receiver public key: ")
    amount = float(input("Enter transaction amount: "))
    transaction = Transaction(sender, receiver, amount)

    # Simulate validator selection
    validator = staking_pool.select_validator()
    if validator:
        print(f"Validator selected: {validator}")
        blockchain.add_transaction(transaction)
        blockchain.mine_pending_transactions(validator)
        print("Transaction added to the blockchain and mined.")
    else:
        print("No validators available. Cannot process the transaction.")

def view_blockchain():
    """Display the blockchain."""
    print("\n==== Blockchain ====")
    for block in blockchain.chain:
        print(block.to_dict())
    print("====================")

def main():
    """Main simulation loop."""
    while True:
        menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            register_node()
        elif choice == "2":
            stake_coins()
        elif choice == "3":
            unstake_coins()
        elif choice == "4":
            create_transaction()
        elif choice == "5":
            view_blockchain()
        elif choice == "6":
            print("Exiting PoloCoin App...")
            db.close_all_connections()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
