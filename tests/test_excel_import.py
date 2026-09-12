from pathlib import Path

from decisionready.excel_import import xlsx_to_document
from decisionready.workspace import analyze_submission


def test_germany_excel_import():
    path = Path("demo_data/DecisionReady_Germany_Project_Demo.xlsx")
    document = xlsx_to_document(path.read_bytes())

    assert document["project"]["project_id"] == "GLP-2026"
    assert document["project"]["name"] == "Global Product Launch 2026"
    assert document["baseline"]["version"] == 1
    assert document["baseline"]["state"]["geography"] == ["US"]
    assert document["baseline"]["state"]["localization"]["german"] is False
    assert document["proposed_state"]["geography"] == ["US", "DE"]
    assert document["proposed_state"]["localization"]["german"] is True


def test_imported_excel_runs_decisionready():
    path = Path("demo_data/DecisionReady_Germany_Project_Demo.xlsx")
    document = xlsx_to_document(path.read_bytes())
    analysis = analyze_submission(document)

    assert len(analysis.preparation.detected_changes) == 4
    assert analysis.preparation.readiness.state.value == "NOT_READY"
    assert {
        item.evidence_id for item in analysis.preparation.evidence
    } == {"E-PRIVACY", "E-SCHEDULE"}
    assert {
        item.approval_id for item in analysis.preparation.approvals
    } == {"A-PRIVACY", "A-PROGRAM"}
