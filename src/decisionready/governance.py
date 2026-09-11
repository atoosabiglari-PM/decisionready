from __future__ import annotations

from dataclasses import dataclass

from decisionready.models import (
    ApprovalRequirement,
    EvidenceRequirement,
    ImpactDomain,
)


@dataclass(frozen=True)
class GovernanceRule:
    domain: ImpactDomain
    evidence_id: str
    evidence_description: str
    approval_id: str
    approval_role: str


GOVERNANCE_RULES = [
    GovernanceRule(
        domain=ImpactDomain.PRIVACY,
        evidence_id="E-PRIVACY",
        evidence_description="Privacy impact assessment",
        approval_id="A-PRIVACY",
        approval_role="Privacy / Legal",
    ),
    GovernanceRule(
        domain=ImpactDomain.SECURITY,
        evidence_id="E-SECURITY",
        evidence_description="Security impact assessment",
        approval_id="A-SECURITY",
        approval_role="Security",
    ),
    GovernanceRule(
        domain=ImpactDomain.COST,
        evidence_id="E-COST",
        evidence_description="Cost impact estimate",
        approval_id="A-FINANCE",
        approval_role="Finance",
    ),
    GovernanceRule(
        domain=ImpactDomain.CONTRACTS,
        evidence_id="E-CONTRACT",
        evidence_description="Contract impact review",
        approval_id="A-LEGAL",
        approval_role="Legal",
    ),
    GovernanceRule(
        domain=ImpactDomain.VENDORS,
        evidence_id="E-VENDOR",
        evidence_description="Vendor impact assessment",
        approval_id="A-VENDOR",
        approval_role="Vendor Management",
    ),
    GovernanceRule(
        domain=ImpactDomain.SCHEDULE,
        evidence_id="E-SCHEDULE",
        evidence_description="Schedule impact analysis",
        approval_id="A-PROGRAM",
        approval_role="Program Sponsor",
    ),
    GovernanceRule(
        domain=ImpactDomain.COMPLIANCE,
        evidence_id="E-COMPLIANCE",
        evidence_description="Compliance impact assessment",
        approval_id="A-COMPLIANCE",
        approval_role="Compliance",
    ),
]


def derive_governance_requirements(
    domains: set[ImpactDomain],
) -> tuple[
    list[EvidenceRequirement],
    list[ApprovalRequirement],
]:
    evidence: list[EvidenceRequirement] = []
    approvals: list[ApprovalRequirement] = []

    for rule in GOVERNANCE_RULES:
        if rule.domain not in domains:
            continue

        evidence.append(
            EvidenceRequirement(
                evidence_id=rule.evidence_id,
                description=rule.evidence_description,
                required=True,
                satisfied=False,
            )
        )

        approvals.append(
            ApprovalRequirement(
                approval_id=rule.approval_id,
                role=rule.approval_role,
                required=True,
                approved=False,
            )
        )

    return evidence, approvals
