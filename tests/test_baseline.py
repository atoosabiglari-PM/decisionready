import pytest

from decisionready.baseline import promote_approved_change
from decisionready.models import (
    Baseline,
    DecisionOutcome,
    DecisionReadiness,
    HumanDecision,
    ProposedChange,
    ReadinessState,
)


def make_baseline():
    return Baseline(
        project_id="PROJ-001",
        version=12,
        name="Global Launch",
        state={
            "geography": ["US"],
            "launch_date": "2026-10-01",
            "privacy": {
                "eu_review": "not_required",
            },
        },
    )


def make_change():
    return ProposedChange(
        change_id="CR-017",
        project_id="PROJ-001",
        title="Add Germany to launch",
        description="Expand launch geography from US to US and Germany.",
        requested_by="VP Product",
    )


def ready_state():
    return DecisionReadiness(
        state=ReadinessState.READY,
        evidence_required=5,
        evidence_satisfied=5,
        approvals_required=3,
        approvals_satisfied=3,
        open_blockers=[],
    )


def approved_decision():
    return HumanDecision(
        change_id="CR-017",
        outcome=DecisionOutcome.APPROVED,
        decided_by="VP Product",
        rationale="Approved with revised launch date.",
    )


def test_approved_ready_change_creates_next_baseline():
    new_baseline = promote_approved_change(
        baseline=make_baseline(),
        change=make_change(),
        readiness=ready_state(),
        decision=approved_decision(),
        approved_updates={
            "geography": ["US", "DE"],
            "launch_date": "2026-10-15",
            "privacy": {
                "eu_review": "approved",
            },
        },
    )

    assert new_baseline.version == 13
    assert new_baseline.state["geography"] == ["US", "DE"]
    assert new_baseline.state["launch_date"] == "2026-10-15"
    assert new_baseline.state["privacy"]["eu_review"] == "approved"


def test_not_ready_change_cannot_be_promoted():
    readiness = ready_state()
    readiness.state = ReadinessState.NOT_READY

    with pytest.raises(ValueError):
        promote_approved_change(
            baseline=make_baseline(),
            change=make_change(),
            readiness=readiness,
            decision=approved_decision(),
            approved_updates={"geography": ["US", "DE"]},
        )


def test_rejected_change_cannot_be_promoted():
    decision = approved_decision()
    decision.outcome = DecisionOutcome.REJECTED

    with pytest.raises(ValueError):
        promote_approved_change(
            baseline=make_baseline(),
            change=make_change(),
            readiness=ready_state(),
            decision=decision,
            approved_updates={"geography": ["US", "DE"]},
        )


def test_change_from_another_project_cannot_be_promoted():
    change = make_change()
    change.project_id = "PROJ-999"

    with pytest.raises(ValueError):
        promote_approved_change(
            baseline=make_baseline(),
            change=change,
            readiness=ready_state(),
            decision=approved_decision(),
            approved_updates={"geography": ["US", "DE"]},
        )
