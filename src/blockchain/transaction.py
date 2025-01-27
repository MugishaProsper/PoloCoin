class Transaction:
  def __init__(self, sender, receiver, amount, signature=None):
    self.sender = sender
    self.receiver = receiver
    self.amount = amount
    self.signature = signature

  def to_dict(self):
    """Convert the transaction to a dictionary"""
    return {
      "sender" : self.sender,
      "receiver" : self.receiver,
      "amount" : self.amount,
      "signature" : self.signature
    }
  
  def calculate_hash(self):
    """Generate a unique hash for the transaction"""
    import hashlib
    transaction_string = f"{self.sender}{self.receiver}{self.amount}"
    return hashlib.sha256(transaction_string.encode()).hexdigest()
  
  def is_valid(self, public_key):
    """Verify the transaction signature with the public key"""
    from ecdsa import VerifyingKey, BadSignatureError
    if self.sender == "Network" :
      return True
    
    try:
      public_key_bytes = bytes.fromhex(public_key)
      verifying_key = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)
      verifying_key.verify(bytes.fromhex(self.signature), self.calculate_hash().encode())
      return True
    except BadSignatureError:
      return False
