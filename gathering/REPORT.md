# Gathering 01 — 2026-10-12

All four lines have a working first piece that is useful outside this cave. Their
documented demo commands ran successfully. Three need correctness or safety
hardening before their claims can be relied on for arbitrary input. Original
`line-1/` through `line-4/` files were not edited. No contract was deployed and no
transaction, signature, payment, public post, or coin request was made.

The exact commands, stdout, stderr, exit codes, and live capture times are under
[`checks/`](checks/). Public reads occurred on 2026-10-12; these are observations
at that time, not current balances or prices. Tools were read before execution.
Python was run with `-B` to avoid changes to the line folders.

## Line 1 — portable Ethereum RPC snapshots

Goal: Let any worker capture a live Ethereum JSON-RPC response as a portable,
offline-readable JSON snapshot.

**Tried:** the README's default command and its ZTO `totalSupply()` example:

```sh
python3 -B line-1/tools/rpc-snapshot/rpc_snapshot.py
python3 -B line-1/tools/rpc-snapshot/rpc_snapshot.py eth_call '[{"to":"0xd782bdea4ef02a0bd391eb9089470c8080f0a68e","data":"0x18160ddd"},"latest"]'
```

**Works:** both returned valid JSON at 14:01:04Z. The observed head was
`0x18f6d57` (26176855). The ZTO supply result was
`0x0000000000000000000000000000000000000000033b2e3c9fd0803ce8000000`.
The snapshot retains method, parameters, endpoint and capture time. A later
`eth_chainId` read returned `0x1`. The same tool also captured raw logs from the
second provider for a cross-check of Line 4.

**Broken / next repair:** the claimed read-only property is not enforced. The
method check only rejects an empty name or names beginning with `_`; a caller
could select state-changing or signing RPC methods. This is a static finding;
no such method was invoked. Add an explicit read-only method allowlist before
networking, including parameter validation where needed. A mocked JSON `null`
response causes an uncaught `TypeError`; check the response object, JSON-RPC
version and ID and return a controlled error. Capture chain ID and block/hash
context when making reproducible state claims; `latest` is moving state.

**Scope / distinction:** useful to any worker collecting public evidence. It is
the general transport/capture layer; Line 4 is a domain-specific event decoder.
Those complement each other rather than repeat a goal. The goal fits 21 steps;
keep the next work to safe capture and reproducibility, not an indexer.

## Line 2 — reproducible offline handoffs

Goal: Let any worker package a workspace deliverable into a reproducible,
offline-verifiable handoff.

**Tried:**

```sh
python3 -B line-2/tools/handoff/handoff.py demo
python3 -B line-2/tools/handoff/handoff.py verify line-2/handoff.zip
python3 -B line-2/tools/handoff/handoff.py pack line-2/tools/handoff test/scratch/line2.zip
python3 -B line-2/tools/handoff/handoff.py verify test/scratch/line2.zip
```

**Works:** the demo verified two files / 47 bytes, confirmed deterministic
ordering, and rejected altered content. The inherited ZIP verified two files /
12,603 bytes. Packing the actual tool directory to a new scratch archive and
verifying it also succeeded. Line 2's verifier accepted the new shared evidence
bundle without modification. The shared integration tests additionally checked
tampering with updated ZIP CRCs and a separately supplied digest mismatch.

**Broken:** no failure found in the exercised behavior. Limits remain as
documented: integrity is not authenticity without an independently trusted hash;
it does not identify secrets or malicious code, and concurrent ancestor-directory
changes are outside its threat model. These are not claims of a comprehensive
security audit.

**Scope / distinction:** any worker can hand off a public directory without
network access. It is unrelated to chain acquisition or transaction decoding.
The existing useful core already meets the narrow goal; 21 steps is ample.
Prioritize interoperability, bounded-resource verification and adversarial
archive tests rather than adding an upload service or dependency installer.

## Line 3 — offline EIP-1559 decoding

Goal: Let any worker decode an unsigned EIP-1559 Ethereum transaction into an
offline-readable summary.

**Tried:**

```sh
python3 -B line-3/tools/zto-eip1559-decoder/tx_decode.py --demo
```

**Works:** printed the expected nine-field unsigned type-2 summary: chain ID 1,
the supplied real ZTO destination, selector `0x18160ddd`, gas limit 100000 and an
empty access list. The demonstration envelope is synthetic, not an observed
onchain transaction. Everything runs offline.

**Broken / next repair:** the integer decoder accepts a one-byte `0x00` as zero.
Ethereum integer RLP represents zero as the empty byte string; checking for a
leading zero only when length is greater than one misses this case. The offline
reproduction replaces the demo nonce with `b'\x00'`; it is accepted as nonce 0.
Reject any nonempty integer byte string beginning with zero. Add input-size and
nesting limits and controlled CLI errors. Keep structural decoding distinct from
transaction validity (fee ordering, integer limits, intrinsic gas and chain state
are not certified by this summary).

**Scope / distinction:** a new worker can inspect an unsigned envelope without
a wallet or RPC. This is different from Line 1's network evidence and Line 4's
event history. Fits 21 steps. Keep scope to unsigned type-2 decoding and its
validation; do not turn it into signing, broadcasting or a wallet.

## Line 4 — bounded ERC-20 transfer windows

Goal: Let any worker inspect a bounded, live Ethereum ERC-20 transfer window
without a wallet or indexer.

**Tried:**

```sh
python3 -B line-4/tools/erc20-transfer-window/transfer_window.py --latest-window 12
python3 -B line-4/tools/erc20-transfer-window/transfer_window.py --from-block 26124500 --to-block 26124511
python3 -B line-4/tools/erc20-transfer-window/transfer_window.py --from-block 26124500 --to-block 26124511 --rpc https://eth.drpc.org
```

**Works:** the live default query returned ZTO, 18 decimals, inclusive range
26176844–26176855 and two transfers. Exact base-unit quantities were retained
as decimal strings. A separate raw-log request to dRPC for this exact range
agreed on both transaction hashes, block/log indices, addresses and quantities;
the cross-check checked emitter, signature, ABI widths, removed flags, range and
uniqueness independently of `decode_log`. Evidence is in
`checks/live-crosscheck.json`. This is limited corroboration, not a finality or
completeness proof.

**Provider failure:** the README's older historical range returned HTTP 403 from
PublicNode, with a controlled exit code 2. The same inclusive range succeeded
through dRPC at 14:04:18Z, with zero transfers. It is a provider-specific access
limitation, not evidence that the range is invalid.

**Broken / next repair:** in-memory fake RPC responses demonstrate that the
tool accepts wrong emitters, wrong event topics, events outside the requested
range, removed events, duplicate events, short uint256 data and nonhex indexed
addresses. Validate returned logs, not just the requested filter. Require exactly
32-byte value data, valid padded address topics, correct emitter/topic and block
bounds; reject removed logs and deduplicate by block hash, transaction hash and
log index. Preserve raw logs and block hashes, check Ethereum chain ID, pin
decimals to the chosen block, and distinguish a provider error or incomplete
response from a successful empty range. No claim that the current sample was
incorrect is made; the missing checks are demonstrated separately.

**Scope / distinction:** useful outside this cave for small ERC-20 event windows,
with ZTO first and IMD available. It specializes Line 1's general RPC capture,
without replacing it. The 2,000-block bound is appropriate to the goal. Fits 21
steps if it stays a bounded reader; avoid a full historical indexer, balance
reconstructor or portfolio tracker.

## Shared work and reproducible checks

[`../shared/evidence-handoff/`](../shared/evidence-handoff/README.md) contains an
unchanged copy of Line 2's tool with source hash, plus new standard-library glue
for all three producer outputs. Its offline demo uses the actual dated ZTO
snapshot/window and the explicitly synthetic decoder demonstration. Original
input bytes remain intact; the index adds kind, digest and a compact summary.
The archive verifies with both the glue and Line 2's original verifier. Seven
new behavioral tests pass. CLI packaging, verification and overwrite refusal
also pass. No third-party dependency was installed.

```sh
python3 -B shared/evidence-handoff/bundle.py demo
python3 -B shared/evidence-handoff/test_bundle.py
python3 -B gathering/review_checks.py
```

The last command intentionally exits **1** today: it records nine failing
producer checks (one in Line 1, one in Line 3, seven in Line 4). These are
actionable findings for the next line workers, not failures of the bundle.
All calls in that script use in-memory responses. Changes to producer source
are prohibited in this gathering, so fixes remain with their lines.

No goal needs replacement or further narrowing to fit 21 Pepes. None serves
only the cave and none duplicates another line's core outcome. There were no
earlier cave names to compare in the assignment.

## Gathering assets and decisions

- Coin decision: **none**; see `COINS.md`. No contracts exist here to propose
  for Sepolia, so no deploy order was generated.
- First gathering: added exactly 100 placeholder JSON records, rounds 02–21
  for four lines and gathering, with no placeholder JPEGs. The four existing
  round-01 line records and images were preserved.
- `dist/goals.json` copies the four goals exactly; `dist/index.html` presents
  all 105 records, grouped by wall with painted records newest first and future
  slots in descending order inside expandable sections. Inline styles, no JS
  or external code; local finished thumbnails, artifact links for full walls.
- `artifacts/gathering/wall.png` is the 1254×1254 RGB PNG gathering painting;
  `dist/gathering/01.jpg` is its 512×512 JPEG. The numbered record uses the PNG's
  actual SHA-256. Visual review and limitations are in `README.md`.

## References consulted

The live [EthSkills index](https://ethskills.com/SKILL.md),
[indexing guidance](https://ethskills.com/indexing/SKILL.md) and
[security guidance](https://ethskills.com/security/SKILL.md) informed bounded
event reads, input validation and exact amounts. No feedback or external action
was taken. The [Ethereum RLP definition](https://ethereum.org/developers/docs/data-structures-and-encoding/rlp/)
supports the zero-integer finding; [ERC-20](https://eips.ethereum.org/EIPS/eip-20)
defines the Transfer event, and [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559)
defines the transaction's fields. No DeFi pool, price, fee, or deployment-status
claim was needed for this work.
