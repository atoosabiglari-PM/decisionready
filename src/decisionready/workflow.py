from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from decisionready.change_detection import detect_changes
from decisionready.governance import derive_governance_requirements
from decisionready.impact_graph import ImpactGraph, build_impact_graph
from decisionready.models import (
    ApprovalRequirement,
    Baseline,
    DecisionReadiness,
    EvidenceRequirement,
    ImpactDomain,
    ProposedChange,
)
from decisionready.readiness import evaluate_readiness
from decisionready.readiness_graph import (
    ReadinessGraph,
    build_readiness_graph,
)


@dataclass
class DecisionPreparation:
    detected_changes: list[dict[str, Any]]
    impact_domains: set[ImpactDomain]
    impact_graph: ImpactGraph
    evidence: list[EvidenceRequirement]
    approvals: list[ApprovalRequirement]
    readiness: DecisionReadiness
    readiness_graph: ReadinessGraph


def prepare_decision(
    baseline: Baseline,
    change: ProposedChange,
    proposed_state: dict[str, Any],
) -> DecisionPreparation:
    if baseline.project_id != change.project_id:
        raise ValueError(
            "Change does not belong to the baseline project."
        )

    detected_changes = detect_changes(
        baseline=baseline.state,
        proposed=proposed_state,
    )

    impact_graph = build_impact_graph(
        change_id=change.change_id,
        title=change.title,
        detected_changes=detected_changes,
    )

    impact_domains = {
        node.domain
        for node in impact_graph.nodes
        if node.node_type == "DOMAIN"
        and node.domain is not None
    }

    evidence, approvals = derive_governance_requirements(
        impact_domains
    )

    readiness = evaluate_readiness(
        evidence=evidence,
        approvals=approvals,
    )

    readiness_graph = build_readiness_graph(
        change_id=change.change_id,
        evidence=evidence,
        approvals=approvals,
    )

    return DecisionPreparation(
        detected_changes=detected_changes,
        impact_domains=impact_domains,
        impact_graph=impact_graph,
        evidence=evidence,
        approvals=approvals,
        readiness=readiness,
        readiness_graph=readiness_graph,
    )
