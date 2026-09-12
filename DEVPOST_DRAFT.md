# DecisionReady - Devpost Draft

## Project title
DecisionReady

## Tagline
Know when there is enough governed evidence to decide.

## Track
Professional Agents

## What it does
DecisionReady is a human-governed AI decision control system for complex program change. It helps program managers, TPMs, governance teams, and executive sponsors determine whether a proposed change is actually ready for a consequential human decision.

A user provides an approved project baseline and a proposed change through a business-friendly Excel workbook or structured JSON. DecisionReady deterministically detects what changed, traces the blast radius across governed project domains, derives required evidence and approvals, and calculates an authoritative readiness state: READY, NOT_READY, or BLOCKED.

A Strands agent backed by Amazon Nova 2 Lite on Amazon Bedrock explains the authoritative result in executive language. The model cannot override readiness and cannot approve the change. Authorized humans supply evidence, record named approvals, and make the final APPROVE / REJECT / DEFER decision. Only a READY + APPROVED change can become the next versioned project baseline, with an audit record preserved.

## Inspiration
Program leaders often have plenty of information but still cannot answer a more important question: do we have enough governed evidence to responsibly make this decision? Project changes are spread across documents, meetings, spreadsheets, approvals, risk reviews, and specialist teams. Traditional AI assistants can summarize that information, but summarization is not governance.

DecisionReady was built around a different question: not "What does the information say?" but "Is this decision ready to be made?"

## How we built it
The system uses Strands Agents SDK for model/tool orchestration and Amazon Nova 2 Lite through Amazon Bedrock for executive explanation. The agent is constrained to call the deterministic DecisionReady analysis tool before assessing a scenario.

The Python decision engine separately owns baseline comparison, change detection, impact mapping, governance rules, evidence requirements, approval requirements, blockers, readiness evaluation, human decision lifecycle, baseline promotion, reporting, and audit history.

The web experience is built with Streamlit and deployed publicly through AWS Elastic Beanstalk. Business users can upload an Excel workbook containing Project, Approved Baseline, and Proposed Change sheets. JSON remains available as an advanced integration path.

## Why the architecture matters
We deliberately separated model intelligence from decision authority:

- Strands + Nova explain and orchestrate.
- Deterministic DecisionReady controls establish readiness.
- Humans make consequential decisions.

READY never means APPROVED.

## Demo scenario
The demo begins with an approved U.S. product-launch baseline. A change proposes adding Germany, moving the launch date, requiring EU privacy review, and adding German localization. DecisionReady detects four changes, identifies privacy/schedule/resource/scope impacts, and derives the required evidence and approvals. The change remains NOT_READY until governance work is satisfied. It then becomes READY, and only an authorized human can approve it and create the next baseline.

## Challenges
The hardest design problem was preventing the language model from becoming the source of truth for governance. We solved this by creating a strict trust boundary: deterministic rules own readiness and baseline promotion, while the model only explains authoritative tool output. We also added deterministic temporal semantics after observing that a model could describe a later date incorrectly without explicit date-direction metadata.

## Accomplishments
- End-to-end governed decision lifecycle
- Strands tool calling with Amazon Nova 2 Lite on Bedrock
- Deterministic READY / NOT_READY / BLOCKED logic
- Human-only APPROVE / REJECT / DEFER authority
- Versioned baseline promotion and audit trail
- Business-friendly Excel intake
- Public AWS deployment
- 46 passing tests

## What we learned
Agentic systems are more trustworthy when the model is powerful where language and orchestration help, while deterministic controls remain authoritative where governance and state transitions matter. The system design became stronger when we treated AI, rules, and human authority as three separate layers.

## What's next
- Persistent multi-user project workspaces
- Native project creation forms with guided baseline establishment
- Enterprise integrations with project, ticketing, ERP, document, and governance systems
- Role-based authorization and approval routing
- Configurable governance policies by organization and project type
- Longitudinal portfolio-level decision intelligence

## Built with
Python, Strands Agents SDK, Amazon Bedrock, Amazon Nova 2 Lite, Streamlit, Pydantic, AWS Elastic Beanstalk, Excel/JSON project intake.

## Links
Public code: https://github.com/atoosabiglari-PM/decisionready
Live demo: http://decisionready-atoosa.us-west-2.elasticbeanstalk.com
Video: [ADD PUBLIC YOUTUBE/VIMEO URL]
AWS Builder ID: [ADD BUILDER ID EMAIL]
