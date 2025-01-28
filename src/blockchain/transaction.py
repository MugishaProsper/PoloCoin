from ecdsa import SECP256k1
from datetime import datetime
from src.utils.Database import Database as db


class Transaction:
  def __init__(self, sender, receiver, amount, signature=None, transaction_type = None, timestamp=None):
    self.sender = sender
    self.receiver = receiver
    self.amount = amount
    self.signature = signature
    self.transaction_type = transaction_type
    self.timestamp = timestamp

  def to_dict(self):
    """Convert the transaction to a dictionary"""
    return {
      "sender" : self.sender,
      "receiver" : self.receiver,
      "amount" : self.amount,
      "signature" : self.signature,
      "transaction_type" : self.transaction_type,
      "timestamp" : self.timestamp
    }
  def save_to_db(self):
    """Save to database"""
    conn = db.get_connection()
    cursor = conn.cursor()
    query = """ INSERT INTO transactions (sender, receiver, amount, signature, transaction_type, timestamp) VALUES (%s, %s, %s, %s, %s, %s) """
    cursor.execute(query, (self.sender, self.receiver, self.amount, self.signature, self.transaction_type, self.timestamp))
    conn.commit()
    db.release_connection(conn)
  
  def calculate_hash(self):
    """Generate a unique hash for the transaction"""
    import hashlib
    transaction_string = f"{self.sender}{self.receiver}{self.amount}{self.transaction_type}{self.timestamp}"
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

  @staticmethod
  def from_dict(data):
    """Reconstruct a transaction from a dictionary"""
    return Transaction(sender=data["sender"], receiver=data["receiver"], amount=data["amount"], signature=data.get("signature"), transaction_type=data.get("transaction_type", "TRANSFER"), timestamp=data.get("timestamp", datetime.now().timestamp()))

  @staticmethod
  def load_from_db(transaction_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    query = """SELECT * FROM transactions WHERE id = %s"""
    cursor.execute(query, (transaction_id,))
    row = cursor.fetchone()
    db.release_connection(conn)
    return Transaction(*row) if row else None