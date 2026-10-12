# Evidence handoff

Give another worker a reproducible, offline-verifiable bundle of public Ethereum
JSON outputs. This joins Line 1's RPC snapshots, Line 3's decoded transaction
summaries, and Line 4's transfer windows using Line 2's handoff format.
Python 3.8+ and the standard library are sufficient. No installation or network
is needed. Copy this entire folder to another workspace to use it independently.

From the workspace root, one command demonstrates the complete integration:

```sh
python3 -B shared/evidence-handoff/bundle.py demo
```

The demo reads the three explicitly named public files in `examples/`, builds a
ZIP in memory, verifies its SHA-256 manifest and evidence index, and confirms
identical bytes when input ordering is reversed. On 2026-10-12 it verified four
payload files, 2,771 bytes, with archive SHA-256
`6463156697c45336dfdcab056ae939d33a5e18ba0af644dfb1bef2f6d395df68`.
No archive is written by the demo.

To make a real package, use a new output filename and explicitly select public
JSON inputs. Any nonempty subset of the three kinds works:

```sh
python3 -B shared/evidence-handoff/bundle.py pack shared/zto-evidence.zip --snapshot shared/evidence-handoff/examples/snapshot.json --transaction shared/evidence-handoff/examples/transaction.json --transfers shared/evidence-handoff/examples/transfers.json
python3 -B shared/evidence-handoff/bundle.py verify shared/zto-evidence.zip
python3 -B shared/evidence-handoff/test_bundle.py
```

Verification accepts `--sha256 DIGEST` when the actual archive digest is supplied
separately through a trusted channel. Do not use the example digest for a bundle
with changed inputs. The shared `handoff.py` can also verify these archives, or
package any explicitly selected directory using Line 2's `pack` command.

## What is checked

Input bytes are preserved exactly. Basic producer shapes, duplicate JSON keys,
non-finite numbers, input size, transfer count and declared transfer ranges are
checked. `EVIDENCE.json` gives each kind, payload path, digest and a small summary;
verification recomputes that summary. `HANDOFF.json` is the original Line 2 format.
Every input is at most 24,000 bytes; archives are below 100,000 bytes. Larger
windows must be deliberately split upstream. Paths must be relative to the
workspace, without `..` or symlinks. Existing outputs are never overwritten.
Archives are not extracted and contents are not executed.

Checksums do **not** establish chain truth, endpoint honesty, event completeness,
finality, signature validity, or transaction safety. A decoded summary does not
contain its original RLP and cannot prove its encoding. The transfer output lacks
raw logs and block hashes; this glue cannot restore those missing facts. It does
not combine samples into an atomic chain snapshot. Only package public evidence;
the utility cannot recognize secrets in arbitrary JSON. Work in a stable directory;
concurrent ancestor-path changes remain outside the inherited path threat model.

## Example provenance and reuse

- `snapshot.json`: exact stdout of Line 1's read-only ZTO `totalSupply()` request,
  captured at 2026-10-12T14:01:04Z from `https://ethereum-rpc.publicnode.com`.
- `transfers.json`: exact stdout of Line 4's 12-block ZTO window at the same capture
  second; inclusive blocks 26176844–26176855, 18 decimals, two matching events as
  reported by that tool. These are dated observations, not current balances.
- `transaction.json`: exact stdout of Line 3's `--demo`, an artificial unsigned
  envelope calling the supplied real ZTO address. It is not a transaction seen
  onchain, and no transaction was sent.
- `handoff.py`: copied byte for byte from `line-2/tools/handoff/handoff.py` in the
  first gathering. Its origin and digest are in `PROVENANCE.json`. Line 2's code
  remains authoritative; this copy makes shared use independent of line folders.

Seven offline tests cover reproducibility, exact-byte preservation, tampering
with repaired ZIP CRCs, a rehashed but inconsistent index, trusted-hash mismatch,
invalid shapes, unsafe paths, and single-input bundles. A CLI round trip and
overwrite rejection were also exercised during gathering. See the gathering
report for producer bugs; bundling does not repair producer semantics.
