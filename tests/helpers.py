"""Shared helpers for the test suite: repository paths, script runners, file writers and a good document.

Standard library only, written for Python 3.9 and newer. Run the suite from the repository root:

    python -m unittest discover -s tests -v

Set PYTHONDONTWRITEBYTECODE=1 (or run python -B) to keep __pycache__ folders out of tests/. The scripts under
test never get one: they say sys.dont_write_bytecode = True, but only after their own bytecode would already
have been written, so this module sets the flag when it is imported, before it loads them.
Every file a test creates lives in a temporary directory; nothing is written inside the repository.

Two ways to run a script, both returning (returncode, stdout, stderr):
  run_script  starts a real child process (PYTHONDONTWRITEBYTECODE=1, PYTHONUTF8=1); the command-line
              test classes use it so the process boundary, exit status and UTF-8 output are exercised.
  run         the default for the many small rule tests: calls the script's main() in this process, which
              avoids hundreds of interpreter start-ups. Set DOCFMT_TEST_SUBPROCESS=1 to make it use
              run_script too (what a CI job can do on a fast machine).
"""
from __future__ import annotations

import contextlib
import importlib.util
import inspect
import io
import json
import os
import struct
import subprocess
import sys
import tempfile
import traceback
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "document-formatting"
SCRIPTS = SKILL / "scripts"
SKELETON = SKILL / "assets" / "skeleton.md"
EXAMPLES = REPO / "examples"
VALIDATOR = REPO / "tools" / "validate_skill.py"
TIMEOUT = 120  # seconds for one child process
BACKSLASH = chr(92)
ALWAYS_SUBPROCESS = os.environ.get("DOCFMT_TEST_SUBPROCESS") == "1"


# --------------------------------------------------------------------------- running and writing

def script_path(name):
    """A script given as an absolute path, a file name in the skill's scripts folder, or a repo-relative path."""
    path = Path(str(name))
    if path.is_absolute():
        return path
    for base in (SCRIPTS, REPO):
        candidate = base / path
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("no script named %s" % name)


def run_script(name, *args, cwd=None, env=None):
    """Run a Python script in a child process and return (returncode, stdout, stderr) as text.

    The child never writes bytecode and always uses UTF-8 for its standard streams."""
    child_env = os.environ.copy()
    child_env["PYTHONDONTWRITEBYTECODE"] = "1"
    child_env["PYTHONUTF8"] = "1"
    if env:
        child_env.update(env)
    command = [sys.executable, "-B", str(script_path(name))] + [str(arg) for arg in args]
    proc = subprocess.run(command, cwd=str(cwd) if cwd else None, env=child_env, timeout=TIMEOUT,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (proc.returncode,
            proc.stdout.decode("utf-8", "replace").replace("\r\n", "\n"),
            proc.stderr.decode("utf-8", "replace").replace("\r\n", "\n"))


_MODULES = {}


def load_script(name):
    """Import a script by path (once) and return the module; its file stem is the module name."""
    path = script_path(name)
    if str(path) not in _MODULES:
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[str(path)] = module
    return _MODULES[str(path)]


def run_main(name, *args, cwd=None):
    """Call a script's main() in this process and return (returncode, stdout, stderr) like a child would.

    SystemExit and uncaught exceptions are turned into the status and stderr text Python itself would give."""
    module = load_script(name)
    argv = [str(arg) for arg in args]
    out, err = io.StringIO(), io.StringIO()
    old_argv, old_cwd = sys.argv, os.getcwd()
    code = 0
    try:
        if cwd:
            os.chdir(str(cwd))
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                if "argv" in inspect.signature(module.main).parameters:
                    code = module.main(argv)
                else:
                    sys.argv = [Path(script_path(name)).name] + argv
                    code = module.main()
            except SystemExit as exc:
                code = exc.code
            except Exception:
                traceback.print_exc(file=err)
                code = 1
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)
    if code is None:
        code = 0
    elif not isinstance(code, int):
        err.write("%s\n" % code)
        code = 1
    return code, out.getvalue(), err.getvalue()


def run(name, *args, cwd=None):
    """run_main by default, run_script when DOCFMT_TEST_SUBPROCESS=1."""
    if ALWAYS_SUBPROCESS:
        return run_script(name, *args, cwd=cwd)
    return run_main(name, *args, cwd=cwd)


def write(tmpdir, relpath, text, newline="\n"):
    """Write UTF-8 text to tmpdir/relpath (parent folders are created) and return the path.

    Line endings are exactly `newline`, whatever the platform."""
    path = Path(str(tmpdir)) / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), "w", encoding="utf-8", newline=newline) as handle:
        handle.write(text)
    return path


def write_bytes(tmpdir, relpath, data):
    path = Path(str(tmpdir)) / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), "wb") as handle:
        handle.write(data)
    return path


def read(path):
    with open(str(path), "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def png_bytes(width, height=300):
    """The opening bytes of a PNG of the given size: all the checker reads is the header."""
    return (b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height)
            + b"\x08\x06\x00\x00\x00" + b"\x00\x00\x00\x00")


def parse_json_output(stdout):
    """The object printed by check_doc.py --json."""
    try:
        return json.loads(stdout)
    except ValueError as exc:
        raise AssertionError("output is not valid JSON (%s): %r" % (exc, stdout[:300]))


class TempDirCase(unittest.TestCase):
    """A test case with a fresh temporary directory in self.tmp (a pathlib.Path), removed afterwards."""

    def setUp(self):
        holder = tempfile.TemporaryDirectory(prefix="docfmt-test-")
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name)


# --------------------------------------------------------------------------- check_doc.py results

class CheckResult(object):
    """The parsed --json output of check_doc.py, plus the process exit code."""

    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.data = parse_json_output(stdout)
        self.findings = []  # (tier, rule, line, message)
        for key, tier in (("blockers", "BLOCKER"), ("majors", "MAJOR"), ("minors", "MINOR")):
            for item in self.data[key]:
                self.findings.append((tier, item["rule"], item["line"], item["message"]))

    @property
    def stats(self):
        return self.data["stats"]

    @property
    def gate(self):
        return self.data["gate"]

    def matching(self, rule, tier=None):
        return [f for f in self.findings if f[1] == rule and (tier is None or f[0] == tier)]

    def has(self, rule, tier=None):
        return bool(self.matching(rule, tier))

    def pairs(self):
        return sorted(set((tier, rule) for tier, rule, _, _ in self.findings))

    def describe(self):
        lines = ["exit %d, gate %s" % (self.returncode, self.gate)]
        lines += ["  %-7s %-3s line %-4s %s" % (tier, rule, line, message[:100])
                  for tier, rule, line, message in self.findings]
        return "\n".join(lines)


class CheckCase(TempDirCase):
    """Base class for tests that run check_doc.py on a document written to the temporary directory."""

    def check(self, text, *flags, name="doc.md", files=None, newline="\n", process=False):
        """Write `text` as tmp/name (plus `files`: relative path -> str or bytes), run check_doc.py --json.

        The script runs in this process unless `process` is true (a real child process)."""
        path = write(self.tmp, name, text, newline=newline)
        for relpath, content in (files or {}).items():
            if isinstance(content, bytes):
                write_bytes(self.tmp, relpath, content)
            else:
                write(self.tmp, relpath, content)
        runner = run_script if process else run
        code, out, err = runner("check_doc.py", path, "--json", *flags)
        return CheckResult(code, out, err)

    def assertHas(self, result, rule, tier=None):
        self.assertTrue(result.has(rule, tier),
                        "expected a %s %s finding\n%s" % (tier or "any-tier", rule, result.describe()))

    def assertLacks(self, result, rule, tier=None):
        self.assertFalse(result.has(rule, tier),
                         "unexpected %s %s finding\n%s" % (tier or "any-tier", rule, result.describe()))

    def assertGate(self, result, blockers=None, majors=None, minors=None):
        for key, want in (("blockers", blockers), ("majors", majors), ("minors", minors)):
            if want is not None:
                self.assertEqual(result.gate[key], want, "%s\n%s" % (key, result.describe()))


# --------------------------------------------------------------------------- a known-good document

_GOOD_TEMPLATE = """\
<!-- zone:human -->
# Cache migration is safe to start: one owner must confirm the date

*2026-10-19 · fixture author · final · for the platform team*

## 👤 START HERE - at a glance (for the platform team)

> ### 🟢 Go - start the migration on Monday
>
> **Bottom line:** The new cache passed every check we ran. One owner must confirm the cutover date.
>
> **Confidence:** medium - two staging runs, no production traffic yet.

> ### 🧭 Decisions needed
>
> - **Dana** decides **the cutover date** by **30 Oct** - recommend: Monday 2 Nov
>
> If we get it wrong: the migration slips by a week.

| | Top risks | Impact | Where it is handled |
|---|---|---|---|
| 🟠 | Warm-up is slow | The first hour is slower | [2 Risks and warm-up](#2-risks-and-warm-up) |

**Key facts:** 2 staging runs · 0 failed checks · 1 open decision
@@PANEL@@
**Read next**

- [1 What changes](#1-what-changes) - the before and after · 1 min
- [2 Risks and warm-up](#2-risks-and-warm-up) - what can go wrong · 2 min
- [A Evidence](#a-evidence) - raw numbers · archive only

*Only deciding? You can stop here.*

## 1 What changes

*The one-paragraph answer to "what is different after the move".*

Requests now hit the new cache first and fall back to the database. Nothing else in the request path changes.
@@BODY@@
**Next →** [2 Risks and warm-up](#2-risks-and-warm-up)

## 2 Risks and warm-up

The cache starts empty, so the first hour is slower. Plan the cutover for a quiet period.
@@FILLER@@
---

<!-- zone:archive -->
## 🗄️ Machine and archive zone - skip unless you need the evidence

*Raw numbers behind section 1 and section 2.*

### A Evidence

*🗄️ Archive - the staging timings; supports section 2.*
@@ARCHIVE@@
<details>
<summary>Staging timings - click to expand</summary>

| Run | Warm-up minutes |
|---|---|
| 1 | 48 |
| 2 | 52 |

</details>
"""


def _slot(text):
    return "\n%s\n" % text.strip("\n") if text else ""


def bullets(count, prefix="Fact"):
    """`count` distinct one-line bullets: bulk that adds lines but no repeated paragraphs."""
    return "\n".join("- %s number %d about the cache move." % (prefix, i) for i in range(1, count + 1))


def table(rows, header=("n", "value")):
    """A Markdown table with `rows` data rows (the header and separator rows come on top)."""
    lines = ["| %s | %s |" % header, "|---|---|"]
    lines += ["| %d | row %d |" % (i, i) for i in range(1, rows + 1)]
    return "\n".join(lines)


def code_block(lines, lang="text"):
    """A fenced code block with exactly `lines` lines inside the fence."""
    body = "\n".join("line %d of the log" % i for i in range(1, lines + 1))
    return "```%s\n%s\n```" % (lang, body)


def good_doc(panel="", body="", filler=0, archive=""):
    """A small human-first document that the checker passes with no finding at all.

    panel   extra Markdown inside the glance panel, before the Read-next list
    body    extra Markdown at the end of section 1 (human zone)
    filler  number of extra bullet lines in section 2 (to make the document long)
    archive extra Markdown in the archive block, before its <details>"""
    text = _GOOD_TEMPLATE
    text = text.replace("@@PANEL@@", _slot(panel))
    text = text.replace("@@BODY@@", _slot(body))
    text = text.replace("@@FILLER@@", _slot(bullets(filler)) if filler else "")
    return text.replace("@@ARCHIVE@@", _slot(archive))


GOOD_DOC = good_doc()


def replace_once(text, old, new):
    """`text` with its single occurrence of `old` replaced; fails if `old` is not there exactly once, so a
    test cannot pass because its mutation silently changed nothing."""
    found = text.count(old)
    if found != 1:
        raise AssertionError("expected exactly one %r in the document, found %d" % (old, found))
    return text.replace(old, new)
