import json
import os
from typing import Any

from config import BALANCES_FILE, BLOCKCHAIN_DATA_FILE, DATA_DIR, WALLETS_FILE


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path: str, default: Any):
    ensure_data_dir()
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path: str, data: Any):
    ensure_data_dir()
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def load_blockchain_data():
    return load_json(BLOCKCHAIN_DATA_FILE, None)


def save_blockchain_data(data):
    save_json(BLOCKCHAIN_DATA_FILE, data)


def load_wallets():
    return load_json(WALLETS_FILE, [])


def save_wallets(wallets):
    save_json(WALLETS_FILE, wallets)


def load_balances():
    return load_json(BALANCES_FILE, {})


def save_balances(balances):
    save_json(BALANCES_FILE, balances)
