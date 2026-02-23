from flask import Flask, jsonify, request, render_template
from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/balance/<address>')
def balance(address):
    return jsonify({
        "balance": blockchain.contract.balance_of(address)
    })


@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_json()

    success = blockchain.add_transaction(
        data['sender'],
        data['receiver'],
        data['amount']
    )

    if not success:
        return jsonify({"message": "Insufficient balance"}), 400

    return jsonify({"message": "Transaction added"})


@app.route('/mine')
def mine():
    block = blockchain.mine()

    if not block:
        return jsonify({"message": "Nothing to mine"}), 400

    return jsonify({
        "hash": block.hash,
        "index": block.index
    })


@app.route('/chain')
def chain():
    return jsonify([block.__dict__ for block in blockchain.chain])


@app.route('/block/<int:index>')
def block_detail(index):
    if index < len(blockchain.chain):
        return render_template("block.html", block=blockchain.chain[index])
    return "Block not found"

@app.route('/address/<address>')
def search_address(address):

    transactions = []

    for block in blockchain.chain:
        for tx in block.transactions:
            if tx["sender"] == address or tx["receiver"] == address:
                transactions.append({
                    "block": block.index,
                    "sender": tx["sender"],
                    "receiver": tx["receiver"],
                    "amount": tx["amount"]
                })

    return jsonify({
        "address": address,
        "balance": blockchain.contract.balance_of(address),
        "transactions": transactions
    })

if __name__ == '__main__':
    app.run(debug=True)