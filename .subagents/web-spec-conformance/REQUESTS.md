# Requests — `web-spec-conformance`

| # | Question | Status |
|---|---|---|
| R-1 | Must internal test vectors be documented in `FORMAT-V2.md`, or is the test file the acceptable source? | open |
| R-2 | Is `zlib.crc32` equivalence the intended contract for the container CRC? | open |
| R-3 | Is the CRC field little-endian on disk? The header stores a `uint32_t` cast to bytes. | open |

## R-1 — test vectors

**Why it matters.** Four constants remain undocumented (`0xdeadbeef`,
`0x800000`, `0xFFFFFFFFFFFFFFFF`, `0x484E4459`). They are test inputs, not
format values: documenting them in the spec would teach readers the wrong thing.

**Recommendation.** Leave them in the tests, but name the file in the spec as
the source of the vectors so the next audit does not re-open the question.

## R-2 — CRC contract

**Recommendation.** Yes: `crc32("123456789") = 0xCBF43926` is the published
IEEE 802.3 check value and is now stated in `docs/FORMAT-V2.md`; the header
pins the same pair in `include/hydra_v2_container.h:227-230`.

## R-3 — byte order

**Recommendation.** Confirm with a one-line test before documenting: the field
is written as a `uint32_t`, so its byte order follows the host unless the code
converts explicitly.
