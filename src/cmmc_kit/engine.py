"""Evaluate questionnaire answers against CMMC Level 1 practices."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA = Path(__file__).parent / "data"
ANSWERS = ("yes", "no", "partial", "na")
MET, NOT_MET, INCOMPLETE = "MET", "NOT MET", "INCOMPLETE"


class DataError(ValueError):
    """Raised when an answers file cannot be read."""


def load_practices() -> dict:
    return json.loads((DATA / "level1.json").read_text(encoding="utf-8"))


def all_question_ids() -> list[str]:
    return [q["id"] for p in load_practices()["practices"] for q in p["questions"]]


def parse_answers(text: str) -> dict:
    """Read and validate an answers file. Unknown question ids and bad values are rejected."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DataError(f"The file is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise DataError("The answers file must be a JSON object with 'organization' and 'answers'.")
    known = set(all_question_ids())
    raw = data.get("answers", {})
    if not isinstance(raw, dict):
        raise DataError("'answers' must be an object keyed by question id.")
    clean: dict[str, dict] = {}
    for qid, val in raw.items():
        if qid not in known:
            raise DataError(f"Unknown question id '{qid}'.")
        entry = {"answer": val} if isinstance(val, str) else dict(val or {})
        ans = str(entry.get("answer", "")).strip().lower()
        if ans in ("", "unanswered"):
            continue
        if ans not in ANSWERS:
            raise DataError(f"Question {qid}: answer must be one of {', '.join(ANSWERS)}, got '{ans}'.")
        entry["answer"] = ans
        clean[qid] = entry
    data["answers"] = clean
    data.setdefault("organization", {})
    return data


def load_answers(path: str | Path) -> dict:
    return parse_answers(Path(path).read_text(encoding="utf-8-sig"))


@dataclass
class PracticeResult:
    id: str
    domain: str
    domain_name: str
    title: str
    requirement: str
    far: str
    nist_800_171: list[str]
    effort: str
    status: str
    questions_total: int
    questions_yes: int
    gaps: list[dict]
    unanswered: list[str]
    notes: list[str]
    evidence: list[str]
    na_justifications: list[str]
    remediation: str


@dataclass
class Result:
    organization: dict
    generated_at: str
    tool_version: str
    practices: list[PracticeResult] = field(default_factory=list)

    @property
    def met(self) -> int:
        return sum(1 for p in self.practices if p.status == MET)

    @property
    def total(self) -> int:
        return len(self.practices)

    @property
    def answered_pct(self) -> float:
        tot = sum(p.questions_total for p in self.practices)
        ans = tot - sum(len(p.unanswered) for p in self.practices)
        return round(100 * ans / tot, 1) if tot else 0.0

    @property
    def ready_to_affirm(self) -> bool:
        # CMMC Level 1 requires every practice to be fully met; plans of action are not permitted at Level 1.
        return self.met == self.total

    def actions(self) -> list[PracticeResult]:
        """Unmet practices, quick wins first, then by number of gaps."""
        todo = [p for p in self.practices if p.status != MET]
        return sorted(todo, key=lambda p: (p.effort != "Quick win", -len(p.gaps), p.id))

    def domains(self) -> list[dict]:
        out: dict[str, dict] = {}
        for p in self.practices:
            d = out.setdefault(p.domain, {"domain": p.domain, "name": p.domain_name, "met": 0, "total": 0})
            d["total"] += 1
            d["met"] += p.status == MET
        return list(out.values())

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.update(met=self.met, total=self.total, answered_pct=self.answered_pct, ready_to_affirm=self.ready_to_affirm)
        return d


def evaluate(answers_doc: dict) -> Result:
    from . import __version__

    catalog = load_practices()
    answers = answers_doc.get("answers", {})
    results: list[PracticeResult] = []
    for p in catalog["practices"]:
        gaps, unanswered, notes, evidence, na = [], [], [], [], []
        yes = 0
        for q in p["questions"]:
            a = answers.get(q["id"])
            if not a:
                unanswered.append(q["id"])
                continue
            if a.get("note") and a["answer"] == "yes":
                notes.append(str(a["note"]))  # only implemented items describe the implementation
            if a.get("evidence"):
                evidence.append(str(a["evidence"]))
            if a["answer"] == "yes":
                yes += 1
            elif a["answer"] == "na":
                if a.get("note"):
                    na.append(str(a["note"]))
                    yes += 1  # not applicable with a written justification counts as satisfied
                else:
                    gaps.append({"question": q["id"], "text": q["text"], "answer": "na",
                                 "issue": "Marked not applicable without a justification."})
            else:
                gaps.append({"question": q["id"], "text": q["text"], "answer": a["answer"],
                             "issue": "Not in place." if a["answer"] == "no" else "Only partly in place.",
                             "note": str(a.get("note") or "")})
        status = NOT_MET if gaps else (INCOMPLETE if unanswered else MET)
        results.append(PracticeResult(
            id=p["id"], domain=p["domain"], domain_name=catalog["domains"][p["domain"]], title=p["title"],
            requirement=p["requirement"], far=p["far"], nist_800_171=p["nist_800_171"], effort=p["effort"],
            status=status, questions_total=len(p["questions"]), questions_yes=yes, gaps=gaps,
            unanswered=unanswered, notes=notes, evidence=evidence, na_justifications=na,
            remediation=p["remediation"],
        ))
    return Result(
        organization=answers_doc.get("organization", {}),
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        tool_version=__version__,
        practices=results,
    )
