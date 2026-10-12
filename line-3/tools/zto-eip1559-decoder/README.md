# ZTO EIP-1559 Decoder

`tx_decode.py` turns an unsigned type-2 Ethereum transaction into readable JSON without using a network, wallet, key, environment variable, or filesystem input. It strictly parses canonical RLP, validates the nine signing-payload fields and access list, and reports fee fields, value, destination and calldata selector. It never signs, sends, or prepares a transaction for broadcast.

The built-in demonstration is an unsigned, zero-value `totalSupply()` call to ZTO's real Ethereum contract (`0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`). It is an inspection sample only, not something to send.

## Try it

```sh
python3 line-3/tools/zto-eip1559-decoder/tx_decode.py --demo
```

I ran that command locally. It printed a decoded EIP-1559 envelope with `chainId` 1, ZTO as `to`, gas limit 100000, empty access list, and calldata selector `0x18160ddd`. A local negative check also confirmed that a legacy envelope and a non-canonical RLP integer are rejected.

The accompanying wall is `artifacts/line-3/wall.png`: a 1254×1254 RGB PNG. Its 512×512 JPEG copy is `dist/line-3/01.jpg`. It preserves the bare cave's rock texture, light, square composition and stone framing; it adds an earth-pigment Pepe inspecting an unlettered scroll. Visual review found no letters, numbers, captions, logos, watermarks, borders, frames, real people, political or hateful symbols, photographs, or 3D-render effects. Pepe's broad mouth and heavy-lidded eyes are visible; both visible hands were reviewed as five-digit hands (four fingers and a thumb). No visual requirements are knowingly unmet.
