from __future__ import annotations

from dataclasses import dataclass

from decisionready.baseline import promote_approved_change
from decisionready.change_log import record_change_decision
from decisionready.models import (
    Baseline,
    ChangeLogEntry,
    DecisionOutcome,
    DecisionReadiness,
    HumanDecision,
    Impact,
    ProposedChange,
)
from decisionready.reporting import (
    ChangeStatusReport,
    build_change_status_report,
)
from decisionready.models import (
    ApprovalRequirement,
    EvidenceRequirement,
)


@dataclass
class DecisionLifecycleResult:
    """Result of applying an authorized human governance decision."""

    decision: HumanDecision
    previous_baseline: Baseline
    new_baseline: Baseline | None
    change_log: ChangeLogEntry
    report: ChangeStatusReport


def apply_human_decision(
    *,
    baseline: Baseline,
    change: ProposedChange,
    readiness: DecisionReadiness,
    decision: HumanDecision,
    impacts: list[Impact],
    evidence: list[EvidenceRequirement],
    approvals: list[ApprovalRequirement],
    approved_updates: dict,
) -> DecisionLifecycleResult:
    """Apply a human decision without allowing AI to approve a change.

    APPROVED:
        Requires READY and creates the next baseline.

    REJECTED / DEFERRED:
        Retains the existing baseline and records the decision.
    """

    if decision.change_id != change.change_id:
        raise ValueError(
            "Human decision does not belong to this change."
        )

    new_baseline: Baseline | None = None

    if decision.outcome == DecisionOutcome.APPROVED:
        new_baseline = promote_approved_change(
            baseline=baseline,
            change=change,
            readiness=readiness,
            decision=decision,
            approved_updates=approved_updates,
        )

    change_log = record_change_decision(
        previous_baseline=baseline,
        change=change,
        decision=decision,
        impacts=impacts,
        new_baseline=new_baseline,
    )

    report = build_change_status_report(
        baseline=(
            new_baseline
            if new_baseline is not None
            else baseline
        ),
        change=change,
        impacts=impacts,
        evidence=evidence,
        approvals=approvals,
        readiness=readiness,
        decision=decision,
    )

    return DecisionLifecycleResult(
        decision=decision,
        previous_baseline=baseline,
        new_baseline=new_baseline,
        change_log=change_log,
        report=report,
    )
