# Design notes - ClaimQuorum

## The trust backbone

ClaimQuorum answers one hard question: *given several independent written
reports, what single verdict should the network commit to?* The parts that make
the answer trustworthy:

1. **Source commitment.** A caller cannot point the oracle at an arbitrary URL.
   Every source must live in the contract's fixed `source_repo`, under
   `datasets/<batch>/`, pinned to a 40-hex commit, and carry a SHA-256 that must
   match the served bytes. This removes "the page changed under us" and "the
   leader and validators saw different text" as failure modes.

2. **Independent reading.** The leader asks its LLM to read each document on its
   own and cast one vote. Documents are explicitly framed as untrusted data,
   never instructions (prompt-injection defence). The model is told to judge
   only on what the document states, not outside knowledge.

3. **Deterministic parse.** Before anything reaches consensus the contract
   enforces an exact grammar: a fixed field set, the label must be on the
   ballot, weight is an int 1..100 (0 for ABSTAIN), and every cast vote's quote
   must be a verbatim substring of the source. Off-grammar proposals are
   rejected deterministically.

4. **Meaning-level validation.** Each validator re-fetches, re-hashes,
   re-parses, then runs a *second, independent* LLM audit that answers true for
   a vote only if the label is the one the full source genuinely supports - and
   it is told to scrutinise ABSTAIN as hard as a cast vote. The proposal is
   accepted only if every vote passes. This is what keeps it from being a
   format-only validator.

5. **Deterministic fold.** The accepted votes are resolved with pure Python so
   the final verdict is byte-identical on every node.

## Weighted categorical fold

- Each source casts one ballot label plus a self-reported strength (1..100), or
  `ABSTAIN` with weight 0.
- Resolution is **confidence-weighted plurality**: tally weight per label, take
  the winner, and require the winning margin to be at least one fifth of the
  total cast weight. Otherwise the batch is `DISPUTED` (an honest "the sources
  do not agree" rather than a coin-flip). Fewer than 3 participating sources is
  `INSUFFICIENT`.
- `agreement_pct` exposes how concentrated the weight was behind the winner.

## State lifecycle

- Batches are append-only canonical-JSON entries in a `DynArray[str]`.
- A `TreeMap[str, str]` maps each batch slug to its round index and enforces
  single-use, so the same labelled batch cannot be replayed.
- `MAX_ROUNDS` bounds storage growth.
- Views return the folded outcome plus the full source and vote record, so a
  downstream contract can both trust the headline and re-audit the inputs.

## Deliberate non-goals

- No frontend - this is a standalone primitive (the Intelligent Contracts
  track), meant to be imported by other contracts and dApps.
- The bundled `datasets/` files are illustrative report shapes, not real
  audits. Production use needs credibly governed, independently produced feeds
  and a separate collusion-resistance story for the source set itself.
