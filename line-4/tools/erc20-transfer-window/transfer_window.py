#!/usr/bin/env python3
"""Read a bounded ERC-20 Transfer log window from Ethereum JSON-RPC.

This program is deliberately read-only.  It neither reads credentials nor creates,
signs, sends, or serializes a transaction.
"""

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request


TOKENS = {
    "zto": "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e",
    "imd": "0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7",
}
DEFAULT_RPC = "https://ethereum-rpc.publicnode.com"
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
DECIMALS_CALL = "0x313ce567"
USER_AGENT = "Pepeolithic-ERC20-Transfer-Window/1.0 (read-only public data)"
MAX_WINDOW = 2_000


class RpcError(RuntimeError):
    """An RPC response could not supply the requested public data."""


def rpc(endpoint, method, params):
    """Perform one JSON-RPC request, returning its result or raising RpcError."""
    body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        separators=(",", ":"),
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RpcError("network or JSON failure: {}".format(exc)) from exc
    if "error" in payload:
        raise RpcError("RPC error: {}".format(payload["error"]))
    if "result" not in payload:
        raise RpcError("RPC response has no result")
    return payload["result"]


def parse_block(value):
    """Accept a non-negative decimal or 0x-prefixed block number."""
    try:
        number = int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("block must be decimal or 0x-prefixed") from exc
    if number < 0:
        raise argparse.ArgumentTypeError("block must not be negative")
    return number


def as_quantity(number):
    return hex(number)


def topic_address(topic):
    if not isinstance(topic, str) or len(topic) != 66 or not topic.startswith("0x"):
        raise RpcError("unexpected indexed address topic")
    return "0x" + topic[-40:].lower()


def display_units(raw, decimals):
    """Format a nonnegative integer using a token's on-chain decimal count."""
    if decimals == 0:
        return str(raw)
    whole, fraction = divmod(raw, 10**decimals)
    if fraction == 0:
        return str(whole)
    return "{}.{}".format(str(whole), str(fraction).zfill(decimals).rstrip("0"))


def decode_log(log, decimals):
    topics = log.get("topics")
    data = log.get("data")
    if not isinstance(topics, list) or len(topics) != 3 or not isinstance(data, str):
        raise RpcError("unexpected Transfer log shape")
    try:
        raw_value = int(data, 16)
        block = int(log["blockNumber"], 16)
        index = int(log["logIndex"], 16)
    except (KeyError, TypeError, ValueError) as exc:
        raise RpcError("unexpected numeric Transfer log field") from exc
    return {
        "block": block,
        "log_index": index,
        "transaction_hash": log.get("transactionHash"),
        "from": topic_address(topics[1]),
        "to": topic_address(topics[2]),
        "raw_value": str(raw_value),
        "value": display_units(raw_value, decimals),
    }


def arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", choices=sorted(TOKENS), default="zto", help="token to inspect (default: zto)")
    parser.add_argument("--from-block", type=parse_block, help="first inclusive block")
    parser.add_argument("--to-block", type=parse_block, help="last inclusive block")
    parser.add_argument("--latest-window", type=int, default=12, help="latest inclusive block window when bounds are omitted (default: 12)")
    parser.add_argument("--rpc", default=DEFAULT_RPC, help="public Ethereum JSON-RPC URL")
    args = parser.parse_args(argv)
    if (args.from_block is None) != (args.to_block is None):
        parser.error("--from-block and --to-block must be supplied together")
    if args.latest_window < 1 or args.latest_window > MAX_WINDOW:
        parser.error("--latest-window must be between 1 and {}".format(MAX_WINDOW))
    if args.from_block is not None and args.to_block < args.from_block:
        parser.error("--to-block must not precede --from-block")
    if args.from_block is not None and args.to_block - args.from_block + 1 > MAX_WINDOW:
        parser.error("the requested block range exceeds {} blocks".format(MAX_WINDOW))
    return args


def main(argv=None):
    args = arguments(argv)
    token_address = TOKENS[args.token]
    head = int(rpc(args.rpc, "eth_blockNumber", []), 16)
    if args.from_block is None:
        to_block = head
        from_block = max(0, head - args.latest_window + 1)
    else:
        from_block, to_block = args.from_block, args.to_block
    decimals_result = rpc(args.rpc, "eth_call", [{"to": token_address, "data": DECIMALS_CALL}, "latest"])
    try:
        decimals = int(decimals_result, 16)
    except (TypeError, ValueError) as exc:
        raise RpcError("token decimals() result is not a hex integer") from exc
    if decimals > 255:
        raise RpcError("token decimals() result is implausibly large")
    filter_object = {
        "address": token_address,
        "fromBlock": as_quantity(from_block),
        "toBlock": as_quantity(to_block),
        "topics": [TRANSFER_TOPIC],
    }
    logs = rpc(args.rpc, "eth_getLogs", [filter_object])
    if not isinstance(logs, list):
        raise RpcError("eth_getLogs result is not a list")
    transfers = [decode_log(log, decimals) for log in logs]
    transfers.sort(key=lambda item: (item["block"], item["log_index"]))
    output = {
        "captured_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "rpc": args.rpc,
        "token": args.token.upper(),
        "token_address": token_address,
        "decimals": decimals,
        "head_at_capture": head,
        "from_block": from_block,
        "to_block": to_block,
        "transfer_count": len(transfers),
        "transfers": transfers,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RpcError as exc:
        print("transfer-window: {}".format(exc), file=sys.stderr)
        raise SystemExit(2)
