"""Guided CMMC Level 1 self-assessment questionnaire.

Run locally:   streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cmmc_kit import __version__, evaluate, load_practices, parse_answers  # noqa: E402
from cmmc_kit.engine import MET, DataError  # noqa: E402
from cmmc_kit.reporting import DISCLAIMER, ssp_html, ssp_markdown, to_csv, to_html  # noqa: E402

S = ROOT / "samples"
CATALOG = load_practices()
DOMAINS = list(CATALOG["domains"].items())  # [(code, name), ...]
STEPS = ["Company profile"] + [name for _, name in DOMAINS] + ["Results"]
LABELS = {"yes": "Yes", "partial": "Partly", "no": "No", "na": "N/A"}
REVERSE = {v: k for k, v in LABELS.items()}
ORG_FIELDS = [
    ("name", "Company name", "text"), ("cage_code", "CAGE code (optional)", "text"),
    ("senior_official", "Senior official who will affirm the results", "text"),
    ("point_of_contact", "Point of contact for this assessment", "text"),
    ("system_name", "Name for the system that handles FCI", "text"),
    ("description", "What does the company do for the Department of Defense?", "area"),
    ("system_boundary", "Which computers, cloud services, and networks handle Federal Contract Information (FCI)?", "area"),
    ("fci_types", "What kinds of FCI do you receive or create (for example purchase orders, drawings, schedules)?", "area"),
]
SOURCES = {
    "Start a new self-assessment": S / "answers_template.json",
    "Sample: small manufacturer with gaps (fictional)": S / "riverbend_components_level1.json",
    "Sample: machining shop, fully met (fictional)": S / "keystone_precision_level1.json",
}

st.set_page_config(page_title="CMMC Readiness Toolkit", page_icon="🛡️", layout="centered")


# ----- state helpers -------------------------------------------------------------------------------

def load_doc(doc: dict) -> None:
    st.session_state.store = {"organization": dict(doc.get("organization", {})),
                              "answers": {k: dict(v) if isinstance(v, dict) else {"answer": v}
                                          for k, v in doc.get("answers", {}).items()}}
    for key in [k for k in st.session_state.keys() if str(k).startswith(("q_", "n_", "o_"))]:
        del st.session_state[key]


def on_source_change() -> None:
    load_doc(json.loads(SOURCES[st.session_state.source].read_text(encoding="utf-8")))
    st.session_state.step = 0 if st.session_state.source.startswith("Start") else len(STEPS) - 1


def save_answer(qid: str) -> None:
    label = st.session_state.get(f"q_{qid}")
    st.session_state.store["answers"].setdefault(qid, {})["answer"] = REVERSE.get(label, "")


def save_note(qid: str) -> None:
    st.session_state.store["answers"].setdefault(qid, {})["note"] = st.session_state.get(f"n_{qid}", "")


def save_org(field: str) -> None:
    st.session_state.store["organization"][field] = st.session_state.get(f"o_{field}", "")


def go(step: int) -> None:
    st.session_state.step = max(0, min(step, len(STEPS) - 1))


if "store" not in st.session_state:
    st.session_state.source = next(iter(SOURCES))
    on_source_change()

store = st.session_state.store


def current_result():
    return evaluate(parse_answers(json.dumps(store)))


# ----- sidebar -------------------------------------------------------------------------------------

with st.sidebar:
    st.header("CMMC Level 1")
    st.radio("Start from", list(SOURCES), key="source", on_change=on_source_change)
    up = st.file_uploader("Or resume from saved answers (.json)", type=["json"])
    if up is not None and st.button("Load saved answers"):
        try:
            load_doc(parse_answers(up.getvalue().decode("utf-8-sig")))
            go(len(STEPS) - 1)
            st.rerun()
        except DataError as exc:
            st.error(f"That file could not be read. {exc}")
    res = current_result()
    st.progress(res.answered_pct / 100, text=f"{res.answered_pct:.0f}% answered")
    st.caption(f"Practices met so far: {res.met} of {res.total}")
    st.divider()
    for i, name in enumerate(STEPS):
        st.button(("▶ " if i == st.session_state.step else "") + f"{i + 1}. {name}", key=f"nav_{i}",
                  on_click=go, args=(i,))
    st.caption(f"cmmc_kit {__version__}. Answers stay in this browser session; download them to save your progress.")

# ----- main ----------------------------------------------------------------------------------------

step = st.session_state.step
st.caption(f"STEP {step + 1} OF {len(STEPS)}")
st.title(STEPS[step])

if step == 0:
    st.write("This guided questionnaire walks a small defense supplier through the 15 CMMC Level 1 "
             "requirements in plain language. At the end you get a readiness result, a prioritized action "
             "plan, and a draft System Security Plan to download.")
    for field, label, kind in ORG_FIELDS:
        val = str(store["organization"].get(field, "") or "")
        if kind == "area":
            st.text_area(label, value=val, key=f"o_{field}", on_change=save_org, args=(field,), height=80)
        else:
            st.text_input(label, value=val, key=f"o_{field}", on_change=save_org, args=(field,))

elif step < len(STEPS) - 1:
    code = DOMAINS[step - 1][0]
    st.write("Answer each question for the systems that handle Federal Contract Information. Choose **Partly** if "
             "something is only done in some places. Use **N/A** only when the item truly does not apply, and "
             "explain why in the note.")
    for p in [x for x in CATALOG["practices"] if x["domain"] == code]:
        with st.container(border=True):
            st.markdown(f"#### {p['id']} · {p['title']}")
            st.caption(f"Requirement: {p['requirement']}")
            for q in p["questions"]:
                saved = store["answers"].get(q["id"], {})
                cur = saved.get("answer", "")
                st.radio(q["text"], list(LABELS.values()),
                         index=list(LABELS).index(cur) if cur in LABELS else None,
                         key=f"q_{q['id']}", horizontal=True, on_change=save_answer, args=(q["id"],))
                st.text_input("How is this done, or why not? (optional, used in your System Security Plan)",
                              value=str(saved.get("note", "") or ""), key=f"n_{q['id']}",
                              on_change=save_note, args=(q["id"],), placeholder=f"Evidence to keep: {q['evidence']}")

else:
    res = current_result()
    c1, c2, c3 = st.columns(3)
    c1.metric("Practices met", f"{res.met} of {res.total}")
    c2.metric("Questions answered", f"{res.answered_pct:.0f}%")
    c3.metric("Quick wins left", sum(1 for p in res.actions() if p.effort == "Quick win"))
    if res.ready_to_affirm:
        st.success("All 15 Level 1 practices are met. You appear ready for the annual self-assessment and the "
                   "senior official's affirmation in SPRS.")
    else:
        st.error(f"Not yet ready: {res.total - res.met} practice(s) need work. Every Level 1 practice must be fully "
                 "met before affirming; open action plans are not allowed at Level 1.")

    st.markdown("### Progress by domain")
    for d in res.domains():
        st.progress(d["met"] / d["total"], text=f"{d['name']}: {d['met']} of {d['total']}")

    st.markdown("### Action plan")
    acts = res.actions()
    if not acts:
        st.write("Nothing left to fix. Keep your evidence current and reassess every year.")
    for p in acts:
        tag = "🟢 Quick win" if p.effort == "Quick win" else "🛠️ Project"
        with st.expander(f"{tag} · {p.id} {p.title} ({p.status.lower()})"):
            for g in p.gaps:
                st.markdown(f"- **{g['issue']}** {g['text']}" + (f"  \n  *{g['note']}*" if g.get("note") else ""))
            if p.unanswered:
                st.markdown(f"- Not answered yet: {', '.join(p.unanswered)}")
            st.markdown(f"**Fix:** {p.remediation}")

    st.markdown("### Downloads")
    org = (store["organization"].get("name") or "company").replace(" ", "_")
    d1, d2 = st.columns(2)
    d1.download_button("📄 Readiness report (HTML)", to_html(res), f"{org}_cmmc_l1_readiness.html", "text/html")
    d2.download_button("📘 Draft System Security Plan (HTML)", ssp_html(res), f"{org}_ssp_draft.html", "text/html")
    d3, d4 = st.columns(2)
    d3.download_button("📝 Draft SSP (Markdown, editable)", ssp_markdown(res), f"{org}_ssp_draft.md",
                       "text/markdown")
    d4.download_button("💾 Save my answers (JSON)", json.dumps(store, indent=2), f"{org}_cmmc_answers.json",
                       "application/json")
    st.download_button("Practice status (CSV)", to_csv(res), f"{org}_cmmc_l1_status.csv", "text/csv")
    st.caption(DISCLAIMER)

st.divider()
b1, _, b2 = st.columns([1, 2, 1])
if step > 0:
    b1.button("← Back", on_click=go, args=(step - 1,))
if step < len(STEPS) - 1:
    b2.button("Next →", on_click=go, args=(step + 1,), type="primary")
