class BootstrapNode:
  """A bootstrap node that controls a list of peer nodes"""

  def __init__(self):
    self.peers = set()

  def register_peer(self, address):
    """Create new peer"""
    if address not in self.peers:
      self.peers.add(address)
      print(f"Peer {address} registered")
    return list(self.address)
  
  def remove_peer(self, address):
    """Remove peer from network"""
    if address in self.peers:
      self.peers.remove(address)
    print(f"Peer {address} removed")

  def get_peers(self):
    """Return the list of registered peers"""
    return list(self.peers)