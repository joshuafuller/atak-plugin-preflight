# Agent instructions

This repository is a pre-flight assistant for ATAK plugin authors.

When helping a user:

1. Ask for or locate the plugin source repository first.
2. Run `python3 preflight.py path/to/plugin-source`.
3. Optionally build an unsigned/debug APK only to validate compilation/runtime.
4. Explain every finding in plain language before suggesting a fix.
5. Never treat a `GAP` as a clean result unless the user explicitly chose
   `--allow-gaps` and the report says the run was partial.
6. Never claim Fortify, TPP signing, or TAK.gov acceptance was reproduced.
7. Keep source, build-input, artifact, and report hashes together in the handoff.
8. Read [docs/knowledge-base.md](docs/knowledge-base.md) before making ATAK
   compatibility claims.

Evidence levels are explicit:

- `verified`: a local check actually passed or failed.
- `inferred`: a conclusion derived from verified local evidence.
- `external-required`: only TPP, Fortify, or a stock ATAK runtime can confirm it.
