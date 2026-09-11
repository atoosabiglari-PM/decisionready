from decisionready.models import (
    ApprovalRequirement,
    Baseline,
    DecisionOutcome,
    EvidenceRequirement,
    HumanDecision,
    Impact,
    ImpactDomain,
    ProposedChange,
)
from decisionready.readiness import evaluate_readiness
from decisionready.reporting import build_change_status_report


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


def test_report_identifies_missing_items():
    evidence = [
        EvidenceRequirement(
            evidence_id="E1",
            description="EU Privacy Approval",
            satisfied=False,
        ),
        EvidenceRequirement(
            evidence_id="E2",
            description="Localization Estimate",
            satisfied=True,
        ),
    ]

    approvals = [
        ApprovalRequirement(
            approval_id="A1",
            role="Legal",
            approved=False,
        )
    ]

    readiness = evaluate_readiness(
        evidence=evidence,
        approvals=approvals,
    )

    report = build_change_status_report(
        baseline=make_baseline(),
        change=make_change(),
        impacts=[
            Impact(
                domain=ImpactDomain.SCOPE,
                summary="Launch geography expands.",
            ),
            Impact(
                domain=ImpactDomain.PRIVACY,
                summary="EU privacy review required.",
            ),
        ],
        evidence=evidence,
        approvals=approvals,
        readiness=readiness,
    )

    assert report.readiness_state == "NOT_READY"
    assert report.baseline_version == 12
    assert report.impact_count == 2
    assert report.impact_domains == ["privacy", "scope"]
    assert report.missing_evidence == ["EU Privacy Approval"]
    assert report.pending_approvals == ["Legal"]
    assert "Collect missing evidence" in report.next_action


def test_ready_report_routes_to_human_decision():
    evidence = [
        EvidenceRequirement(
            evidence_id="E1",
            description="Privacy Approval",
            satisfied=True,
        )
    ]

    approvals = [
        ApprovalRequirement(
            approval_id="A1",
            role="Legal",
            approved=True,
            approver="Legal Lead",
        )
    ]

    readiness = evaluate_readiness(
        evidence=evidence,
        approvals=approvals,
    )

    report = build_change_status_report(
        baseline=make_baseline(),
        change=make_change(),
        impacts=[],
        evidence=evidence,
        approvals=approvals,
        readiness=readiness,
    )

    assert report.readiness_state == "READY"
    assert "authorized human" in report.next_action


def test_approved_decision_reports_baseline_promotion_next():
    evidence = []
    approvals = []

    readiness = evaluate_readiness(
        evidence=evidence,
        approvals=approvals,
    )

    decision = HumanDecision(
        change_id="CR-017",
        outcome=DecisionOutcome.APPROVED,
        decided_by="VP Product",
        rationale="Approved.",
    )

    report = build_change_status_report(
        baseline=make_baseline(),
        change=make_change(),
        impacts=[],
        evidence=evidence,
        approvals=approvals,
        readiness=readiness,
        decision=decision,
    )

    assert report.human_decision == "APPROVED"
    assert report.decided_by == "VP Product"
    assert "next baseline" in report.next_action
