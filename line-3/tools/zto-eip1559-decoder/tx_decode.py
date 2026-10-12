#!/usr/bin/env python3
"""Decode an unsigned EIP-1559 Ethereum transaction without network access."""
import json
import sys

ZTO = "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e"


def rlp_item(data, position=0):
    """Return (an RLP byte string or list, next_position), rejecting non-canonical data."""
    if position >= len(data):
        raise ValueError("truncated RLP item")
    first = data[position]
    if first < 0x80:
        return bytes([first]), position + 1
    if first <= 0xb7:
        size = first - 0x80
        start = position + 1
        end = start + size
        if end > len(data) or (size == 1 and data[start] < 0x80):
            raise ValueError("non-canonical or truncated RLP string")
        return data[start:end], end
    if first <= 0xbf:
        length_size = first - 0xb7
        start = position + 1
        end = start + length_size
        if end > len(data) or data[start] == 0:
            raise ValueError("non-canonical or truncated RLP length")
        size = int.from_bytes(data[start:end], "big")
        body = end + size
        if size < 56 or body > len(data):
            raise ValueError("non-canonical or truncated RLP string")
        return data[end:body], body
    if first <= 0xf7:
        size = first - 0xc0
        start = position + 1
        end = start + size
    else:
        length_size = first - 0xf7
        start = position + 1
        end = start + length_size
        if end > len(data) or data[start] == 0:
            raise ValueError("non-canonical or truncated RLP length")
        size = int.from_bytes(data[start:end], "big")
        if size < 56:
            raise ValueError("non-canonical RLP list")
        end += size
    if end > len(data):
        raise ValueError("truncated RLP list")
    values = []
    cursor = start if first <= 0xf7 else position + 1 + length_size
    while cursor < end:
        value, cursor = rlp_item(data, cursor)
        values.append(value)
    if cursor != end:
        raise ValueError("malformed RLP list")
    return values, end


def integer(value, name):
    if not isinstance(value, bytes) or (len(value) > 1 and value[0] == 0):
        raise ValueError(f"invalid {name}")
    return int.from_bytes(value, "big")


def rlp_encode(value):
    if isinstance(value, int):
        value = b"" if value == 0 else value.to_bytes((value.bit_length() + 7) // 8, "big")
    if isinstance(value, list):
        payload = b"".join(rlp_encode(item) for item in value)
        offset = 0xc0
    else:
        if not isinstance(value, bytes):
            raise TypeError("RLP values must be integers, byte strings, or lists")
        if len(value) == 1 and value[0] < 0x80:
            return value
        payload = value
        offset = 0x80
    if len(payload) < 56:
        return bytes([offset + len(payload)]) + payload
    length = len(payload).to_bytes((len(payload).bit_length() + 7) // 8, "big")
    return bytes([offset + 55 + len(length)]) + length + payload


def access_list(value):
    if not isinstance(value, list):
        raise ValueError("accessList must be an RLP list")
    decoded = []
    for entry in value:
        if not isinstance(entry, list) or len(entry) != 2 or not isinstance(entry[0], bytes) or len(entry[0]) != 20:
            raise ValueError("invalid access-list address")
        if not isinstance(entry[1], list) or any(not isinstance(slot, bytes) or len(slot) != 32 for slot in entry[1]):
            raise ValueError("invalid access-list storage key")
        decoded.append({"address": "0x" + entry[0].hex(), "storageKeys": ["0x" + slot.hex() for slot in entry[1]]})
    return decoded


def decode(transaction_hex):
    if transaction_hex.startswith("0x"):
        transaction_hex = transaction_hex[2:]
    if len(transaction_hex) % 2 or not transaction_hex:
        raise ValueError("transaction must be non-empty, even-length hexadecimal")
    try:
        raw = bytes.fromhex(transaction_hex)
    except ValueError as error:
        raise ValueError("transaction is not hexadecimal") from error
    if raw[0] != 2:
        raise ValueError("only EIP-1559 typed transactions (0x02) are supported")
    fields, end = rlp_item(raw, 1)
    if end != len(raw) or not isinstance(fields, list) or len(fields) != 9:
        raise ValueError("an unsigned EIP-1559 transaction must contain exactly nine fields")
    names = ("chainId", "nonce", "maxPriorityFeePerGas", "maxFeePerGas", "gasLimit", "to", "value", "data", "accessList")
    result = {"type": "EIP-1559", "typeByte": "0x02"}
    for index, name in enumerate(names):
        field = fields[index]
        if name == "to":
            if not isinstance(field, bytes) or len(field) not in (0, 20):
                raise ValueError("to must be empty or a 20-byte address")
            result[name] = None if not field else "0x" + field.hex()
        elif name == "data":
            if not isinstance(field, bytes):
                raise ValueError("data must be bytes")
            result[name] = "0x" + field.hex()
        elif name == "accessList":
            result[name] = access_list(field)
        else:
            result[name] = integer(field, name)
    result["calldataSelector"] = result["data"][:10] if len(result["data"]) >= 10 else None
    return result


def demo_transaction():
    """An unsigned, non-payable call to ZTO's real contract: totalSupply()."""
    payload = [1, 0, 1_000_000_000, 2_000_000_000, 100_000, bytes.fromhex(ZTO[2:]), 0, bytes.fromhex("18160ddd"), []]
    return "0x02" + rlp_encode(payload).hex()


def main(arguments):
    if arguments == ["--demo"]:
        print(json.dumps(decode(demo_transaction()), indent=2, sort_keys=True))
        return
    if len(arguments) != 1:
        raise SystemExit("usage: tx_decode.py --demo | 0x02...")
    print(json.dumps(decode(arguments[0]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
