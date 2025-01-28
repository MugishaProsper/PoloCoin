from src.network.node import Node
import threading
import time

# Create multiple nodes
node1 = Node(host="127.0.0.1", port=5000)
node2 = Node(host="127.0.0.1", port=5001)
node3 = Node(host="127.0.0.1", port=5002)

# Start the nodes in separate threads
threading.Thread(target=node1.start, daemon=True).start()
threading.Thread(target=node2.start, daemon=True).start()
threading.Thread(target=node3.start, daemon=True).start()

# Wait for nodes to initialize
time.sleep(2)

# Connect nodes to each other
node2.connect_to_peer("127.0.0.1", 5000)
node3.connect_to_peer("127.0.0.1", 5000)

# Mock blockchain and staking pool for testing
class MockBlockchain:
    def __init__(self):
        self.chain = []
        self.transaction_pool = []
        self.staking_pool = MockStakingPool()

    def process_transaction(self, transaction):
        self.transaction_pool.append(transaction)
        return True

    def process_staking(self, transaction):
        return self.staking_pool.add_stake(transaction.sender, transaction.amount)

    def process_unstaking(self, transaction):
        return self.staking_pool.remove_stake(transaction.sender, transaction.amount)

class MockStakingPool:
    def __init__(self):
        self.stakes = {}

    def add_stake(self, sender, amount):
        if sender not in self.stakes:
            self.stakes[sender] = 0
        self.stakes[sender] += amount
        print(f"Staked {amount} for {sender}. Total stake: {self.stakes[sender]}")
        return True

    def remove_stake(self, sender, amount):
        if sender in self.stakes and self.stakes[sender] >= amount:
            self.stakes[sender] -= amount
            print(f"Unstaked {amount} for {sender}. Remaining stake: {self.stakes[sender]}")
            return True
        print(f"Failed to unstake {amount} for {sender}. Insufficient stake.")
        return False

# Replace each node's blockchain with the mock implementation
node1.blockchain = MockBlockchain()
node2.blockchain = MockBlockchain()
node3.blockchain = MockBlockchain()

# Perform staking and unstaking transactions
time.sleep(1)
node1.stake(sender="user_1", amount=100)  # Stake 100 for user_1
time.sleep(1)
node2.unstake(sender="user_1", amount=50)  # Unstake 50 for user_1
time.sleep(1)
node3.stake(sender="user_2", amount=200)  # Stake 200 for user_2
time.sleep(1)

# Keep the script running to allow node communication
time.sleep(10)
