from decisionready.models import (
    ApprovalRequirement,
    EvidenceRequirement,
)
from decisionready.readiness_graph import build_readiness_graph


def test_readiness_graph_shows_missing_evidence_and_pending_approval():
    evidence = [
        EvidenceRequirement(
            evidence_id="E1",
            description="EU Privacy Approval",
            required=True,
            satisfied=False,
        ),
        EvidenceRequirement(
            evidence_id="E2",
            description="Localization Estimate",
            required=True,
            satisfied=True,
            source="Finance",
        ),
    ]

    approvals = [
        ApprovalRequirement(
            approval_id="A1",
            role="Legal",
            required=True,
            approved=False,
        ),
        ApprovalRequirement(
            approval_id="A2",
            role="Product VP",
            required=True,
            approved=True,
            approver="VP Product",
        ),
    ]

    graph = build_readiness_graph(
        change_id="CR-017",
        evidence=evidence,
        approvals=approvals,
        blockers=[],
    )

    root = next(
        node
        for node in graph.nodes
        if node.node_type == "DECISION"
    )

    assert root.status == "NOT_READY"
    assert root.metadata["evidence_required"] == 2
    assert root.metadata["evidence_satisfied"] == 1
    assert root.metadata["approvals_required"] == 2
    assert root.metadata["approvals_satisfied"] == 1

    eu_privacy = next(
        node
        for node in graph.nodes
        if node.node_id == "EVIDENCE-E1"
    )

    assert eu_privacy.status == "MISSING"

    legal = next(
        node
        for node in graph.nodes
        if node.node_id == "APPROVAL-A1"
    )

    assert legal.status == "PENDING"


def test_readiness_graph_shows_ready_when_everything_is_satisfied():
    evidence = [
        EvidenceRequirement(
            evidence_id="E1",
            description="Security Review",
            satisfied=True,
        )
    ]

    approvals = [
        ApprovalRequirement(
            approval_id="A1",
            role="Program Sponsor",
            approved=True,
            approver="Sponsor",
        )
    ]

    graph = build_readiness_graph(
        change_id="CR-020",
        evidence=evidence,
        approvals=approvals,
    )

    root = next(
        node
        for node in graph.nodes
        if node.node_type == "DECISION"
    )

    assert root.status == "READY"


def test_readiness_graph_shows_blocker_nodes():
    graph = build_readiness_graph(
        change_id="CR-021",
        evidence=[],
        approvals=[],
        blockers=[
            "Contract prohibits requested territory",
        ],
    )

    root = next(
        node
        for node in graph.nodes
        if node.node_type == "DECISION"
    )

    assert root.status == "BLOCKED"

    blocker = next(
        node
        for node in graph.nodes
        if node.node_type == "BLOCKER"
    )

    assert blocker.label == (
        "Contract prohibits requested territory"
    )
    assert blocker.status == "OPEN"
