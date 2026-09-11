from __future__ import annotations

from decisionready.models import (
    Baseline,
    ChangeLogEntry,
    DecisionOutcome,
    HumanDecision,
    Impact,
    ProposedChange,
)


def record_change_decision(
    previous_baseline: Baseline,
    change: ProposedChange,
    decision: HumanDecision,
    impacts: list[Impact],
    new_baseline: Baseline | None = None,
) -> ChangeLogEntry:
    if change.project_id != previous_baseline.project_id:
        raise ValueError("Change does not belong to this project.")

    if decision.change_id != change.change_id:
        raise ValueError("Decision does not belong to this change.")

    if decision.outcome == DecisionOutcome.APPROVED:
        if new_baseline is None:
            raise ValueError(
                "An approved change must reference its new baseline."
            )

        if new_baseline.project_id != previous_baseline.project_id:
            raise ValueError(
                "New baseline does not belong to this project."
            )

        if new_baseline.version != previous_baseline.version + 1:
            raise ValueError(
                "Approved change must create exactly the next baseline version."
            )

        new_version = new_baseline.version

    else:
        if new_baseline is not None:
            raise ValueError(
                "Rejected or deferred changes cannot create a new baseline."
            )

        new_version = None

    return ChangeLogEntry(
        change_id=change.change_id,
        previous_baseline_version=previous_baseline.version,
        new_baseline_version=new_version,
        outcome=decision.outcome,
        impacts=impacts,
        decision_by=decision.decided_by,
    )
