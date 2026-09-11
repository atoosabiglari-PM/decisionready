from decisionready.models import (
    Baseline,
    ProposedChange,
    ReadinessState,
)
from decisionready.workflow import prepare_decision


def test_prepare_decision_builds_full_germany_workflow():
    baseline = Baseline(
        project_id="PROJ-001",
        version=12,
        name="Global Launch",
        state={
            "geography": ["US"],
            "launch_date": "2026-10-01",
            "privacy": {
                "eu_review": "not_required",
            },
        },
    )

    change = ProposedChange(
        change_id="CR-017",
        project_id="PROJ-001",
        title="Add Germany to launch",
        description="Expand launch geography to Germany.",
        requested_by="VP Product",
    )

    proposed_state = {
        "geography": ["US", "DE"],
        "launch_date": "2026-10-15",
        "privacy": {
            "eu_review": "required",
        },
    }

    prepared = prepare_decision(
        baseline=baseline,
        change=change,
        proposed_state=proposed_state,
    )

    assert len(prepared.detected_changes) == 3

    domain_values = {
        domain.value
        for domain in prepared.impact_domains
    }

    assert "scope" in domain_values
    assert "schedule" in domain_values
    assert "privacy" in domain_values

    evidence_ids = {
        item.evidence_id
        for item in prepared.evidence
    }

    approval_ids = {
        item.approval_id
        for item in prepared.approvals
    }

    assert "E-SCHEDULE" in evidence_ids
    assert "E-PRIVACY" in evidence_ids

    assert "A-PROGRAM" in approval_ids
    assert "A-PRIVACY" in approval_ids

    assert prepared.readiness.state == ReadinessState.NOT_READY

    readiness_root = next(
        node
        for node in prepared.readiness_graph.nodes
        if node.node_type == "DECISION"
    )

    assert readiness_root.status == "NOT_READY"


def test_prepare_decision_rejects_cross_project_change():
    baseline = Baseline(
        project_id="PROJ-001",
        version=1,
        name="Program",
        state={"scope": "US"},
    )

    change = ProposedChange(
        change_id="CR-999",
        project_id="PROJ-999",
        title="Invalid change",
        description="Wrong project.",
        requested_by="Tester",
    )

    try:
        prepare_decision(
            baseline=baseline,
            change=change,
            proposed_state={"scope": "EU"},
        )
    except ValueError as exc:
        assert "baseline project" in str(exc)
    else:
        raise AssertionError(
            "Expected cross-project change to be rejected."
        )
