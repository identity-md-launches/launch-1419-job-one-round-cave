# Four Stones, One Bundle

Pepe gathers four stones into one bundle for the next worker to carry.

This is Gathering 01, the first gathering in the supplied cave. The mark joins
the four lines' useful work: a snapshot, a handoff, a decoded envelope and an
event window. The shared piece is **Evidence handoff**.

## Deliverables

- `artifacts/gathering/wall.png`: 1254 × 1254, PNG, 8-bit RGB.
- `dist/gathering/01.jpg`: 512 × 512, baseline color JPEG, 66,802 bytes.
- `dist/gathering/01.json`: numbered record, image URL derived from the actual
  wall file's SHA-256: `483850c1c8e4755f593362cc72176b8cc0accd652095574f3880fdbb6c847959`.
- `REPORT.md`: line-by-line trial results and actionable defects.
- `COINS.md`: no new coin required.
- `shared/evidence-handoff/`: independent offline Python tool and examples.
- `dist/index.html` and `dist/goals.json`: every record and the four exact goals.

## Visual review

The bare cave was the supplied `.imd/reads/artifacts/cave`, with SHA-256
`9cbb7bb2a41efa92e010921f287819c9ffb02c4375fa9496c8468701d8e00cc5`.
There was no earlier gathering record or painting to preserve. The built-in
imagegen tool edited that cave, followed by a targeted correction to make the
hands individually countable. Only the final wall and its required JPEG were
saved as new pictures in the workspace.

I inspected the full-size generated wall and the actual finished JPEG. The
square size, rock layout, major cracks, warm torchlight and framing remain.
Pepe has a broad mouth and heavy-lidded eyes, painted in worn charcoal, ochre
and chalk tones with the rock showing through. Each visible hand has **four
fingers and one thumb**; no handprints appear. No letters, numbers, captions,
signatures, logos, watermarks, artificial frames, real people, or political or
hateful symbols were observed. The added figure is flat cave pigment.

Unmet visual requirements: **none identified on visual inspection**. Limitation:
the generative edit slightly softens the stone's fine texture; preservation is
visual, not pixel-for-pixel identity. This review is a human-readable observation,
not an automated certification of artwork quality.

The JPEG is a reduction of the actual wall, not a separate generated composition.
`make_thumbnail.py` performs the required format conversion using only Python's
standard library; no Pillow or other package was installed. It supports the
specific noninterlaced 8-bit RGB/RGBA PNG format and writes a baseline 4:2:0 JPEG.

## Run and rebuild

From the repository root:

```sh
python3 -B shared/evidence-handoff/bundle.py demo
python3 -B shared/evidence-handoff/test_bundle.py
python3 -B gathering/build_gallery.py
python3 -B gathering/check_deliverable.py
```

To reproduce only the thumbnail: `python3 -B gathering/make_thumbnail.py`.
The gallery builder reads local records and goals; it does not repaint walls,
create placeholder rounds, or edit line source. It requires no network. Finished
previews load locally in the gallery; full walls and unpainted cave images use
the specified artifact URLs. The gallery was checked structurally; no browser
automation was available in this dependency-free environment.

`python3 -B gathering/review_checks.py` separately reproduces the nine known
producer failures and exits 1 until those are fixed by their respective lines.
It is not part of the passing deliverable-structure check.

The final image prompts are preserved in `IMAGE-PROMPTS.md` for provenance.
