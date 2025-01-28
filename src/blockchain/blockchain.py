import random
from time import sleep

from src.blockchain.staking import StakingSystem
from src.blockchain.block import Block

class Blockchain :
  def __init__(self):
    self.chain = []
    self.staking_pool = {}
    self.slash_penalty = 0.1 # 10% of stake
    self.balances = {}
    self.create_genesis_block()
    self.pending_transactions = []
    self.staking_system = StakingSystem()

  def slash_validator(self, validator):
    """Reduce a validator's stake for unknown behaviour"""
    if validator in self.staking_pool:
      penalty = self.staking_pool[validator] * self.slash_penalty
      self.staking_pool[validator] -= penalty
      print(f"Validator {validator} has been slashed by {penalty:.2f} tokens")
      if self.staking_pool[validator] <= 0:
        print(f"Validator {validator} is removed from staking pool")
        del self.staking_pool[validator]

  def validate_block(self):
    """Simulate block validation by other nodes"""
    return random.choice([True, True, False])

  def create_genesis_block(self):
    genesis_block = Block(0, "Genesis Block", "0")
    self.chain.append(genesis_block)
    self.balances["Network"] = 1000
  
  def add_stake(self, address, amount):
    """Allow users to stake their coins"""
    if address not in self.staking_pool:
      self.staking_pool[address] = 0
    self.staking_pool[address] += amount
    return True
  
  def select_validator(self):
    total_stake = sum(self.staking_pool.values())
    if total_stake == 0:
      return None
    
    selection = random.uniform(0, total_stake)
    current = 0
    for validator, stake in self.staking_pool.items():
      current += stake
      if current >= selection:
        return validator
    return None
  
  def add_block(self, transactions):
    previous_block = self.chain[-1]
    validator = self.select_validator()
    if not validator:
      print("No validator selected -- Empty staking pool")
      return None
    
    print(f"Validator {validator} is selected to create the block")
    new_block = Block(len(self.chain), transactions, previous_block.hash)
    # Validate block
    if self.validate_block(new_block):
      self.chain.append(new_block)
      print(f"Block {new_block.index} added by {validator}")
      # Implement rewarding transaction fees
      transaction_fees = self.calculate_transaction_fees(transactions)
      self.reward_validator(validator, transaction_fees)
    else:
      print(f"Block {new_block} rejected. {validator} is penalized")
      self.slash_validator(validator)

  def mine_block(self, block, difficulty=4):
    # PoW : Adjust nonce until hash starts with '0' * difficulty
    prefix = '0' * difficulty
    while not block.hash.startswith(prefix):
      block.nonce += 1
      block.hash = block.calculate_hash()


  def is_chain_valid(self, chain):
    if not chain:
      print("The blockchain is empty")
      return False

    """Validate the entire blockchain"""
    for i in range(1, len(chain)):
      current_block = chain[i]
      previous_block = chain[i-1]

      if current_block.hash != current_block.calculate_hash():
        print(f"Block {current_block.index} has an invalid hash")
        return False
      
      if current_block.previous_hash != previous_block.hash:
        print(f"Block {current_block.index} hash invalid previous hash")
        return False
    return True
  
  def calculate_transaction_fees(self, transactions):
    return len(transactions) * 0.01
  
  def reward_validator(self, validator, reward):
    if validator in self.staking_pool:
      self.staking_pool[validator] += reward
      print(f"Validator {validator} rewarded with {reward:.2f} tokens")

  def withdraw_stake(self, address, amount):
    """Allow validators to withdraw their staked coins"""
    if address in self.staking_pool and self.staking_pool[address] >= amount:
      self.staking_pool[address] -= amount
      print(f"Validator {address} withdrew {amount:.2f} tokens")
      if self.staking_pool[address] <= 0:
        del self.staking_pool[address]
      return True
    print(f"Insufficient stake of {address}")
    return False
  
  def process_transaction(self, transaction):
    """Validate and process a transaction"""
    if transaction.transaction_type == "TRANSFER":
      if self.get_balance(transaction.sender) >= transaction.amount:
        self.update_balance(transaction.sender, -transaction.amount)
        self.update_balance(transaction.recipient, transaction.amount)
        return True
    elif transaction.transaction_type == "STAKE":
      if self.get_balance(transaction.sender) >= transaction.amount:
        self.update_balance(transaction.sender, -transaction.amount)
        return True
    elif transaction.transaction_type == "UNSTAKE":
      if self.staking_pool.get_stake(transaction.sender) >= transaction.amount:
        self.update_balance(transaction.sender, transaction.amount)
        return True
    return False
  
  def create_block(self):
    """Create a new block with a validator selected by DPoS"""
    active_validators = self.staking_system.select_validator()
    if not active_validators:
      raise Exception("No available validators")
    validator = random.choice(active_validators)
    reward = self.staking_system.calculate_reward(len(active_validators), block_time=8)
    new_block = Block(
      index=len(self.chain) + 1,
      transactions=self.pending_transactions,
      previous_hash=self.get_last_block().hash,
      validator = validator
    )
    self.pending_transactions = []
    self.chain.append(new_block)
    
    # Distribute rewards
    self.staking_system.distribute_rewards(validator, reward)
    print(f"Block created by validator {validator}. Reward : {reward:.2f}")

  def process_staking(self, transaction):
    """Handle staking transactions"""
    sender_wallet = self.get_wallet(transaction.sender)
    if sender_wallet and sender_wallet.balance >= transaction.amount:
      sender_wallet.balance -= transaction.amount
      self.staking_pool.add_stake(transaction.sender, transaction.amount)
      print(f"Staked {transaction.amount} for {transaction.sender}")
      return True
    return False

  def process_unstaking(self, transaction):
    """Handle unstaking transactions"""
    stake = self.staking_pool.get_stake(transaction.sender)
    if stake and stake >= transaction.amount:
      self.staking_pool.remove_stake(transaction.sender, transaction.amount)
      sender_wallet = self.get_wallet(transaction.sender)
      sender_wallet.balance += transaction.amount
      print(f"Unstaked {transaction.amount} for {transaction.sender}")
      return True
    return False

  def __len__(self):
    return len(self.chain)