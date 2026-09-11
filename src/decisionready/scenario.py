from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from decisionready.models import Baseline, ProposedChange
from decisionready.workflow import DecisionPreparation, prepare_decision


def load_scenario(path: str | Path) -> dict[str, Any]:
    scenario_path = Path(path)

    with scenario_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_scenario(path: str | Path) -> DecisionPreparation:
    data = load_scenario(path)

    baseline = Baseline(
        project_id=data["project"]["project_id"],
        version=data["baseline"]["version"],
        name=data["project"]["name"],
        state=data["baseline"]["state"],
    )

    change = ProposedChange(
        change_id=data["change"]["change_id"],
        project_id=data["project"]["project_id"],
        title=data["change"]["title"],
        description=data["change"]["description"],
        requested_by=data["change"]["requested_by"],
    )

    return prepare_decision(
        baseline=baseline,
        change=change,
        proposed_state=data["proposed_state"],
    )
