import urllib.parse

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
import requests

import wallet

app = Flask(__name__, template_folder='./templates')


@app.route('/')
def index():
    return render_template('./index.html')


@app.route('/wallet', methods=['POST'])
def create_wallet():
    my_wallet = wallet.Wallet()
    response = {
        'private_key': my_wallet.private_key,
        'public_key': my_wallet.public_key,
        'blockchain_address': my_wallet.blockchain_address,
    }
    return jsonify(response), 200


@app.route('/transaction', methods=['POST'])
def create_transaction():
    request_json = request.json
    required = (
        'sender_private_key',
        'sender_blockchain_address',
        'recipient_blockchain_address',
        'sender_public_key',
        'value')
    if not all(k in request_json for k in required):
        return 'missing values', 400

    sender_private_key = request_json['sender_private_key']
    sender_blockchain_address = request_json['sender_blockchain_address']
    recipient_blockchain_address = request_json['recipient_blockchain_address']
    sender_public_key = request_json['sender_public_key']
    value = float(request_json['value'])

    transaction = wallet.Transaction(
        sender_private_key,
        sender_public_key,
        sender_blockchain_address,
        recipient_blockchain_address,
        value)

    json_data = {
        'sender_blockchain_address': sender_blockchain_address,
        'recipient_blockchain_address': recipient_blockchain_address,
        'sender_public_key': sender_public_key,
        'value': value,
        'signature': transaction.generate_signature(),
    }

    response = requests.post(
        urllib.parse.urljoin(app.config['gw'], 'transactions'),
        json=json_data, timeout=3)

    if response.status_code == 201:
        return jsonify({'message': 'success'}), 201
    return jsonify({'message': 'fail', 'response': response}), 400


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    port = 8000
    app.config['gw'] = 'http://localhost:5000'

    app.run(port=port, threaded=True, debug=True)
