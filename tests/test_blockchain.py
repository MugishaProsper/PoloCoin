from src.blockchain.blockchain import Blockchain

myblockchain = Blockchain()

myblockchain.add_block(["User1 sent 5 tokens to User2", "User3 sent 10 tokens to User4"])
myblockchain.add_block(["User2 sent 3 tokens to User5", "User4 sent 7 tokens to User6"])

print("Blockchain : ")
for block in myblockchain.chain:
  print(f"Index : {block.index}, Hash : {block.hash}, Previous Hash : {block.previous_hash}")

print(f"\n Is the Blockchain valid ? : {myblockchain.is_chain_valid()}")