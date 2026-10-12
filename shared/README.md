# Shared pieces

[`evidence-handoff/`](evidence-handoff/README.md) shares Line 2's deterministic
handoff utility and joins the public JSON outputs from Lines 1, 3 and 4 into one
offline-verifiable archive. It has no network or third-party dependencies.

```sh
python3 -B shared/evidence-handoff/bundle.py demo
```

The original line folders are unchanged. This is a reusable worker tool, not a
record viewer. The examples are dated ZTO observations plus an unsigned decoder
demo, with their different evidence status documented explicitly.
