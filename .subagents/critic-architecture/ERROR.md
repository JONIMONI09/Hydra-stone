# Error Log — `critic-architecture`

Append-only, newest last.

## 2026-10-29 — a typedef was reported as an unused declaration

**What happened.** `hydra_kv_cache_t` appeared in the "declared, never used" list.
It is a `typedef`, and the identifier is used through the type name in headers
the scanner did not join.

**Evidence.** `grep -rn "hydra_kv_cache_t" include/ src/` shows the definition and
the uses.

**What changed.** The detector skips `typedef` lines and any declaration whose
name appears in a header with a different extension set; the remaining candidates
are real duplicates, not type aliases.

## 2026-10-29 — the duplicate-decoder finding was real and is closed

**What happened.** `_decode_bf16` existed twice (`tools/gguf_reader.py`,
`tools/safetensors_to_hydra.py`) with the same rule in two places.

**What changed.** Both were compared over all 65,536 BF16 patterns (0
differences), then the conversion moved to `tools/bf16.py`. Two thin adapters
remain, and they differ only in the exception type they raise — the duplicated
*rule* is gone.
