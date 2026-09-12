from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from decisionready.decision_lifecycle import DecisionLifecycleResult, apply_human_decision
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
from decisionready.readiness import evaluate_readiness
from decisionready.workflow import DecisionPreparation, prepare_decision


@dataclass
class WorkspaceAnalysis:
    baseline: Baseline
    change: ProposedChange
    proposed_state: dict[str, Any]
    preparation: DecisionPreparation


def analyze_submission(document: dict[str, Any]) -> WorkspaceAnalysis:
    try:
        project = document["project"]
        baseline_data = document["baseline"]
        change_data = document["change"]
        proposed_state = document["proposed_state"]
    except KeyError as exc:
        raise ValueError(f"Missing required section: {exc.args[0]}") from exc

    if not isinstance(baseline_data.get("state"), dict):
        raise ValueError("baseline.state must be a JSON object.")
    if not isinstance(proposed_state, dict):
        raise ValueError("proposed_state must be a JSON object.")

    baseline = Baseline(
        project_id=str(project["project_id"]).strip(),
        version=int(baseline_data["version"]),
        name=str(project["name"]).strip(),
        state=baseline_data["state"],
    )
    change = ProposedChange(
        change_id=str(change_data["change_id"]).strip(),
        project_id=baseline.project_id,
        title=str(change_data["title"]).strip(),
        description=str(change_data["description"]).strip(),
        requested_by=str(change_data["requested_by"]).strip(),
    )

    for value, label in [
        (baseline.project_id, "Project ID"),
        (baseline.name, "Project name"),
        (change.change_id, "Change ID"),
        (change.title, "Change title"),
        (change.requested_by, "Requested by"),
    ]:
        if not value:
            raise ValueError(f"{label} is required.")

    preparation = prepare_decision(
        baseline=baseline,
        change=change,
        proposed_state=proposed_state,
    )
    return WorkspaceAnalysis(
        baseline=baseline,
        change=change,
        proposed_state=proposed_state,
        preparation=preparation,
    )


def apply_governance_updates(
    analysis: WorkspaceAnalysis,
    *,
    evidence_updates: dict[str, dict[str, Any]] | None = None,
    approval_updates: dict[str, dict[str, Any]] | None = None,
    blockers: list[str] | None = None,
) -> tuple[list[EvidenceRequirement], list[ApprovalRequirement], DecisionReadiness]:
    evidence_updates = evidence_updates or {}
    approval_updates = approval_updates or {}

    evidence = []
    for item in analysis.preparation.evidence:
        update = evidence_updates.get(item.evidence_id, {})
        source = str(update.get("source") or "").strip()
        satisfied = bool(update.get("satisfied")) and bool(source)
        evidence.append(
            item.model_copy(update={"satisfied": satisfied, "source": source or None})
        )

    approvals = []
    for item in analysis.preparation.approvals:
        update = approval_updates.get(item.approval_id, {})
        approver = str(update.get("approver") or "").strip()
        approved = bool(update.get("approved")) and bool(approver)
        approvals.append(
            item.model_copy(update={"approved": approved, "approver": approver or None})
        )

    readiness = evaluate_readiness(
        evidence=evidence,
        approvals=approvals,
        blockers=blockers or [],
    )
    return evidence, approvals, readiness


def record_workspace_decision(
    analysis: WorkspaceAnalysis,
    *,
    evidence: list[EvidenceRequirement],
    approvals: list[ApprovalRequirement],
    readiness: DecisionReadiness,
    outcome: DecisionOutcome,
    decided_by: str,
    rationale: str,
) -> DecisionLifecycleResult:
    decided_by = decided_by.strip()
    rationale = rationale.strip()
    if not decided_by:
        raise ValueError("Decision maker is required.")
    if not rationale:
        raise ValueError("Decision rationale is required.")

    impacts = [
        Impact(
            domain=domain,
            summary=f"{domain.value.title()} impact detected by DecisionReady change analysis.",
            affected_items=[],
        )
        for domain in sorted(
            analysis.preparation.impact_domains,
            key=lambda item: item.value,
        )
    ]

    decision = HumanDecision(
        change_id=analysis.change.change_id,
        outcome=outcome,
        decided_by=decided_by,
        rationale=rationale,
    )

    return apply_human_decision(
        baseline=analysis.baseline,
        change=analysis.change,
        readiness=readiness,
        decision=decision,
        impacts=impacts,
        evidence=evidence,
        approvals=approvals,
        approved_updates=analysis.proposed_state,
    )


def lifecycle_to_dict(result: DecisionLifecycleResult) -> dict[str, Any]:
    return {
        "decision": result.decision.model_dump(mode="json"),
        "previous_baseline": result.previous_baseline.model_dump(mode="json"),
        "new_baseline": (
            result.new_baseline.model_dump(mode="json")
            if result.new_baseline is not None
            else None
        ),
        "change_log": result.change_log.model_dump(mode="json"),
        "report": result.report.model_dump(mode="json"),
    }
