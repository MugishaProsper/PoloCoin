import random

class StakingSystem:
  def __init__(self):
    self.stakes = {}
    self.delefations = {}
    self.validator_candidates = {}

  def stake_tokens(self, node_id, amount):
      """Allow a node to stake tokens"""
      if node_id in self.stakes:
        self.stakes[node_id] += amount
      else:
        self.stakes[node_id] = amount
      print(f"Node {node_id} stakes {amount}. Total stake : {self.stakes[node_id]}")

  def select_validator(self):
      """Select a validator based on stake"""
      total_stake = sum(self.stakes.value())
      if total_stake == 0:
        raise Exception("No stakes available for validation")
      
      weights = [stake/total_stake for stake in self.stakes.value()]
      nodes = list(self.stakes.keys())
      selected_node = random.choices(nodes, weights=weights, k=1)[0]
      print(f"Validator selected : {selected_node}")
      return selected_node
    
  def slash_tokens(self, node_id, penalty):
    """Penalize a node for misbehaviour"""
    if node_id in self.stakes:
      self.stakes[node_id] = max(0, self.stakes[node_id] - penalty)
      print(f"Node {node_id} penalized by {penalty}. Remaining stake : {self.stakes[node_id]}")

  def distribute_rewards(self, validator, reward_amount):
    """Distribute rewards to the validator"""
    if validator in self.stakes:
      self.stakes[validator] += reward_amount
      print(f"Validator {validator} rewarded with {reward_amount}. Total stake : {self.stakes[validator]}")

  def register_candidate(self, candidate_id):
    """Register a node as a validator candidate"""
    if candidate_id not in self.validator_candidates:
      self.validator_candidates[candidate_id] = 0
      print(f"Node {candidate_id} registered as a validator candidate")

  def delegate_stake(self, delegator_id, candidate_id, amount):
    """Delegate stake to a validator candidate"""
    if candidate_id not in self.validator_candidates:
      raise Exception(f"Candidate {candidate_id} is not registered")
    
    self.delegations[delegator_id] = (candidate_id, amount)

    self.validator_candidates[candidate_id] += amount
    print(f"Delegator {delegator_id} delegated {amount} to candidate {candidate_id}")

  def select_validators(self, max_validators=5):
    """Select the top candidates as active validators"""
    sorted_candidates = sorted(
      self.validator_candidates.items(),
      key=lambda x: x[1],
      reverse=True
    )
    selected_validators = sorted_candidates[:max_validators]
    print(f"Selected validators : {[v[0] for v in selected_validators]}")
    return [v[0] for v in selected_validators]
  
  def calculate_rewards(self, num_validators, block_time):
    """Calculate rewards based on network conditions"""
    base_rewards = 50
    if num_validators < 10:
      base_rewards += 20
    if block_time < 10:
      base_rewards += 10

    return base_rewards
  
  def slash_validator(self, validator_id, penalty):
    """Penalize a validator for misbehaviour"""
    if validator_id in self.stakes:
      self.stakes[validator_id] = max(0, self.stakes[validator_id] - penalty)
      print(f"Validator {validator_id} slashed by {penalty}. Remaining stake : {self.stakes[validator_id]}")
      if self.stakes[validator_id] == 0:
        self.remove_validator(validator_id)

  def remove_validator(self, validator_id):
    """Remove a validator from the list of candidates"""
    if validator_id in self.validator_candidates:
      del self.validator_candidates[validator_id]
      print(f"Validator {validator_id} removed from the candidate list")