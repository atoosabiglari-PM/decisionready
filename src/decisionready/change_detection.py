from __future__ import annotations

from typing import Any


def detect_changes(
    baseline: dict[str, Any],
    proposed: dict[str, Any],
    prefix: str = "",
) -> list[dict[str, Any]]:
    """
    Compare an approved baseline with a proposed state.

    Returns deterministic change records containing:
    path, previous_value, proposed_value, and change_type.
    """
    changes: list[dict[str, Any]] = []

    all_keys = sorted(set(baseline) | set(proposed))

    for key in all_keys:
        path = f"{prefix}.{key}" if prefix else key

        in_baseline = key in baseline
        in_proposed = key in proposed

        if not in_baseline:
            changes.append(
                {
                    "path": path,
                    "previous_value": None,
                    "proposed_value": proposed[key],
                    "change_type": "ADDED",
                }
            )
            continue

        if not in_proposed:
            changes.append(
                {
                    "path": path,
                    "previous_value": baseline[key],
                    "proposed_value": None,
                    "change_type": "REMOVED",
                }
            )
            continue

        old_value = baseline[key]
        new_value = proposed[key]

        if isinstance(old_value, dict) and isinstance(new_value, dict):
            changes.extend(
                detect_changes(
                    old_value,
                    new_value,
                    prefix=path,
                )
            )
        elif old_value != new_value:
            changes.append(
                {
                    "path": path,
                    "previous_value": old_value,
                    "proposed_value": new_value,
                    "change_type": "MODIFIED",
                }
            )

    return changes
