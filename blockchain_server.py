import urllib.parse

from flask import Flask
from flask import jsonify
from flask import request
import requests

import blockchain
import wallet

PORT = 8000
app = Flask(__name__)

cache = {}


def get_blockchain():
    cached_blockchain = cache.get('blockchain')
    if not cached_blockchain:
        miners_wallet = wallet.Wallet()
        cache['blockchain'] = blockchain.BlockChain(
            miners_wallet.blockchain_address, port=PORT)
    return cache['blockchain']


@app.route('/chain', methods=['GET'])
def get_chain():
    block_chain = get_blockchain()
    res = {
        'chain': block_chain.chain
    }
    return jsonify(res), 200


@app.route('/mine', methods=['GET'])
def mine():
    block_chain = get_blockchain()
    is_mined = block_chain.mining()
    if is_mined:
        return jsonify({'message': 'succuess'}), 200
    return jsonify({'message': 'fail'}), 400


@app.route('/transactions', methods=['GET', 'POST'])
def transaction():
    block_chain = get_blockchain()
    if request.method == 'GET':
        transactions = block_chain.transaction_pool
        res = {
            'transactions': transactions,
            'length': len(transactions)
        }
        return jsonify(res), 200

    if request.method == 'POST':
        print(request.json)
        request_json = request.json
        required = {
            'sender_blockchain_address',
            'recipient_blockchain_address',
            'value',
            'sender_public_key',
            'signature',
        }
        if not all(k in request_json for k in required):
            return jsonify({'message': 'missing values'}), 400

        is_create = block_chain.create_transaction(
            request_json['sender_blockchain_address'],
            request_json['recipient_blockchain_address'],
            request_json['value'],
            request_json['sender_public_key'],
            request_json['signature']
        )
        if not is_create:
            return jsonify({'message': 'fail'}), 400
        return jsonify({'message': 'success'}), 201


if __name__ == '__main__':
    app.run(port=PORT, debug=True)
