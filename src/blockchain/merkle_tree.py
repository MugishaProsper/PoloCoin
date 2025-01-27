import hashlib

class MerkleTree :
  def __init__(self, transactions):
    self.transactions = transactions
    self.merkle_root = self.build_merkle_tree(transactions)

  def hash_transactions(self, transaction):
    return hashlib.sha256(transaction.encode()).hexdigest()
  
  def build_merkle_tree(self, transactions):
    # Recursively build Merkle Tree and return the root hash
    if not transactions:
      return None
    # If there's only 1 transaction, return its hash

    if(len(transactions)) == 1 :
      return self.hash_transactions(transactions[0])
    
    # Hash each transaction

    hashed_transactions = [self.hash_transactions(tx) for tx in transactions]

    # Pair adjacent hashes and combine them
    while len(hashed_transactions) > 1 :
      temp = []

      for i in range(0, len(hashed_transactions), 2):
        left = hashed_transactions[i]
        right = hashed_transactions[i+1] if i+1 < len(hashed_transactions) else left # Handle odd count
        temp.append(self.hash_pair(left, right))

      hashed_transactions = temp
    
    return hashed_transactions[0]
  
  @staticmethod
  def hash_pair(left, right):
    # Hash a pair of transactions
    return hashlib.sha256((left + right).encode()).hexdigest()