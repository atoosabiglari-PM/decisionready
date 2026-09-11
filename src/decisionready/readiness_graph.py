from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from decisionready.models import (
    ApprovalRequirement,
    EvidenceRequirement,
)
from decisionready.readiness import evaluate_readiness


@dataclass
class ReadinessNode:
    node_id: str
    label: str
    node_type: str
    status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReadinessEdge:
    source: str
    target: str
    relationship: str


@dataclass
class ReadinessGraph:
    nodes: list[ReadinessNode]
    edges: list[ReadinessEdge]


def build_readiness_graph(
    change_id: str,
    evidence: list[EvidenceRequirement],
    approvals: list[ApprovalRequirement],
    blockers: list[str] | None = None,
) -> ReadinessGraph:
    blockers = blockers or []

    readiness = evaluate_readiness(
        evidence=evidence,
        approvals=approvals,
        blockers=blockers,
    )

    root_id = f"DECISION-{change_id}"

    nodes: list[ReadinessNode] = [
        ReadinessNode(
            node_id=root_id,
            label=f"Decision readiness for {change_id}",
            node_type="DECISION",
            status=readiness.state.value,
            metadata={
                "evidence_required": readiness.evidence_required,
                "evidence_satisfied": readiness.evidence_satisfied,
                "approvals_required": readiness.approvals_required,
                "approvals_satisfied": readiness.approvals_satisfied,
                "open_blockers": len(readiness.open_blockers),
            },
        )
    ]

    edges: list[ReadinessEdge] = []

    evidence_group = "GROUP-EVIDENCE"
    approval_group = "GROUP-APPROVALS"
    blocker_group = "GROUP-BLOCKERS"

    nodes.append(
        ReadinessNode(
            node_id=evidence_group,
            label="Evidence",
            node_type="GROUP",
        )
    )
    nodes.append(
        ReadinessNode(
            node_id=approval_group,
            label="Approvals",
            node_type="GROUP",
        )
    )
    nodes.append(
        ReadinessNode(
            node_id=blocker_group,
            label="Blockers",
            node_type="GROUP",
        )
    )

    for group_id in (
        evidence_group,
        approval_group,
        blocker_group,
    ):
        edges.append(
            ReadinessEdge(
                source=root_id,
                target=group_id,
                relationship="REQUIRES",
            )
        )

    for item in evidence:
        node_id = f"EVIDENCE-{item.evidence_id}"

        if not item.required:
            status = "OPTIONAL"
        elif item.satisfied:
            status = "SATISFIED"
        else:
            status = "MISSING"

        nodes.append(
            ReadinessNode(
                node_id=node_id,
                label=item.description,
                node_type="EVIDENCE",
                status=status,
                metadata={
                    "required": item.required,
                    "source": item.source,
                },
            )
        )

        edges.append(
            ReadinessEdge(
                source=evidence_group,
                target=node_id,
                relationship="CONTAINS",
            )
        )

    for item in approvals:
        node_id = f"APPROVAL-{item.approval_id}"

        if not item.required:
            status = "OPTIONAL"
        elif item.approved:
            status = "APPROVED"
        else:
            status = "PENDING"

        nodes.append(
            ReadinessNode(
                node_id=node_id,
                label=item.role,
                node_type="APPROVAL",
                status=status,
                metadata={
                    "required": item.required,
                    "approver": item.approver,
                },
            )
        )

        edges.append(
            ReadinessEdge(
                source=approval_group,
                target=node_id,
                relationship="CONTAINS",
            )
        )

    for index, blocker in enumerate(blockers, start=1):
        node_id = f"BLOCKER-{index:03d}"

        nodes.append(
            ReadinessNode(
                node_id=node_id,
                label=blocker,
                node_type="BLOCKER",
                status="OPEN",
            )
        )

        edges.append(
            ReadinessEdge(
                source=blocker_group,
                target=node_id,
                relationship="CONTAINS",
            )
        )

    return ReadinessGraph(
        nodes=nodes,
        edges=edges,
    )
