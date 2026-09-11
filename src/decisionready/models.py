from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ImpactDomain(str, Enum):
    SCOPE = "scope"
    SCHEDULE = "schedule"
    COST = "cost"
    RESOURCES = "resources"
    SECURITY = "security"
    PRIVACY = "privacy"
    COMPLIANCE = "compliance"
    CONTRACTS = "contracts"
    VENDORS = "vendors"
    ARCHITECTURE = "architecture"
    DEPENDENCIES = "dependencies"
    MILESTONES = "milestones"
    RISKS = "risks"


class ReadinessState(str, Enum):
    NOT_READY = "NOT_READY"
    READY = "READY"
    BLOCKED = "BLOCKED"


class DecisionOutcome(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"


class Baseline(BaseModel):
    project_id: str
    version: int = Field(ge=1)
    name: str
    state: dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProposedChange(BaseModel):
    change_id: str
    project_id: str
    title: str
    description: str
    requested_by: str
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Impact(BaseModel):
    domain: ImpactDomain
    summary: str
    affected_items: list[str] = Field(default_factory=list)


class EvidenceRequirement(BaseModel):
    evidence_id: str
    description: str
    required: bool = True
    satisfied: bool = False
    source: str | None = None


class ApprovalRequirement(BaseModel):
    approval_id: str
    role: str
    required: bool = True
    approved: bool = False
    approver: str | None = None


class DecisionReadiness(BaseModel):
    state: ReadinessState
    evidence_required: int
    evidence_satisfied: int
    approvals_required: int
    approvals_satisfied: int
    open_blockers: list[str] = Field(default_factory=list)


class HumanDecision(BaseModel):
    change_id: str
    outcome: DecisionOutcome
    decided_by: str
    rationale: str
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChangeLogEntry(BaseModel):
    change_id: str
    previous_baseline_version: int
    new_baseline_version: int | None = None
    outcome: DecisionOutcome
    impacts: list[Impact] = Field(default_factory=list)
    decision_by: str
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
