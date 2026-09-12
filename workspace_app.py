from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from decisionready.agent import build_agent
from decisionready.demo_lifecycle import run_governed_demo
from decisionready.excel_import import xlsx_to_document
from decisionready.models import DecisionOutcome
from decisionready.scenario import load_scenario, run_scenario
from decisionready.workspace import (
    analyze_submission,
    apply_governance_updates,
    lifecycle_to_dict,
    record_workspace_decision,
)

DEMO_SCENARIO = Path("demo_data/germany_launch.json")

SELF_PROJECT = {
    "scenario_name": "DecisionReady Hackathon Build",
    "industry": "AI / Program Management",
    "project": {"project_id": "DR-001", "name": "DecisionReady Hackathon Build"},
    "baseline": {
        "version": 1,
        "state": {
            "delivery_mode": "CLI demo",
            "hosting": "CloudShell",
            "architecture": {"web_ui": False, "human_governance": True},
            "security": {"bedrock_runtime_access": False},
            "tests": 46,
        },
    },
    "change": {
        "change_id": "DR-CR-001",
        "title": "Launch public governed project workspace",
        "description": (
            "Move DecisionReady from a fixed demo to a public workspace where "
            "PMs and TPMs can submit their own projects and changes."
        ),
        "requested_by": "Product Owner",
    },
    "proposed_state": {
        "delivery_mode": "Public web application",
        "hosting": "Elastic Beanstalk",
        "architecture": {"web_ui": True, "human_governance": True},
        "security": {"bedrock_runtime_access": True},
        "tests": 46,
    },
}

BLANK_PROJECT = {
    "scenario_name": "New Project",
    "industry": "Enterprise Program",
    "project": {"project_id": "PROJ-001", "name": "My Project"},
    "baseline": {
        "version": 1,
        "state": {
            "scope": "Current approved scope",
            "launch_date": "2026-10-01",
            "budget": 100000,
        },
    },
    "change": {
        "change_id": "CR-001",
        "title": "Proposed project change",
        "description": "Describe the proposed change and why it is needed.",
        "requested_by": "Program Manager",
    },
    "proposed_state": {
        "scope": "Updated proposed scope",
        "launch_date": "2026-10-15",
        "budget": 120000,
    },
}

st.set_page_config(
    page_title="DecisionReady",
    page_icon="DR",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .stApp{
        background:radial-gradient(circle at 8% 0%,rgba(42,109,246,.055),transparent 28%),
                   linear-gradient(180deg,#F8FAFD 0%,#FFFFFF 34%,#F7F9FC 100%);
        color:#172033;
      }
      .block-container{max-width:1220px;padding-top:1.7rem;padding-bottom:4rem}
      h1,h2,h3{color:#172033;letter-spacing:-.02em}
      .hero{
        background:linear-gradient(135deg,#0D1B2A 0%,#14263D 70%,#17395E 100%);
        color:white;padding:1.9rem 2.2rem;border-radius:24px;
        box-shadow:0 18px 50px rgba(17,39,67,.18);margin-bottom:1rem
      }
      .kicker{font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;color:#9FC2FF;font-weight:800}
      .hero-title{font-size:2.55rem;line-height:1.05;font-weight:850;margin-top:.35rem}
      .hero-sub{font-size:1rem;line-height:1.55;color:#D4DEEB;max-width:900px;margin-top:.65rem}
      .section{font-size:.72rem;color:#667085;text-transform:uppercase;letter-spacing:.11em;font-weight:800;margin-top:.4rem}
      .status{border-radius:17px;padding:1rem 1.1rem;border:1px solid #F1D28A;background:#FFF9EB}
      .status.ready{border-color:#9FDAB6;background:#EFFAF3}
      .status.blocked{border-color:#E8A6A6;background:#FFF2F2}
      .chip{display:inline-block;border-radius:999px;padding:.3rem .62rem;background:#FFE6A8;color:#7A4B00;font-size:.78rem;font-weight:800}
      .chip.ready{background:#CBF0D8;color:#17603B}
      .chip.blocked{background:#FFD6D6;color:#8D1A1A}
      .card{border:1px solid #E3E8F0;background:rgba(255,255,255,.97);border-radius:15px;padding:.85rem .95rem;margin-bottom:.65rem;box-shadow:0 5px 18px rgba(20,35,60,.035)}
      .muted{color:#667085;font-size:.9rem}
      .tag{display:inline-block;padding:.34rem .62rem;border-radius:999px;background:#EEF4FF;color:#2456A6;border:1px solid #D8E5FF;margin:.15rem .2rem .15rem 0;font-size:.82rem;font-weight:700}
      [data-testid="stMetric"]{background:rgba(255,255,255,.97);border:1px solid #E3E8F0;padding:1rem 1.05rem;border-radius:15px;box-shadow:0 8px 24px rgba(20,35,60,.04)}
      div.stButton>button{border-radius:12px;font-weight:750;min-height:2.8rem}
      div.stButton>button[kind="primary"]{background:#245DF5;border-color:#245DF5}
      .footer{margin-top:2rem;text-align:center;color:#7A8699;font-size:.78rem}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="kicker">Human-Governed Decision Control Plane</div>
      <div class="hero-title">DecisionReady</div>
      <div class="hero-sub">
        Submit a real project change. DecisionReady detects what changed,
        traces the blast radius, derives governance requirements, evaluates
        readiness, and preserves the consequential decision for an authorized human.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def load_form(doc: dict) -> None:
    st.session_state["f_scenario_name"] = doc.get("scenario_name", doc["project"]["name"])
    st.session_state["f_industry"] = doc.get("industry", "")
    st.session_state["f_project_id"] = doc["project"]["project_id"]
    st.session_state["f_project_name"] = doc["project"]["name"]
    st.session_state["f_baseline_version"] = int(doc["baseline"]["version"])
    st.session_state["f_change_id"] = doc["change"]["change_id"]
    st.session_state["f_change_title"] = doc["change"]["title"]
    st.session_state["f_change_description"] = doc["change"]["description"]
    st.session_state["f_requested_by"] = doc["change"]["requested_by"]
    st.session_state["f_baseline_state"] = json.dumps(doc["baseline"]["state"], indent=2)
    st.session_state["f_proposed_state"] = json.dumps(doc["proposed_state"], indent=2)


def form_document() -> dict:
    baseline_state = json.loads(st.session_state["f_baseline_state"])
    proposed_state = json.loads(st.session_state["f_proposed_state"])
    if not isinstance(baseline_state, dict) or not isinstance(proposed_state, dict):
        raise ValueError("Baseline and proposed state must each be a JSON object.")

    project_id = st.session_state["f_project_id"].strip()
    project_name = st.session_state["f_project_name"].strip()

    return {
        "scenario_name": st.session_state["f_scenario_name"].strip() or project_name,
        "industry": st.session_state["f_industry"].strip(),
        "project": {"project_id": project_id, "name": project_name},
        "baseline": {
            "version": int(st.session_state["f_baseline_version"]),
            "state": baseline_state,
        },
        "change": {
            "change_id": st.session_state["f_change_id"].strip(),
            "title": st.session_state["f_change_title"].strip(),
            "description": st.session_state["f_change_description"].strip(),
            "requested_by": st.session_state["f_requested_by"].strip(),
        },
        "proposed_state": proposed_state,
    }


def temp_scenario(doc: dict) -> str:
    temp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="decisionready-workspace-",
        delete=False,
        encoding="utf-8",
    )
    with temp:
        json.dump(doc, temp, indent=2)
    return temp.name


if "f_project_id" not in st.session_state:
    load_form(SELF_PROJECT)

workspace_tab, demo_tab = st.tabs(["Project Workspace", "Germany Demo"])

with workspace_tab:
    st.markdown('<div class="section">01 · Submit a project change</div>', unsafe_allow_html=True)
    st.header("Project Workspace")
    st.caption(
        "Business users can upload an Excel project workbook. JSON remains available "
        "for advanced integrations."
    )

    upload_left, upload_right = st.columns([0.72, 0.28])
    with upload_left:
        uploaded = st.file_uploader(
            "Upload project file",
            type=["xlsx", "json"],
            help=(
                "Recommended: DecisionReady Excel workbook (.xlsx). "
                "JSON is supported for system-to-system integrations."
            ),
        )
    with upload_right:
        demo_path = Path("demo_data/DecisionReady_Germany_Project_Demo.xlsx")
        if demo_path.exists():
            st.write("")
            st.download_button(
                "Download Germany demo Excel",
                data=demo_path.read_bytes(),
                file_name="DecisionReady_Germany_Project_Demo.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
            )

    if uploaded is not None and st.button(
        "Analyze uploaded project",
        type="primary",
        use_container_width=True,
    ):
        try:
            if uploaded.name.lower().endswith(".xlsx"):
                imported = xlsx_to_document(uploaded.getvalue())
            else:
                imported = json.loads(
                    uploaded.getvalue().decode("utf-8")
                )

            analysis = analyze_submission(imported)
            load_form(imported)
            st.session_state["workspace_payload"] = imported
            st.session_state.pop("workspace_lifecycle", None)

            for key in list(st.session_state):
                if key.startswith(("ev_", "ap_", "blocker_")):
                    del st.session_state[key]

            st.success(
                "Project imported. DecisionReady established the approved "
                "baseline and analyzed the proposed change."
            )
            st.rerun()
        except Exception as exc:
            st.error(f"Could not import project: {exc}")

    st.markdown(
        "**No JSON required.** The Excel workbook carries the project, approved "
        "baseline, and proposed change in familiar business tables."
    )

    show_manual = st.toggle(
        "Enter or edit a project manually (advanced)",
        value=False,
    )

    if show_manual:
        with st.form("project_form"):
            p1, p2, p3 = st.columns([1.2, 1.0, .55])
            with p1:
                st.text_input("Project name", key="f_project_name")
            with p2:
                st.text_input("Project ID", key="f_project_id")
            with p3:
                st.number_input("Baseline", min_value=1, step=1, key="f_baseline_version")
    
            p4, p5 = st.columns(2)
            with p4:
                st.text_input("Workspace / scenario", key="f_scenario_name")
            with p5:
                st.text_input("Industry / program type", key="f_industry")
    
            st.markdown("#### Proposed change")
            x1, x2 = st.columns(2)
            with x1:
                st.text_input("Change ID", key="f_change_id")
                st.text_input("Requested by", key="f_requested_by")
            with x2:
                st.text_input("Change title", key="f_change_title")
                st.text_area("Why is this change needed?", key="f_change_description", height=100)
    
            st.markdown("#### Advanced structured baseline → proposed state")
            st.caption(
                "Use structured project facts such as scope, launch_date, budget, privacy, "
                "security, vendor, contract, architecture, milestone, dependency, risk, or compliance."
            )
            s1, s2 = st.columns(2)
            with s1:
                st.text_area("Current approved baseline data", key="f_baseline_state", height=290)
            with s2:
                st.text_area("Proposed state data", key="f_proposed_state", height=290)
    
            submitted = st.form_submit_button(
                "Submit project for DecisionReady analysis",
                type="primary",
                use_container_width=True,
            )
    
        if submitted:
            try:
                doc = form_document()
                analysis = analyze_submission(doc)
                st.session_state["workspace_payload"] = doc
                st.session_state.pop("workspace_lifecycle", None)
                for key in list(st.session_state):
                    if key.startswith(("ev_", "ap_", "blocker_")):
                        del st.session_state[key]
                if analysis.preparation.detected_changes:
                    st.success("Project submitted. DecisionReady created the authoritative change-readiness package.")
                else:
                    st.warning("Project submitted, but no baseline delta was detected.")
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON: line {exc.lineno}, column {exc.colno}.")
            except Exception as exc:
                st.error(str(exc))
    
    if "workspace_payload" in st.session_state:
        doc = st.session_state["workspace_payload"]
        analysis = analyze_submission(doc)
        prep = analysis.preparation
        initial = prep.readiness

        st.divider()
        st.markdown('<div class="section">02 · Authoritative analysis</div>', unsafe_allow_html=True)
        st.header(doc["project"]["name"])

        css = "ready" if initial.state.value == "READY" else "blocked" if initial.state.value == "BLOCKED" else ""
        st.markdown(
            f"""
            <div class="status {css}">
              <span class="chip {css}">{initial.state.value}</span>
              <div style="font-weight:800;font-size:1.08rem;margin-top:.55rem">
                {doc["change"]["change_id"]} · {doc["change"]["title"]}
              </div>
              <div class="muted">READY means governance conditions are satisfied. It does not mean APPROVED.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Evidence", f"{initial.evidence_satisfied}/{initial.evidence_required}")
        m2.metric("Approvals", f"{initial.approvals_satisfied}/{initial.approvals_required}")
        m3.metric("Detected changes", len(prep.detected_changes))
        m4.metric("Impact domains", len(prep.impact_domains))

        left, right = st.columns([1.05, .95], gap="large")
        with left:
            st.subheader("What changed")
            for item in prep.detected_changes:
                label = item["path"].replace(".", " › ").replace("_", " ").title()
                st.markdown(
                    f"""<div class="card"><strong>{label}</strong>
                    <div class="muted">{item["previous_value"]} → {item["proposed_value"]} · {item["change_type"]}</div></div>""",
                    unsafe_allow_html=True,
                )
            st.subheader("Blast radius")
            tags = "".join(
                f'<span class="tag">{domain.value.upper()}</span>'
                for domain in sorted(prep.impact_domains, key=lambda item: item.value)
            )
            st.markdown(tags or "No impacts detected.", unsafe_allow_html=True)

        with right:
            st.subheader("Governance threshold")
            if not prep.evidence and not prep.approvals:
                st.info("No evidence or approval rule is triggered by the current deterministic policy.")
            for item in prep.evidence:
                st.markdown(
                    f'<div class="card"><strong>{item.evidence_id}</strong><div class="muted">{item.description}</div></div>',
                    unsafe_allow_html=True,
                )
            for item in prep.approvals:
                st.markdown(
                    f'<div class="card"><strong>{item.approval_id}</strong><div class="muted">{item.role} approval</div></div>',
                    unsafe_allow_html=True,
                )

        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "Export project package",
                data=json.dumps(doc, indent=2),
                file_name=f'{doc["project"]["project_id"]}.decisionready.json',
                mime="application/json",
                use_container_width=True,
            )
        with d2:
            ai_clicked = st.button(
                "Generate live Strands + Nova brief",
                type="primary",
                use_container_width=True,
                key="workspace_ai",
            )

        if ai_clicked:
            path = temp_scenario(doc)
            try:
                with st.spinner("Running submitted project through Strands + Amazon Nova 2 Lite..."):
                    agent = build_agent()
                    response = agent(
                        "Analyze this user-submitted DecisionReady scenario using the authoritative "
                        "DecisionReady tool. Explain detected changes, impacts, governance requirements, "
                        "blockers, readiness state, and recommended next actions. "
                        f"Scenario path: {path}"
                    )
                    st.markdown(str(response))
            except Exception as exc:
                st.error(f"Live AI brief failed: {exc}")
            finally:
                Path(path).unlink(missing_ok=True)

        st.divider()
        st.markdown('<div class="section">03 · Governance workspace</div>', unsafe_allow_html=True)
        st.header("Satisfy evidence and approvals")
        st.caption(
            "Human-entered governance controls. Evidence only counts with a source; "
            "approval only counts with a named approver."
        )

        evidence_updates = {}
        approval_updates = {}
        e_col, a_col = st.columns(2, gap="large")

        with e_col:
            st.subheader("Evidence")
            if not prep.evidence:
                st.caption("No evidence required.")
            for item in prep.evidence:
                sat = st.checkbox(
                    f"{item.evidence_id} · {item.description}",
                    key=f"ev_sat_{analysis.change.change_id}_{item.evidence_id}",
                )
                source = st.text_input(
                    f"Source for {item.evidence_id}",
                    key=f"ev_src_{analysis.change.change_id}_{item.evidence_id}",
                    placeholder="e.g. Security Impact Assessment SEC-014",
                )
                evidence_updates[item.evidence_id] = {"satisfied": sat, "source": source}

        with a_col:
            st.subheader("Approvals")
            if not prep.approvals:
                st.caption("No approvals required.")
            for item in prep.approvals:
                approved = st.checkbox(
                    f"{item.approval_id} · {item.role}",
                    key=f"ap_ok_{analysis.change.change_id}_{item.approval_id}",
                )
                approver = st.text_input(
                    f"Named approver for {item.approval_id}",
                    key=f"ap_who_{analysis.change.change_id}_{item.approval_id}",
                    placeholder=f"e.g. {item.role} owner",
                )
                approval_updates[item.approval_id] = {"approved": approved, "approver": approver}

        blockers_text = st.text_area(
            "Explicit blockers (optional, one per line)",
            key=f"blocker_{analysis.change.change_id}",
            height=85,
        )
        blockers = [line.strip() for line in blockers_text.splitlines() if line.strip()]

        evidence, approvals, current = apply_governance_updates(
            analysis,
            evidence_updates=evidence_updates,
            approval_updates=approval_updates,
            blockers=blockers,
        )

        css = "ready" if current.state.value == "READY" else "blocked" if current.state.value == "BLOCKED" else ""
        st.markdown(
            f"""
            <div class="status {css}">
              <span class="chip {css}">{current.state.value}</span>
              <div style="margin-top:.5rem;font-weight:750">
                Evidence {current.evidence_satisfied}/{current.evidence_required}
                · Approvals {current.approvals_satisfied}/{current.approvals_required}
                · Blockers {len(current.open_blockers)}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown('<div class="section">04 · Authorized human decision</div>', unsafe_allow_html=True)
        st.header("Approve, reject, or defer")

        if current.state.value == "READY":
            outcomes = ["APPROVED", "REJECTED", "DEFERRED"]
        else:
            outcomes = ["DEFERRED", "REJECTED"]
            st.info("APPROVE is locked until the deterministic readiness state is READY.")

        h1, h2 = st.columns([.4, .6])
        with h1:
            outcome_text = st.selectbox("Decision", outcomes, key=f"decision_{analysis.change.change_id}")
            decided_by = st.text_input(
                "Decision made by",
                key=f"decision_by_{analysis.change.change_id}",
                placeholder="Authorized human / governance body",
            )
        with h2:
            rationale = st.text_area(
                "Decision rationale",
                key=f"decision_reason_{analysis.change.change_id}",
                height=125,
            )

        if st.button(
            "Record governed human decision",
            type="primary",
            use_container_width=True,
            key="record_decision",
        ):
            try:
                result = record_workspace_decision(
                    analysis,
                    evidence=evidence,
                    approvals=approvals,
                    readiness=current,
                    outcome=DecisionOutcome(outcome_text),
                    decided_by=decided_by,
                    rationale=rationale,
                )
                st.session_state["workspace_lifecycle"] = lifecycle_to_dict(result)
                st.success(result.report.next_action)
            except Exception as exc:
                st.error(str(exc))

        if "workspace_lifecycle" in st.session_state:
            result = st.session_state["workspace_lifecycle"]
            st.subheader("Governed decision record")
            q1, q2, q3 = st.columns(3)
            q1.metric("Outcome", result["decision"]["outcome"])
            q2.metric("Previous baseline", f'v{result["previous_baseline"]["version"]}')
            q3.metric(
                "New baseline",
                f'v{result["new_baseline"]["version"]}' if result["new_baseline"] else "Retained",
            )
            with st.expander("Audit record", expanded=True):
                st.json(result["change_log"])
            if result["new_baseline"]:
                with st.expander("New governed baseline", expanded=True):
                    st.json(result["new_baseline"])
            st.download_button(
                "Export governed decision record",
                data=json.dumps(result, indent=2),
                file_name=f'{doc["project"]["project_id"]}-{doc["change"]["change_id"]}-decision.json',
                mime="application/json",
                use_container_width=True,
            )

with demo_tab:
    st.markdown('<div class="section">Reference demo</div>', unsafe_allow_html=True)
    st.header("Germany product-launch scenario")
    data = load_scenario(DEMO_SCENARIO)
    prep = run_scenario(DEMO_SCENARIO)
    r = prep.readiness

    g1, g2, g3 = st.columns(3)
    g1.metric("Initial readiness", r.state.value)
    g2.metric("Evidence", f"{r.evidence_satisfied}/{r.evidence_required}")
    g3.metric("Approvals", f"{r.approvals_satisfied}/{r.approvals_required}")

    if st.button("Generate Germany Strands + Nova brief", use_container_width=True):
        try:
            with st.spinner("Analyzing with Amazon Nova 2 Lite..."):
                agent = build_agent()
                response = agent(
                    "Analyze this DecisionReady scenario using the authoritative DecisionReady tool. "
                    "Explain the change, impacts, governance requirements, blockers, readiness state, "
                    f"and next actions. Scenario path: {DEMO_SCENARIO}"
                )
                st.markdown(str(response))
        except Exception as exc:
            st.error(str(exc))

    if st.button("Run Germany governed lifecycle demo", type="primary", use_container_width=True):
        result = run_governed_demo(DEMO_SCENARIO)
        before, after = st.columns(2)
        before.metric("Before", result["initial"]["readiness"])
        after.metric("After governance", result["final"]["readiness"])
        st.success(result["report"]["next_action"])
        with st.expander("Audit record", expanded=True):
            st.json(result["audit"])
        with st.expander("New governed baseline"):
            st.json(result["final"]["new_baseline_state"])

st.markdown(
    '<div class="footer">DecisionReady · Strands Agents · Amazon Nova 2 Lite · Amazon Bedrock · Deterministic governance · Human authority</div>',
    unsafe_allow_html=True,
)
