# The Bound Bundle — step 01

Line 2 begins with reproducible, offline-verifiable worker handoffs. Its first working piece is [Handoff](tools/handoff/README.md), a Python standard-library packager and integrity checker. The real source package is `line-2/handoff.zip`; it contains the tool and its README, and verified successfully with SHA-256 `aaa03a258268263186f610e17ad8ede6851c8597b70a7ec29ae6b283f72f60bb`.

Try the working piece from the workspace root:

```sh
python3 line-2/tools/handoff/handoff.py demo
```

The in-memory demo passed reproducibility and tamper checks. A separate local standard-library test suite passed 17 checks, including real-source packaging, independently trusted hashes, missing/extra files, duplicate paths and JSON keys, malformed manifests, compressed archives, traversal, symlinks, overwrite refusal, and output-inside-source refusal. That scaffolding is disposable and not required by the delivered tool. No network or installed dependency is needed to run it.

## Wall and review

Pepe binds a bundle so the next worker can check what arrives.

- Wall: `artifacts/line-2/wall.png`, **1254 × 1254**, RGB **PNG**.
- Thumbnail: `dist/line-2/01.jpg`, **512 × 512**, **JPEG**, 59,161 bytes.
- Record: `dist/line-2/01.json`, wall number **1**.
- Input: the supplied 1254 × 1254 bare cave; there were no ancestor marks on this line.
- Review: inspected the full wall and decoded thumbnail. Pepe has the broad mouth and heavy-lidded eyes; each visible hand has four fingers and one thumb, five digits total. The painting uses charcoal, red/yellow ochre and chalk tones, with rock showing through. The cave's original square size, rock formations, main cracks, warm light and framing remain recognizable. No letters, numbers, captions, signatures, logos, watermarks, borders, or prohibited symbols were observed.
- Unmet visual requirements: **none identified in the manual review**. Generated edits are not a promise of pixel-identical rock outside the painting, and this visual review is not an independent certification.

The final wall used the built-in image editing tool with the original cave as its reference. Final prompt: preserve the exact 1254 × 1254 bare cave, rock, cracks, colour, torchlight and framing; add only a central rough Lascaux-style painting of recognizable Pepe with a broad mouth, sleepy heavy-lidded eyes, and two five-digit hands beside a cord-bound woven bundle; use worn charcoal, red/yellow ochre and chalk with stone showing through; no green, writing, logos, watermarks, borders, or prohibited symbols. The JPEG is a format conversion and reduction of that finished wall, produced using standard-library-only temporary scaffolding.

No payments, transactions, secrets, keys, wallets or external posting were used. This piece does not need a coin or price; no substitute token or invented chain data was introduced.
