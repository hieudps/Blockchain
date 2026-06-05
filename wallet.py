import hashlib
import time
import uuid


def create_wallet_address(label=""):
    """Tao dia chi vi demo bang SHA-256 tu UUID va thoi gian."""
    raw_value = f"{label}-{uuid.uuid4()}-{time.time()}"
    return "WALLET-" + hashlib.sha256(raw_value.encode()).hexdigest()[:32].upper()


def create_wallet(label=""):
    address = create_wallet_address(label)
    return {
        "address": address,
        "label": label.strip() or f"Wallet {address[-6:]}",
        "created_at": time.time(),
    }
