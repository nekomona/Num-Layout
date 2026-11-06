"""Tests for deterministic release archive packaging."""

from hashlib import sha1
from pathlib import Path
import tarfile
import tempfile
import unittest

from tools.package_release import package, release_slug


class ReleasePackageTests(unittest.TestCase):
    def test_archive_contains_only_runtime_tree_and_checksum_matches(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "nlayout"
            (source / "icons").mkdir(parents=True)
            (source / "__pycache__").mkdir()
            (source / "numeric_assist.il").write_text("skill\n", encoding="utf-8")
            (source / "wire_refresh.py").write_text("helper\n", encoding="utf-8")
            (source / "icons" / "tool.png").write_bytes(b"png")
            (source / "__pycache__" / "ignored.pyc").write_bytes(b"cache")

            first_archive, first_checksum = package(source, "v1.2.3", root / "out")
            first_bytes = first_archive.read_bytes()
            second_archive, second_checksum = package(source, "v1.2.3", root / "out")

            self.assertEqual(first_bytes, second_archive.read_bytes())
            self.assertEqual(first_checksum.read_text(encoding="ascii"),
                             f"{sha1(first_bytes).hexdigest()}  {first_archive.name}\n")
            self.assertEqual(first_checksum.read_text(encoding="ascii"), second_checksum.read_text(encoding="ascii"))
            with tarfile.open(first_archive, "r:gz") as bundle:
                names = bundle.getnames()
            self.assertEqual(
                names,
                ["nlayout", "nlayout/icons", "nlayout/icons/tool.png",
                 "nlayout/numeric_assist.il", "nlayout/wire_refresh.py"],
            )
            self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))
            environment = (root / "out" / "release.env").read_text(encoding="ascii")
            self.assertIn("ARCHIVE_FILE=nlayout-v1.2.3.tar.gz", environment)
            self.assertIn("CHECKSUM_FILE=nlayout-v1.2.3.tar.gz.sha1", environment)

    def test_release_slug_sanitizes_tag(self):
        self.assertEqual(release_slug("release/v1.0.0"), "release-v1.0.0")
        self.assertEqual(release_slug(" v2.1 "), "v2.1")


if __name__ == "__main__":
    unittest.main()
