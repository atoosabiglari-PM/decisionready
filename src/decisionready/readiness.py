from __future__ import annotations

from decisionready.models import (
    ApprovalRequirement,
    DecisionReadiness,
    EvidenceRequirement,
    ReadinessState,
)


def evaluate_readiness(
    evidence: list[EvidenceRequirement],
    approvals: list[ApprovalRequirement],
    blockers: list[str] | None = None,
) -> DecisionReadiness:
    blockers = blockers or []

    required_evidence = [item for item in evidence if item.required]
    satisfied_evidence = [item for item in required_evidence if item.satisfied]

    required_approvals = [item for item in approvals if item.required]
    satisfied_approvals = [item for item in required_approvals if item.approved]

    if blockers:
        state = ReadinessState.BLOCKED
    elif (
        len(required_evidence) == len(satisfied_evidence)
        and len(required_approvals) == len(satisfied_approvals)
    ):
        state = ReadinessState.READY
    else:
        state = ReadinessState.NOT_READY

    return DecisionReadiness(
        state=state,
        evidence_required=len(required_evidence),
        evidence_satisfied=len(satisfied_evidence),
        approvals_required=len(required_approvals),
        approvals_satisfied=len(satisfied_approvals),
        open_blockers=blockers,
    )
