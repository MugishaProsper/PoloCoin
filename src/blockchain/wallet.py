import hashlib
from ecdsa import SigningKey, SECP256k1


class Wallet:
  def __init__(self):
    """Generate a new wallet with private-public key pair"""
    self.private_key = SigningKey.generate(curve=SECP256k1)
    self.public_key = self.private_key.get_verifying_key()

  def get_address(self):
    """Generate a wallet address from the public key"""
    public_key_bytes = self.public_key.to_string()
    return hashlib.sha256(public_key_bytes).hexdigest()
  
  def sign_transaction(self, transaction_data):
    """Sign transaction data with the private key"""
    return self.private_key.sign(transaction_data.encode()).hex()
  def __init__(self, address):
    self.address = address
    self.balance = 100 # default balance

  def stake(self, amount):
    """Stake sample coins in staking pool"""
    if amount > self.balance:
      return False
    self.balance -= amount
    return amount