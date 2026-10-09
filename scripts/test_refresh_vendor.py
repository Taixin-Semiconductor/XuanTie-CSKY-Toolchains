#!/usr/bin/env python3
"""Existing archive outputs must survive refused rebuilds."""
import runpy
from pathlib import Path
import tempfile
import unittest

VENDOR = runpy.run_path(str(Path(__file__).with_name("refresh-elfuse-vendor.py")))

class ArchiveOutputCollisionTests(unittest.TestCase):
    def test_existing_archive_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "tree" / "csky-elfabiv2-macos-arm64-elfuse"
            root.mkdir(parents=True)
            (root / "payload.txt").write_text("package source", encoding="utf-8")
            archive = base / "source-and-output.tar.xz"
            original = b"immutable source archive bytes"
            archive.write_bytes(original)
            with self.assertRaises(VENDOR["PackageError"]):
                VENDOR["create_archive"](root, archive)
            self.assertEqual(archive.read_bytes(), original)

if __name__ == "__main__":
    unittest.main()
