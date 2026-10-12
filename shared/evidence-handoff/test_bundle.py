"""Offline behavioral checks. Run: python3 -B shared/evidence-handoff/test_bundle.py"""
import io
import json
from pathlib import Path
import sys
import unittest
import zipfile

sys.dont_write_bytecode = True
import bundle
import handoff


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).parent / "examples"
        self.inputs = {k: (root / (k + ".json")).read_bytes() for k in bundle.KINDS}

    def test_reproducible_and_exact(self):
        data = bundle.build(self.inputs)
        self.assertEqual(data, bundle.build(dict(reversed(list(self.inputs.items())))))
        self.assertTrue(bundle.verify(data, handoff.digest(data))["verified"])
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for kind, payload in self.inputs.items():
                self.assertEqual(payload, archive.read("evidence/" + kind + ".json"))

    def test_changed_payload_with_updated_crc(self):
        data = bundle.build(self.inputs)
        changed = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(data)) as src, zipfile.ZipFile(changed, "w") as dst:
            for entry in src.infolist():
                payload = src.read(entry.filename)
                if entry.filename == "evidence/snapshot.json":
                    payload += b" "
                dst.writestr(entry, payload)
        with self.assertRaises(ValueError):
            bundle.verify(changed.getvalue())

    def test_index_checked_even_after_rehash(self):
        data = bundle.build(self.inputs)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            files = {n: archive.read(n) for n in archive.namelist() if n != "HANDOFF.json"}
        index = json.loads(files["EVIDENCE.json"])
        index["entries"][0]["summary"] = {}
        files["EVIDENCE.json"] = json.dumps(index).encode()
        with self.assertRaises(ValueError):
            bundle.verify(handoff.build(files))

    def test_trusted_digest_mismatch(self):
        with self.assertRaises(ValueError):
            bundle.verify(bundle.build(self.inputs), handoff.digest(b"different bytes"))

    def test_shape_and_limits(self):
        for bad in (b"[]", b'{"method":1,"method":2}', b'{"result":NaN}', b" "*24001):
            with self.subTest(data=bad[:50]), self.assertRaises(ValueError):
                bundle.build({"snapshot": bad})
        with self.assertRaises(ValueError):
            bundle.build({})
        with self.assertRaises(ValueError):
            bundle.build({"unsupported": b"{}"})
        bad = json.loads(self.inputs["transfers"])
        bad["transfer_count"] += 1
        with self.assertRaises(ValueError):
            bundle.build({"transfers": json.dumps(bad).encode()})

    def test_paths_stay_in_workspace(self):
        for path in ("../outside.json", "/outside.json"):
            with self.assertRaises(ValueError):
                bundle.read_input(path)

    def test_individual_inputs_supported(self):
        for kind, data in self.inputs.items():
            self.assertEqual(bundle.verify(bundle.build({kind: data}))["kinds"], [kind])


if __name__ == "__main__":
    unittest.main()
