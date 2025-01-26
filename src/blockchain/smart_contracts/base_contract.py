import hashlib
import time

class BaseContract:
  def __init__(self, creator_address):
    self.contract_id = self.generate_contract_id()
    self.creator_address = creator_address
    self.timestamp = time.time()
    self.state = {}
    self.events = []

  def generate_contract_id(self):
    """Generate a unique ID for the contract"""
    return hashlib.sha256(str(time.time()).encode()).hexdigest()
  
  def emit_event(self, event_name, event_data):
    """Record an event emitted by the contract"""
    event = {"name" : event_name, "data" : event_data, "timestamp" : time.time()}
    self.events.append(event)
    print(f"Event emitted : {event}")

  def get_state(self):
    """Return the current state of the contract"""
    return self.state
  
  def execute(self, *args, **kwargs):
    """Execute the contract's main function -- To be overriden by subclasses"""
    raise NotImplementedError("Subclasses must implement this method")

