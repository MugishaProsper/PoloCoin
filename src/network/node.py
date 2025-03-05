import socket
import threading
import json

from cryptography.hazmat.primitives import serialization

from src.blockchain.transaction import Transaction
from src.staking.staking_pool import StakingPool
from src.utils.crypto_utils import generate_keys, serialize_key
from src.network.dht import DHT

from src.network.messages import create_block_message, create_transaction_message
from src.utils.crypto_utils import encrypt_message, sign_message, decrypt_message, verify_signature
from src.utils.Database import Database as db


class Node:
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.peers = [] # Connected nodes
    self.blockchain = None
    self.private_key, self.public_key = generate_keys()
    print(f"Node public key : {serialize_key(self.public_key).decode()}")
    self.dht = DHT()
    self.dht.set_node_id(self.public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode())
    self.staking_pool = StakingPool()

  def start(self):
    """Start the node server"""
    server_thread = threading.Thread(target=self.listen_for_connections)
    server_thread.start()

  def listen_for_connections(self):
    """Listen for incoming connections"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((self.host, self.port))
    server_socket.listen(5)
    print(f"Node listening on {self.host}:{self.port} ...")

    while True:
      client_socket, address = server_socket.accept()
      print(f"New connection from {address}")
      client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
      client_thread.start()

  def handle_client(self, client_socket):
    """Handle incoming messages from a peer"""
    try:
      while True:
        data = client_socket.recv(1024).decode()
        if data:
          message = json.loads(data)
          self.handle_message(message)
    except ConnectionResetError:
      print("Connection lost")
    finally:
      client_socket.close()

  def handle_message(self, message):
    """Handle incoming messages from a peer"""
    print("Received message : ", message)
    if message["type"] == "BLOCK":
      self.add_block_to_chain(message["data"])
    elif message["type"] == "TRANSACTION":
      transaction_data = message["data"]
      transaction = Transaction.from_dict(transaction_data)
      # Handle staking/unstaking separately
      if transaction.transaction_type == "STAKE":
        self.handle_staking(transaction)
      elif transaction.transaction_type == "UNSTAKE":
        self.handle_unstaking(transaction)
      else :
        self.add_transaction_to_pool(transaction_data)
    elif message["type"] == "REQUEST_CHAIN":
      self.broadcast_chain(peer_socket)
    elif message["type"] == "CHAIN_RESPONSE":
      self.handle_chain_request(message["data"])
    elif message["type"] == "PEER_UPDATE":
      self.handle_peer_update(message["data"])

  def handle_staking(self, transaction):
    """Process staking transactions"""
    if self.blockchain.process_staking(transaction):
      print(f"Staking transaction : {transaction.to_dict()}")
      self.broadcast(create_transaction_message(transaction))
    else:
      print(f"Failed to process staking transaction : {transaction.to_dict()}")

  def handle_unstaking(self, transaction):
    """Process unstaking transactions"""
    if self.blockchain.process_unstaking(transaction):
      print(f"Unstaking transaction processed : {transaction.to_dict()}")
      self.broadcast(create_transaction_message(transaction))
    else :
      print(f"Failed to process unstaking transaction : {transaction.to_dict()}")
  def create_staking_transaction(self, amount):
    """Create and broadcast a staking transaction"""
    transaction = {
      "sender" : serialize_key(self.public_key).decode(),
      "recipient" : None,
      "amount" : amount,
      "transaction_type" : "STAKE"
    }
    self.broadcast(transaction)

  def create_unstaking_transaction(self, amount):
    transaction = {
      "sender" : serialize_key(self.public_key).decode(),
      "recipient" : None,
      "amount" : amount,
      "transaction_type" : "UNSTAKE"
    }
    self.broadcast(transaction)

  def connect_to_peer(self, peer_host, peer_port):
    """Connect to another peer"""
    try:
      peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      peer_socket.connect((peer_host, peer_port))
      self.peers.append(peer_socket)
      print(f"Connected to peer at {peer_host}:{peer_port}")
    except ConnectionError:
      print(f"Failed to connect to peer at {peer_host}:{peer_port}")

  def broadcast(self, message):
    """Send a message to all connected peers"""
    for peer in self.peers:
      peer.send(json.dumps(message).encode())

  def add_block_to_chain(self, block_data):
    """Add a block to the local blockchain"""
    validator = self.select_validator()
    if validator == serialize_key(self.public_key).decode():
      from src.blockchain.block import Block
      new_block = Block.from_dict(block_data)
      if self.blockchain.add_block(new_block.transactions):
        print(f"Block {new_block.index} added to the blockchain")
        self.broadcast(create_block_message(new_block))
        self.reward_validator(validator, 10)
      else:
        print("Block validation failed")
    else:
        print("This node is not selected to add the block")

  def add_transaction_to_pool(self, transaction_data):
    """Add a transaction to the blockchain's transaction pool"""
    from src.blockchain.transaction import Transaction
    new_transaction = Transaction.from_dict(transaction_data)

    if new_transaction.transaction_type in ["STAKE", "UNSTAKE"]:
      print("This transaction type should be processed through handle_staking and handle_unstaking")
      return
    if self.blockchain.process_transaction(new_transaction):
      print(f"Transaction added to the pool : {new_transaction.to_dict()}")
      self.broadcast(create_transaction_message(new_transaction))

  def request_chain_from_peers(self):
    """Request the latest blockchain from all peers"""
    message = {
      "type" : "REQUEST_CHAIN",
      "data" : None
    }
    self.broadcast(message)

  def handle_chain_request(self, chain_data):
    """Replace the local blockchain if the received chain is longer and valid"""
    from src.blockchain.block import Block
    new_chain = [Block.from_dict(block) for block in chain_data]
    if len(new_chain) > len(self.blockchain.chain) and self.blockchain.is_chain_valid(new_chain):
      self.blockchain.chain = new_chain
      print("Local blockchain updated to the received chain")
    else :
      print("Received chain not longer than the local one")

  def broadcast_chain(self, peer_socket):
    """Send the local blockchain to a peer"""
    chain_data = [ block.to_dict() for block in self.blockchain.chain ]
    message = {
      "type" : "BLOCK",
      "data" : chain_data
    }
    peer_socket.send(json.dumps(message).encode())

  def send_secure_message(self, peer_socket, message, recipient_public_key):
    """Encrypt and sign a message before sending it to a peer"""
    encrypted_message = encrypt_message(message, recipient_public_key)
    signature = sign_message(message, self.private_key)
    payload = {
      "encrypted_message" : encrypted_message.hex(),
      "signature" : signature.hex()
    }
    peer_socket.send(json.dumps(payload).encode())

  def handle_secure_message(self, payload, sender_public_key):
    """Decrypt and verify a message from a peer"""
    encrypted_message = bytes.fromhex(payload["encrypted_message"])
    signature = bytes.fromhex(payload["signature"])

    message = decrypt_message(encrypted_message, self.private_key)

    if verify_signature(message, signature, sender_public_key):
      print("Verified message : ", message)
      return message
    else:
      print("Failed to verify message")
      return None

  def connect_to_bootstrap_node(self, bootstrap_host, boostrap_port):
    import socket
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((bootstrap_host, boostrap_port))
        s.sendall(f"REGISTER {self.host}:{self:port}".encode())
        response = s.recv(1024).decode()
        peers = response.split(",")
        self.peers.extend(peers)
        print(f"Connected to bootstrap. Peers : {self.peers}")
    except Exception as e:
      print(f"Failed to connect to bootstrap node : {e}")

  def broadcast_peers(self):
    """Send the updated peer list to all connected peers"""
    message = {
      "type" : "PEER_UPDATE",
      "data" : self.peers
    }
    self.broadcast(message)

  def handle_peer_update(self, new_peers):
    """Merge received peer list with local peers"""
    self.peers = list(set(self.peers) + new_peers)
    print(f"Update peers : {self.peers}")

  def check_peer_health(self):
    """Periodically check the health of peers"""
    while True:
      for peer in self.peers.copy():
        try:
          host, port = peer.split(":")
          with socket.create_connection((host, int(port)), timeout=2):
            pass
        except Exception:
          print(f"Peer {peer} is unresponsive. Removing from peers list")
          self.peers.remove(peer)

      self.broadcast_peers()
      threading.Event().wait(30)

  def query_dht_for_peers(self, target_id):
    """Query the DHT to find peers closest to target ID"""
    peers = self.dht.get_peers(target_id)
    print(f"Found peers closest to {target_id} : {peers}")
    return peers

  def stake_coins(self, amount):
    """Allows a user to stake their coins"""
    if self.blockchain.balance >= amount:
      self.blockchain.balance -= amount
      self.staking_pool.add_stake(self.public_key, amount)
      print(f"Staked {amount} coins")
    else:
      print("Not enough coins to stake")

  def unstake_coins(self, amount):
    """Allows a user to unstake their coins"""
    if self.staking_pool.get_stake(self.public_key) >= amount:
      self.staking_pool.remove_stake(self.public_key, amount)
      self.blockchain.balance += amount
      print(f"Unstaked {amount} coins")
    else:
      print("Not enough coins to unstake")

  def select_validator(self):
    """Select a validator from the staking pool"""
    validator = self.staking_pool.select_validator()
    print(f"Selected validator : {validator}")
    return validator
  def reward_validator(self, validator_public_key, reward_amount):
    """Reward the validator for adding a block"""
    self.blockchain.update_balance(validator_public_key, reward_amount)
    print(f"Rewarded {reward_amount} coins to validator {validator_public_key}")

  def stake(self, sender, amount):
    """Create and broadcast a staking transaction"""
    transaction = Transaction(sender=sender, receiver=None, amount=amount, transaction_type="STAKE")
    self.broadcast(create_transaction_message(transaction))

  def unstake(self, sender, amount):
    """Create and broadcast an unstaking transaction"""
    transaction = Transaction(sender=sender, receiver=None, amount=amount, transaction_type="UNSTAKE")
    self.broadcast(create_transaction_message(transaction))

  def to_dict(self):
    return {"public_key" : self.public_key, "host" : self.host, "port" : self.port}

  def save_to_db(self):
    """Save the node to the database"""
    conn = db.get_connection()
    cursor = conn.cursor()
    query = """INSERT INTO nodes (public_key, host, port) VALUES (%s, %s, %s) ON CONFLICT (public_key) DO NOTHING;"""
    public_key_pem = self.public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
    cursor.execute(query, (public_key_pem, self.host, self.port))
    conn.commit()
    db.release_connection(conn)

  @staticmethod
  def load_all_nodes():
    """Load all nodes from the database"""
    conn = db.get_connection()
    cursor = conn.cursor()
    query = "SELECT public_key, host, port FROM nodes;"
    cursor.execute(query)
    rows = cursor.fetchall()
    db.release_connection(conn)
    return [Node(*row) for row in rows]

  def broadcast_transaction(self, transaction):
    """Broadcast a transaction to all connected nodes"""
    nodes = Node.load_all_nodes()
    for node in nodes:
      if node.host != self.host or node.port != self.port:
        print(f"Sending a transaction to {node.host}:{node.port}")

  def add_transaction(self, transaction):
    """Add a transaction to the database and broadcast it"""
    transaction.save_to_db()
    self.broadcast_transaction(transaction)