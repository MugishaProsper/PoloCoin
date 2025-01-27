from  src.blockchain.smart_contracts.base_contract import BaseContract

class VotingContract(BaseContract):
    def __init__(self, creator_address):
        super().__init__(creator_address)
        self.state["proposals"] = {}
        self.state["vote_records"] = {}

    def create_proposal(self, proposal_id, description, options):
        """Create a new proposal for voting"""
        if proposal_id in self.state["proposals"]:
            raise Exception("Proposal ID already exists")

        self.state["proposals"][proposal_id] = {
            "description" : description,
            "options" : {options : 0 for option in options },
            "votes" : {},
            "active" : True
        }
        self.emit_event("ProposalCreated", { "proposal_id" : proposal_id, "description" : description })
        print(f"Proposal {proposal_id} created")

    def cast_vote(self, user_id, proposal_id, option):
        """Cast a vote for proposal"""
        proposal = self.state["proposals"].get(proposal_id)
        if not proposal or not proposal["active"]:
            raise Exception("Invalid or inactive proposal")

        if user_id in proposal["votes"]:
            raise Exception("User has already voted on this proposal")

        if option not in proposal["options"]:
            raise Exception("Invalid voting option")

        proposal["votes"][user_id] = option
        proposal["options"][option] += 1
        self.state["vote_records"].setdefault(user_id, {})[proposal_id] = option
        self.emit_event("VoteCast", {"user_id" : user_id, "proposal_id" : proposal_id, "option" : option })
        print(f"User {user_id} voted for '{option}' in proposal {proposal_id}")


    def tally_votes(self, proposal_id):
        """Conclude voting on a proposal and return the result"""
        proposal = self.state["proposals"].get(proposal_id)
        if not proposal:
            raise Exception("Proposal not found")

        if not proposal["active"]:
            raise Exception("Proposal is already concluded")

        proposal["active"] = False
        self.emit_event("VotingConcluded", { "proposal_id" : proposal_id, "results" : proposal["options"] })
        print(f"Voting concluded for proposal {proposal_id}. Results : {proposal["options"]}")
        return proposal["options"]

    def get_proposal_state(self, proposal_id):
        """Get the current state of proposal"""
        return self.state["proposals"].get(proposal_id, "Proposal not found")