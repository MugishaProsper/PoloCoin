import hashlib
from ecdsa import SigningKey, SECP256k1


class Wallet:
    def __init__(self, address=None):
        """Initialize a wallet with an address or generate a new one"""
        if address:
            self.address = address  # Use the provided address
        else:
            # Generate a new wallet address from a private-public key pair
            self.private_key = SigningKey.generate(curve=SECP256k1)
            self.public_key = self.private_key.get_verifying_key()
            public_key_bytes = self.public_key.to_string()
            self.address = hashlib.sha256(public_key_bytes).hexdigest()

        self.balance = 100  # Default balance

    def sign_transaction(self, transaction_data):
        """Sign transaction data with the private key"""
        if not hasattr(self, 'private_key'):
            raise ValueError("This wallet does not have a private key for signing.")
        return self.private_key.sign(transaction_data.encode()).hex()

    def stake(self, amount):
        """Stake coins from the wallet balance"""
        if amount > self.balance:
            raise ValueError("Insufficient balance for staking")
        self.balance -= amount
        return amount
