import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

BLOCKCHAIN_DATA_FILE = os.path.join(DATA_DIR, "blockchain_data.json")
WALLETS_FILE = os.path.join(DATA_DIR, "wallets.json")
BALANCES_FILE = os.path.join(DATA_DIR, "balances.json")

TOKEN_NAME = "HIEU COIN"
TOKEN_SYMBOL = "HIEU"
GENESIS_OWNER = "Alice"
INITIAL_SUPPLY = 1_000_000
DEFAULT_DIFFICULTY = 3
MINING_REWARD = 50
DEFAULT_GAS_FEE = 1
DEMO_WALLET_BALANCE = 100
