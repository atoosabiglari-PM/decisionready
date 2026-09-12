# DecisionReady

**A human-governed AI decision control system for complex program change.**

DecisionReady helps program managers, TPMs, governance teams, and executive sponsors determine whether a proposed project change has enough governed evidence to be decided - before a consequential human decision is made.

> Most AI assistants give leaders more information. DecisionReady asks whether there is enough governed evidence to make the decision at all.

## Live Demo

http://decisionready-atoosa.us-west-2.elasticbeanstalk.com

The deployed workspace supports a business-friendly Excel project upload, advanced JSON import, deterministic change analysis, governance completion, live Strands + Amazon Nova 2 Lite explanation, authorized human APPROVE / REJECT / DEFER, and baseline promotion.

## How It Works

```text
Project + Approved Baseline
            ↓
      Proposed Change
            ↓
 Deterministic Change Detection
            ↓
 Impact / Blast-Radius Analysis
            ↓
 Governance Requirements
 Evidence + Human Approvals
            ↓
 NOT_READY / READY / BLOCKED
            ↓
 Strands + Nova Executive Brief
            ↓
 Authorized Human Decision
 APPROVE / REJECT / DEFER
            ↓
 New Versioned Baseline + Audit Record
```

## Why DecisionReady Is Different

DecisionReady separates three responsibilities that should not be collapsed into one AI model:

- **Strands + Amazon Nova 2 Lite** explain and orchestrate.
- **The deterministic DecisionReady engine** owns change detection, impact domains, governance requirements, blockers, readiness, and baseline promotion rules.
- **Authorized humans** own consequential decisions. `READY` never means `APPROVED`.

The language model can help people understand the decision package without being allowed to redefine the authoritative readiness result or approve the change.

## Core Capabilities

- Establish an approved project baseline
- Submit a proposed project change
- Import a business-friendly `.xlsx` project workbook
- Import/export structured JSON for advanced integrations
- Detect field-level changes against the approved baseline
- Trace blast radius across scope, schedule, privacy, security, cost, vendors, contracts, compliance, architecture, dependencies, milestones, risks, and resources
- Derive required governance evidence and human approvals
- Evaluate `READY`, `NOT_READY`, or `BLOCKED`
- Generate a live executive explanation through Strands + Amazon Nova 2 Lite on Amazon Bedrock
- Capture human evidence sources and named approvers
- Allow an authorized human to `APPROVE`, `REJECT`, or `DEFER`
- Promote only `READY + APPROVED` changes into the next versioned baseline
- Preserve an auditable change log and decision report

## Germany Demo Scenario

The primary demo models a global product launch expanding from the United States into Germany.

**Approved Baseline v1**

- Geography: United States
- Launch date: October 1, 2026
- EU privacy review: not required
- German localization: no

**Proposed change - CR-GER-001**

- Add Germany while retaining the U.S. launch
- Move the launch date to October 15, 2026
- Require EU privacy review
- Require German localization

DecisionReady deterministically detects four changes and derives governance requirements including privacy evidence, schedule evidence, Privacy / Legal approval, and Program Sponsor approval. The change remains `NOT_READY` until those requirements are satisfied. Once the deterministic state becomes `READY`, an authorized human may approve, reject, or defer the change. An approval then creates the next governed baseline.

A ready-to-use workbook is included at:

`demo_data/DecisionReady_Germany_Project_Demo.xlsx`

## Architecture

![DecisionReady Architecture](docs/evidence/DecisionReady_Architecture.png)

Detailed architecture: [`docs/architecture.md`](docs/architecture.md)

## AWS + Agent Stack

- **Strands Agents SDK** - agent orchestration and tool use
- **Amazon Bedrock** - managed model runtime
- **Amazon Nova 2 Lite** - executive explanation model
- **AWS Elastic Beanstalk** - public application deployment
- **Streamlit** - web workspace
- **Python + Pydantic** - deterministic domain and governance logic

Default Bedrock model ID: `us.amazon.nova-2-lite-v1:0`

Default region: `us-west-2`

## Run Locally

Requires Python 3.13+.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m streamlit run workspace_app.py --server.address 0.0.0.0 --server.port 8080
```

## Tests

Current verified suite: **46 passing tests**.

The suite covers the deterministic decision engine, governance lifecycle, Strands/Nova integration helpers, project workspace behavior, and Excel import path.

## Trust Boundary

**AI may explain. AI may not approve.**

- The model cannot change authoritative readiness.
- Missing evidence or approvals are unmet requirements, not automatically blockers.
- `READY` means the configured governance threshold has been satisfied.
- Only an authorized human can make the final `APPROVED`, `REJECTED`, or `DEFERRED` decision.
- Only `READY + APPROVED` can create a new baseline.

## Current Prototype Scope

The deployed hackathon prototype supports end-to-end governed project-change analysis in a single application session, including Excel/JSON intake, governance completion, human decision, and baseline promotion. Persistent multi-user project storage and enterprise system connectors are natural next steps beyond the hackathon build.

## Repository Highlights

- `workspace_app.py` - public project workspace
- `src/decisionready/workspace.py` - user-submitted project lifecycle
- `src/decisionready/excel_import.py` - business-friendly Excel intake
- `src/decisionready/workflow.py` - deterministic decision preparation
- `src/decisionready/governance.py` - governance rules
- `src/decisionready/readiness.py` - authoritative readiness evaluation
- `src/decisionready/decision_lifecycle.py` - authorized human decision lifecycle
- `src/decisionready/agent.py` - Strands + Amazon Nova 2 Lite agent
- `demo_data/DecisionReady_Germany_Project_Demo.xlsx` - primary demo workbook
- `docs/architecture.md` - trust boundary and architecture
- `docs/evidence/` - submission evidence, screenshots, architecture image, and thumbnail

## License

Apache License 2.0
