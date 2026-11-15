"""Guided CMMC Level 1 self-assessment questionnaire.

Run locally:   streamlit run app/streamlit_app.py

Layout: no sidebar. A step tracker across the top shows each domain and how much of it is answered;
the questionnaire runs one domain per page with Back and Next buttons.
"""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ui  # noqa: E402
from cmmc_kit import __version__, evaluate, load_practices, parse_answers  # noqa: E402
from cmmc_kit.engine import MET, DataError  # noqa: E402
from cmmc_kit.reporting import DISCLAIMER, ssp_html, ssp_markdown, to_csv, to_html  # noqa: E402

S = ROOT / "samples"
CATALOG = load_practices()
DOMAINS = list(CATALOG["domains"].items())  # [(code, name), ...]
STEPS = ["Company profile"] + [name for _, name in DOMAINS] + ["Results"]
SHORT = ["Profile"] + [code for code, _ in DOMAINS] + ["Results"]
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
PAL = ui.Palette(accent="#B5C18E", band="#262B1D", band_text="#F2F4EA", band_sub="#C3C8B2",
                 card="#2B3122", line="#434B35", ink="#E8EADF", muted="#A9AF98")
STATUS_COLOR = {MET: "#7FB069", "NOT MET": "#D9534F", "INCOMPLETE": "#C9A227"}

ui.setup("CMMC Level 1 readiness", "Defense supply chain · 15 practices · FAR 52.204-21",
         "A guided self-assessment for small defense suppliers. Answer plain-language questions for each "
         "domain, then get a readiness result, a prioritized action plan and a draft System Security Plan.",
         "🛡️", PAL)
st.markdown("""<style>
.stButton button { width: 100%; }
.q-card { background:#2B3122; border:1px solid #434B35; border-radius:12px; padding:14px 16px 4px; margin-bottom:12px; }
</style>""", unsafe_allow_html=True)


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



def domain_progress(code: str) -> tuple[int, int]:
    qids = [q["id"] for p in CATALOG["practices"] if p["domain"] == code for q in p["questions"]]
    done = sum(1 for q in qids if store["answers"].get(q, {}).get("answer"))
    return done, len(qids)


def load_upload() -> None:
    up = st.session_state.get("resume_file")
    if up is None:
        return
    try:
        load_doc(parse_answers(up.getvalue().decode("utf-8-sig")))
        go(len(STEPS) - 1)
    except DataError as exc:
        st.session_state.load_error = f"That file could not be read. {exc}"


# ----- top row: where to start, resume, progress ---------------------------------------------------

res = current_result()
t1, t2, t3 = st.columns([2.4, 1.1, 2.2], vertical_alignment="top")
with t1:
    st.selectbox("Start from", list(SOURCES), key="source", on_change=on_source_change)
with t2:
    with st.popover("Resume saved answers", use_container_width=True):
        st.file_uploader("Saved answers (.json)", type=["json"], key="resume_file")
        st.button("Load saved answers", on_click=load_upload, type="primary")
with t3:
    st.progress(res.answered_pct / 100,
                text=f"{res.answered_pct:.0f}% answered · {res.met} of {res.total} practices met")
if st.session_state.get("load_error"):
    st.error(st.session_state.pop("load_error"))

# ----- step tracker --------------------------------------------------------------------------------

step = st.session_state.step
cols = st.columns(len(STEPS))
for i, (col, short) in enumerate(zip(cols, SHORT)):
    if 0 < i < len(STEPS) - 1:
        done, total = domain_progress(DOMAINS[i - 1][0])
        mark = "✓ " if done == total else f"{done}/{total} "
    else:
        mark = ""
    col.button(f"{mark}{short}", key=f"nav_{i}", on_click=go, args=(i,),
               type="primary" if i == step else "secondary", help=STEPS[i])

st.markdown(f"<div class='g-sec'>Step {step + 1} of {len(STEPS)} · {escape(STEPS[step])}</div>",
            unsafe_allow_html=True)

if step == 0:
    st.write("This questionnaire walks you through the 15 CMMC Level 1 requirements in plain language. "
             "Start with the company details below; they go into the draft System Security Plan.")
    c1, c2 = st.columns(2)
    for n, (field, label, kind) in enumerate(ORG_FIELDS):
        val = str(store["organization"].get(field, "") or "")
        target = st if kind == "area" else (c1 if n % 2 == 0 else c2)
        if kind == "area":
            target.text_area(label, value=val, key=f"o_{field}", on_change=save_org, args=(field,), height=80)
        else:
            target.text_input(label, value=val, key=f"o_{field}", on_change=save_org, args=(field,))

elif step < len(STEPS) - 1:
    code = DOMAINS[step - 1][0]
    st.caption("Answer for the systems that handle Federal Contract Information. Choose Partly if something is "
               "only done in some places. Use N/A only when the item truly does not apply, and explain why in "
               "the note.")
    for p in [x for x in CATALOG["practices"] if x["domain"] == code]:
        with st.container(border=True):
            pr = next((r for r in res.practices if r.id == p["id"]), None)
            status = ui.pill(pr.status.lower(), STATUS_COLOR.get(pr.status, "#777")) if pr else ""
            st.markdown(f"<div class='h' style='font-size:17px;font-weight:650'>{status}{escape(p['id'])} · "
                        f"{escape(p['title'])}</div>", unsafe_allow_html=True)
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
    quick = sum(1 for p in res.actions() if p.effort == "Quick win")
    ui.tiles([(f"{res.met} of {res.total}", "Practices met", "#7FB069" if res.ready_to_affirm else "#D9534F"),
              (f"{res.answered_pct:.0f}%", "Questions answered"),
              (quick, "Quick wins left", "#C9A227"),
              (len(res.actions()) - quick, "Projects left", "#D9534F")], PAL)
    if res.ready_to_affirm:
        st.success("All 15 Level 1 practices are met. You appear ready for the annual self-assessment and the "
                   "senior official's affirmation in SPRS.")
    else:
        st.error(f"Not yet ready: {res.total - res.met} practice(s) need work. Every Level 1 practice must be fully "
                 "met before affirming; open action plans are not allowed at Level 1.")

    ui.section("Readiness by domain")
    dcols = st.columns(3)
    for n, d in enumerate(res.domains()):
        pct = 100 * d["met"] / d["total"]
        color = "#7FB069" if d["met"] == d["total"] else ("#C9A227" if d["met"] else "#D9534F")
        dcols[n % 3].markdown(
            f"<div class='g-tile' style='border-top-color:{color};margin-bottom:10px'>"
            f"<b>{d['met']}/{d['total']}</b><span>{escape(d['domain'])} · {escape(d['name'])}</span>"
            f"{ui.bar(pct, color)}</div>", unsafe_allow_html=True)

    ui.section("Action plan", "Quick wins first, then projects.")
    acts = res.actions()
    if not acts:
        st.write("Nothing left to fix. Keep your evidence current and reassess every year.")
    for p in acts:
        tag = ui.pill("Quick win", "#7FB069") if p.effort == "Quick win" else ui.pill("Project", "#8C6D46")
        body = "".join(f"<div class='d'><b>{escape(g['issue'])}</b> {escape(g['text'])}"
                       + (f"<br><i class='s'>{escape(g['note'])}</i>" if g.get("note") else "") + "</div>"
                       for g in p.gaps)
        if p.unanswered:
            body += f"<div class='s'>Not answered yet: {escape(', '.join(p.unanswered))}</div>"
        body += f"<div class='f'><b>Fix:</b> {escape(p.remediation)}</div>"
        ui.card(f"<div class='h'>{tag}{ui.pill(p.status.lower(), STATUS_COLOR.get(p.status, '#777'))}"
                f"{escape(p.id)} · {escape(p.title)}</div>", body, accent=STATUS_COLOR.get(p.status))

    org = (store["organization"].get("name") or "company").replace(" ", "_")
    ui.downloads([("Readiness report (HTML)", to_html(res), f"{org}_cmmc_l1_readiness.html", "text/html"),
                  ("Draft SSP (HTML)", ssp_html(res), f"{org}_ssp_draft.html", "text/html"),
                  ("Draft SSP (Markdown)", ssp_markdown(res), f"{org}_ssp_draft.md", "text/markdown")])
    s1, s2 = st.columns(2)
    s1.download_button("Save my answers (JSON)", json.dumps(store, indent=2), f"{org}_cmmc_answers.json",
                       "application/json", use_container_width=True)
    s2.download_button("Practice status (CSV)", to_csv(res), f"{org}_cmmc_l1_status.csv", "text/csv",
                       use_container_width=True)

st.write("")
b1, _, b2 = st.columns([1, 3, 1])
if step > 0:
    b1.button("← Back", on_click=go, args=(step - 1,), use_container_width=True)
if step < len(STEPS) - 1:
    b2.button(f"Next: {SHORT[step + 1]} →", on_click=go, args=(step + 1,), type="primary",
              use_container_width=True)

ui.footer("cmmc_kit", __version__, "cmmc-readiness-toolkit",
          DISCLAIMER + " Answers stay in this browser session; download them to save your progress.")
