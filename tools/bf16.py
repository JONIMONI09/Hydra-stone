"""BF16 decoding — the one implementation (R12).

WHY THIS MODULE EXISTS
    Both converters decode BF16 tensors and each had its own copy:
    `tools/gguf_reader.py` widened with slice assignment and returned an
    `array('f')`; `tools/safetensors_to_hydra.py` widened value by value with
    `struct` and returned a list. Two copies of one conversion rule are two
    future bugs (R12), and a BF16 bug would show up in one import path but not
    the other.

    Before merging them, both were compared against EACH OTHER and against an
    independent reference (R9), over the complete 16-bit input space:
    65536 patterns, 0 mismatches, 0 mismatches against
    `struct.unpack('<f', struct.pack('<I', h << 16))` for every non-NaN
    pattern (254 NaN patterns were excluded from the payload comparison
    because a float32 NaN does not survive a round trip through a Python
    float). Run 2026-10-29; the same comparison is what `tools/gguf_test.py`
    gates indirectly through both readers.

WHAT BF16 IS
    BF16 is the top 16 bits of an IEEE-754 binary32 value: sign, 8 exponent
    bits, 7 mantissa bits. Widening it is a pure bit move, so BF16 can
    represent the full float32 exponent range with reduced precision — no
    rounding is involved and none is performed here.
"""

import sys
from array import array

_LITTLE = sys.byteorder == 'little'


def decode_bf16(raw, n):
    """Decode `n` little-endian BF16 values from `raw` into an `array('f')`.

    Slice assignment rather than a Python loop on purpose: a 4096x4096 tensor
    is 16.7 M values, and a per-value loop takes seconds where this takes
    milliseconds. `array('f')` is a real float32 buffer, so the values are
    bit-exact float32, not Python doubles that merely look right.
    """
    if len(raw) != 2 * n:
        raise ValueError('BF16 payload is %d bytes, expected %d' % (len(raw), 2 * n))
    halves = array('H')
    halves.frombytes(raw)
    if not _LITTLE:
        halves.byteswap()
    wide = bytearray(4 * n)
    view = memoryview(wide)
    low = halves.tobytes()
    view[0::4] = bytes(n)
    view[1::4] = bytes(n)
    view[2::4] = low[0::2]
    view[3::4] = low[1::2]
    view.release()
    out = array('f')
    out.frombytes(wide)
    if not _LITTLE:
        out.byteswap()
    return out
