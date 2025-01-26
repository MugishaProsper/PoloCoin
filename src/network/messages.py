def create_block_message(block):
  return { "type" : "BLOCK", "data" : block.to_dict() }

def create_transaction_message(transaction):
  return { "type" : "TRANSACTION", "data" : transaction.to_dict() }