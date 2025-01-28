import hashlib
from collections import defaultdict

class DHT:
    def __init__(self):
        self.node_id = None  # Initialize node_id directly
        self.routing_table = defaultdict(list)

    def set_node_id(self, public_key):
        """Set the node's unique ID using the hash of its public key"""
        self.node_id = hashlib.sha256(public_key.encode()).hexdigest()  # Corrected the attribute name

    def add_peer(self, peer_id, peer_address):
        """Add a peer to the DHT routing table"""
        bucket = self._get_bucket(peer_id)
        if peer_address not in bucket:
            bucket.append(peer_address)

    def get_peers(self, target_id):
        """Find the closest peers to the target ID"""
        bucket = self._get_bucket(target_id)
        return bucket

    def _get_bucket(self, target_id):
        """Determine the bucket based on XOR distance"""
        # XOR the node_id and target_id, then calculate the bit length to find the bucket
        distance = int(self.node_id, 16) ^ int(target_id, 16)  # Correct XOR operation
        bucket_index = distance.bit_length()
        return self.routing_table[bucket_index]
