import binascii
from ecdsa import NIST256p
from ecdsa import SigningKey
import base58
import hashlib
import codecs

from ecdsa.ecdsa import Private_key
from blockachain import BlockChain
import utils


class Wallet:
    def __init__(self):
        self._private_key = SigningKey.generate(curve=NIST256p)
        self._public_key = self._private_key.get_verifying_key()
        self._blockchain_address = self.generate_blockchain_address()

    @property
    def private_key(self):
        return self._private_key.to_string().hex()

    @property
    def public_key(self):
        return self._public_key.to_string().hex()

    @property
    def blockchain_address(self):
        return self._blockchain_address

    def generate_blockchain_address(self):
        public_key_bytes = self._public_key.to_string()
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()

        ripemed160_bpk = hashlib.new('ripemd160')
        ripemed160_bpk.update(sha256_bpk_digest)
        ripemed160_bpk_digest = ripemed160_bpk.digest()
        ripemed160_bpk_hex = codecs.encode(ripemed160_bpk_digest, 'hex')

        network_byte = b'00'
        network_bitcoin_publick_key = network_byte + ripemed160_bpk_hex
        network_bitcoin_publick_key_bytes = codecs.decode(
            network_bitcoin_publick_key, 'hex')

        sha256_bpk = hashlib.sha256(network_bitcoin_publick_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        sha256_nbpk = hashlib.sha256(sha256_bpk_digest)
        sha256_nbpk_digest = sha256_nbpk.digest()
        sha256_hex = codecs.encode(sha256_nbpk_digest, 'hex')

        checksum = sha256_hex[:8]

        address_hex = (network_bitcoin_publick_key + checksum).decode('utf-8')

        blockchain_address = base58.b58encode(
            binascii.unhexlify(address_hex)).decode('utf-8')
        return blockchain_address


class Transaction:
    def __init__(self, sender_private_key, sender_publick_key, sender_blockchain_address, recipient_blockchain_address, value):
        self.sender_private_key = sender_private_key
        self.sender_publick_key = sender_publick_key
        self.sender_blockchain_address = sender_blockchain_address
        self.recipient_blockchain_address = recipient_blockchain_address
        self.value = value

    def generate_signature(self):
        sha256 = hashlib.sha256()
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': self.sender_blockchain_address,
            'recipient_blockchain_address': self.recipient_blockchain_address,
            'value': self.value
        })
        sha256.update(str(transaction).encode('utf-8'))
        message = sha256.digest()
        private_key = SigningKey.from_string(
            bytes().fromhex(self.sender_private_key), curve=NIST256p)
        private_key_sign = private_key.sign(message)
        signature = private_key_sign.hex()
        return signature


if __name__ == '__main__':
    walletM = Wallet()
    walletA = Wallet()
    walletB = Wallet()
    t = Transaction(walletA.private_key, walletA.public_key,
                    walletA.blockchain_address, walletB.blockchain_address, 1.0)

    blockchain = BlockChain(blockchain_address=walletM.blockchain_address)
    is_add = blockchain.add_transaction(walletA.blockchain_address, walletB.blockchain_address,
                                        1.0, walletA.public_key, t.generate_signature())
    print('Added?', is_add)
    blockchain.mining()
    utils.pprint(blockchain.chain)

    print('A', blockchain.calc_total_amout(walletA.blockchain_address))
    print('B', blockchain.calc_total_amout(walletB.blockchain_address))
