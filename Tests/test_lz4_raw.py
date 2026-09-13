import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Tools"))
from decode_lz4_raw import LZ4DecodeError, decode_lz4_raw  # noqa: E402


class LZ4RawTests(unittest.TestCase):
    def test_literal_only_block(self):
        self.assertEqual(decode_lz4_raw(bytes([0x50]) + b"hello"), b"hello")

    def test_overlapping_match(self):
        # One literal followed by a six-byte overlapping match at offset one.
        self.assertEqual(decode_lz4_raw(bytes([0x12, ord("a"), 1, 0])), b"a" * 7)

    def test_known_physics_pair_and_expected_size(self):
        self.assertEqual(
            decode_lz4_raw(bytes.fromhex("40 00 00 00 00"), expected_size=4),
            b"\x00" * 4,
        )

    def test_invalid_offset_is_rejected(self):
        with self.assertRaises(LZ4DecodeError):
            decode_lz4_raw(bytes([0x00, 1, 0]))


if __name__ == "__main__":
    unittest.main()
