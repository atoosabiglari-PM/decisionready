from __future__ import annotations

from collections import Counter

from pydantic import BaseModel, Field

from decisionready.models import (
    ApprovalRequirement,
    Baseline,
    DecisionOutcome,
    DecisionReadiness,
    EvidenceRequirement,
    HumanDecision,
    Impact,
    ProposedChange,
)


class ChangeStatusReport(BaseModel):
    project_id: str
    change_id: str
    change_title: str

    baseline_version: int
    readiness_state: str

    impact_domains: list[str] = Field(default_factory=list)
    impact_count: int = 0

    evidence_required: int = 0
    evidence_satisfied: int = 0
    missing_evidence: list[str] = Field(default_factory=list)

    approvals_required: int = 0
    approvals_satisfied: int = 0
    pending_approvals: list[str] = Field(default_factory=list)

    blockers: list[str] = Field(default_factory=list)

    human_decision: str | None = None
    decided_by: str | None = None

    next_action: str


def build_change_status_report(
    baseline: Baseline,
    change: ProposedChange,
    impacts: list[Impact],
    evidence: list[EvidenceRequirement],
    approvals: list[ApprovalRequirement],
    readiness: DecisionReadiness,
    decision: HumanDecision | None = None,
) -> ChangeStatusReport:
    domain_counts = Counter(
        impact.domain.value
        for impact in impacts
    )

    missing_evidence = [
        item.description
        for item in evidence
        if item.required and not item.satisfied
    ]

    pending_approvals = [
        item.role
        for item in approvals
        if item.required and not item.approved
    ]

    if decision is not None:
        next_action = _decision_next_action(decision.outcome)
    elif readiness.state.value == "BLOCKED":
        next_action = "Resolve blocking conditions before decision preparation."
    elif readiness.state.value == "NOT_READY":
        next_action = (
            "Collect missing evidence and approvals, then reevaluate readiness."
        )
    else:
        next_action = (
            "Present the decision package to the authorized human decision-maker."
        )

    return ChangeStatusReport(
        project_id=change.project_id,
        change_id=change.change_id,
        change_title=change.title,
        baseline_version=baseline.version,
        readiness_state=readiness.state.value,
        impact_domains=sorted(domain_counts.keys()),
        impact_count=len(impacts),
        evidence_required=readiness.evidence_required,
        evidence_satisfied=readiness.evidence_satisfied,
        missing_evidence=missing_evidence,
        approvals_required=readiness.approvals_required,
        approvals_satisfied=readiness.approvals_satisfied,
        pending_approvals=pending_approvals,
        blockers=readiness.open_blockers,
        human_decision=(
            decision.outcome.value
            if decision is not None
            else None
        ),
        decided_by=(
            decision.decided_by
            if decision is not None
            else None
        ),
        next_action=next_action,
    )


def _decision_next_action(
    outcome: DecisionOutcome,
) -> str:
    if outcome == DecisionOutcome.APPROVED:
        return (
            "Promote the approved change into the next baseline "
            "and record the change log."
        )

    if outcome == DecisionOutcome.REJECTED:
        return (
            "Retain the current baseline and record the rejected change."
        )

    return (
        "Retain the current baseline and record the deferred change "
        "for future review."
    )
