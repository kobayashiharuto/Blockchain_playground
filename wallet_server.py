import urllib.parse

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
import requests

import blockchain
from blockchain_server import transaction
import wallet

PORT = 5000
app = Flask(__name__, template_folder='./templates')


@app.route('/')
def index():
    return render_template('./index.html')


@app.route('/wallet', methods=['POST'])
def get_wallet():
    my_wallet = wallet.Wallet()
    res = {
        'private_key': my_wallet.private_key,
        'public_key': my_wallet.public_key,
        'blockchain_address': my_wallet.blockchain_address
    }
    return jsonify(res), 200


@app.route('/transaction', methods=['POST'])
def create_transaction():
    request_json = request.json
    print(request_json)
    required = (
        'sender_private_key',
        'sender_blockchain_address',
        'recipient_blockchain_address',
        'sender_public_key',
        'value',
    )
    if not all(k in request_json for k in required):
        return 'missing values', 400

    sender_private_key = request_json['sender_private_key']
    sender_public_key = request_json['sender_public_key']
    sender_blockchain_address = request_json['sender_blockchain_address']
    recipient_blockchain_address = request_json['recipient_blockchain_address']
    value = request_json['value']

    transaction = wallet.Transaction(
        sender_private_key,
        sender_public_key,
        sender_blockchain_address,
        recipient_blockchain_address,
        value)

    json_data = {
        'sender_public_key': sender_public_key,
        'recipient_blockchain_address': recipient_blockchain_address,
        'sender_blockchain_address': sender_blockchain_address,
        'value': value,
        'signature': transaction.generate_signature()
    }

    res = requests.post(
        'http://localhost:8000/transactions',
        json=json_data, timeout=3
    )

    if res.status_code == '201':
        return jsonify({'message': 'succuess'}), 201
    return jsonify({'message': 'fail', 'responce': res}), 400


if __name__ == '__main__':
    app.run(port=PORT, debug=True)
