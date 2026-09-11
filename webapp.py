import streamlit as st
from decisionready.agent import build_agent
from decisionready.demo_lifecycle import run_governed_demo
from decisionready.scenario import run_scenario

SCENARIO = "demo_data/germany_launch.json"

st.set_page_config(
    page_title="DecisionReady",
    page_icon="✅",
    layout="wide",
)

st.title("DecisionReady")
st.caption("Human-governed AI for complex program decisions")
st.info(
    "READY does not mean APPROVED. DecisionReady prepares consequential "
    "decisions; authorized humans make them."
)

prep = run_scenario(SCENARIO)
r = prep.readiness

a, b, c = st.columns(3)
a.metric("Readiness", r.state.value)
b.metric("Evidence", f"{r.evidence_satisfied}/{r.evidence_required}")
c.metric("Approvals", f"{r.approvals_satisfied}/{r.approvals_required}")

st.subheader("Impact domains")
st.write(", ".join(sorted(d.value for d in prep.impact_domains)))

left, right = st.columns(2)

with left:
    st.subheader("Required evidence")
    for item in prep.evidence:
        st.write(f"⏳ {item.evidence_id} — {item.description}")

with right:
    st.subheader("Required approvals")
    for item in prep.approvals:
        st.write(f"⏳ {item.approval_id} — {item.role}")

st.divider()
st.subheader("AI Executive Brief")

if st.button("Generate live Strands + Nova brief", type="primary"):
    with st.spinner("Analyzing with Amazon Nova 2 Lite..."):
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
            st.error("Live AI brief unavailable in this deployment.")
            st.caption(str(exc))

st.divider()
st.subheader("Governed Lifecycle")
st.caption(
    "Simulates completion of required evidence and approvals, then records "
    "an authorized human approval."
)

if st.button("Run full governed lifecycle"):
    result = run_governed_demo(SCENARIO)

    before, after = st.columns(2)

    with before:
        st.metric("Before", result["initial"]["readiness"])
        st.write(
            "Evidence "
            + result["initial"]["evidence"]
            + " · Approvals "
            + result["initial"]["approvals"]
        )
        st.write(f'Baseline v{result["initial"]["baseline_version"]}')

    with after:
        st.metric("After governance", result["final"]["readiness"])
        st.write("Human decision: " + result["final"]["human_decision"])
        st.write(
            "New baseline: v"
            + str(result["final"]["new_baseline_version"])
        )

    st.success(result["report"]["next_action"])

    with st.expander("Audit record"):
        st.json(result["audit"])

st.divider()
st.caption(
    "Strands Agents · Amazon Nova 2 Lite · Amazon Bedrock · "
    "Deterministic governance · Human authority"
)
