import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cmmc_kit import evaluate, load_answers, load_practices, parse_answers  # noqa: E402
from cmmc_kit.cli import main  # noqa: E402
from cmmc_kit.engine import INCOMPLETE, MET, NOT_MET, DataError, all_question_ids  # noqa: E402
from cmmc_kit.reporting import SSP_WRITERS, WRITERS  # noqa: E402

S = ROOT / "samples"
WEAK = S / "riverbend_components_level1.json"
STRONG = S / "keystone_precision_level1.json"


def doc(answers, org=None):
    return parse_answers(json.dumps({"organization": org or {"name": "T"}, "answers": answers}))


def all_yes():
    return {q: "yes" for q in all_question_ids()}


def status(result, pid):
    return next(p.status for p in result.practices if p.id == pid)


class TestCatalog(unittest.TestCase):
    def test_fifteen_level1_practices(self):
        c = load_practices()
        self.assertEqual(len(c["practices"]), 15)
        self.assertEqual(len({p["id"] for p in c["practices"]}), 15)
        self.assertEqual(len(all_question_ids()), len(set(all_question_ids())))
        self.assertTrue(all(p["far"].startswith("52.204-21(b)(1)") for p in c["practices"]))


class TestParsing(unittest.TestCase):
    def test_rejects_unknown_ids_and_values(self):
        with self.assertRaisesRegex(DataError, "Unknown question"):
            doc({"ZZ-1": "yes"})
        with self.assertRaisesRegex(DataError, "answer must be"):
            doc({"AC1-1": "maybe"})
        with self.assertRaisesRegex(DataError, "valid JSON"):
            parse_answers("{nope")

    def test_blank_answers_are_skipped(self):
        d = doc({"AC1-1": {"answer": "", "note": ""}, "AC1-2": "YES"})
        self.assertNotIn("AC1-1", d["answers"])
        self.assertEqual(d["answers"]["AC1-2"]["answer"], "yes")


class TestEvaluation(unittest.TestCase):
    def test_all_yes_is_ready(self):
        r = evaluate(doc(all_yes()))
        self.assertEqual(r.met, 15)
        self.assertTrue(r.ready_to_affirm)

    def test_one_partial_fails_the_practice_and_readiness(self):
        a = all_yes()
        a["SI2-1"] = "partial"
        r = evaluate(doc(a))
        self.assertEqual(status(r, "SI.L1-B.1.XIII"), NOT_MET)
        self.assertFalse(r.ready_to_affirm)

    def test_unanswered_is_incomplete_not_met(self):
        a = all_yes()
        del a["PE2-2"]
        r = evaluate(doc(a))
        self.assertEqual(status(r, "PE.L1-B.1.IX"), INCOMPLETE)
        self.assertFalse(r.ready_to_affirm)

    def test_not_applicable_needs_a_justification(self):
        a = all_yes()
        a["SC2-1"] = {"answer": "na"}
        self.assertEqual(status(evaluate(doc(a)), "SC.L1-B.1.XI"), NOT_MET)
        a["SC2-1"] = {"answer": "na", "note": "No public-facing systems; website hosted by a vendor."}
        self.assertEqual(status(evaluate(doc(a)), "SC.L1-B.1.XI"), MET)

    def test_quick_wins_come_first(self):
        r = evaluate(load_answers(WEAK))
        efforts = [p.effort for p in r.actions()]
        self.assertEqual(efforts, sorted(efforts, key=lambda e: e != "Quick win"))

    def test_implementation_notes_exclude_gap_notes(self):
        r = evaluate(load_answers(WEAK))
        p = next(x for x in r.practices if x.id == "AC.L1-B.1.I")
        self.assertFalse(any("personal phones are not" in n for n in p.notes))
        self.assertTrue(any("personal phones are not" in g["note"] for g in p.gaps))

    def test_samples(self):
        self.assertFalse(evaluate(load_answers(WEAK)).ready_to_affirm)
        self.assertTrue(evaluate(load_answers(STRONG)).ready_to_affirm)
        self.assertEqual(evaluate(load_answers(S / "answers_template.json")).answered_pct, 0.0)


class TestOutputs(unittest.TestCase):
    def test_writers_and_escaping(self):
        r = evaluate(doc(all_yes(), org={"name": "<script>x</script>"}))
        for fmt, w in {**WRITERS, **{f"ssp_{k}": v for k, v in SSP_WRITERS.items()}}.items():
            self.assertTrue(w(r).strip(), fmt)
        self.assertNotIn("<script>x</script>", WRITERS["html"](r))
        self.assertNotIn("<script>x</script>", SSP_WRITERS["html"](r))
        json.loads(WRITERS["json"](r))

    def test_ssp_contains_every_practice(self):
        md = SSP_WRITERS["md"](evaluate(load_answers(WEAK)))
        for p in load_practices()["practices"]:
            self.assertIn(p["id"], md)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(main([str(WEAK), "--ssp", "--out", tmp, "--fail-unless-ready"]), 2)
            self.assertTrue(any(Path(tmp).glob("*_ssp_draft.html")))
            self.assertEqual(main([str(STRONG), "--out", tmp, "--fail-unless-ready"]), 0)
            bad = Path(tmp) / "bad.json"
            bad.write_text("[1]", encoding="utf-8")
            self.assertEqual(main([str(bad), "--out", tmp]), 1)


if __name__ == "__main__":
    unittest.main()
