# DecisionReady Architecture

DecisionReady separates AI reasoning, deterministic governance, and human authority.

## Architecture

```mermaid
flowchart TD
    U[Program Manager] --> S[Strands Agent]
    S <--> N[Amazon Nova 2 Lite / Bedrock]
    S --> D[DecisionReady Tool]

    D --> C[Change Detection]
    C --> I[Impact Analysis]
    I --> G[Governance Requirements]
    G --> R[Readiness Evaluation]

    R -->|NOT_READY / BLOCKED| S
    R -->|READY| H[Authorized Human Decision]

    H -->|APPROVED + READY| B[New Versioned Baseline]
    H -->|APPROVED / REJECTED / DEFERRED| L[Change Log]

    B --> P[Decision Report]
    L --> P
```

## Trust Boundary
**AI:** Strands + Nova explain and orchestrate.
**DecisionReady:** deterministic rules own readiness, evidence, approvals, blockers, and baseline promotion.
**Human:** READY does not mean APPROVED. Only an authorized human can approve the change.

## Germany Demo
Baseline v12 -> NOT_READY -> governance satisfied -> READY -> human APPROVED -> baseline v13.
