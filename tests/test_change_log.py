import pytest

from decisionready.change_log import record_change_decision
from decisionready.models import (
    Baseline,
    DecisionOutcome,
    HumanDecision,
    Impact,
    ImpactDomain,
    ProposedChange,
)


def make_baseline():
    return Baseline(
        project_id="PROJ-001",
        version=12,
        name="Global Launch",
        state={"geography": ["US"]},
    )


def make_change():
    return ProposedChange(
        change_id="CR-017",
        project_id="PROJ-001",
        title="Add Germany to launch",
        description="Expand launch geography.",
        requested_by="VP Product",
    )


def make_impacts():
    return [
        Impact(
            domain=ImpactDomain.SCOPE,
            summary="Geography expands to Germany.",
        ),
        Impact(
            domain=ImpactDomain.PRIVACY,
            summary="EU privacy review required.",
        ),
    ]


def test_approved_change_records_new_baseline():
    decision = HumanDecision(
        change_id="CR-017",
        outcome=DecisionOutcome.APPROVED,
        decided_by="VP Product",
        rationale="Approved.",
    )

    new_baseline = Baseline(
        project_id="PROJ-001",
        version=13,
        name="Global Launch",
        state={"geography": ["US", "DE"]},
    )

    entry = record_change_decision(
        previous_baseline=make_baseline(),
        change=make_change(),
        decision=decision,
        impacts=make_impacts(),
        new_baseline=new_baseline,
    )

    assert entry.previous_baseline_version == 12
    assert entry.new_baseline_version == 13
    assert entry.outcome == DecisionOutcome.APPROVED
    assert entry.decision_by == "VP Product"
    assert len(entry.impacts) == 2


def test_rejected_change_keeps_baseline_unchanged():
    decision = HumanDecision(
        change_id="CR-017",
        outcome=DecisionOutcome.REJECTED,
        decided_by="VP Product",
        rationale="Not approved.",
    )

    entry = record_change_decision(
        previous_baseline=make_baseline(),
        change=make_change(),
        decision=decision,
        impacts=make_impacts(),
    )

    assert entry.new_baseline_version is None
    assert entry.outcome == DecisionOutcome.REJECTED


def test_deferred_change_keeps_baseline_unchanged():
    decision = HumanDecision(
        change_id="CR-017",
        outcome=DecisionOutcome.DEFERRED,
        decided_by="VP Product",
        rationale="Review next phase.",
    )

    entry = record_change_decision(
        previous_baseline=make_baseline(),
        change=make_change(),
        decision=decision,
        impacts=make_impacts(),
    )

    assert entry.new_baseline_version is None
    assert entry.outcome == DecisionOutcome.DEFERRED


def test_approved_change_requires_new_baseline():
    decision = HumanDecision(
        change_id="CR-017",
        outcome=DecisionOutcome.APPROVED,
        decided_by="VP Product",
        rationale="Approved.",
    )

    with pytest.raises(ValueError):
        record_change_decision(
            previous_baseline=make_baseline(),
            change=make_change(),
            decision=decision,
            impacts=make_impacts(),
        )


def test_rejected_change_cannot_create_new_baseline():
    decision = HumanDecision(
        change_id="CR-017",
        outcome=DecisionOutcome.REJECTED,
        decided_by="VP Product",
        rationale="Rejected.",
    )

    new_baseline = Baseline(
        project_id="PROJ-001",
        version=13,
        name="Global Launch",
        state={"geography": ["US", "DE"]},
    )

    with pytest.raises(ValueError):
        record_change_decision(
            previous_baseline=make_baseline(),
            change=make_change(),
            decision=decision,
            impacts=make_impacts(),
            new_baseline=new_baseline,
        )
