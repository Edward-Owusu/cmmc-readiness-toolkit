"""Write the readiness report and a draft System Security Plan (SSP)."""

from __future__ import annotations

import csv
import io
import json
from html import escape

from .engine import MET, Result

DISCLAIMER = (
    "This report was produced by a self-assessment aid from the answers supplied. It is not a CMMC assessment, "
    "certification, or legal advice. Level 1 self-assessment results and the annual affirmation by a senior "
    "company official are submitted through the Supplier Performance Risk System (SPRS). Confirm current "
    "requirements in 32 CFR Part 170, your contract, and official DoD CMMC guidance."
)
SSP_NOTE = (
    "Draft generated from questionnaire answers. Review, complete, and approve it before use. A System Security "
    "Plan is a formal requirement at CMMC Level 2; at Level 1 it is good practice and supports the self-assessment."
)


def _org(r: Result, key: str, default: str = "Not provided") -> str:
    v = r.organization.get(key)
    return str(v) if v not in (None, "") else default


# ----- readiness report --------------------------------------------------------------------------

def to_json(r: Result) -> str:
    return json.dumps(r.to_dict(), indent=2, default=str)


def to_csv(r: Result) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["practice", "title", "domain", "status", "effort", "far", "nist_800_171", "gaps", "remediation"])
    for p in r.practices:
        w.writerow([p.id, p.title, p.domain_name, p.status, p.effort, p.far, "; ".join(p.nist_800_171),
                    " | ".join(f"{g['question']}: {g['issue']}" for g in p.gaps), p.remediation])
    return buf.getvalue()


def to_markdown(r: Result) -> str:
    lines = [f"# CMMC Level 1 readiness: {_org(r, 'name')}", "",
             f"Generated {r.generated_at} | {r.answered_pct:.0f}% of questions answered", "",
             f"- Practices met: **{r.met} of {r.total}**",
             f"- Ready for the annual Level 1 self-assessment affirmation: **{'Yes' if r.ready_to_affirm else 'Not yet'}**",
             "", "## Action plan (quick wins first)", ""]
    acts = r.actions()
    if not acts:
        lines.append("All 15 practices are met.")
    for i, p in enumerate(acts, 1):
        lines.append(f"{i}. **{p.id} {p.title}** ({p.effort}, {p.status.lower()})")
        for g in p.gaps:
            lines.append(f"   - {g['question']}: {g['issue']} {g['text']}")
        if p.unanswered:
            lines.append(f"   - Unanswered: {', '.join(p.unanswered)}")
        lines.append(f"   - Fix: {p.remediation}")
    lines += ["", "## All practices", "", "| Practice | Title | Domain | Status |", "|---|---|---|---|"]
    lines += [f"| {p.id} | {p.title} | {p.domain_name} | {p.status} |" for p in r.practices]
    lines += ["", f"_{DISCLAIMER}_", ""]
    return "\n".join(lines)


_CSS = """
:root{--ink:#22261b;--muted:#5d6450;--line:#d8d3bd;--paper:#fbfaf4;--wash:#efecdf;--olive:#4b5320;--khaki:#c3b98b;
--met:#3f6212;--gap:#a16207;--miss:#9f1d1d}
*{box-sizing:border-box}
body{margin:0;background:var(--wash);color:var(--ink);font:15px/1.6 "Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.band{background:var(--olive);color:#f3f1e4;border-bottom:6px solid var(--khaki)}
.band .in{max-width:980px;margin:0 auto;padding:30px 24px}
.kicker{text-transform:uppercase;letter-spacing:.14em;font-size:12px;opacity:.85;margin:0}
h1{font-size:28px;margin:6px 0 4px}
.band p{margin:0;opacity:.9}
main{max-width:980px;margin:0 auto;padding:26px 24px 60px}
h2{font-size:19px;text-transform:uppercase;letter-spacing:.06em;color:var(--olive);border-bottom:2px solid var(--khaki);padding-bottom:6px;margin:34px 0 14px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}
.tile{background:var(--paper);border:1px solid var(--line);padding:16px}
.tile b{display:block;font-size:30px}
.tile span{color:var(--muted);font-size:13px}
.verdict{padding:14px 18px;border-left:6px solid var(--miss);background:var(--paper);margin-top:14px;font-weight:600}
.verdict.ok{border-left-color:var(--met)}
.dom{display:grid;grid-template-columns:220px 1fr 60px;gap:10px;align-items:center;margin:6px 0}
.bar{height:12px;background:#ddd8c3}.bar i{display:block;height:100%;background:var(--olive)}
ol.plan{padding-left:20px}ol.plan>li{background:var(--paper);border:1px solid var(--line);padding:12px 16px;margin:10px 0}
.chip{display:inline-block;font-size:11px;font-weight:700;padding:1px 8px;border-radius:2px;color:#fff;background:var(--gap);margin-left:6px;text-transform:uppercase}
.chip.qw{background:var(--met)}.chip.pr{background:var(--olive)}
.table-wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;background:var(--paper);font-size:14px}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:#e6e1cb}
ol.plan ul{margin:8px 0;padding-left:20px}
.s-MET{color:var(--met);font-weight:700}.s-NOT-MET{color:var(--miss);font-weight:700}.s-INCOMPLETE{color:var(--gap);font-weight:700}
.note{color:var(--muted);font-size:13px;margin-top:30px}
.req{font-style:italic;color:var(--muted)}
section.prac{background:var(--paper);border:1px solid var(--line);padding:14px 18px;margin:12px 0}
section.prac h3{margin:0 0 4px;font-size:16px}
dl{display:grid;grid-template-columns:170px 1fr;gap:4px 12px;margin:10px 0}dt{color:var(--muted)}dd{margin:0}
"""


def _cls(status: str) -> str:
    return "s-" + status.replace(" ", "-")


def to_html(r: Result) -> str:
    e = escape
    doms = "".join(
        f'<div class="dom"><span>{e(d["name"])}</span><div class="bar"><i style="width:{100 * d["met"] / d["total"]:.0f}%"></i></div>'
        f'<span>{d["met"]}/{d["total"]}</span></div>' for d in r.domains())
    plan = []
    for p in r.actions():
        chip = '<span class="chip qw">Quick win</span>' if p.effort == "Quick win" else '<span class="chip pr">Project</span>'
        gaps = "".join(f"<li>{e(g['issue'])} {e(g['text'])}" + (f" <em>{e(g['note'])}</em>" if g.get("note") else "") + "</li>"
                       for g in p.gaps)
        if p.unanswered:
            gaps += f"<li>Not yet answered: {e(', '.join(p.unanswered))}</li>"
        plan.append(f"<li><strong>{e(p.id)} {e(p.title)}</strong>{chip}<ul>{gaps}</ul>"
                    f"<p><strong>Fix:</strong> {e(p.remediation)}</p></li>")
    rows = "".join(f'<tr><td>{e(p.id)}</td><td>{e(p.title)}</td><td>{e(p.domain_name)}</td>'
                   f'<td>{e(p.far)}</td><td>{e(", ".join(p.nist_800_171))}</td><td class="{_cls(p.status)}">{e(p.status)}</td></tr>'
                   for p in r.practices)
    verdict = ('<div class="verdict ok">All 15 Level 1 practices are met. You appear ready to complete the annual '
               'self-assessment and affirmation in SPRS.</div>' if r.ready_to_affirm else
               f'<div class="verdict">Not yet ready: {r.total - r.met} practice(s) still need work. Every Level 1 '
               'practice must be fully met before affirming; open action plans are not allowed at Level 1.</div>')
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>CMMC Level 1 readiness: {e(_org(r, 'name'))}</title><style>{_CSS}</style></head><body>
<div class="band"><div class="in"><p class="kicker">CMMC Level 1 readiness report</p><h1>{e(_org(r, 'name'))}</h1>
<p>Generated {e(r.generated_at)} by cmmc_kit {e(r.tool_version)}. {r.answered_pct:.0f}% of questions answered.</p></div></div>
<main>
<div class="tiles"><div class="tile"><b>{r.met} / {r.total}</b><span>Practices met</span></div>
<div class="tile"><b>{sum(1 for p in r.actions() if p.effort == 'Quick win')}</b><span>Quick wins remaining</span></div>
<div class="tile"><b>{sum(len(p.gaps) for p in r.practices)}</b><span>Individual gaps</span></div></div>
{verdict}
<h2>Progress by domain</h2>{doms}
<h2>Action plan</h2>{'<ol class="plan">' + ''.join(plan) + '</ol>' if plan else '<p>No actions needed.</p>'}
<h2>All practices</h2><div class="table-wrap"><table><thead><tr><th>Practice</th><th>Title</th><th>Domain</th><th>FAR reference</th><th>NIST SP 800-171</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">{e(DISCLAIMER)}</p></main></body></html>"""


# ----- System Security Plan ------------------------------------------------------------------------

def _impl(p) -> str:
    if p.notes:
        return " ".join(p.notes)
    return "Implementation description to be completed."


def ssp_markdown(r: Result) -> str:
    L = [f"# System Security Plan (draft): {_org(r, 'system_name', _org(r, 'name'))}", "",
         f"> {SSP_NOTE}", "",
         "## 1. System identification", "",
         f"- **Organization:** {_org(r, 'name')}",
         f"- **CAGE code:** {_org(r, 'cage_code')}",
         f"- **Employees:** {_org(r, 'employees')}",
         f"- **System name:** {_org(r, 'system_name')}",
         f"- **Point of contact:** {_org(r, 'point_of_contact')}",
         f"- **Senior official responsible for affirmation:** {_org(r, 'senior_official')}",
         f"- **Prepared:** {r.generated_at}", "",
         "### Business description", "", _org(r, "description"), "",
         "### System boundary", "", _org(r, "system_boundary"), "",
         "### Federal Contract Information handled", "", _org(r, "fci_types"), "",
         f"## 2. Requirement implementation ({r.met} of {r.total} met)", ""]
    for p in r.practices:
        L += [f"### {p.id} {p.title}", "", f"*Requirement ({p.far}; NIST SP 800-171 {', '.join(p.nist_800_171)}):* {p.requirement}", "",
              f"- **Status:** {p.status}",
              f"- **Implementation:** {_impl(p)}"]
        if p.evidence:
            L.append(f"- **Evidence:** {'; '.join(p.evidence)}")
        if p.na_justifications:
            L.append(f"- **Not applicable justification:** {'; '.join(p.na_justifications)}")
        if p.status != MET:
            gaps = " | ".join(f"{g['issue']} ({g['question']})" + (f" {g['note']}" if g.get("note") else "") for g in p.gaps)
            if p.unanswered:
                gaps += ("; " if gaps else "") + f"Not yet assessed: {', '.join(p.unanswered)}"
            L += [f"- **Gaps:** {gaps}", f"- **Planned action:** {p.remediation}"]
        L.append("")
    L += ["## 3. Approval", "", "| Role | Name | Signature | Date |", "|---|---|---|---|",
          f"| Senior official | {_org(r, 'senior_official', '')} | | |",
          f"| Point of contact | {_org(r, 'point_of_contact', '')} | | |", "", f"_{DISCLAIMER}_", ""]
    return "\n".join(L)


def ssp_html(r: Result) -> str:
    e = escape
    secs = []
    for p in r.practices:
        dd = [f"<dt>Status</dt><dd class='{_cls(p.status)}'>{e(p.status)}</dd>",
              f"<dt>Implementation</dt><dd>{e(_impl(p))}</dd>"]
        if p.evidence:
            dd.append(f"<dt>Evidence</dt><dd>{e('; '.join(p.evidence))}</dd>")
        if p.na_justifications:
            dd.append(f"<dt>Not applicable</dt><dd>{e('; '.join(p.na_justifications))}</dd>")
        if p.status != MET:
            gaps = " | ".join(f"{g['issue']} ({g['question']})" + (f" {g['note']}" if g.get("note") else "") for g in p.gaps)
            if p.unanswered:
                gaps += ("; " if gaps else "") + f"Not yet assessed: {', '.join(p.unanswered)}"
            dd += [f"<dt>Gaps</dt><dd>{e(gaps)}</dd>", f"<dt>Planned action</dt><dd>{e(p.remediation)}</dd>"]
        secs.append(f'<section class="prac"><h3>{e(p.id)} {e(p.title)}</h3>'
                    f'<p class="req">{e(p.requirement)} ({e(p.far)}; NIST SP 800-171 {e(", ".join(p.nist_800_171))})</p>'
                    f'<dl>{"".join(dd)}</dl></section>')
    ident = "".join(f"<dt>{e(k)}</dt><dd>{e(_org(r, v))}</dd>" for k, v in [
        ("Organization", "name"), ("CAGE code", "cage_code"), ("Employees", "employees"), ("System name", "system_name"),
        ("Point of contact", "point_of_contact"), ("Senior official", "senior_official"),
        ("Business description", "description"), ("System boundary", "system_boundary"), ("FCI handled", "fci_types")])
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>System Security Plan (draft): {e(_org(r, 'name'))}</title><style>{_CSS}</style></head><body>
<div class="band"><div class="in"><p class="kicker">System Security Plan, draft</p><h1>{e(_org(r, 'system_name', _org(r, 'name')))}</h1>
<p>{e(_org(r, 'name'))}. Prepared {e(r.generated_at)}. {r.met} of {r.total} CMMC Level 1 practices met.</p></div></div>
<main><p class="verdict">{e(SSP_NOTE)}</p>
<h2>1. System identification</h2><section class="prac"><dl>{ident}</dl></section>
<h2>2. Requirement implementation</h2>{''.join(secs)}
<h2>3. Approval</h2><div class="table-wrap"><table><thead><tr><th>Role</th><th>Name</th><th>Signature</th><th>Date</th></tr></thead>
<tbody><tr><td>Senior official</td><td>{e(_org(r, 'senior_official', ''))}</td><td></td><td></td></tr>
<tr><td>Point of contact</td><td>{e(_org(r, 'point_of_contact', ''))}</td><td></td><td></td></tr></tbody></table></div>
<p class="note">{e(DISCLAIMER)}</p></main></body></html>"""


WRITERS = {"json": to_json, "csv": to_csv, "md": to_markdown, "html": to_html}
SSP_WRITERS = {"md": ssp_markdown, "html": ssp_html}
