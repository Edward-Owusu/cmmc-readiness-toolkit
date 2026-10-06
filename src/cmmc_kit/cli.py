"""Command-line interface.

Examples:
    cmmc-check samples/riverbend_components_level1.json
    cmmc-check answers.json --format html md --ssp --out reports --fail-unless-ready
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .engine import DataError, evaluate, load_answers
from .reporting import SSP_WRITERS, WRITERS


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cmmc-check", description="CMMC Level 1 readiness check and draft System Security Plan.")
    p.add_argument("answers", help="Path to the questionnaire answers JSON file")
    p.add_argument("--format", nargs="+", choices=sorted(WRITERS), default=["html"], help="Readiness report formats")
    p.add_argument("--ssp", action="store_true", help="Also write a draft System Security Plan (Markdown and HTML)")
    p.add_argument("--out", default="reports", help="Output directory (default: reports)")
    p.add_argument("--fail-unless-ready", action="store_true", help="Exit with code 2 unless all 15 practices are met")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        r = evaluate(load_answers(args.answers))
    except (OSError, DataError) as exc:
        print(f"Could not read input: {exc}", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(args.answers).stem
    for fmt in args.format:
        path = out / f"{stem}_readiness.{fmt}"
        path.write_text(WRITERS[fmt](r), encoding="utf-8")
        print(f"Wrote {path}")
    if args.ssp:
        for fmt, writer in SSP_WRITERS.items():
            path = out / f"{stem}_ssp_draft.{fmt}"
            path.write_text(writer(r), encoding="utf-8")
            print(f"Wrote {path}")
    name = r.organization.get("name") or "Organization"
    print(f"\n{name} | CMMC Level 1 | {r.answered_pct:.0f}% answered")
    print(f"Practices met: {r.met} of {r.total} | Ready to affirm: {'Yes' if r.ready_to_affirm else 'Not yet'}")
    for d in r.domains():
        print(f"  {d['name']:<38} {d['met']}/{d['total']}")
    quick = [p for p in r.actions() if p.effort == "Quick win"]
    if quick:
        print(f"Quick wins to start with: {', '.join(p.id for p in quick[:5])}")
    if args.fail_unless_ready and not r.ready_to_affirm:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
