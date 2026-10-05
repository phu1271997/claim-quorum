# Portal submission - Intelligent Contracts (Builder track)

Repo: https://github.com/phu1271997/claim-quorum
Network: GenLayer Studionet (chain id 61999)
Address: `0x0dBF2313044E5E35af59d940b101087232Bf529B`

**Title**
ClaimQuorum - consensus categorical verdict from independent prose reports

**Description (<1000 chars)**
ClaimQuorum is a reusable GenLayer adjudication primitive. A caller sets one
fixed question and a short ballot of labels, then opens a batch with 3 to 7
source documents, each pinned to a GitHub commit and a SHA-256 hash. Every
validator fetches the same bytes, confirms the hash, and asks its own LLM to
read each document and cast one labelled vote from the ballot, with a strength
and a verbatim quote, or to abstain. Consensus is on the meaning of each vote,
not JSON shape: a validator agrees only when its own independent audit finds
each label is the one that source genuinely supports. The contract resolves the
batch deterministically by confidence-weighted plurality, flags a dispute when
the winning margin is thin, and stores the batch on chain. Parameterised by
(repo, question, labels), so one deployment serves multi-report fact checks,
claim triage, eligibility or policy-compliance rulings.

**Verification (<500 chars)**
Deployed on Studionet at 0x0dBF2313044E5E35af59d940b101087232Bf529B (deploy
Result: SUCCESS, get_state reads back the configured question and ballot).
Source, README, design notes and deterministic tests (weighted plurality,
dispute margin, abstain handling, verbatim-quote and source-commitment
validation) at https://github.com/phu1271997/claim-quorum
