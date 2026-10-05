"""Deterministic-core tests for ClaimQuorum (off-chain, no GenVM).

conftest.py installs a `genlayer` stub before these imports run.
"""
import pytest

from contracts import claim_quorum as cq

UE = cq.gl.vm.UserError

REPO = "owner/repo"
COMMIT = "a" * 40
LABELS = ["SUPPORTED", "REFUTED", "UNVERIFIABLE"]


def _url(batch, name):
    return f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/datasets/{batch}/{name}.md"


def _src(sid, batch, name):
    return {"id": sid, "url": _url(batch, name), "sha256": "b" * 64}


def _votes(items):
    rows = []
    for i, it in enumerate(items):
        if it is None:
            rows.append({"index": i, "label": cq.ABSTAIN, "weight": 0, "quote": ""})
        else:
            label, weight = it
            rows.append({"index": i, "label": label, "weight": weight, "quote": "q" * 12})
    return {"votes": rows}


def test_resolve_weighted_plurality():
    parsed = _votes([("SUPPORTED", 90), ("SUPPORTED", 80), ("REFUTED", 10)])
    out = cq._resolve("b1", "q", LABELS, parsed)
    assert out["status"] == "RESOLVED"
    assert out["consensus_label"] == "SUPPORTED"
    assert out["participating"] == 3
    assert out["tally"]["SUPPORTED"] == 170
    assert out["agreement_pct"] == 170 * 100 // 180


def test_resolve_dispute_when_margin_too_thin():
    parsed = _votes([("SUPPORTED", 50), ("REFUTED", 48), ("UNVERIFIABLE", 5)])
    out = cq._resolve("b1", "q", LABELS, parsed)
    assert out["status"] == "DISPUTED"
    assert out["consensus_label"] is None


def test_resolve_insufficient_with_abstentions():
    parsed = _votes([("SUPPORTED", 90), None, None])
    out = cq._resolve("b1", "q", LABELS, parsed)
    assert out["status"] == "INSUFFICIENT"
    assert out["abstained"] == 2
    assert out["participating"] == 1


def test_read_labels_rejects_abstain_and_dupes():
    assert cq._read_labels(LABELS) == LABELS
    with pytest.raises(UE):
        cq._read_labels(["SUPPORTED"])                 # too few
    with pytest.raises(UE):
        cq._read_labels(["SUPPORTED", "ABSTAIN"])      # ABSTAIN not allowed
    with pytest.raises(UE):
        cq._read_labels(["SAME", "SAME"])              # duplicate


def test_parse_votes_requires_verbatim_quote():
    docs = ["the service met its SLA every day this month, fully"]
    good = {"votes": [{"index": 0, "label": "SUPPORTED", "weight": 80,
                       "quote": "the service met its SLA"}]}
    assert cq._parse_votes(good, docs, LABELS)["votes"][0]["label"] == "SUPPORTED"
    bad = {"votes": [{"index": 0, "label": "SUPPORTED", "weight": 80,
                      "quote": "this quote is not in the document at all"}]}
    with pytest.raises(UE):
        cq._parse_votes(bad, docs, LABELS)


def test_sources_validation():
    good = [_src("a", "sla-2026-q3", "a"), _src("b", "sla-2026-q3", "b"),
            _src("c", "sla-2026-q3", "c")]
    assert len(cq._read_sources(good, REPO, "sla-2026-q3")) == 3
    with pytest.raises(UE):
        cq._read_sources(good, "other/repo", "sla-2026-q3")          # wrong repo
    dupe = [_src("a", "p", "a"), _src("a", "p", "b"), _src("c", "p", "c")]
    with pytest.raises(UE):
        cq._read_sources(dupe, REPO, "p")                            # duplicate id
