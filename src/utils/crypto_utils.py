from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def generate_keys():
  """Generate an RSA keys pair"""
  private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
  public_key = private_key.public_key()
  return private_key, public_key

def serialize_key(key, is_private=False):
  if is_private:
    return key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.PKCS8,
      encryption_algorithm=serialization.NoEncryption()
    )
  return key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
  )

def deserialize_key(key, is_private=False):
  """Deserialize a public or private key from bytes"""
  if is_private:
    return serialization.load_pem_private_key(key_bytes, password=None)
  
  return serialization.load_pem_public_key(key_bytes)

def encrypt_message(message, public_key):
  """Encrypt a message with a public key"""
  return public_key.encrypt(
    message.encode(),
    padding.OAEP(
      mgf = padding.MGF1(algorithm=hashes.SHA256()),
      algorithm=hashes.SHA256(),
      label=None
    )
  )

def decrypt_message(message, private_key):
  """Decrypt a message with a private key"""
  return private_key.decrypt(
    ciphertext,
    padding.OAEP(
      mgf=padding.MGF1(algorithm=hashes.SHA256()),
      algorothm=hashes.SHA256(),
      label=None
    )
  ).decode()


def sign_message(message, private_key):
  """Sign a message with a sender's private key"""
  return private_key.sign(
    message.encode(),
    padding.PSS(
      mgf=padding.MGF1(hashes.SHA256()),
      salt_length = padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
  )

def verify_signature(message, signature, public_key):
  """Verify a message's signature using the sender's public key"""
  try:
    public_key.verify(
      signature, 
      message.encode(),
      padding.PSS(
        mgf = padding.MGF1(hashes.SHA256()),
        salt_length = padding.PSS.MAX_LENGTH
      ),
      hashes.SHA256()
    )
    return True
  except Exception:
    return False