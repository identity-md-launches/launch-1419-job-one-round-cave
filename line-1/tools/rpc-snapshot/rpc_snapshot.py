#!/usr/bin/env python3
"""Capture one read-only Ethereum JSON-RPC response as portable JSON."""
import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request

DEFAULT_RPC = "https://ethereum-rpc.publicnode.com"
USER_AGENT = "Pepeolithic-RPC-Snapshot/1.0 (read-only public data)"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("method", nargs="?", default="eth_blockNumber", help="JSON-RPC method (default: eth_blockNumber)")
    parser.add_argument("params", nargs="?", default="[]", help="parameters as a JSON array (default: [])")
    parser.add_argument("--rpc", default=DEFAULT_RPC, help="public Ethereum JSON-RPC endpoint")
    args = parser.parse_args()
    try:
        params = json.loads(args.params)
        if not isinstance(params, list):
            raise ValueError("params must be a JSON array")
        if not args.method or args.method.startswith("_"):
            raise ValueError("method must be a public JSON-RPC method")
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": args.method, "params": params}).encode()
        request = urllib.request.Request(args.rpc, data=body, headers={"Content-Type": "application/json", "User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if "error" in payload:
            raise RuntimeError(json.dumps(payload["error"], sort_keys=True))
        if "result" not in payload:
            raise RuntimeError("response has neither result nor error")
    except (ValueError, urllib.error.URLError, TimeoutError, RuntimeError) as exc:
        print(f"rpc-snapshot: {exc}", file=sys.stderr)
        return 1
    snapshot = {
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "endpoint": args.rpc,
        "method": args.method,
        "params": params,
        "result": payload["result"],
    }
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
