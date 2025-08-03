from flask import Flask, request, render_template, redirect, url_for, jsonify
import json
import time
from hashlib import sha256

app = Flask(__name__)

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.difficulty = 2  # Lower difficulty for easier mining
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), [], "0")
        self.chain.append(genesis_block)

    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, amount):
        try:
            amount = float(amount)
        except ValueError:
            return False
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return True

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def mine(self, miner_address):
        if not self.current_transactions:
            return None

        # Reward the miner
        self.current_transactions.append({
            'sender': "Network",
            'recipient': miner_address,
            'amount': 10.0
        })

        last_block = self.last_block()
        new_block = Block(
            index=last_block.index + 1,
            timestamp=time.time(),
            transactions=self.current_transactions,
            previous_hash=last_block.hash
        )
        new_block.hash = self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.current_transactions = []
        return new_block

    def to_dict(self):
        return [block.__dict__ for block in self.chain]

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            if curr.previous_hash != prev.hash or curr.hash != curr.compute_hash():
                return False
        return True

blockchain = Blockchain()

# Simple user list
users = ['alice', 'bob', 'carol']

@app.route('/')
def index():
    return render_template('index.html', users=users)

@app.route('/send', methods=['POST'])
def send():
    sender = request.form['sender']
    recipient = request.form['recipient']
    amount = request.form['amount']
    if sender not in users or recipient not in users:
        return "Unknown user!", 400
    success = blockchain.add_transaction(sender, recipient, amount)
    if not success:
        return "Invalid amount!", 400
    return redirect(url_for('index'))

@app.route('/mine', methods=['POST'])
def mine():
    miner = request.form['miner']
    if miner not in users:
        return "Unknown miner!", 400
    block = blockchain.mine(miner)
    if not block:
        return "No transactions to mine!", 400
    return redirect(url_for('index'))

@app.route('/chain')
def get_chain():
    return jsonify(blockchain.to_dict())

@app.route('/valid')
def check_validity():
    valid = blockchain.is_chain_valid()
    return jsonify({"valid": valid})

@app.route('/pending')
def pending_transactions():
    return jsonify(blockchain.current_transactions)

if __name__ == '__main__':
    app.run(debug=True)
