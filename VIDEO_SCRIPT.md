# DecisionReady - 5 Minute Video Script

Target length: **4:30-4:50**. Do not exceed 5:00.

## 0:00-0:35 - Problem

"Program leaders rarely suffer from a lack of information. They suffer from uncertainty about whether there is enough governed evidence to make a consequential decision. Project changes are scattered across spreadsheets, documents, approvals, meetings, privacy reviews, schedules, and specialist teams. Most AI assistants summarize information. DecisionReady asks a harder question: is this decision actually ready to be made?"

## 0:35-0:55 - Who it is for / key idea

"DecisionReady is for program managers, TPMs, change boards, compliance teams, and executive sponsors. It separates AI explanation, deterministic governance, and human authority. AI may explain. AI may not approve."

Show the architecture image briefly.

## 0:55-1:35 - Upload the Germany project

Open Project Workspace.
Upload `DecisionReady_Germany_Project_Demo.xlsx`.
Click **Analyze uploaded project**.

"This workbook represents a normal program artifact: project context, the currently approved baseline, and a proposed change. The baseline is a U.S.-only launch on October 1. The change proposes adding Germany, moving the launch to October 15, requiring EU privacy review, and German localization."

## 1:35-2:25 - Deterministic analysis

Show the four detected changes, impact domains, evidence, approvals, and NOT_READY.

"DecisionReady deterministically compares the proposed state with the approved baseline. It detects exactly what changed, maps the blast radius, and derives governance requirements. Because privacy and schedule are affected, it requires privacy evidence, schedule evidence, Privacy/Legal approval, and Program Sponsor approval. The authoritative state is NOT_READY."

## 2:25-2:55 - Strands + Nova

Click **Generate live Strands + Nova brief**.

"The Strands agent calls the DecisionReady tool and Amazon Nova 2 Lite explains the authoritative result in executive language. The model is not allowed to invent or override the readiness state."

## 2:55-3:45 - Governance becomes READY

Enter the demo evidence and approvals:
- Privacy Impact Assessment PIA-DE-001
- Schedule Impact Analysis SIA-DE-001
- Privacy Counsel
- Program Sponsor

"Now the deterministic engine recalculates readiness. The change becomes READY. But READY does not mean APPROVED. It only means the configured governance threshold has been satisfied."

## 3:45-4:20 - Human decision + new baseline

Choose APPROVED.
Decision made by: Change Governance Board.
Record the decision.

"Only now can an authorized human approve the change. DecisionReady records the decision and promotes the approved proposed state into the next governed baseline. That new baseline becomes the reference point for the next future change."

Show audit trail and new baseline.

## 4:20-4:45 - Closing

"DecisionReady is not another chat interface. It is a governed decision system built with Strands Agents and Amazon Bedrock: project baseline, change detection, impact, governance, readiness, human authority, and auditability in one workflow. Build systems, not tool stacks."

End on thumbnail/title card + live URL + GitHub URL.
