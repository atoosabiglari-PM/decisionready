from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path
from typing import Any

from strands import Agent, tool
from strands.models import BedrockModel

from decisionready.scenario import run_scenario
from decisionready.workflow import DecisionPreparation


DEFAULT_MODEL_ID = "us.amazon.nova-2-lite-v1:0"
DEFAULT_REGION = "us-west-2"


def annotate_detected_change(
    change: dict[str, Any],
) -> dict[str, Any]:
    """Add deterministic semantics where they can be derived safely."""

    annotated = dict(change)

    previous = change.get("previous_value")
    proposed = change.get("proposed_value")

    if isinstance(previous, str) and isinstance(proposed, str):
        try:
            previous_date = date.fromisoformat(previous)
            proposed_date = date.fromisoformat(proposed)
        except ValueError:
            return annotated

        delta_days = (proposed_date - previous_date).days

        if delta_days > 0:
            direction = "LATER"
        elif delta_days < 0:
            direction = "EARLIER"
        else:
            direction = "UNCHANGED"

        annotated["temporal_change"] = {
            "direction": direction,
            "days": abs(delta_days),
        }

    return annotated


def preparation_to_dict(
    preparation: DecisionPreparation,
) -> dict[str, Any]:
    """Convert authoritative DecisionReady output into agent-safe JSON data."""

    return {
        "detected_changes": [
            annotate_detected_change(change)
            for change in preparation.detected_changes
        ],
        "impact_domains": sorted(
            domain.value for domain in preparation.impact_domains
        ),
        "evidence": [
            item.model_dump(mode="json")
            for item in preparation.evidence
        ],
        "approvals": [
            item.model_dump(mode="json")
            for item in preparation.approvals
        ],
        "readiness": preparation.readiness.model_dump(mode="json"),
        "impact_graph": {
            "node_count": len(
                getattr(preparation.impact_graph, "nodes", [])
            ),
            "edge_count": len(
                getattr(preparation.impact_graph, "edges", [])
            ),
        },
        "readiness_graph": {
            "node_count": len(
                getattr(preparation.readiness_graph, "nodes", [])
            ),
            "edge_count": len(
                getattr(preparation.readiness_graph, "edges", [])
            ),
        },
    }


@tool
def analyze_decision_scenario(
    scenario_path: str,
) -> dict[str, Any]:
    """Run the authoritative DecisionReady analysis for a scenario.

    The deterministic DecisionReady engine calculates changes, impacts,
    governance requirements, approvals, evidence requirements, blockers,
    and readiness. Its readiness result is authoritative and must not be
    changed by the language model.

    Args:
        scenario_path: Path to a DecisionReady scenario JSON file.
    """

    path = Path(scenario_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"DecisionReady scenario not found: {scenario_path}"
        )

    preparation = run_scenario(path)
    return preparation_to_dict(preparation)


SYSTEM_PROMPT = """
You are DecisionReady, an AI decision-readiness orchestration agent for
complex enterprise programs.

You use the deterministic DecisionReady engine as the authoritative source
for change impacts, governance requirements, evidence, approvals, blockers,
and readiness.

MANDATORY RULES:

1. When asked to assess a DecisionReady scenario, call
   analyze_decision_scenario before giving a readiness assessment.

2. Never invent, override, or modify the readiness state returned by the
   DecisionReady engine.

3. Never claim that READY means APPROVED.
   READY only means the change has satisfied the current readiness controls.
   Final approval remains a human governance decision.

4. Clearly distinguish:
   - detected change
   - impact domains
   - required evidence
   - required approvals
   - unresolved blockers
   - readiness state
   - recommended next actions

5. If evidence or approvals are missing, identify them explicitly.

6. Treat previous_value and proposed_value as authoritative facts.
   When temporal_change is present, use its direction and day count exactly.
   Never describe a LATER date as an acceleration or an EARLIER date as a delay.

7. The readiness.open_blockers field is authoritative for the word "blocker".
   Missing evidence or approvals may make a scenario NOT_READY, but do not call
   them blockers unless they are explicitly listed in open_blockers. Call them
   unmet requirements instead.

8. Do not fabricate evidence, approvals, project facts, governance status,
   causal claims, or schedule meaning.

9. Explain results in concise executive language suitable for a program
   manager, change board, compliance reviewer, or executive sponsor.

Your purpose is not to replace human decision-makers. Your purpose is to
make decisions decision-ready.
""".strip()


def build_agent() -> Agent:
    """Create the DecisionReady Strands agent backed by Amazon Nova 2 Lite."""

    model = BedrockModel(
        model_id=os.getenv(
            "DECISIONREADY_MODEL_ID",
            DEFAULT_MODEL_ID,
        ),
        region_name=os.getenv(
            "AWS_REGION",
            DEFAULT_REGION,
        ),
        temperature=0.0,
    )

    return Agent(
        model=model,
        tools=[analyze_decision_scenario],
        system_prompt=SYSTEM_PROMPT,
        callback_handler=None,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a DecisionReady scenario through Strands + Nova."
    )
    parser.add_argument(
        "scenario",
        help="Path to the scenario JSON file.",
    )
    args = parser.parse_args()

    agent = build_agent()

    response = agent(
        "Analyze this DecisionReady scenario using the authoritative "
        "DecisionReady tool. Explain the change, impacts, governance "
        "requirements, blockers, readiness state, and next actions. "
        f"Scenario path: {args.scenario}"
    )

    print(response)


if __name__ == "__main__":
    main()
