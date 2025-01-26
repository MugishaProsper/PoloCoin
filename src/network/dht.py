import hashlib
from collections import defaultdict

class DHT:
  def __init__(self):
    self.node.id = None
    self.routing_table = defaultdict(list)

  def set_note_id(self, public_key):
    """Set the node's unique ID using the hash of its public key"""
    self.node.id = hashlib.sha256(public_key.encode()).hexdigest()

  def add_peer(self, peer_id, peer_address):
    """Add a peer to the DHT routing table"""
    bucket = self._get_bucket(peer_id)
    if peer_address not in bucket:
      bucket.append(peer_address)

  def get_peers(self, target_id):
    """Find the closest to target ID"""
    bucket = self._get_bucket(target_id)
    return bucket
  
  def _get_bucket(self, target_id):
    """Determine the bucket based on XOR distance"""
    distance = int(self.node_id, 16 ^ int(target_id, 16))
    bucket_index = distance.bit_length()
    return self.routing_table[bucket_index]