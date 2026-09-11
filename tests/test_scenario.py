from decisionready.scenario import load_scenario, run_scenario
from decisionready.models import ReadinessState


def test_germany_scenario_loads():
    data = load_scenario("demo_data/germany_launch.json")

    assert data["scenario_id"] == "SCENARIO-001"
    assert data["project"]["project_id"] == "PROJ-001"
    assert data["baseline"]["version"] == 12
    assert data["change"]["change_id"] == "CR-017"


def test_germany_scenario_runs_through_decisionready():
    result = run_scenario(
        "demo_data/germany_launch.json"
    )

    assert result.readiness.state == ReadinessState.NOT_READY

    changed_paths = {
        item["path"]
        for item in result.detected_changes
    }

    assert "geography" in changed_paths
    assert "launch_date" in changed_paths
    assert "privacy.eu_review" in changed_paths
    assert "localization.german" in changed_paths

    domain_values = {
        domain.value
        for domain in result.impact_domains
    }

    assert "scope" in domain_values
    assert "schedule" in domain_values
    assert "privacy" in domain_values
    assert "resources" in domain_values
