from decisionready.governance import derive_governance_requirements
from decisionready.models import ImpactDomain


def test_privacy_domain_requires_privacy_evidence_and_approval():
    evidence, approvals = derive_governance_requirements(
        {ImpactDomain.PRIVACY}
    )

    assert len(evidence) == 1
    assert evidence[0].evidence_id == "E-PRIVACY"
    assert evidence[0].description == "Privacy impact assessment"
    assert evidence[0].satisfied is False

    assert len(approvals) == 1
    assert approvals[0].approval_id == "A-PRIVACY"
    assert approvals[0].role == "Privacy / Legal"
    assert approvals[0].approved is False


def test_multiple_domains_create_multiple_requirements():
    evidence, approvals = derive_governance_requirements(
        {
            ImpactDomain.PRIVACY,
            ImpactDomain.COST,
            ImpactDomain.SCHEDULE,
        }
    )

    evidence_ids = {item.evidence_id for item in evidence}
    approval_ids = {item.approval_id for item in approvals}

    assert evidence_ids == {
        "E-PRIVACY",
        "E-COST",
        "E-SCHEDULE",
    }

    assert approval_ids == {
        "A-PRIVACY",
        "A-FINANCE",
        "A-PROGRAM",
    }


def test_unmapped_domain_creates_no_governance_requirement():
    evidence, approvals = derive_governance_requirements(
        {ImpactDomain.SCOPE}
    )

    assert evidence == []
    assert approvals == []


def test_duplicate_domains_do_not_duplicate_requirements():
    domains = {
        ImpactDomain.SECURITY,
        ImpactDomain.SECURITY,
    }

    evidence, approvals = derive_governance_requirements(domains)

    assert len(evidence) == 1
    assert len(approvals) == 1
