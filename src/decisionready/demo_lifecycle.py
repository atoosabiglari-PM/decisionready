from __future__ import annotations

import argparse
from pathlib import Path

from decisionready.decision_lifecycle import apply_human_decision
from decisionready.models import (
    Baseline,
    DecisionOutcome,
    HumanDecision,
    Impact,
    ProposedChange,
)
from decisionready.readiness import evaluate_readiness
from decisionready.scenario import load_scenario, run_scenario


def run_governed_demo(path: str | Path) -> dict:
    """Run a complete governed DecisionReady lifecycle demonstration."""

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

    # Phase 1: authoritative initial analysis.
    preparation = run_scenario(path)

    initial_readiness = preparation.readiness

    # Phase 2: simulate completion of the governance work.
    evidence_sources = {
        "E-PRIVACY": "Privacy Impact Assessment PIA-DE-001",
        "E-SCHEDULE": "Schedule Impact Analysis SIA-DE-001",
    }

    approval_owners = {
        "A-PRIVACY": "Privacy Counsel",
        "A-PROGRAM": "Program Sponsor",
    }

    completed_evidence = [
        item.model_copy(
            update={
                "satisfied": True,
                "source": evidence_sources.get(
                    item.evidence_id,
                    item.source,
                ),
            }
        )
        if item.evidence_id in evidence_sources
        else item
        for item in preparation.evidence
    ]

    completed_approvals = [
        item.model_copy(
            update={
                "approved": True,
                "approver": approval_owners.get(
                    item.approval_id,
                    item.approver,
                ),
            }
        )
        if item.approval_id in approval_owners
        else item
        for item in preparation.approvals
    ]

    # Re-evaluate readiness using the deterministic engine.
    final_readiness = evaluate_readiness(
        evidence=completed_evidence,
        approvals=completed_approvals,
    )

    # Build audit/reporting impacts from the authoritative impact domains.
    impacts = [
        Impact(
            domain=domain,
            summary=(
                f"{domain.value.title()} impact detected "
                "by DecisionReady change analysis."
            ),
            affected_items=[],
        )
        for domain in sorted(
            preparation.impact_domains,
            key=lambda item: item.value,
        )
    ]

    # Phase 3: human governance decision.
    human_decision = HumanDecision(
        change_id=change.change_id,
        outcome=DecisionOutcome.APPROVED,
        decided_by="Change Governance Board",
        rationale=(
            "Required evidence and approvals were satisfied; "
            "the authorized human governance body approved the change."
        ),
    )

    lifecycle = apply_human_decision(
        baseline=baseline,
        change=change,
        readiness=final_readiness,
        decision=human_decision,
        impacts=impacts,
        evidence=completed_evidence,
        approvals=completed_approvals,
        approved_updates=data["proposed_state"],
    )

    return {
        "scenario": data["scenario_name"],
        "change_id": change.change_id,
        "initial": {
            "baseline_version": baseline.version,
            "readiness": initial_readiness.state.value,
            "evidence": (
                f"{initial_readiness.evidence_satisfied}/"
                f"{initial_readiness.evidence_required}"
            ),
            "approvals": (
                f"{initial_readiness.approvals_satisfied}/"
                f"{initial_readiness.approvals_required}"
            ),
        },
        "governance_completed": {
            "evidence": [
                {
                    "id": item.evidence_id,
                    "satisfied": item.satisfied,
                    "source": item.source,
                }
                for item in completed_evidence
            ],
            "approvals": [
                {
                    "id": item.approval_id,
                    "approved": item.approved,
                    "approver": item.approver,
                }
                for item in completed_approvals
            ],
        },
        "final": {
            "readiness": final_readiness.state.value,
            "human_decision": human_decision.outcome.value,
            "decided_by": human_decision.decided_by,
            "new_baseline_version": (
                lifecycle.new_baseline.version
                if lifecycle.new_baseline is not None
                else None
            ),
            "new_baseline_state": (
                lifecycle.new_baseline.state
                if lifecycle.new_baseline is not None
                else None
            ),
        },
        "audit": {
            "previous_baseline_version": (
                lifecycle.change_log.previous_baseline_version
            ),
            "new_baseline_version": (
                lifecycle.change_log.new_baseline_version
            ),
            "outcome": lifecycle.change_log.outcome.value,
            "decision_by": lifecycle.change_log.decision_by,
        },
        "report": lifecycle.report.model_dump(mode="json"),
    }


def main() -> None:
    import json

    parser = argparse.ArgumentParser(
        description="Run the full DecisionReady governed lifecycle demo."
    )
    parser.add_argument("scenario")
    args = parser.parse_args()

    result = run_governed_demo(args.scenario)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
