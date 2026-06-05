import os
import sys


LOCAL_DEPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".deps")
if os.path.isdir(LOCAL_DEPS) and LOCAL_DEPS not in sys.path:
    sys.path.insert(0, LOCAL_DEPS)

from flask import Flask, jsonify, render_template, request

from blockchain import Blockchain


app = Flask(__name__)
blockchain = Blockchain()


def json_error(message, status=400):
    return jsonify({"success": False, "message": message}), status


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/wallet/create", methods=["POST"])
def create_wallet():
    data = request.get_json(silent=True) or {}
    label = data.get("label", "")
    initial_balance = data.get("initial_balance", 100)

    try:
        wallet = blockchain.create_wallet(label=label, initial_balance=initial_balance)
    except ValueError as exc:
        return json_error(str(exc))

    return jsonify({"success": True, "wallet": wallet})


@app.route("/api/wallets")
def get_wallets():
    return jsonify({"wallets": blockchain.wallets})


@app.route("/api/wallet/login", methods=["POST"])
def wallet_login():
    data = request.get_json(silent=True) or {}
    address = data.get("address", "").strip()

    if not address:
        return json_error("Vui long nhap dia chi vi")

    wallet = blockchain.login_wallet(address)
    return jsonify({"success": True, "wallet": wallet})


@app.route("/api/transaction", methods=["POST"])
@app.route("/transfer", methods=["POST"])
def add_transaction():
    data = request.get_json(silent=True) or {}

    try:
        result = blockchain.add_transaction(
            sender=data.get("sender", ""),
            receiver=data.get("receiver", ""),
            amount=data.get("amount", 0),
        )
    except ValueError as exc:
        return json_error(str(exc))

    return jsonify({"success": True, "message": "Da them giao dich vao pending pool", "transaction": result})


@app.route("/api/mine", methods=["POST"])
def mine_post():
    data = request.get_json(silent=True) or {}
    miner = data.get("miner", "").strip()

    if not miner:
        return json_error("Vui long nhap dia chi miner")

    try:
        result = blockchain.mine_pending_transactions(miner)
    except ValueError as exc:
        return json_error(str(exc))

    return jsonify({"success": True, **result})


@app.route("/mine")
def mine_get():
    try:
        result = blockchain.mine_pending_transactions("Miner")
    except ValueError as exc:
        return json_error(str(exc))

    return jsonify({"success": True, **result})


@app.route("/api/chain")
@app.route("/chain")
def get_chain():
    return jsonify(blockchain.to_dict())


@app.route("/api/balance/<address>")
@app.route("/balance/<address>")
def get_balance(address):
    return jsonify({"address": address, "balance": blockchain.contract.balance_of(address)})


@app.route("/api/address/<address>/transactions")
@app.route("/address/<address>")
def address_transactions(address):
    return jsonify(blockchain.get_address_history(address))


@app.route("/api/validate")
def validate_chain():
    return jsonify(blockchain.validate_chain())


@app.route("/api/tamper", methods=["POST"])
def tamper_block():
    data = request.get_json(silent=True) or {}

    try:
        result = blockchain.tamper_block(
            block_index=data.get("block_index"),
            sender=data.get("sender"),
            receiver=data.get("receiver"),
            amount=data.get("amount"),
        )
    except ValueError as exc:
        return json_error(str(exc))

    return jsonify({"success": True, **result})


@app.route("/api/reset", methods=["POST"])
def reset_chain():
    blockchain.reset()
    return jsonify({"success": True, "message": "Da reset blockchain", **blockchain.stats()})


@app.route("/api/settings/difficulty", methods=["POST"])
def update_difficulty():
    data = request.get_json(silent=True) or {}

    try:
        difficulty = blockchain.update_difficulty(data.get("difficulty"))
    except ValueError as exc:
        return json_error(str(exc))

    return jsonify({"success": True, "difficulty": difficulty})


@app.route("/api/stats")
def stats():
    return jsonify(blockchain.stats())


@app.route("/api/stats/advanced")
def advanced_stats():
    return jsonify(blockchain.advanced_stats())


@app.route("/block/<int:index>")
def block_detail(index):
    block = blockchain.get_block(index)
    if block is None:
        return "Block not found", 404
    return render_template("block.html", block=block)


if __name__ == "__main__":
    app.run(debug=True)
