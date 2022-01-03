import json
from flask import Flask
from flask import jsonify

import blockchain
import wallet

PORT = 5000
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


if __name__ == '__main__':
    app.run(port=PORT, debug=True)
