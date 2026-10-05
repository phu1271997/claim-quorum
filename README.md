# ClaimQuorum

A standalone **GenLayer Intelligent Contract primitive** that turns several
independently published prose reports into one **categorical verdict** the whole
validator set agrees on.

A caller sets one fixed question and a short ballot of allowed labels, then
opens a batch with 3..7 source documents. Each document is pinned to a GitHub
commit and a SHA-256 digest. Every validator fetches the same bytes, confirms
the hash, and asks its own LLM to read each document and cast one labelled vote
with a strength and a verbatim quote, or to abstain. The contract then resolves
the batch **deterministically** by confidence-weighted plurality, flags a
dispute when the margin is thin, and stores the batch on chain.

> Sibling primitive: [FigureQuorum](https://github.com/phu1271997/figure-quorum)
> folds numbers the same way ClaimQuorum folds verdicts.

## Why this is a primitive, not a demo

- **Parameterised at construction** - `(source_repo, question, labels)` - so one
  deployment serves fact checks, claim triage, eligibility or policy-compliance
  rulings, stance aggregation. Nothing about the use case is hardcoded.
- **Non-determinism is the point.** Strip the web fetch and the LLM judgement
  and there is no primitive left; the whole value is distilling a defensible
  verdict from unstructured human text.
- **The validator checks meaning, not shape.** Each validator re-fetches every
  document, re-hashes the bytes, re-parses the proposal deterministically, then
  runs an *independent* LLM audit that answers true for a vote only if the label
  is the one that source genuinely supports (or a justified ABSTAIN), backed by
  its quote. Two nodes that would read a source differently do **not** agree; a
  vote that merely has the right JSON keys does not pass.

## How consensus works

1. A caller opens a batch with 3..7 sources. Each is `{id, url, sha256}` and the
   `url` must be a commit-pinned raw GitHub file inside the fixed `source_repo`,
   under `datasets/<batch>/...md`.
2. **Leader** fetches each document, verifies size and `sha256`, then asks its
   LLM to read every document independently and emit one vote per document: a
   ballot label with weight 1..100 and a verbatim quote, or ABSTAIN (weight 0).
3. The contract **parses the proposal deterministically** - strict field set,
   label must be on the ballot, every quote must be a verbatim span of the
   source.
4. **Validators** repeat fetch + hash + parse, then run a second independent LLM
   audit of each vote against the full source. Accepted only if every vote
   passes for every validator.
5. The accepted votes are resolved deterministically: tally weight per label,
   take the winner, and require the winning margin to be at least one fifth of
   the total cast weight. Fewer than 3 participating sources is `INSUFFICIENT`; a
   thin margin is `DISPUTED`; otherwise `RESOLVED` with the consensus label and
   an `agreement_pct`.

## Public API

- `open_batch(batch: str, sources_json: str)` - run a new batch.
- `get_latest() -> dict`
- `get_round(index: int) -> dict`
- `get_batch(batch: str) -> dict`
- `get_state() -> dict`

`sources_json` is a JSON array:

```json
[
  {"id":"audit-north","url":"https://raw.githubusercontent.com/phu1271997/claim-quorum/<40-hex-commit>/datasets/sla-2026-q3/audit-north.md","sha256":"<64 hex>"},
  {"id":"audit-south","url":"https://raw.githubusercontent.com/phu1271997/claim-quorum/<40-hex-commit>/datasets/sla-2026-q3/audit-south.md","sha256":"<64 hex>"},
  {"id":"status-page","url":"https://raw.githubusercontent.com/phu1271997/claim-quorum/<40-hex-commit>/datasets/sla-2026-q3/status-page.md","sha256":"<64 hex>"}
]
```

Pin the commit (not a branch) so the bytes can never change under the hash. See
[`datasets/README.md`](datasets/README.md).

## Deployed on Studionet

- Address: `0x0dBF2313044E5E35af59d940b101087232Bf529B`
- source_repo: `phu1271997/claim-quorum`
- Network: GenLayer Studionet (chain id `61999`, RPC `https://studio.genlayer.com/api`)
- Explorer: <https://explorer-studio.genlayer.com/address/0x0dBF2313044E5E35af59d940b101087232Bf529B>

## Develop

```bash
pip install -r requirements.txt
python3 scripts/deploy.py --check-only       # validate schema, no key needed

source ~/.genlayer/env.sh                     # exports GENLAYER_PRIVATE_KEY
python3 scripts/deploy.py                      # deploy to studionet

pytest -q                                      # deterministic resolution tests
```

[`tests/test_logic.py`](tests/test_logic.py) covers weighted-plurality
resolution vs. dispute, insufficient-data handling, the ABSTAIN path,
verbatim-quote enforcement, and source-commitment validation.

## License

MIT - see [LICENSE](LICENSE).
