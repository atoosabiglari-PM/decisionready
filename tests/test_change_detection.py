from decisionready.change_detection import detect_changes


def test_detects_modified_nested_and_added_fields():
    baseline = {
        "geography": ["US"],
        "launch_date": "2026-10-01",
        "privacy": {
            "eu_review": "not_required",
        },
    }

    proposed = {
        "geography": ["US", "DE"],
        "launch_date": "2026-10-15",
        "privacy": {
            "eu_review": "required",
        },
        "localization": {
            "required": True,
        },
    }

    changes = detect_changes(baseline, proposed)

    assert changes == [
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
            "path": "localization",
            "previous_value": None,
            "proposed_value": {
                "required": True,
            },
            "change_type": "ADDED",
        },
        {
            "path": "privacy.eu_review",
            "previous_value": "not_required",
            "proposed_value": "required",
            "change_type": "MODIFIED",
        },
    ]


def test_detects_removed_fields():
    baseline = {
        "vendor": {
            "territory": "US",
            "legacy_clause": True,
        }
    }

    proposed = {
        "vendor": {
            "territory": "US",
        }
    }

    changes = detect_changes(baseline, proposed)

    assert changes == [
        {
            "path": "vendor.legacy_clause",
            "previous_value": True,
            "proposed_value": None,
            "change_type": "REMOVED",
        }
    ]


def test_no_change_returns_empty_list():
    state = {
        "scope": "US",
        "launch_date": "2026-10-01",
    }

    assert detect_changes(state, state) == []
