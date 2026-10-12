# ERC-20 Transfer Window

`transfer_window.py` captures a bounded, ordered window of real Ethereum `Transfer` events for an ERC-20 without a wallet, key, indexer, transaction, or filesystem input. It uses only the Python standard library and makes read-only JSON-RPC requests with the dedicated User-Agent `Pepeolithic-ERC20-Transfer-Window/1.0 (read-only public data)`.

ZTO (`0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`) is the default token. `--token imd` selects IMD (`0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7`). The result includes the chain head seen at capture, the exact inclusive block range, the on-chain `decimals()` result, and every matching log in block/log-index order. Token quantities are reported both as exact integer base units and rendered decimal units.

## Try it

```sh
python3 line-4/tools/erc20-transfer-window/transfer_window.py --latest-window 12
```

I ran that command against the live default public endpoint. It returned a read-only JSON document for ZTO, including the endpoint, a 12-block inclusive range ending at the observed head, the contract's on-chain decimal count, and the matching transfer log count. The head, range, and events naturally change as Ethereum advances.

For an independently reproducible historical lookup, choose a bounded inclusive range (at most 2,000 blocks):

```sh
python3 line-4/tools/erc20-transfer-window/transfer_window.py --from-block 26124500 --to-block 26124511
```

The tool validates range limits before networking and rejects malformed RPC results rather than quietly guessing. It is a log window reader, not a balance calculator: it does not infer an address's full balance from a partial range. A public endpoint can rate-limit or retain limited historical logs; use `--rpc` to point at another public Ethereum JSON-RPC endpoint when necessary.

## Wall asset

The accompanying finished wall is `artifacts/line-4/wall.png`, a 1254×1254 RGB PNG; `dist/line-4/01.jpg` is its 512×512 RGB JPEG copy. I visually reviewed both after generation. The added ochre, charcoal, and chalk cave figure is Pepe with his broad mouth and heavy-lidded eyes, studying an unlettered stone and nearby unlettered pebbles. The original rock, cracks, warm torchlight, and cave framing remain visible. Both visible hands were reviewed as five-digit hands (four fingers and a thumb). No letters, numbers, captions, signatures, logos, watermarks, artificial borders or frames, photographs, 3D renders, real people, political symbols, or hateful symbols are present. No visual requirements are knowingly unmet.
