import logging
import sys
import hashlib
import json
import time

import utils

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

MINING_DIFF = 3
MINING_SENDER = 'THE BLOCKCHAIN'
MINING_REWARD = 1.0

logger = logging.getLogger(__name__)


class BlockChain:
    def __init__(self, blockchain_address=None):
        self.transaction_pool = []
        self.chain = []
        self.create_block(0, self.hash({}))
        self.blockchain_address = blockchain_address

    def create_block(self, nonce, previous_hash):
        block = utils.sorted_dict_by_key({
            'timestamp': time.time(),
            'transactions': self.transaction_pool,
            'nonce': nonce,
            'previous_hash': previous_hash
        })
        self.chain.append(block)
        self.transaction_pool = []
        return block

    def hash(self, block):
        sorted_block = json.dumps(block, sort_keys=True)
        return hashlib.sha256(sorted_block.encode()).hexdigest()

    def add_transaction(self, sender_address, recipient_address, value):
        transaction = utils.sorted_dict_by_key({
            'sender_address': sender_address,
            'recipient_address': recipient_address,
            'value': float(value)
        })
        self.transaction_pool.append(transaction)
        return True

    def valid_proof(self, transactions, previous_hash, nonce, diff=MINING_DIFF):
        guess_block = utils.sorted_dict_by_key({
            'transactions': transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        })
        guess_hash = self.hash(guess_block)
        return guess_hash[:diff] == '0'*diff

    def proof_of_works(self):
        transactions = self.transaction_pool.copy()
        previous_hash = self.hash(self.chain[-1])
        nonce = 0
        while self.valid_proof(transactions, previous_hash, nonce) is False:
            nonce += 1
        return nonce

    def mining(self):
        self.add_transaction(
            sender_address=MINING_SENDER,
            recipient_address=self.blockchain_address,
            value=MINING_REWARD
        )
        nonce = self.proof_of_works()
        previous_hash = self.hash(self.chain[-1])
        self.create_block(nonce, previous_hash)
        logger.info({'action': 'mining', 'status': 'success'})
        return True

    def calc_total_amout(self, address):
        total_amout = 0
        for block in self.chain:
            for transaction in block['transactions']:
                value = float(transaction['value'])
                if address == transaction['sender_address']:
                    total_amout -= value
                if address == transaction['recipient_address']:
                    total_amout += value
        return total_amout


if __name__ == '__main__':
    my_blockchain_adress = 'my_blockchain_address'
    block_chain = BlockChain(my_blockchain_adress)

    block_chain.add_transaction('A', 'B', 1.0)
    block_chain.mining()
    utils.pprint(block_chain.chain)

    block_chain.add_transaction('C', 'D', 2.0)
    block_chain.add_transaction('X', 'Y', 3.0)
    block_chain.mining()
    utils.pprint(block_chain.chain)

    print('my', block_chain.calc_total_amout(my_blockchain_adress))
    print('C', block_chain.calc_total_amout('C'))
    print('D', block_chain.calc_total_amout('D'))