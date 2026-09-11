from decisionready.models import (
    ApprovalRequirement,
    EvidenceRequirement,
    ReadinessState,
)
from decisionready.readiness import evaluate_readiness


def test_ready_when_all_required_items_satisfied():
    evidence = [
        EvidenceRequirement(
            evidence_id="E1",
            description="Privacy review",
            satisfied=True,
        )
    ]
    approvals = [
        ApprovalRequirement(
            approval_id="A1",
            role="Product VP",
            approved=True,
            approver="VP Product",
        )
    ]

    result = evaluate_readiness(evidence, approvals)

    assert result.state == ReadinessState.READY
    assert result.evidence_required == 1
    assert result.evidence_satisfied == 1
    assert result.approvals_required == 1
    assert result.approvals_satisfied == 1


def test_not_ready_when_required_evidence_missing():
    evidence = [
        EvidenceRequirement(
            evidence_id="E1",
            description="Privacy review",
            satisfied=False,
        )
    ]
    approvals = [
        ApprovalRequirement(
            approval_id="A1",
            role="Product VP",
            approved=True,
            approver="VP Product",
        )
    ]

    result = evaluate_readiness(evidence, approvals)

    assert result.state == ReadinessState.NOT_READY
    assert result.evidence_satisfied == 0


def test_not_ready_when_required_approval_missing():
    evidence = [
        EvidenceRequirement(
            evidence_id="E1",
            description="Privacy review",
            satisfied=True,
        )
    ]
    approvals = [
        ApprovalRequirement(
            approval_id="A1",
            role="Legal",
            approved=False,
        )
    ]

    result = evaluate_readiness(evidence, approvals)

    assert result.state == ReadinessState.NOT_READY
    assert result.approvals_satisfied == 0


def test_blocked_when_blocker_exists():
    result = evaluate_readiness(
        evidence=[],
        approvals=[],
        blockers=["Contract prohibits requested territory"],
    )

    assert result.state == ReadinessState.BLOCKED
    assert result.open_blockers == [
        "Contract prohibits requested territory"
    ]


def test_optional_items_do_not_prevent_readiness():
    evidence = [
        EvidenceRequirement(
            evidence_id="E1",
            description="Optional market research",
            required=False,
            satisfied=False,
        )
    ]
    approvals = [
        ApprovalRequirement(
            approval_id="A1",
            role="Optional observer",
            required=False,
            approved=False,
        )
    ]

    result = evaluate_readiness(evidence, approvals)

    assert result.state == ReadinessState.READY
