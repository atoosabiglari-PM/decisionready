import json
from pathlib import Path

import streamlit as st

from decisionready.agent import build_agent
from decisionready.demo_lifecycle import run_governed_demo
from decisionready.scenario import load_scenario, run_scenario

SCENARIO = Path("demo_data/germany_launch.json")

st.set_page_config(
    page_title="DecisionReady",
    page_icon="DR",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at 10% 0%, rgba(42, 109, 246, 0.06), transparent 28%),
                linear-gradient(180deg, #F8FAFD 0%, #FFFFFF 34%, #F7F9FC 100%);
            color: #172033;
        }

        .block-container {
            max-width: 1220px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            color: #172033;
            letter-spacing: -0.02em;
        }

        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.96);
            border: 1px solid #E3E8F0;
            padding: 1rem 1.1rem;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(20, 35, 60, 0.05);
        }

        [data-testid="stMetricLabel"] {
            color: #667085;
        }

        [data-testid="stMetricValue"] {
            color: #172033;
        }

        .dr-hero {
            background: linear-gradient(135deg, #0D1B2A 0%, #14263D 72%, #17395E 100%);
            color: white;
            padding: 2rem 2.25rem;
            border-radius: 24px;
            box-shadow: 0 18px 50px rgba(17, 39, 67, 0.18);
            margin-bottom: 1.2rem;
        }

        .dr-kicker {
            font-size: 0.78rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #9FC2FF;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }

        .dr-title {
            font-size: 2.6rem;
            line-height: 1.04;
            font-weight: 800;
            margin: 0;
        }

        .dr-subtitle {
            font-size: 1.02rem;
            line-height: 1.55;
            color: #D4DEEB;
            max-width: 850px;
            margin-top: 0.75rem;
            margin-bottom: 0;
        }

        .dr-context {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.7rem;
            margin-top: 1.4rem;
        }

        .dr-context-item {
            padding: 0.8rem 0.9rem;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.055);
            border-radius: 13px;
        }

        .dr-context-label {
            color: #AFC0D3;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .dr-context-value {
            color: white;
            margin-top: 0.25rem;
            font-weight: 650;
        }

        .dr-panel {
            background: rgba(255,255,255,0.96);
            border: 1px solid #E3E8F0;
            border-radius: 18px;
            padding: 1.2rem 1.25rem;
            box-shadow: 0 8px 24px rgba(20, 35, 60, 0.04);
            min-height: 100%;
        }

        .dr-section-label {
            font-size: 0.73rem;
            color: #667085;
            text-transform: uppercase;
            letter-spacing: 0.11em;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .dr-panel-title {
            font-size: 1.05rem;
            color: #172033;
            font-weight: 750;
            margin-bottom: 0.85rem;
        }

        .dr-status {
            border-radius: 18px;
            padding: 1.2rem 1.3rem;
            border: 1px solid #F1D28A;
            background: linear-gradient(180deg, #FFF9EB 0%, #FFFDF7 100%);
            margin-bottom: 1rem;
        }

        .dr-status-ready {
            border-color: #9FDAB6;
            background: linear-gradient(180deg, #EFFAF3 0%, #FBFFFC 100%);
        }

        .dr-status-blocked {
            border-color: #E8A6A6;
            background: linear-gradient(180deg, #FFF2F2 0%, #FFF9F9 100%);
        }

        .dr-status-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            border-radius: 999px;
            padding: 0.35rem 0.65rem;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.04em;
        }

        .chip-not-ready {
            background: #FFE6A8;
            color: #7A4B00;
        }

        .chip-ready {
            background: #CBF0D8;
            color: #17603B;
        }

        .chip-blocked {
            background: #FFD6D6;
            color: #8D1A1A;
        }

        .dr-check {
            border: 1px solid #E5EAF1;
            background: #FAFBFD;
            border-radius: 12px;
            padding: 0.75rem 0.85rem;
            margin-bottom: 0.6rem;
        }

        .dr-check strong {
            color: #172033;
        }

        .dr-muted {
            color: #667085;
            font-size: 0.9rem;
        }

        .dr-tag {
            display: inline-block;
            padding: 0.34rem 0.62rem;
            border-radius: 999px;
            background: #EEF4FF;
            color: #2456A6;
            border: 1px solid #D8E5FF;
            margin: 0.18rem 0.22rem 0.18rem 0;
            font-size: 0.82rem;
            font-weight: 650;
        }

        .dr-timeline {
            border-left: 2px solid #D8E3F2;
            padding-left: 1rem;
            margin-left: 0.25rem;
        }

        .dr-timeline-step {
            margin: 0.7rem 0;
            color: #344054;
        }

        .dr-timeline-step b {
            color: #172033;
        }

        .dr-human {
            border: 1px solid #CAD8EA;
            border-radius: 18px;
            padding: 1.1rem 1.2rem;
            background: #F8FBFF;
        }

        div.stButton > button {
            border-radius: 12px;
            font-weight: 700;
            padding: 0.7rem 1rem;
        }

        div.stButton > button[kind="primary"] {
            background: #245DF5;
            border-color: #245DF5;
        }

        .dr-footer {
            margin-top: 2rem;
            text-align: center;
            color: #7A8699;
            font-size: 0.78rem;
        }

        @media (max-width: 900px) {
            .dr-context {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .dr-title {
                font-size: 2.1rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

data = load_scenario(SCENARIO)
prep = run_scenario(SCENARIO)
r = prep.readiness

project_name = data["project"]["name"]
change_id = data["change"]["change_id"]
change_title = data["change"]["title"]
baseline_version = data["baseline"]["version"]
requested_by = data["change"]["requested_by"]

status_class = {
    "READY": "dr-status dr-status-ready",
    "BLOCKED": "dr-status dr-status-blocked",
}.get(r.state.value, "dr-status")

chip_class = {
    "READY": "dr-status-chip chip-ready",
    "BLOCKED": "dr-status-chip chip-blocked",
}.get(r.state.value, "dr-status-chip chip-not-ready")

st.markdown(
    f"""
    <div class="dr-hero">
        <div class="dr-kicker">Decision Control Plane</div>
        <div class="dr-title">DecisionReady</div>
        <p class="dr-subtitle">
            Know when there is enough governed evidence to decide.
            AI prepares the decision. Deterministic controls establish readiness.
            Authorized humans make the consequential decision.
        </p>
        <div class="dr-context">
            <div class="dr-context-item">
                <div class="dr-context-label">Program</div>
                <div class="dr-context-value">{project_name}</div>
            </div>
            <div class="dr-context-item">
                <div class="dr-context-label">Change</div>
                <div class="dr-context-value">{change_id}</div>
            </div>
            <div class="dr-context-item">
                <div class="dr-context-label">Baseline</div>
                <div class="dr-context-value">v{baseline_version}</div>
            </div>
            <div class="dr-context-item">
                <div class="dr-context-label">Requested by</div>
                <div class="dr-context-value">{requested_by}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="{status_class}">
        <div class="dr-section-label">Current Decision Readiness</div>
        <span class="{chip_class}">{r.state.value}</span>
        <div style="margin-top:.65rem;font-size:1.08rem;font-weight:750;color:#172033">
            {change_title}
        </div>
        <div class="dr-muted" style="margin-top:.35rem">
            READY means governance conditions are satisfied. It does not mean APPROVED.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Evidence", f"{r.evidence_satisfied}/{r.evidence_required}")
m2.metric("Approvals", f"{r.approvals_satisfied}/{r.approvals_required}")
m3.metric("Impact domains", len(prep.impact_domains))
m4.metric("Open blockers", len(r.open_blockers))

st.write("")
left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.markdown(
        '<div class="dr-section-label">01 · Change Intelligence</div>',
        unsafe_allow_html=True,
    )
    st.subheader("What changed")

    for item in prep.detected_changes:
        previous = item.get("previous_value")
        proposed = item.get("proposed_value")
        label = item["path"].replace(".", " › ").replace("_", " ").title()

        extra = ""
        temporal = item.get("temporal_change")
        if temporal:
            extra = f' · {temporal["days"]} days {temporal["direction"].lower()}'

        st.markdown(
            f"""
            <div class="dr-check">
                <strong>{label}</strong><br/>
                <span class="dr-muted">{previous} → {proposed}{extra}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="dr-section-label" style="margin-top:1.2rem">02 · Blast Radius</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Impact domains")

    tags = "".join(
        f'<span class="dr-tag">{domain.value.upper()}</span>'
        for domain in sorted(prep.impact_domains, key=lambda x: x.value)
    )
    st.markdown(tags, unsafe_allow_html=True)

with right:
    st.markdown(
        '<div class="dr-section-label">03 · Governance Threshold</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Evidence & approvals")

    st.markdown(
        '<div class="dr-panel-title">Required evidence</div>',
        unsafe_allow_html=True,
    )
    for item in prep.evidence:
        icon = "✅" if item.satisfied else "⏳"
        st.markdown(
            f"""
            <div class="dr-check">
                {icon} <strong>{item.evidence_id}</strong><br/>
                <span class="dr-muted">{item.description}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="dr-panel-title" style="margin-top:1rem">Required approvals</div>',
        unsafe_allow_html=True,
    )
    for item in prep.approvals:
        icon = "✅" if item.approved else "⏳"
        st.markdown(
            f"""
            <div class="dr-check">
                {icon} <strong>{item.approval_id}</strong><br/>
                <span class="dr-muted">{item.role}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

st.markdown(
    '<div class="dr-section-label">04 · AI Executive Brief</div>',
    unsafe_allow_html=True,
)
st.subheader("Explain the decision package")

st.caption(
    "Amazon Nova 2 Lite explains the authoritative DecisionReady result. "
    "The model does not set readiness or approve the change."
)

if st.button("Generate live Strands + Nova brief", type="primary", use_container_width=True):
    with st.spinner("Running DecisionReady through Strands + Amazon Nova 2 Lite..."):
        try:
            agent = build_agent()
            response = agent(
                "Analyze this DecisionReady scenario using the authoritative "
                "DecisionReady tool. Explain the change, impacts, governance "
                "requirements, blockers, readiness state, and next actions. "
                f"Scenario path: {SCENARIO}"
            )
            st.markdown(str(response))
        except Exception as exc:
            st.error(
                "The deterministic DecisionReady demo is available, but this "
                "deployment cannot currently reach the Bedrock model."
            )
            with st.expander("Technical detail"):
                st.code(str(exc))

st.divider()

st.markdown(
    '<div class="dr-section-label">05 · Human-Governed Lifecycle</div>',
    unsafe_allow_html=True,
)
st.subheader("From proposal to governed baseline")

c1, c2 = st.columns([0.65, 0.35], gap="large")

with c1:
    st.markdown(
        """
        <div class="dr-timeline">
            <div class="dr-timeline-step"><b>Baseline v12</b> · approved U.S. launch</div>
            <div class="dr-timeline-step"><b>CR-017</b> · Germany expansion proposed</div>
            <div class="dr-timeline-step"><b>NOT_READY</b> · evidence and approvals outstanding</div>
            <div class="dr-timeline-step"><b>Governance work</b> · evidence + approvals completed</div>
            <div class="dr-timeline-step"><b>READY</b> · eligible for human governance decision</div>
            <div class="dr-timeline-step"><b>Human decision</b> · APPROVE / REJECT / DEFER</div>
            <div class="dr-timeline-step"><b>Baseline v13</b> · only after READY + human APPROVED</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="dr-human">
            <div class="dr-section-label">Human Authority</div>
            <div style="font-weight:800;font-size:1.05rem;color:#172033">
                READY ≠ APPROVED
            </div>
            <div class="dr-muted" style="margin-top:.45rem">
                DecisionReady prepares and governs the package.
                The authorized human retains the consequential decision.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

if st.button("Run governed lifecycle demo", type="primary", use_container_width=True):
    result = run_governed_demo(SCENARIO)

    st.success(
        "Governance requirements satisfied. Human decision recorded. "
        f'Baseline v{result["final"]["new_baseline_version"]} is now active.'
    )

    before, after = st.columns(2)

    with before:
        st.markdown("#### Before")
        st.metric("Readiness", result["initial"]["readiness"])
        st.write(
            f'Evidence **{result["initial"]["evidence"]}** · '
            f'Approvals **{result["initial"]["approvals"]}**'
        )
        st.caption(f'Baseline v{result["initial"]["baseline_version"]}')

    with after:
        st.markdown("#### After governance")
        st.metric("Readiness", result["final"]["readiness"])
        st.write(f'Human decision **{result["final"]["human_decision"]}**')
        st.caption(
            f'New baseline v{result["final"]["new_baseline_version"]}'
        )

    st.markdown("#### Audit trail")
    st.json(result["audit"])

    with st.expander("New governed baseline"):
        st.json(result["final"]["new_baseline_state"])

st.markdown(
    """
    <div class="dr-footer">
        DecisionReady · Strands Agents · Amazon Nova 2 Lite · Amazon Bedrock ·
        Deterministic governance · Human authority
    </div>
    """,
    unsafe_allow_html=True,
)
