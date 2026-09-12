from decisionready.models import DecisionOutcome, ReadinessState
from decisionready.workspace import (
    analyze_submission,
    apply_governance_updates,
    record_workspace_decision,
)


def project_doc():
    return {
        "scenario_name": "DecisionReady Hackathon Build",
        "industry": "AI / Program Management",
        "project": {"project_id": "DR-001", "name": "DecisionReady Hackathon Build"},
        "baseline": {
            "version": 1,
            "state": {
                "delivery_mode": "CLI demo",
                "hosting": "CloudShell",
                "security": {"bedrock_runtime_access": False},
                "architecture": {"web_ui": False},
            },
        },
        "change": {
            "change_id": "DR-CR-001",
            "title": "Launch public governed project workspace",
            "description": "Move DecisionReady into an interactive PM workspace.",
            "requested_by": "Product Owner",
        },
        "proposed_state": {
            "delivery_mode": "Public web application",
            "hosting": "Elastic Beanstalk",
            "security": {"bedrock_runtime_access": True},
            "architecture": {"web_ui": True},
        },
    }


def test_workspace_accepts_arbitrary_project():
    analysis = analyze_submission(project_doc())
    assert analysis.baseline.project_id == "DR-001"
    assert analysis.preparation.detected_changes
    assert analysis.preparation.readiness.state == ReadinessState.NOT_READY


def test_workspace_can_reach_ready_and_approve():
    analysis = analyze_submission(project_doc())
    evidence_updates = {
        item.evidence_id: {"satisfied": True, "source": f"Evidence {item.evidence_id}"}
        for item in analysis.preparation.evidence
    }
    approval_updates = {
        item.approval_id: {"approved": True, "approver": f"Owner {item.approval_id}"}
        for item in analysis.preparation.approvals
    }
    evidence, approvals, readiness = apply_governance_updates(
        analysis,
        evidence_updates=evidence_updates,
        approval_updates=approval_updates,
    )
    assert readiness.state == ReadinessState.READY

    result = record_workspace_decision(
        analysis,
        evidence=evidence,
        approvals=approvals,
        readiness=readiness,
        outcome=DecisionOutcome.APPROVED,
        decided_by="Change Governance Board",
        rationale="Governance controls satisfied.",
    )
    assert result.new_baseline is not None
    assert result.new_baseline.version == 2
    assert result.new_baseline.state == project_doc()["proposed_state"]


def test_evidence_and_approval_require_audit_identity():
    analysis = analyze_submission(project_doc())
    evidence_updates = {
        item.evidence_id: {"satisfied": True, "source": ""}
        for item in analysis.preparation.evidence
    }
    approval_updates = {
        item.approval_id: {"approved": True, "approver": ""}
        for item in analysis.preparation.approvals
    }
    evidence, approvals, readiness = apply_governance_updates(
        analysis,
        evidence_updates=evidence_updates,
        approval_updates=approval_updates,
    )
    assert all(not item.satisfied for item in evidence)
    assert all(not item.approved for item in approvals)
    assert readiness.state == ReadinessState.NOT_READY
