# Contributing

Thank you for helping preserve the client through clean-room interoperability
work.

## Useful Contributions

- Add schema-backed protocol handlers with packet-level tests.
- Investigate quest, tutorial, character, combat, inventory, or persistence
  behavior using legally obtained local evidence.
- Improve setup documentation and Windows tooling.
- Reproduce reported behavior against the separately signed local test client.

## Do Not Upload

- APK, AAB, OBB, or extracted game asset files.
- Decompiled proprietary source or large bytecode dumps.
- Signing keys, account tokens, device identifiers, or private logs.
- Copyrighted screenshots, logos, music, video, or character art.

Use small factual descriptions, hashes, offsets, protocol field names, and
independently written compatibility code instead.

## Development

```powershell
Set-Location .\preservation_server
py -3.12 -m pytest -q
```

Keep changes focused and add tests for every protocol behavior change. Before
submitting:

1. Confirm all tests pass.
2. Run `git diff --check`.
3. Verify no proprietary or personal material is staged.
4. Explain what was observed, what was inferred, and what remains unverified.

## Reporting Results

Include the client version, the last successful screen or protocol phase, and
sanitized server log lines. Replace account IDs, tokens, device IDs, IP
addresses, and other personal data before posting.
