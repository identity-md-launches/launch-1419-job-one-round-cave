# Handoff

Package a workspace directory as a deterministic ZIP containing a SHA-256 manifest. Another worker can verify every file offline without extracting or executing anything. Python 3.8+ and its standard library are sufficient; no installation, network, configuration, wallets, or environment-variable access is needed.

Run this from the workspace root to see reproducibility and rejection of altered content:

```sh
python3 line-2/tools/handoff/handoff.py demo
```

The demo runs entirely in memory. When tried, it verified two files (47 bytes), produced identical archive bytes despite reversed input order, and rejected a changed `hello.py` even when the ZIP's CRC was updated. Its archive SHA-256 was `c4c6347ac82b95216670f9bbf88a8d2e9ff741721dd35d6113d8c25d0dddc524`.

For a real handoff, select a directory of public deliverables only, then run:

```sh
python3 line-2/tools/handoff/handoff.py pack line-2/tools/handoff line-2/handoff.zip
python3 line-2/tools/handoff/handoff.py verify line-2/handoff.zip
```

The output must be a new file outside the source directory. Packing refuses to overwrite existing files. All user paths must be relative to the current workspace and must not contain `..` or symlinks. Source files must be regular files; empty directories, executable permissions and timestamps are not preserved. Archives use sorted paths, fixed timestamps, fixed permissions and uncompressed entries for reproducibility across Python installations. The reserved root filename `HANDOFF.json` cannot be a source file. Limits are 1,000 payload files and 64 MiB of payload.

Verification rejects duplicate paths, traversal names, unlisted files, missing files, unsupported manifest versions, mismatched lengths/hashes, compressed entries, encrypted entries and nonregular entries. No extraction command exists. Do not package credentials, wallets, keys, environment files, or confidential material. This utility packages only the directory explicitly selected by the user and cannot determine whether arbitrary file content is sensitive. Work in a stable directory: concurrent changes to ancestor directories are outside this first version's threat model.

A manifest alone detects corruption; an attacker can replace both content and its manifest. To detect that, obtain the package hash separately from a trusted source and pass it with `verify ARCHIVE --sha256 HASH`. This is an integrity checker, not a signer, malware scanner, dependency resolver, or proof that code works.

Local checks also exercised a real package of this tool and failures for tampered content, extra/missing entries, duplicate JSON keys, unsafe paths, symlinks, incorrect trusted hashes and overwrite attempts. The shipped tool requires no files from the temporary test scaffolding.
