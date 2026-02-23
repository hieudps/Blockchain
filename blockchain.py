import hashlib
import json
from time import time
from contract import TokenContract


class Block:

    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:

    difficulty = 3

    def __init__(self):
        self.chain = []
        self.pending_transactions = []

        # Deploy Smart Contract
        self.contract = TokenContract("HIEU COIN", "HIEU", 1000000)
        self.contract.deploy("Alice")

        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, [], time(), "0")
        self.chain.append(genesis)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):

        if self.contract.balance_of(sender) < amount:
            return False

        self.pending_transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })

        return True

    def proof_of_work(self, block):
        while not block.hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            block.hash = block.compute_hash()

    def mine(self):

        if not self.pending_transactions:
            return None

        # Thực thi giao dịch
        for tx in self.pending_transactions:
            success = self.contract.transfer(
                tx["sender"],
                tx["receiver"],
                tx["amount"]
            )
            if not success:
                return None

        # 🎁 Mining Reward
        miner_address = "Miner"
        reward = 50

        self.contract.balances[miner_address] = \
            self.contract.balance_of(miner_address) + reward

        reward_transaction = {
            "sender": "SYSTEM",
            "receiver": miner_address,
            "amount": reward
        }

        block_transactions = self.pending_transactions + [reward_transaction]

        new_block = Block(
            self.last_block.index + 1,
            block_transactions,
            time(),
            self.last_block.hash
        )

        self.proof_of_work(new_block)

        self.chain.append(new_block)
        self.pending_transactions = []

        return new_block