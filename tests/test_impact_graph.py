from decisionready.impact_graph import build_impact_graph
from decisionready.models import ImpactDomain


def test_builds_change_domain_and_impact_nodes():
    detected_changes = [
        {
            "path": "geography",
            "previous_value": ["US"],
            "proposed_value": ["US", "DE"],
            "change_type": "MODIFIED",
        },
        {
            "path": "launch_date",
            "previous_value": "2026-10-01",
            "proposed_value": "2026-10-15",
            "change_type": "MODIFIED",
        },
        {
            "path": "privacy.eu_review",
            "previous_value": "not_required",
            "proposed_value": "required",
            "change_type": "MODIFIED",
        },
    ]

    graph = build_impact_graph(
        change_id="CR-017",
        title="Add Germany to launch",
        detected_changes=detected_changes,
    )

    node_ids = {node.node_id for node in graph.nodes}

    assert "CR-017" in node_ids
    assert "DOMAIN-SCOPE" in node_ids
    assert "DOMAIN-SCHEDULE" in node_ids
    assert "DOMAIN-PRIVACY" in node_ids

    impact_nodes = [
        node for node in graph.nodes
        if node.node_type == "IMPACT"
    ]

    assert len(impact_nodes) == 3


def test_assigns_expected_domains():
    detected_changes = [
        {
            "path": "budget.total",
            "previous_value": 100000,
            "proposed_value": 140000,
            "change_type": "MODIFIED",
        },
        {
            "path": "vendor.territory",
            "previous_value": "US",
            "proposed_value": "US+DE",
            "change_type": "MODIFIED",
        },
        {
            "path": "security.review",
            "previous_value": "complete",
            "proposed_value": "reopen",
            "change_type": "MODIFIED",
        },
    ]

    graph = build_impact_graph(
        change_id="CR-018",
        title="Expand release",
        detected_changes=detected_changes,
    )

    domains = {
        node.domain
        for node in graph.nodes
        if node.node_type == "DOMAIN"
    }

    assert ImpactDomain.COST in domains
    assert ImpactDomain.VENDORS in domains
    assert ImpactDomain.SECURITY in domains


def test_graph_edges_connect_change_to_domains():
    detected_changes = [
        {
            "path": "launch_date",
            "previous_value": "2026-10-01",
            "proposed_value": "2026-10-15",
            "change_type": "MODIFIED",
        }
    ]

    graph = build_impact_graph(
        change_id="CR-019",
        title="Move launch date",
        detected_changes=detected_changes,
    )

    assert any(
        edge.source == "CR-019"
        and edge.target == "DOMAIN-SCHEDULE"
        and edge.relationship == "IMPACTS"
        for edge in graph.edges
    )

    assert any(
        edge.source == "DOMAIN-SCHEDULE"
        and edge.relationship == "CONTAINS"
        for edge in graph.edges
    )
