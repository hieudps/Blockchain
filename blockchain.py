import hashlib
import json
import time

from config import (
    DEFAULT_DIFFICULTY,
    DEFAULT_GAS_FEE,
    DEMO_WALLET_BALANCE,
    GENESIS_OWNER,
    INITIAL_SUPPLY,
    MINING_REWARD,
    TOKEN_NAME,
    TOKEN_SYMBOL,
)
from smart_contract import TokenContract
from storage import (
    load_balances,
    load_blockchain_data,
    load_wallets,
    save_balances,
    save_blockchain_data,
    save_wallets,
)
from wallet import create_wallet


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0, block_hash=None, difficulty=0):
        self.index = int(index)
        self.transactions = transactions
        self.timestamp = float(timestamp)
        self.previous_hash = previous_hash
        self.nonce = int(nonce)
        self.difficulty = int(difficulty)
        self.hash = block_hash or self.compute_hash()

    def compute_hash(self):
        # Hash chi tinh tren du lieu goc cua block, khong dua self.hash vao.
        block_string = json.dumps(
            {
                "index": self.index,
                "transactions": self.transactions,
                "timestamp": self.timestamp,
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
                "difficulty": self.difficulty,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            index=data["index"],
            transactions=data.get("transactions", []),
            timestamp=data.get("timestamp", time.time()),
            previous_hash=data.get("previous_hash", "0"),
            nonce=data.get("nonce", 0),
            block_hash=data.get("hash"),
            difficulty=data.get("difficulty", 0),
        )


class Blockchain:
    def __init__(self):
        self.difficulty = DEFAULT_DIFFICULTY
        self.mining_reward = MINING_REWARD
        self.gas_fee = DEFAULT_GAS_FEE
        self.chain = []
        self.pending_transactions = []
        self.wallets = []
        self.current_wallet = None
        self.contract = TokenContract(TOKEN_NAME, TOKEN_SYMBOL, INITIAL_SUPPLY)
        self.load_or_initialize()

    @property
    def last_block(self):
        return self.chain[-1]

    def load_or_initialize(self):
        data = load_blockchain_data()
        self.wallets = load_wallets()
        balances = load_balances()
        self.contract = TokenContract(TOKEN_NAME, TOKEN_SYMBOL, INITIAL_SUPPLY, balances)

        if data:
            self.difficulty = int(data.get("difficulty", DEFAULT_DIFFICULTY))
            self.mining_reward = float(data.get("mining_reward", MINING_REWARD))
            self.gas_fee = float(data.get("gas_fee", DEFAULT_GAS_FEE))
            self.pending_transactions = data.get("pending_transactions", [])
            self.current_wallet = data.get("current_wallet")
            self.chain = [Block.from_dict(block) for block in data.get("chain", [])]

        if not self.chain:
            self.reset(save=False)
        else:
            self.contract.deploy(GENESIS_OWNER)
            self.save()

    def create_genesis_block(self):
        genesis_transaction = {
            "type": "genesis",
            "sender": "SYSTEM",
            "receiver": GENESIS_OWNER,
            "amount": INITIAL_SUPPLY,
            "gas_fee": 0,
            "timestamp": time.time(),
        }
        return Block(0, [genesis_transaction], time.time(), "0", difficulty=0)

    def reset(self, save=True):
        self.difficulty = DEFAULT_DIFFICULTY
        self.mining_reward = MINING_REWARD
        self.gas_fee = DEFAULT_GAS_FEE
        self.pending_transactions = []
        self.wallets = [{"address": GENESIS_OWNER, "label": "Genesis Owner", "created_at": time.time()}]
        self.current_wallet = GENESIS_OWNER
        self.contract = TokenContract(TOKEN_NAME, TOKEN_SYMBOL, INITIAL_SUPPLY)
        self.contract.deploy(GENESIS_OWNER)
        self.chain = [self.create_genesis_block()]

        if save:
            self.save()

    def save(self):
        save_blockchain_data(
            {
                "difficulty": self.difficulty,
                "mining_reward": self.mining_reward,
                "gas_fee": self.gas_fee,
                "pending_transactions": self.pending_transactions,
                "current_wallet": self.current_wallet,
                "chain": [block.to_dict() for block in self.chain],
            }
        )
        save_wallets(self.wallets)
        save_balances(self.contract.balances)

    def create_wallet(self, label="", initial_balance=DEMO_WALLET_BALANCE):
        try:
            initial_balance = float(initial_balance)
        except (TypeError, ValueError):
            raise ValueError("So du ban dau khong hop le")

        if initial_balance < 0:
            raise ValueError("So du ban dau khong duoc am")

        wallet = create_wallet(label)
        self.wallets.append(wallet)
        self.contract.credit(wallet["address"], initial_balance)
        self.current_wallet = wallet["address"]
        self.save()
        wallet["balance"] = self.contract.balance_of(wallet["address"])
        return wallet

    def login_wallet(self, address):
        address = address.strip()
        wallet = next((item for item in self.wallets if item["address"] == address), None)

        if wallet is None:
            wallet = {"address": address, "label": f"Imported {address[:10]}", "created_at": time.time()}
            self.wallets.append(wallet)
            self.contract.balances.setdefault(address, 0)

        self.current_wallet = address
        self.save()
        return {**wallet, "balance": self.contract.balance_of(address)}

    def add_transaction(self, sender, receiver, amount):
        sender = str(sender).strip()
        receiver = str(receiver).strip()

        if not sender:
            sender = self.current_wallet or ""

        if not sender or not receiver:
            raise ValueError("Sender va receiver khong duoc de trong")

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValueError("So token khong hop le")

        if amount <= 0:
            raise ValueError("So token phai lon hon 0")

        total_cost = amount + self.gas_fee
        if self.contract.balance_of(sender) < total_cost:
            raise ValueError("So du khong du de tra amount va gas fee")

        transaction = {
            "type": "transfer",
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "gas_fee": self.gas_fee,
            "timestamp": time.time(),
        }
        self.pending_transactions.append(transaction)
        self.save()
        return transaction

    def proof_of_work(self, block):
        target = "0" * self.difficulty
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.compute_hash()
        return block.hash

    def mine_pending_transactions(self, miner_address):
        miner_address = miner_address.strip()
        if not miner_address:
            raise ValueError("Dia chi miner khong duoc de trong")

        if not self.pending_transactions:
            raise ValueError("Khong co giao dich nao trong pending pool")

        block_transactions = []
        total_gas = 0

        for tx in self.pending_transactions:
            sender = tx["sender"]
            receiver = tx["receiver"]
            amount = float(tx["amount"])
            gas_fee = float(tx.get("gas_fee", self.gas_fee))

            if self.contract.balance_of(sender) < amount + gas_fee:
                raise ValueError(f"Giao dich cua {sender} khong du so du")

            self.contract.debit(sender, amount + gas_fee)
            self.contract.credit(receiver, amount)
            total_gas += gas_fee
            block_transactions.append(tx)

        reward_amount = self.mining_reward + total_gas
        self.contract.credit(miner_address, reward_amount)
        reward_transaction = {
            "type": "reward",
            "sender": "SYSTEM",
            "receiver": miner_address,
            "amount": reward_amount,
            "gas_fee": 0,
            "timestamp": time.time(),
            "note": f"Mining reward {self.mining_reward} + gas fee {total_gas}",
        }
        block_transactions.append(reward_transaction)

        new_block = Block(
            index=self.last_block.index + 1,
            transactions=block_transactions,
            timestamp=time.time(),
            previous_hash=self.last_block.hash,
            difficulty=self.difficulty,
        )

        start_time = time.time()
        self.proof_of_work(new_block)
        mining_time = round(time.time() - start_time, 4)

        self.chain.append(new_block)
        self.pending_transactions = []
        self.save()

        return {
            "message": "Dao block thanh cong",
            "block": new_block.to_dict(),
            "mining_time": mining_time,
            "miner_balance": self.contract.balance_of(miner_address),
            "reward": reward_amount,
        }

    def validate_chain(self):
        errors = []
        for index, block in enumerate(self.chain):
            target = "0" * block.difficulty
            recalculated_hash = block.compute_hash()
            if block.hash != recalculated_hash:
                errors.append({"block": block.index, "message": "Hash hien tai khong khop voi du lieu block"})

            if index > 0 and block.previous_hash != self.chain[index - 1].hash:
                errors.append({"block": block.index, "message": "previous_hash khong khop voi block truoc"})

            if index > 0 and not block.hash.startswith(target):
                errors.append({"block": block.index, "message": "Block khong thoa man difficulty Proof of Work"})

        return {
            "valid": len(errors) == 0,
            "message": "Blockchain hop le" if len(errors) == 0 else "Blockchain khong hop le",
            "errors": errors,
        }

    def tamper_block(self, block_index, sender=None, receiver=None, amount=None):
        try:
            block_index = int(block_index)
        except (TypeError, ValueError):
            raise ValueError("Chi so block khong hop le")

        if block_index <= 0 or block_index >= len(self.chain):
            raise ValueError("Chi co the sua block da mine, khong sua genesis block")

        block = self.chain[block_index]
        if not block.transactions:
            block.transactions.append({})

        target_transaction = block.transactions[0]
        if sender is not None and str(sender).strip():
            target_transaction["sender"] = str(sender).strip()
        if receiver is not None and str(receiver).strip():
            target_transaction["receiver"] = str(receiver).strip()
        if amount is not None and str(amount).strip() != "":
            target_transaction["amount"] = float(amount)
        target_transaction["tampered"] = True
        target_transaction["tampered_at"] = time.time()

        # Co tinh khong tinh lai hash de chung minh du lieu bi sua se lam chain sai.
        self.save()
        return {"message": "Da sua du lieu block de demo tinh bat bien", "validation": self.validate_chain()}

    def get_block(self, index):
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None

    def get_address_history(self, address):
        transactions = []
        address = address.strip()

        for block in self.chain:
            for tx in block.transactions:
                if tx.get("sender") == address or tx.get("receiver") == address:
                    transactions.append(
                        {
                            "status": "confirmed",
                            "block": block.index,
                            "sender": tx.get("sender"),
                            "receiver": tx.get("receiver"),
                            "amount": tx.get("amount", 0),
                            "gas_fee": tx.get("gas_fee", 0),
                            "type": tx.get("type", "transfer"),
                            "timestamp": tx.get("timestamp", block.timestamp),
                        }
                    )

        for tx in self.pending_transactions:
            if tx.get("sender") == address or tx.get("receiver") == address:
                transactions.append(
                    {
                        "status": "pending",
                        "block": None,
                        "sender": tx.get("sender"),
                        "receiver": tx.get("receiver"),
                        "amount": tx.get("amount", 0),
                        "gas_fee": tx.get("gas_fee", 0),
                        "type": tx.get("type", "transfer"),
                        "timestamp": tx.get("timestamp", time.time()),
                    }
                )

        return {"address": address, "balance": self.contract.balance_of(address), "transactions": transactions}

    def update_difficulty(self, difficulty):
        try:
            difficulty = int(difficulty)
        except (TypeError, ValueError):
            raise ValueError("Difficulty khong hop le")

        if difficulty < 1 or difficulty > 5:
            raise ValueError("Difficulty nen nam trong khoang 1 den 5 de demo")

        self.difficulty = difficulty
        self.save()
        return self.difficulty

    def total_confirmed_transactions(self):
        return sum(len(block.transactions) for block in self.chain)

    def stats(self):
        return {
            "total_blocks": len(self.chain),
            "total_transactions": self.total_confirmed_transactions(),
            "pending_transactions": len(self.pending_transactions),
            "total_wallets": len(self.wallets),
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward,
            "gas_fee": self.gas_fee,
            "current_wallet": self.current_wallet,
        }

    def advanced_stats(self):
        chain_data = [block.to_dict() for block in self.chain]
        wallet_balances = [
            {
                "address": wallet["address"],
                "label": wallet.get("label", wallet["address"]),
                "balance": self.contract.balance_of(wallet["address"]),
            }
            for wallet in self.wallets
        ]

        return {
            **self.stats(),
            "blocks_by_time": [
                {"block": block.index, "timestamp": block.timestamp, "transactions": len(block.transactions)}
                for block in self.chain
            ],
            "transactions_per_block": [
                {"block": block.index, "transactions": len(block.transactions)}
                for block in self.chain
            ],
            "wallet_balances": wallet_balances,
            "chain": chain_data,
            "pending": self.pending_transactions,
            "balances": self.contract.balances,
        }

    def to_dict(self):
        return {
            **self.stats(),
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions_list": self.pending_transactions,
        }
