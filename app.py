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
        "address": address,
        "balance": blockchain.contract.balance_of(address)
    })


@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_json()

    blockchain.add_transaction(
        data['sender'],
        data['receiver'],
        data['amount']
    )

    return jsonify({"message": "Transaction added to pending pool"})


@app.route('/mine')
def mine():
    block = blockchain.mine()

    if not block:
        return jsonify({"message": "No transactions to mine"}), 400

    return jsonify({
        "block_index": block.index,
        "hash": block.hash
    })


@app.route('/chain')
def chain():
    return jsonify([block.__dict__ for block in blockchain.chain])


if __name__ == '__main__':
    app.run(debug=True)