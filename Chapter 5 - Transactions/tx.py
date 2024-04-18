from helper import hash256, little_endian_to_int, read_variant
from script import Script


class Tx:
    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet

    def __repr__(self):
        tx_ins = ""
        for tx in self.tx_ins:
            tx_ins += tx.__repr__() + "\n"

        tx_outs = ""
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + "\n"
        return "tx: {}\nversion: {}\ntx_ins:\n{}tx_outs:\n{}locktime: {}".format(
            self.id(),
            self.version,
            tx_ins,
            tx_outs,
            self.locktime,
        )

    def id(self):
        """Human-readable hexadecimal of the transaction hash."""
        return self.hash().hex()

    def hash(self):
        """Binary hash of the legacy serialization"""
        return hash256(self.serialize())[::-1]

    @classmethod
    def parse(cls, s, testnet=False):
        # version = serialization[0:4]
        version = little_endian_to_int(s.read(4))

        num_inputs = read_variant(s)
        inputs = []
        for n in range(num_inputs):
            inputs.append(TxIn.parse(s))

        num_outputs = read_variant(s)
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))
        return cls(version, inputs, outputs, None, testnet=testnet)


class TxIn:
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xFFFFFFFF):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig

    def __repr__(self):
        return "{}:{}".format(
            self.prev_tx.hex(),
            self.prev_index,
        )

    def parse(cls, s):
        prev_tx = s.read(32)[::-1]
        prev_index = little_endian_to_int(s.read(4))
        script_sig = Script.parse(s)
        sequence = little_endian_to_int(s.read(4))
        return cls(prev_tx, prev_index, script_sig, sequence)


class TxOut:
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return "{}:{}".format(self.amount, self.script_pubkey)

    def parse(cls, s):
        """Takes a byte stream and parses the tx_output at the start.
        Returns a TxOut object.
        """
        amount = little_endian_to_int(s.read(8))
        script_pubkey = Script.parse(s)
        return cls(amount, script_pubkey)
