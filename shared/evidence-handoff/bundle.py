#!/usr/bin/env python3
"""Bundle public JSON evidence for offline handoff; never contact a network."""
import argparse
import io
import json
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
import handoff

LIMIT = 24000
KINDS = ("snapshot", "transaction", "transfers")
NOTICE = "Checksums establish byte integrity, not chain truth, completeness, finality, or transaction validity."


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    return type(value) is int and value >= 0


def parse(data):
    require(len(data) <= LIMIT, "JSON input exceeds 24,000 bytes")
    def constant(value):
        raise ValueError("non-finite JSON number: " + value)
    result = json.loads(data, object_pairs_hook=handoff.unique_object,
                        parse_constant=constant)
    require(isinstance(result, dict), "expected a JSON object")
    return result


def describe(kind, data):
    """Check producer shape, not Ethereum semantics. Preserve input bytes exactly."""
    obj = parse(data)
    if kind == "snapshot":
        require(all(k in obj for k in ("captured_at", "endpoint", "method", "params", "result")),
                "snapshot lacks required producer fields")
        require(all(isinstance(obj[k], str) and obj[k] for k in ("captured_at", "endpoint", "method"))
                and isinstance(obj["params"], list), "invalid snapshot metadata")
        return {"method": obj["method"], "captured_at": obj["captured_at"]}
    if kind == "transaction":
        require(obj.get("type") == "EIP-1559" and obj.get("typeByte") == "0x02",
                "expected a decoded EIP-1559 summary")
        require(all(integer(obj.get(k)) for k in ("chainId", "nonce", "value", "gasLimit",
                                                  "maxFeePerGas", "maxPriorityFeePerGas")),
                "invalid transaction numeric fields")
        require("to" in obj and (obj["to"] is None or isinstance(obj["to"], str))
                and isinstance(obj.get("data"), str) and isinstance(obj.get("accessList"), list),
                "invalid transaction summary fields")
        return {"chain_id": obj["chainId"], "to": obj["to"]}
    if kind == "transfers":
        require(obj.get("read_only") is True and isinstance(obj.get("token_address"), str)
                and isinstance(obj.get("captured_at"), str), "invalid transfer metadata")
        require(all(integer(obj.get(k)) for k in ("from_block", "to_block", "head_at_capture",
                                                  "decimals", "transfer_count")),
                "invalid transfer numeric fields")
        require(obj["from_block"] <= obj["to_block"] and obj["decimals"] <= 255,
                "invalid range or decimals")
        require(isinstance(obj.get("transfers"), list)
                and len(obj["transfers"]) == obj["transfer_count"], "transfer count mismatch")
        for event in obj["transfers"]:
            require(isinstance(event, dict) and integer(event.get("block"))
                    and obj["from_block"] <= event["block"] <= obj["to_block"],
                    "transfer outside declared range")
        return {"token_address": obj["token_address"], "from_block": obj["from_block"],
                "to_block": obj["to_block"], "transfer_count": obj["transfer_count"]}
    raise ValueError("unsupported evidence kind")


def build(inputs):
    require(inputs and set(inputs) <= set(KINDS), "supply at least one supported input")
    files, entries = {}, []
    for kind, data in sorted(inputs.items()):
        summary = describe(kind, data)
        name = "evidence/" + kind + ".json"
        files[name] = data
        entries.append({"kind": kind, "path": name, "sha256": handoff.digest(data),
                        "summary": summary})
    files["EVIDENCE.json"] = (json.dumps({"version": 1, "notice": NOTICE, "entries": entries},
                                        sort_keys=True, indent=2) + "\n").encode()
    packed = handoff.build(files)
    require(len(packed) < 100000, "bundle exceeds this workspace's file limit")
    return packed


def verify(data, expected=None):
    result = handoff.verify(data, expected)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        require("EVIDENCE.json" in archive.namelist(), "missing evidence index")
        index = parse(archive.read("EVIDENCE.json"))
        require(set(index) == {"version", "notice", "entries"}
                and type(index["version"]) is int and index["version"] == 1
                and index["notice"] == NOTICE and isinstance(index["entries"], list),
                "unsupported evidence index")
        require(1 <= len(index["entries"]) <= len(KINDS), "invalid evidence count")
        inputs = {}
        for entry in index["entries"]:
            require(isinstance(entry, dict) and set(entry) == {"kind", "path", "sha256", "summary"},
                    "invalid index entry")
            kind = entry["kind"]
            require(isinstance(kind, str) and kind in KINDS and kind not in inputs,
                    "invalid or duplicate evidence kind")
            require(entry["path"] == "evidence/" + kind + ".json", "invalid evidence path")
            payload = archive.read(entry["path"])
            require(entry["sha256"] == handoff.digest(payload)
                    and entry["summary"] == describe(kind, payload), "index differs from evidence")
            inputs[kind] = payload
        require(set(archive.namelist()) == {"HANDOFF.json", "EVIDENCE.json"}
                | {"evidence/" + k + ".json" for k in inputs}, "unexpected bundle entries")
    result.update(kinds=sorted(inputs), notice=NOTICE)
    return result


def read_input(raw):
    return handoff.regular_bytes(handoff.workspace_path(raw), LIMIT)


def demo():
    folder = Path(__file__).absolute().parent.relative_to(Path.cwd()) / "examples"
    inputs = {kind: read_input(str(folder / (kind + ".json"))) for kind in KINDS}
    packed = build(inputs)
    require(packed == build(dict(reversed(list(inputs.items())))), "non-deterministic archive")
    result = verify(packed, handoff.digest(packed))
    result["deterministic"] = True
    result["example_data"] = "Recorded public ZTO reads and a synthetic unsigned decoder demonstration."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="verify recorded examples in memory, entirely offline")
    pack = commands.add_parser("pack", help="package explicitly selected public JSON files")
    pack.add_argument("output", help="new relative workspace ZIP path")
    for kind in KINDS:
        pack.add_argument("--" + kind, help="public " + kind + " JSON file")
    check = commands.add_parser("verify", help="verify without extraction or execution")
    check.add_argument("archive")
    check.add_argument("--sha256", help="archive digest received through a trusted channel")
    args = parser.parse_args()
    try:
        if args.command == "demo":
            result = demo()
        elif args.command == "pack":
            output = handoff.workspace_path(args.output, must_exist=False)
            inputs = {kind: read_input(getattr(args, kind)) for kind in KINDS if getattr(args, kind)}
            data = build(inputs)
            result = verify(data)
            with output.open("xb") as handle:
                handle.write(data)
            result["output"] = args.output
        else:
            data = handoff.regular_bytes(handoff.workspace_path(args.archive), 100000)
            result = verify(data, args.sha256)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, KeyError, zipfile.BadZipFile,
            UnicodeError, RecursionError, NotImplementedError) as exc:
        print("evidence-handoff: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
