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
        block_data = {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
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
        genesis_block = Block(0, [], time(), "0")
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):
        # Giao dịch được đưa vào pending pool
        self.pending_transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })

    def proof_of_work(self, block):
        # Tìm nonce sao cho hash thỏa điều kiện difficulty
        while not block.hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            block.hash = block.compute_hash()

    def mine(self):

        if not self.pending_transactions:
            return None

        # State transition xảy ra tại thời điểm mining
        for tx in self.pending_transactions:
            success = self.contract.transfer(
                tx["sender"],
                tx["receiver"],
                tx["amount"]
            )
            if not success:
                return None

        new_block = Block(
            index=self.last_block.index + 1,
            transactions=self.pending_transactions,
            timestamp=time(),
            previous_hash=self.last_block.hash
        )

        self.proof_of_work(new_block)

        self.chain.append(new_block)
        self.pending_transactions = []

        return new_block