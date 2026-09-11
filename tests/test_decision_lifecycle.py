import pytest

from decisionready.decision_lifecycle import apply_human_decision
from decisionready.models import (
    ApprovalRequirement,
    Baseline,
    DecisionOutcome,
    DecisionReadiness,
    HumanDecision,
    Impact,
    ImpactDomain,
    ProposedChange,
    ReadinessState,
    EvidenceRequirement,
)


def make_baseline():
    return Baseline(
        project_id="P-001",
        version=1,
        name="DecisionReady Demo",
        state={
            "launch_date": "2026-10-01",
        },
    )


def make_change():
    return ProposedChange(
        change_id="C-001",
        project_id="P-001",
        title="Move launch date",
        description="Move launch date",
        requested_by="program-manager",
    )


def test_approved_ready_change_creates_new_baseline():
    baseline = make_baseline()
    change = make_change()

    readiness = DecisionReadiness(
        state=ReadinessState.READY,
        evidence_required=1,
        evidence_satisfied=1,
        approvals_required=1,
        approvals_satisfied=1,
    )

    decision = HumanDecision(
        change_id="C-001",
        outcome=DecisionOutcome.APPROVED,
        decided_by="Executive Sponsor",
        rationale="Required controls satisfied.",
    )

    evidence = [
        EvidenceRequirement(
            evidence_id="E-SCHEDULE",
            description="Schedule impact analysis",
            satisfied=True,
        )
    ]

    approvals = [
        ApprovalRequirement(
            approval_id="A-PROGRAM",
            role="Program Sponsor",
            approved=True,
            approver="Executive Sponsor",
        )
    ]

    impacts = [
        Impact(
            domain=ImpactDomain.SCHEDULE,
            summary="Launch date changed",
            affected_items=["launch_date"],
        )
    ]

    result = apply_human_decision(
        baseline=baseline,
        change=change,
        readiness=readiness,
        decision=decision,
        impacts=impacts,
        evidence=evidence,
        approvals=approvals,
        approved_updates={
            "launch_date": "2026-10-15",
        },
    )

    assert result.new_baseline is not None
    assert result.new_baseline.version == 2
    assert result.new_baseline.state["launch_date"] == "2026-10-15"

    assert result.change_log.outcome == DecisionOutcome.APPROVED
    assert result.change_log.new_baseline_version == 2

    assert result.report.human_decision == "APPROVED"


def test_not_ready_change_cannot_be_approved():
    baseline = make_baseline()
    change = make_change()

    readiness = DecisionReadiness(
        state=ReadinessState.NOT_READY,
        evidence_required=1,
        evidence_satisfied=0,
        approvals_required=1,
        approvals_satisfied=0,
    )

    decision = HumanDecision(
        change_id="C-001",
        outcome=DecisionOutcome.APPROVED,
        decided_by="Executive Sponsor",
        rationale="Attempted premature approval.",
    )

    with pytest.raises(
        ValueError,
        match="cannot become baseline",
    ):
        apply_human_decision(
            baseline=baseline,
            change=change,
            readiness=readiness,
            decision=decision,
            impacts=[],
            evidence=[],
            approvals=[],
            approved_updates={
                "launch_date": "2026-10-15",
            },
        )


@pytest.mark.parametrize(
    "outcome",
    [
        DecisionOutcome.REJECTED,
        DecisionOutcome.DEFERRED,
    ],
)
def test_non_approved_decisions_do_not_change_baseline(outcome):
    baseline = make_baseline()
    change = make_change()

    readiness = DecisionReadiness(
        state=ReadinessState.NOT_READY,
        evidence_required=1,
        evidence_satisfied=0,
        approvals_required=1,
        approvals_satisfied=0,
    )

    decision = HumanDecision(
        change_id="C-001",
        outcome=outcome,
        decided_by="Executive Sponsor",
        rationale="Human governance decision.",
    )

    result = apply_human_decision(
        baseline=baseline,
        change=change,
        readiness=readiness,
        decision=decision,
        impacts=[],
        evidence=[],
        approvals=[],
        approved_updates={},
    )

    assert result.new_baseline is None
    assert result.change_log.new_baseline_version is None
    assert result.change_log.outcome == outcome
