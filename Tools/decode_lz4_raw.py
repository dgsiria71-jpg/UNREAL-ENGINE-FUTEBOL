"""Decode and verify raw LZ4 blocks used by recovered mobile config blobs.

The recovery packs store LZ4 *raw blocks* without a frame header.  This module
implements only the block format and deliberately requires an optional expected
size when the caller has one.  It never guesses a codec or silently accepts
trailing bytes.
"""
from __future__ import annotations

import argparse
from pathlib import Path


class LZ4DecodeError(ValueError):
    """Raised when a raw LZ4 block violates the format or bounds."""


def decode_lz4_raw(payload: bytes, *, expected_size: int | None = None) -> bytes:
    """Decode one standard LZ4 raw block.

    The last sequence may contain literals only.  Match copies are expanded
    byte-by-byte because overlap is part of the LZ4 format.  The decoder is
    bounded by the input and optional expected size so malformed recovery
    inputs cannot cause unbounded allocation.
    """
    source = memoryview(payload)
    src = 0
    output = bytearray()
    while src < len(source):
        token = int(source[src])
        src += 1

        literal_length = token >> 4
        if literal_length == 15:
            while True:
                if src >= len(source):
                    raise LZ4DecodeError("literal length extension is truncated")
                extension = int(source[src])
                src += 1
                literal_length += extension
                if extension != 255:
                    break

        literal_end = src + literal_length
        if literal_end > len(source):
            raise LZ4DecodeError("literal payload exceeds source length")
        output.extend(source[src:literal_end])
        src = literal_end

        # A final literal-only sequence is valid and has no match offset.
        if src == len(source):
            break
        if src + 2 > len(source):
            raise LZ4DecodeError("match offset is truncated")
        offset = int(source[src]) | (int(source[src + 1]) << 8)
        src += 2
        if offset == 0 or offset > len(output):
            raise LZ4DecodeError(
                f"invalid match offset {offset} for output length {len(output)}"
            )

        match_length = token & 0x0F
        if match_length == 15:
            while True:
                if src >= len(source):
                    raise LZ4DecodeError("match length extension is truncated")
                extension = int(source[src])
                src += 1
                match_length += extension
                if extension != 255:
                    break
        match_length += 4

        if expected_size is not None and len(output) + match_length > expected_size:
            raise LZ4DecodeError("decoded output exceeds expected size")
        for _ in range(match_length):
            output.append(output[-offset])

    if expected_size is not None and len(output) != expected_size:
        raise LZ4DecodeError(
            f"decoded size {len(output)} does not match expected size {expected_size}"
        )
    return bytes(output)


def verify_pair(compressed: Path, decoded: Path) -> tuple[bool, str]:
    expected = decoded.read_bytes()
    try:
        actual = decode_lz4_raw(compressed.read_bytes(), expected_size=len(expected))
    except LZ4DecodeError as exc:
        return False, f"{compressed.name}: {exc}"
    if actual != expected:
        return False, f"{compressed.name}: decoded bytes differ"
    return True, compressed.name


def verify_directories(compressed_dir: Path, decoded_dir: Path) -> int:
    pairs = sorted(compressed_dir.iterdir())
    failures: list[str] = []
    checked = 0
    for compressed in pairs:
        if not compressed.is_file():
            continue
        decoded = decoded_dir / f"{compressed.name}.bin"
        if not decoded.is_file():
            failures.append(f"{compressed.name}: missing decoded counterpart")
            continue
        checked += 1
        ok, message = verify_pair(compressed, decoded)
        if not ok:
            failures.append(message)
    if failures:
        print(f"LZ4_RAW_VERIFY: FAIL checked={checked} failures={len(failures)}")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print(f"LZ4_RAW_VERIFY: GREEN checked={checked}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="raw LZ4 input file")
    parser.add_argument("--output", type=Path, help="decoded output file")
    parser.add_argument("--expected-size", type=int)
    parser.add_argument("--compressed-dir", type=Path)
    parser.add_argument("--decoded-dir", type=Path)
    args = parser.parse_args()

    if args.compressed_dir or args.decoded_dir:
        if not args.compressed_dir or not args.decoded_dir:
            parser.error("--compressed-dir and --decoded-dir must be supplied together")
        return verify_directories(args.compressed_dir, args.decoded_dir)

    if not args.input or not args.output:
        parser.error("--input and --output are required unless verifying directories")
    decoded = decode_lz4_raw(args.input.read_bytes(), expected_size=args.expected_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(decoded)
    print(f"LZ4_RAW_DECODE: GREEN bytes={len(decoded)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
