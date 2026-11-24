"""Regression coverage for missing icon references and broken ZIP assets."""

import copy
import io
import json
from pathlib import Path
import struct
import unittest
from zipfile import ZipFile
import zlib

from branding_assets import branding_files, ICON_FIELDS

ROOT = Path(__file__).resolve().parent.parent


class BrandingAssetsTest(unittest.TestCase):
    def setUp(self):
        self.interface = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())["interface"]
        self.png = (ROOT / "assets/logo.png").read_bytes()
        self.assets = {"assets/logo.png": self.png}

    def test_all_four_slots_resolve_to_packaged_official_logo(self):
        result = branding_files(self.interface, self.assets.__getitem__)
        self.assertEqual(result, self.assets)
        self.assertEqual({self.interface[key] for key in ICON_FIELDS}, {"./assets/logo.png"})

    def test_missing_field_cannot_silently_fall_back_to_generic_icon(self):
        for key in ICON_FIELDS:
            with self.subTest(key=key):
                interface = copy.deepcopy(self.interface)
                del interface[key]
                with self.assertRaisesRegex(ValueError, key):
                    branding_files(interface, self.assets.__getitem__)

    def test_rejects_unbundled_and_external_paths(self):
        for path in ["./assets/missing.png", "https://example.com/icon.png", "./../icon.png", "./C:\\icon.png"]:
            with self.subTest(path=path):
                interface = {**self.interface, "logo": path}
                with self.assertRaises(ValueError):
                    branding_files(interface, self.assets.__getitem__)

    def test_rejects_non_images_truncation_and_bad_headers(self):
        for data in [b"<html>Not found</html>", self.png[:-12], self.png[:29] + b"bad!" + self.png[33:]]:
            with self.subTest(size=len(data)):
                with self.assertRaises(ValueError):
                    branding_files(self.interface, lambda _: data)

    def test_rejects_undersized_non_square_and_oversized_icons(self):
        for width, height in [(16, 16), (200, 100), (5000, 5000)]:
            with self.subTest(size=(width, height)):
                data = bytearray(self.png)
                data[16:24] = struct.pack(">II", width, height)
                data[29:33] = struct.pack(">I", zlib.crc32(data[12:29]))
                with self.assertRaisesRegex(ValueError, "48–4096"):
                    branding_files(self.interface, lambda _: bytes(data))

    def test_actual_zip_lookup_detects_missing_asset(self):
        buffer = io.BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr(".codex-plugin/plugin.json", "{}")
        with ZipFile(buffer) as archive:
            with self.assertRaisesRegex(ValueError, "missing packaged asset"):
                branding_files(self.interface, archive.read)

    def test_actual_zip_roundtrip_preserves_asset_bytes(self):
        buffer = io.BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr("assets/logo.png", self.png)
        with ZipFile(buffer) as archive:
            self.assertEqual(branding_files(self.interface, archive.read), self.assets)


if __name__ == "__main__":
    unittest.main()
