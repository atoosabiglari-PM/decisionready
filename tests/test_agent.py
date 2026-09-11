import json

from decisionready.agent import analyze_decision_scenario


def test_agent_tool_uses_deterministic_engine(tmp_path):
    scenario = {
        "project": {
            "project_id": "TEST-001",
            "name": "DecisionReady Test",
        },
        "baseline": {
            "version": 1,
            "state": {
                "scope": {
                    "service": "existing"
                }
            },
        },
        "change": {
            "change_id": "CHG-001",
            "title": "Change service",
            "description": "Test deterministic agent integration",
            "requested_by": "test-user",
        },
        "proposed_state": {
            "scope": {
                "service": "updated"
            }
        },
    }

    path = tmp_path / "scenario.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")

    result = analyze_decision_scenario(str(path))

    assert "detected_changes" in result
    assert "impact_domains" in result
    assert "evidence" in result
    assert "approvals" in result
    assert "readiness" in result
    assert result["readiness"]["state"] in {
        "READY",
        "NOT_READY",
        "BLOCKED",
    }


def test_agent_tool_annotates_date_direction(tmp_path):
    scenario = {
        "project": {
            "project_id": "TEST-DATE",
            "name": "Date Direction Test",
        },
        "baseline": {
            "version": 1,
            "state": {
                "launch_date": "2026-10-01",
            },
        },
        "change": {
            "change_id": "CHG-DATE",
            "title": "Move launch date",
            "description": "Validate deterministic date direction",
            "requested_by": "test-user",
        },
        "proposed_state": {
            "launch_date": "2026-10-15",
        },
    }

    path = tmp_path / "date-scenario.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")

    result = analyze_decision_scenario(str(path))

    change = next(
        item
        for item in result["detected_changes"]
        if item["path"] == "launch_date"
    )

    assert change["temporal_change"] == {
        "direction": "LATER",
        "days": 14,
    }
