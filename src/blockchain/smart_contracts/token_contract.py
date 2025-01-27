from src.blockchain.smart_contracts.base_contract import BaseContract

class TokenContract(BaseContract):
  def __init__(self, creator_address, token_name, token_symbol, initial_supply):
    super().__init__(creator_address)
    self.state["name"] = token_name
    self.state["symbol"] = token_symbol
    self.state["total_supply"] = initial_supply
    self.state["balances"] = { creator_address : initial_supply }

  def transfer(self, sender, recipient, amount):
    """Transfer tokens from one user to another"""
    if sender not in self.state["balances"] or self.state["balances"][sender] < amount:
      raise Exception("Insufficient balance")
    
    self.state["balances"][sender] -= amount
    self.state["balances"].setdefault(recipient, 0)
    self.state["balances"][recipient] += amount

    self.emit_event("Transfer", {"from" : sender, "to" : recipient, "amount" : amount })

  def mint(self, recipient, amount):
    """Mint new tokens  and add them to a recipient's balance"""
    if self.creator_address !=  recipient:
      raise Exception("Only the creator can mint tokens")

    self.state["total_supply"] += amount
    self.state["balances"][recipient] += amount
    self.emit_event("Mint", {"to" : recipient, "amount" : amount })

  def balance_of(self, address):
    """Get the balance of an address"""
    return self.state["balances"].get(address, 0)