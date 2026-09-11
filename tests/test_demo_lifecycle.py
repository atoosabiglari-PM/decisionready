from pathlib import Path

from decisionready.demo_lifecycle import run_governed_demo


def test_germany_demo_full_governed_lifecycle():
    scenario = (
        Path(__file__).parents[1]
        / "demo_data"
        / "germany_launch.json"
    )

    result = run_governed_demo(scenario)

    assert result["initial"]["baseline_version"] == 12
    assert result["initial"]["readiness"] == "NOT_READY"
    assert result["initial"]["evidence"] == "0/2"
    assert result["initial"]["approvals"] == "0/2"

    assert result["final"]["readiness"] == "READY"
    assert result["final"]["human_decision"] == "APPROVED"
    assert result["final"]["new_baseline_version"] == 13

    assert result["audit"]["previous_baseline_version"] == 12
    assert result["audit"]["new_baseline_version"] == 13
    assert result["audit"]["outcome"] == "APPROVED"

    state = result["final"]["new_baseline_state"]

    assert "DE" in state["geography"]
    assert state["launch_date"] == "2026-10-15"
    assert state["localization"]["german"] is True
    assert state["privacy"]["eu_review"] == "required"

    assert result["report"]["baseline_version"] == 13
    assert "Baseline v13 is now active" in result["report"]["next_action"]
