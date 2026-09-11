from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from decisionready.models import ImpactDomain


@dataclass
class ImpactNode:
    node_id: str
    label: str
    node_type: str
    domain: ImpactDomain | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactEdge:
    source: str
    target: str
    relationship: str


@dataclass
class ImpactGraph:
    nodes: list[ImpactNode]
    edges: list[ImpactEdge]


DOMAIN_RULES: dict[str, ImpactDomain] = {
    "geography": ImpactDomain.SCOPE,
    "launch_date": ImpactDomain.SCHEDULE,
    "localization": ImpactDomain.RESOURCES,
    "privacy": ImpactDomain.PRIVACY,
    "security": ImpactDomain.SECURITY,
    "vendor": ImpactDomain.VENDORS,
    "contract": ImpactDomain.CONTRACTS,
    "budget": ImpactDomain.COST,
    "cost": ImpactDomain.COST,
    "architecture": ImpactDomain.ARCHITECTURE,
    "milestone": ImpactDomain.MILESTONES,
    "dependency": ImpactDomain.DEPENDENCIES,
    "risk": ImpactDomain.RISKS,
    "compliance": ImpactDomain.COMPLIANCE,
}


def infer_domain(path: str) -> ImpactDomain:
    root = path.split(".")[0].lower()

    for keyword, domain in DOMAIN_RULES.items():
        if keyword in root:
            return domain

    return ImpactDomain.SCOPE


def build_impact_graph(
    change_id: str,
    title: str,
    detected_changes: list[dict[str, Any]],
) -> ImpactGraph:
    nodes: list[ImpactNode] = [
        ImpactNode(
            node_id=change_id,
            label=title,
            node_type="CHANGE",
        )
    ]
    edges: list[ImpactEdge] = []

    domain_nodes: dict[ImpactDomain, str] = {}

    for index, change in enumerate(detected_changes, start=1):
        domain = infer_domain(change["path"])

        if domain not in domain_nodes:
            domain_id = f"DOMAIN-{domain.value.upper()}"
            domain_nodes[domain] = domain_id

            nodes.append(
                ImpactNode(
                    node_id=domain_id,
                    label=domain.value.replace("_", " ").title(),
                    node_type="DOMAIN",
                    domain=domain,
                )
            )

            edges.append(
                ImpactEdge(
                    source=change_id,
                    target=domain_id,
                    relationship="IMPACTS",
                )
            )

        change_node_id = f"IMPACT-{index:03d}"

        nodes.append(
            ImpactNode(
                node_id=change_node_id,
                label=change["path"],
                node_type="IMPACT",
                domain=domain,
                metadata={
                    "change_type": change["change_type"],
                    "previous_value": change["previous_value"],
                    "proposed_value": change["proposed_value"],
                },
            )
        )

        edges.append(
            ImpactEdge(
                source=domain_nodes[domain],
                target=change_node_id,
                relationship="CONTAINS",
            )
        )

    return ImpactGraph(
        nodes=nodes,
        edges=edges,
    )
