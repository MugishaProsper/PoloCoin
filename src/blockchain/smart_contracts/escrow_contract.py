from src.blockchain.smart_contracts.base_contract import BaseContract

class EscrowContract(BaseContract):
    def __init__(self, sender, recipient, amount, condition, mediator=None):
        super().__init__(sender)
        self.state["sender"] = sender
        self.state["recipient"] = recipient
        self.state["amount"] = amount
        self.state["condition"] = condition
        self.state["mediator"] = mediator
        self.state["funded"] = False
        self.state["status"] = "Pending"

    def deposit(self, sender):
        """Deposit funds into the escrow"""
        if sender != self.state["sender"]:
            raise Exception("Only the sender can deposit funds")

        if self.state["funded"]:
            raise Exception("Funds already deposited")

        self.state["funded"] = True
        self.state["status"] = "Funded"
        self.emit_event("Funds Deposited", {"sender" : sender, "amount" : self.state["amount"]})
        print(f"Funds deposited by {sender}")

    def release(self, condition_met):
        """Release funds to the recipient if the condition is met"""
        if not self.state["funded"]:
            raise Exception("Funds have not been deposited")
        if not condition_met:
            raise Exception("Condition for release not met")

        self.state["status"] = "Released"
        self.emit_event("Funds Released", { "recipient" : self.state["recipient"], "amount" : self.state["amount"]})
        print(f"Funds released to {self.state["recipient"]}")

    def refund(self, sender, mediator=None):
        """Refund funds to the sender"""
        if not self.state["funded"]:
            raise Exception("Funds have not been deposited")
        if self.state["status"] == "Released" :
            raise Exception("Funds have already been released")
        if mediator and mediator != self.state["mediator"] :
            raise Exception("Only assigned mediator can resolve disputes")

        self.state["status"] = "Refunded"
        self.emit_event("FundsRefunded", { "sender" : sender, "amount" : self.state["amount"]})
        print(f"Funds refunded by {sender}")

    def get_escrow_state(self):
        """Get the current state of the escrow"""
        return self.state


class MultiPartyEscrowContract(EscrowContract):
    def __init__(self, sender, recipients, amounts, condition, mediators=None):
        super().__init__(sender, None, None, condition, mediators)
        if len(recipients) != len(amounts):
            raise Exception("Number of recipients and amounts must match.")

        self.state["recipients"] = recipients  # List of recipients
        self.state["amounts"] = amounts  # Corresponding amounts for each recipient

    def release(self, condition_met):
        """Release funds to multiple recipients."""
        if not self.state["funded"]:
            raise Exception("Funds have not been deposited.")
        if not condition_met:
            raise Exception("Condition for release not met.")

        for recipient, amount in zip(self.state["recipients"], self.state["amounts"]):
            print(f"Released {amount} to {recipient}.")

        self.state["status"] = "Released"
        self.emit_event("FundsReleased", {
            "recipients": self.state["recipients"],
            "amounts": self.state["amounts"]
        })


from datetime import datetime, timedelta


class TimeLockedEscrowContract(EscrowContract):
    def __init__(self, sender, recipient, amount, condition, deadline, mediator=None):
        super().__init__(sender, recipient, amount, condition, mediator)
        self.state["deadline"] = deadline  # Deadline as a UNIX timestamp

    def release(self, condition_met):
        """Release funds if the condition is met or the deadline has passed."""
        current_time = datetime.now().timestamp()
        if current_time > self.state["deadline"]:
            print(f"Deadline reached. Releasing funds to {self.state['recipient']}.")
        elif not condition_met:
            raise Exception("Condition for release not met, and deadline not reached.")
        else:
            print(f"Condition met. Releasing funds to {self.state['recipient']}.")

        self.state["status"] = "Released"
        self.emit_event("FundsReleased", {"recipient": self.state["recipient"], "amount": self.state["amount"]})


class OracleEscrowContract(EscrowContract):
    def __init__(self, sender, recipient, amount, oracle_url, mediator=None):
        super().__init__(sender, recipient, amount, None, mediator)
        self.state["oracle_url"] = oracle_url  # URL of the oracle service

    def fetch_condition_status(self):
        """Simulate fetching data from an oracle."""
        # For simplicity, assume the oracle always returns True.
        # In practice, this would make a network request to the oracle.
        print(f"Fetching condition status from {self.state['oracle_url']}...")
        condition_met = True
        print(f"Condition met: {condition_met}")
        return condition_met

    def release(self):
        """Release funds based on oracle data."""
        if not self.state["funded"]:
            raise Exception("Funds have not been deposited.")

        condition_met = self.fetch_condition_status()
        if not condition_met:
            raise Exception("Condition for release not met.")

        super().release(condition_met)

class MultiSigEscrowContract(EscrowContract):
    def __init__(self, sender, recipient, amount, condition, mediators):
        super().__init__(sender, recipient, amount, condition, mediators)
        self.state["mediator_approvals"] = {mediator: False for mediator in mediators}

    def approve(self, mediator):
        """Mediator approves the resolution."""
        if mediator not in self.state["mediator_approvals"]:
            raise Exception("Invalid mediator.")
        self.state["mediator_approvals"][mediator] = True
        self.emit_event("MediatorApproved", {"mediator": mediator})
        print(f"Mediator {mediator} approved resolution.")

    def check_consensus(self):
        """Check if the majority of mediators approve."""
        approvals = list(self.state["mediator_approvals"].values())
        return approvals.count(True) > len(approvals) // 2

    def release(self, condition_met=False):
        """Release funds only if consensus is reached."""
        if not self.check_consensus():
            raise Exception("Consensus not reached among mediators.")
        super().release(condition_met)
