"""The delivery gate applied to the shipped examples.

examples/NN-slug/with-skill/*.md (the report and its sibling evidence file, not final_reply.md) must give
no Blocker and at most two Majors: the gate of references/review-rubric.md. examples/NN-slug/without-skill/
report.md, the baseline written without the skill, must still give at least one Major, so the checker
keeps telling the two apart. The number of scenarios is not fixed: the tests walk whatever is there.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers as h  # noqa: E402

MAX_MAJORS_TO_DELIVER = 2


def label(path):
    return path.relative_to(h.REPO).as_posix()


def check(path):
    code, out, err = h.run("check_doc.py", path, "--json")
    if not out.strip():
        raise AssertionError("check_doc.py printed nothing for %s (exit %d): %s" % (label(path), code, err))
    return h.CheckResult(code, out, err)


class ExamplesGateTests(unittest.TestCase):
    def test_every_with_skill_document_passes_the_delivery_gate(self):
        paths = sorted(p for p in h.EXAMPLES.glob("*/with-skill/*.md") if p.name != "final_reply.md")
        if not paths:
            self.skipTest("no examples/*/with-skill/*.md documents under %s" % h.EXAMPLES)
        for path in paths:
            with self.subTest(document=label(path)):
                result = check(path)
                self.assertEqual(result.gate["blockers"], 0, result.describe())
                self.assertLessEqual(result.gate["majors"], MAX_MAJORS_TO_DELIVER, result.describe())

    def test_every_without_skill_baseline_still_has_a_major(self):
        paths = sorted(h.EXAMPLES.glob("*/without-skill/report.md"))
        if not paths:
            self.skipTest("no examples/*/without-skill/report.md baselines under %s" % h.EXAMPLES)
        for path in paths:
            with self.subTest(document=label(path)):
                result = check(path)
                self.assertGreaterEqual(result.gate["majors"], 1, result.describe())


if __name__ == "__main__":
    unittest.main()
