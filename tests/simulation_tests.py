import time
from src.utils.Database import Database as db
from src.network.node import Node
from src.blockchain.blockchain import Blockchain
from src.blockchain.transaction import Transaction
from src.staking.staking_pool import StakingPool

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

# Create nodes
node1 = Node(host="127.0.0.1", port=5000)
node2 = Node(host="127.0.0.1", port=5001)
node3 = Node(host="127.0.0.1", port=5002)

# Start nodes
node1.start()
node2.start()
node3.start()

# Wait for nodes to initialize
time.sleep(2)

# Connect nodes to each other
node2.connect_to_peer("127.0.0.1", 5000)
node3.connect_to_peer("127.0.0.1", 5000)


def register_nodes():
    """Register nodes in the network."""
    print("Registering nodes...")
    node1.save_to_db()
    node2.save_to_db()
    node3.save_to_db()
    print("Nodes registered.")


def stake_coins():
    """Stake coins for nodes."""
    print("Staking coins...")
    node1.stake(sender=node1.public_key, amount=100)
    node2.stake(sender=node2.public_key, amount=150)
    node3.stake(sender=node3.public_key, amount=200)
    print("Coins staked.")


def create_transactions():
    """Create transactions between nodes."""
    print("Creating transactions...")
    transaction1 = Transaction(sender=node1.public_key, receiver=node2.public_key, amount=10)
    transaction2 = Transaction(sender=node2.public_key, receiver=node3.public_key, amount=20)

    blockchain.add_transaction(transaction1)
    blockchain.add_transaction(transaction2)

    blockchain.mine_pending_transactions(node1.public_key)
    print("Transactions created and mined.")


def view_blockchain():
    """View the current state of the blockchain."""
    print("Viewing blockchain...")
    for block in blockchain.chain:
        print(block.to_dict())
    print("Blockchain viewed.")


def unstake_coins():
    """Unstake coins from nodes."""
    print("Unstaking coins...")
    node1.unstake(sender=node1.public_key, amount=50)
    node2.unstake(sender=node2.public_key, amount=75)
    node3.unstake(sender=node3.public_key, amount=100)
    print("Coins unstaked.")


def main():
    """Main function to run the test."""
    register_nodes()
    stake_coins()
    create_transactions()
    view_blockchain()
    unstake_coins()
    view_blockchain()


if __name__ == "__main__":
    main()