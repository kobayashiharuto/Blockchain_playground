from ecdsa import NIST256p
from ecdsa import SigningKey
import base58
import hashlib
import codecs


class Wallet:
    def __init__(self):
        self._private_key = SigningKey.generate(curve=NIST256p)
        self._public_key = self._private_key.get_verifying_key()

    @property
    def private_key(self):
        return self._private_key.to_string().hex()

    @property
    def public_key(self):
        return self._public_key.to_string().hex()

    def generate_blockchain_address(self):
        public_key_bytes = self._public_key.to_string()
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        


if __name__ == '__main__':
    wallet = Wallet()
    print(wallet.private_key)
    print(wallet.public_key)
