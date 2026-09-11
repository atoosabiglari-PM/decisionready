from __future__ import annotations

from copy import deepcopy
from typing import Any

from decisionready.models import (
    Baseline,
    DecisionOutcome,
    DecisionReadiness,
    HumanDecision,
    ProposedChange,
    ReadinessState,
)


def _merge_state(
    current: dict[str, Any],
    updates: dict[str, Any],
) -> dict[str, Any]:
    result = deepcopy(current)

    for key, value in updates.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _merge_state(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def promote_approved_change(
    baseline: Baseline,
    change: ProposedChange,
    readiness: DecisionReadiness,
    decision: HumanDecision,
    approved_updates: dict[str, Any],
) -> Baseline:
    if change.project_id != baseline.project_id:
        raise ValueError("Change does not belong to this project.")

    if decision.change_id != change.change_id:
        raise ValueError("Decision does not belong to this change.")

    if readiness.state != ReadinessState.READY:
        raise ValueError(
            "A change cannot become baseline until the decision is READY."
        )

    if decision.outcome != DecisionOutcome.APPROVED:
        raise ValueError(
            "Only an APPROVED human decision may create a new baseline."
        )

    return Baseline(
        project_id=baseline.project_id,
        version=baseline.version + 1,
        name=baseline.name,
        state=_merge_state(
            baseline.state,
            approved_updates,
        ),
    )
