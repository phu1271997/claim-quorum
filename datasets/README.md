# datasets/

Source documents, grouped by batch:

```
datasets/<batch>/<source-id>.md
```

Each file is an untrusted prose report. The contract never runs a file as
instructions - it only reads it as data and casts one vote.

## Pinning a source

A source entry passed to `open_batch` is:

```json
{"id": "audit-north", "url": "https://raw.githubusercontent.com/phu1271997/claim-quorum/<commit>/datasets/<batch>/audit-north.md", "sha256": "<digest>"}
```

Rules enforced on chain:

- the `url` must sit inside the contract's fixed `source_repo`;
- the path must be `datasets/<batch>/<id>.md`;
- the commit must be a full 40-hex **commit SHA**, never a branch, so the bytes
  cannot change under the hash;
- `sha256` must equal the SHA-256 of the exact bytes served.

## Computing a digest

```bash
git rev-parse HEAD                                       # the 40-hex commit to pin
shasum -a 256 datasets/sla-2026-q3/audit-north.md        # the digest to pin
```

The files under `sla-2026-q3/` are illustrative report shapes, not real audits.
Replace them with credibly governed, independently produced feeds before using
the primitive for anything that matters.
