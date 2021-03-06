# all imports
import time
import redis
import hashlib
import json
import sys
from typing import List
from dotscoin.Transaction import Transaction
from dotscoin.TransactionOutput import TransactionOutput
from collections import Set, Mapping, deque

class Block:

    def __init__(self): 
        """ Initialization """
        """ Iniialization/Object definition """

        self.hash: str = ""
        self.timestamp = int(time.time())
        self.transactions: List[Transaction] = []
        self.previous_block_hash: str = ""
        self.merkle_root: str = ""
        self.height: int = 0
        self.version: str = "0.0.1"
        self.size: int = 0
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.add_previous_block()

    def add_previous_block(self):
        """ Connecting new block to previous block """

        raw = self.redis_client.lindex('chain', -1)
        if raw is not None and json.loads(raw.decode('utf-8')) is not None:
            self.previous_block_hash = json.loads(raw.decode("utf-8"))["hash"]
            self.height = int(json.loads(raw.decode("utf-8"))["height"])+ 1 

    def add_transaction(self, transaction: Transaction):
        """ Adding a new transaction """
        self.transactions.append(transaction)

    def to_json(self):
        """ Converting object to JSON """

        return {
            'hash': self.hash,
            'timestamp': self.timestamp,
            'transactions': [tx.to_json() for tx in self.transactions],
            'previous_block_hash': self.previous_block_hash,
            'merkle_root': self.merkle_root,
            'height': self.height,
            'version': self.version,
            'size': self.size
        }

    def calcalute_block_size(self):
        """ Calculating the size of the block """

        size = 0
        message={
            'hash': self.hash,
            'timestamp': self.timestamp,
            'transactions': [tx.to_json() for tx in self.transactions],
            'previous_block_hash': self.previous_block_hash,
            'merkle_root': self.merkle_root,
            'height': self.height,
            'version': self.version,
            'size': self.size
        }
        for key in message.keys():
            size += sys.getsizeof(message[key]) 
        self.size = size

    @staticmethod
    def from_json(data):
        """ Mapping data from JSON to object """

        tmp = Block()
        tmp.hash = data['hash']
        tmp.timestamp = data['timestamp']
        tmp.transactions = [Transaction.from_json(
            tx) for tx in data['transactions']]
        tmp.previous_block_hash = data['previous_block_hash']
        tmp.merkle_root = data['merkle_root']
        tmp.height = data['height']
        tmp.version = data['version']
        tmp.size = data['size']
        return tmp

    def compute_hash(self):
        """ Computing hash of the block. Algo used --> SHA256 """

        message = {
            "timestamp": self.timestamp,
            "transactions": [tx.to_json() for tx in self.transactions],
            "previous_block_hash": self.previous_block_hash,
            "merkle_root": self.merkle_root,
            "height": self.height,
            "version": self.version,
            "size": self.size
        }

        self.hash = hashlib.sha256(json.dumps(message).encode("utf-8")).hexdigest()

    def calculate_merkle_root(self, transactions=[]):
        """ Calculating merkle root of the block """

        new_tran = []
        if len(transactions) == 0:
            transactions = [tx.hash for tx in self.transactions]
        if len(transactions) > 1:
            if transactions[-1] == transactions[-2]:
                return ""
        for i in range(0, len(transactions), 2):
            h = hashlib.sha256()
            if i+1 == len(transactions):
                h.update(
                    ((transactions[i]) + (transactions[i])).encode("UTF-8"))
                new_tran.append(h.hexdigest())
            else:
                h.update(
                    ((transactions[i]) + (transactions[i+1])).encode("UTF-8"))
                new_tran.append(h.hexdigest())

        if len(new_tran) == 1:
            self.merkle_root = new_tran[0]
            return
        else:
            # recursive call
            self.calculate_merkle_root(new_tran)

    def create_coinbase_transaction(self):
        tx = Transaction()
        output = TransactionOutput()
        read_file = open("node_data.json", "r")
        raw = read_file.read()
        my_node = json.loads(raw)

        output.value = 50
        output.address = my_node["address"]
        output.n = 0

        tx.add_output(output)
        tx.generate_hash()

        self.add_transaction(tx)
