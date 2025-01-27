from src.blockchain.blockchain import Blockchain

# Initialize the blockchain
my_blockchain = Blockchain()

# Add blocks with sample transactions
my_blockchain.add_block(["User1 sent 5 tokens to User2", "User3 sent 10 tokens to User4"])
my_blockchain.add_block(["User2 sent 3 tokens to User5", "User4 sent 7 tokens to User6"])

# Print the blockchain
print("Blockchain:")
for block in my_blockchain.chain:
    print(f"Index: {block.index}, Hash: {block.hash}, Previous: {block.previous_hash}")

# Validate the blockchain
print("\nIs the Blockchain valid?")
print(my_blockchain.is_chain_valid(my_blockchain))
