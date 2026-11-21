#!/usr/bin/env python3
"""The Poster for a Place That Isn't There — Kestrel.

Delivers the vintage travel poster for Kestrel, a country that does
not exist: a low sun over a still lake, three mountain ridges, pine
silhouettes, and the promise that the sky keeps. The same imaginary
country as the "Passport of Kestrel" entry, so the two form one world.

The poster image is rendered once, during development, from the
deterministic Pillow generator that lives in this repository's git
history (drawn from seeded coordinates, a fixed palette, no network
and no clock), and committed here as entry.png. This entrypoint is
stdlib-only: it copies that committed image to the output directory
and verifies it, so it runs cleanly in any plain Python 3 image with
no third-party packages installed.
"""
import hashlib
import os
import shutil
import struct
import sys

BYTE_LIMIT = 1_048_576
EXPECTED_DIMS = (1024, 1024)


def png_dimensions(path):
    """Read a PNG's dimensions from its IHDR chunk (stdlib only)."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    if header[12:16] != b"IHDR":
        raise ValueError("missing IHDR chunk")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(out_dir, "entry.png")

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(source, target)

    # Read it back and verify the exact output before reporting success,
    # so a wrong size or an oversized file can never pass silently.
    size = os.path.getsize(target)
    dims = png_dimensions(target)
    if dims != EXPECTED_DIMS:
        print(f"bad dimensions: {dims}", file=sys.stderr)
        return 1
    if size > BYTE_LIMIT:
        print(f"too big: {size} bytes > {BYTE_LIMIT}", file=sys.stderr)
        return 1
    with open(target, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()[:16]
    print(f"entry.png {dims[0]}x{dims[1]} {size} bytes sha256:{digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
