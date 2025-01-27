import hashlib
import time
from src.blockchain.merkle_tree import MerkleTree

class Block:
  def __init__(self, index, transactions, previous_hash):
    self.index = index
    self.timestamp = time.time()
    self.transactions = transactions
    self.previous_hash = previous_hash
    self.nonce = 0

    # Generate Merkle root
    self.merkle_root = self.calculate_merkle_root()

    self.hash = self.calculate_hash()

  def calculate_merkle_root(self):
      # Generate Merkle root using Merkle class
      if not self.transactions :
        return None
      
      merkle_tree = MerkleTree(self.transactions)
      return merkle_tree.merkle_root

  def calculate_hash(self):
      block_string = f"{self.index}{self.timestamp}{self.merkle_root}{self.previous_hash}{self.nonce}"
      return hashlib.sha256(block_string.encode()).hexdigest()
  def __str__(self):
      return f"Block(Index : {self.index}, Hash : {self.hash})"