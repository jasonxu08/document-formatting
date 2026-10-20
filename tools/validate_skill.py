#!/usr/bin/env python3
"""Validate Agent Skill folders against the Agent Skills specification (https://agentskills.io).

Usage:
    python tools/validate_skill.py [SKILL_DIR ...] [--strict] [--no-pyyaml]

Without SKILL_DIR it validates every direct child folder of <repo>/skills/ that contains a SKILL.md
(<repo> is the parent of the folder this script lives in).

Output is one line per finding, `ERROR path: message` or `WARN path: message`, in a fixed order, and
`OK <name>` for a skill that has no finding at all. Exit code: 0 when there is no ERROR (with --strict,
no WARN either), 1 otherwise, 2 for a usage error (unknown option, folder missing, nothing to validate).

Per skill:
  * SKILL.md starts with YAML frontmatter between `---` lines. It is parsed with PyYAML when that is
    installed, else with a small built-in parser (top-level `key: value` scalars, plain or quoted, and one
    nested mapping such as `metadata:`). The built-in parser rejects what real YAML parsers choke on: an
    unquoted value that contains ': ' or starts with one of [ { * & ! | > % @ or a backtick.
  * name: required, ^[a-z0-9]+(-[a-z0-9]+)*$, at most 64 characters, equal to the folder name.
  * description: required, non-empty, at most 1024 characters, no '<' or '>'.
  * license and allowed-tools are strings, compatibility is a string of at most 500 characters,
    metadata is a mapping whose keys and values are all strings (quote "1.0", not 1.0). Other top-level
    keys are a WARN. More than 500 lines in SKILL.md is a WARN.
  * Every relative path the SKILL.md body references exists, with the same letter case (so it also works
    on Linux): Markdown links, and backticked words that start with references/, scripts/ or assets/.
  * Every *.py file compiles (checked with compile(), which writes no bytecode).
  * A file over 1 MB, or a __pycache__ folder, is a WARN.

Per repository (only when the file exists; the repo is <repo> for skills in <repo>/skills/<name>, or the
repository this script lives in):
  * .claude-plugin/plugin.json and marketplace.json parse as JSON. plugin.json needs a string `name`;
    marketplace.json needs `name`, `owner.name` and a non-empty `plugins` list of entries with `name`,
    `source` and `description`. Every entry name equals the plugin.json name, and a `source` starting
    with ./ is an existing folder inside the repo.
  * plugin.json `version` equals the SKILL.md metadata.version.
  * CHANGELOG.md has a `## [X.Y.Z]` heading (a date may follow) for the SKILL.md metadata.version, else WARN.

Only the standard library is required.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import warnings
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode = True  # no bytecode for modules imported from here on; running this file writes none

REPO = Path(__file__).resolve().parent.parent

NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KNOWN_FIELDS = ("name", "description", "license", "compatibility", "metadata", "allowed-tools")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
MAX_LINES = 500
MAX_BYTES = 1024 * 1024
REFERENCE_PREFIXES = ("references/", "scripts/", "assets/")

FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'))?\s*\)")
LINK_DEFINITION = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]*>|\S+)"
                             r"(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^)\n]*\)))?\s*$")
URL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]+:")
PLACEHOLDER_CHARS = "*<>{}$|"
CHANGELOG_HEADING = re.compile(r"^##[ \t]+\[v?(\d+\.\d+\.\d+[0-9A-Za-z.+-]*)\]", re.M)

KEY_LINE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_.-]*)[ \t]*:(?:[ \t]+(.*?))?[ \t]*$")
UNSAFE_FIRST = "[]{},&*!|>%@`"
YAML_NULL = re.compile(r"^(?:~|null|Null|NULL)$")
YAML_BOOL = re.compile(r"^(?:yes|Yes|YES|no|No|NO|true|True|TRUE|false|False|FALSE|on|On|ON|off|Off|OFF)$")
YAML_INT = re.compile(r"^(?:[-+]?0b[0-1_]+|[-+]?0[0-7_]+|[-+]?(?:0|[1-9][0-9_]*)|[-+]?0x[0-9a-fA-F_]+"
                      r"|[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+)$")
YAML_FLOAT = re.compile(r"^(?:[-+]?[0-9][0-9_]*\.[0-9_]*(?:[eE][-+][0-9]+)?|\.[0-9][0-9_]*(?:[eE][-+][0-9]+)?"
                        r"|[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$")
YAML_DATE = re.compile(r"^(?:[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}(?:[Tt]|[ \t]+)"
                       r"[0-9]{1,2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]*)?(?:[ \t]*(?:Z|[-+][0-9]{1,2}(?::[0-9]{2})?))?)$")
ESCAPES = {"0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n", "v": "\v", "f": "\f", "r": "\r",
           "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0",
           "L": "\u2028", "P": "\u2029"}
HEX_ESCAPES = {"x": 2, "u": 4, "U": 8}


class Report(object):
    """The findings of one group (a skill, or the repo-level files), in the order they were found."""

    def __init__(self):
        self.items = []

    def error(self, path, message):
        self.items.append(("ERROR", path, message))

    def warn(self, path, message):
        self.items.append(("WARN", path, message))

    def count(self, level):
        return sum(1 for item in self.items if item[0] == level)


def describe(value):
    """What a parsed frontmatter value is, for messages."""
    if value is None:
        return "an empty value"
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, (int, float)):
        return "a number"
    if isinstance(value, dict):
        return "a mapping"
    if isinstance(value, (list, tuple)):
        return "a list"
    if isinstance(value, (datetime.date, datetime.datetime)):
        return "a date"
    return "a %s" % type(value).__name__


# --------------------------------------------------------------------------- frontmatter parsing

def split_frontmatter(lines):
    """(frontmatter lines, index of the first body line, problem or None)."""
    if not lines or lines[0].rstrip() != "---":
        return None, 0, "no YAML frontmatter: the file must start with a line containing only '---'"
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            return lines[1:index], index + 1, None
    return None, 0, "frontmatter is not closed: there is no second '---' line"


def resolve_plain(text):
    """The Python value a YAML 1.1 parser gives a plain scalar (only str versus non-str matters here)."""
    if text == "" or YAML_NULL.match(text):
        return None
    if YAML_BOOL.match(text):
        return True
    if YAML_INT.match(text):
        return 0
    if YAML_FLOAT.match(text):
        return 0.0
    if YAML_DATE.match(text):
        return datetime.date(2000, 1, 1)
    return text


def parse_quoted(raw):
    """(value, problem) for a quoted scalar that has to end on the same line."""
    quote, out, i = raw[0], [], 1
    while i < len(raw):
        ch = raw[i]
        if quote == '"' and ch == "\\":
            esc = raw[i + 1:i + 2]
            if esc in HEX_ESCAPES:
                digits = raw[i + 2:i + 2 + HEX_ESCAPES[esc]]
                if len(digits) != HEX_ESCAPES[esc] or not re.match(r"^[0-9a-fA-F]+$", digits):
                    return None, "invalid \\%s escape in a quoted value" % esc
                out.append(chr(int(digits, 16)))
                i += 2 + len(digits)
                continue
            if esc not in ESCAPES:
                return None, "unknown escape sequence in a quoted value"
            out.append(ESCAPES[esc])
            i += 2
            continue
        if ch == quote:
            if quote == "'" and raw[i + 1:i + 2] == "'":
                out.append("'")
                i += 2
                continue
            tail = raw[i + 1:]
            if tail.strip() and not re.match(r"^\s+#", tail):
                return None, "unexpected text after the closing quote"
            return "".join(out), None
        out.append(ch)
        i += 1
    return None, "unterminated quoted value (a quoted value must end on the same line)"


def parse_scalar(raw):
    """(value, problem) for the text after `key:`."""
    if raw == "" or raw.startswith("#"):
        return None, None
    first = raw[0]
    if first in "\"'":
        return parse_quoted(raw)
    if first in UNSAFE_FIRST or (first in "-?:" and (len(raw) == 1 or raw[1] in " \t")):
        return None, "is not YAML-safe; quote it (a plain value cannot start with %r)" % first
    plain = re.split(r"\s#", raw, maxsplit=1)[0].rstrip()
    if ": " in plain or ":\t" in plain or plain.endswith(":"):
        return None, "is not YAML-safe; quote it (a plain value cannot contain ': ')"
    return resolve_plain(plain), None


def parse_simple_yaml(lines):
    """The built-in parser: (data, problems, keys that had a problem). `problems` are messages."""
    data, problems, bad = {}, [], set()
    open_key, nested, nested_indent = None, None, None
    for number, raw in enumerate(lines, 2):  # frontmatter line 1 is file line 2
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if raw[indent:indent + 1] == "\t":
            problems.append("line %d: tabs cannot indent YAML" % number)
            continue
        match = KEY_LINE.match(raw[indent:].rstrip())
        if indent == 0:
            open_key, nested, nested_indent = None, None, None
            if not match:
                problems.append("line %d: cannot read this line as 'key: value' (the built-in parser "
                                "does not support lists, multi-line values or flow style)" % number)
                continue
            key, value = match.group(1), match.group(2) or ""
            if key in data:
                problems.append("line %d: duplicate key '%s'" % (number, key))
                continue
            if value == "" or value.startswith("#"):
                data[key] = None
                open_key = key
                continue
            parsed, problem = parse_scalar(value)
            if problem:
                problems.append("line %d: '%s' %s" % (number, key, problem))
                bad.add(key)
            else:
                data[key] = parsed
            continue
        if open_key is None:
            problems.append("line %d: unexpected indentation (the built-in parser reads only one nested "
                            "mapping and no multi-line values; keep each value on one line)" % number)
            continue
        if nested is None:
            nested, nested_indent = {}, indent
            data[open_key] = nested
        if indent != nested_indent:
            problems.append("line %d: inconsistent or deeper indentation is not supported by the "
                            "built-in parser" % number)
            continue
        if not match:
            problems.append("line %d: cannot read this line as 'key: value'" % number)
            continue
        key, value = match.group(1), match.group(2) or ""
        if key in nested:
            problems.append("line %d: duplicate key '%s' in '%s'" % (number, key, open_key))
            continue
        parsed, problem = parse_scalar(value)
        if problem:
            problems.append("line %d: '%s.%s' %s" % (number, open_key, key, problem))
            bad.add(open_key)
        else:
            nested[key] = parsed
    return data, problems, bad


def parse_with_pyyaml(yaml, text):
    """(data or None, problems, bad keys) using PyYAML."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        reason = getattr(exc, "problem", None) or (str(exc).splitlines() or ["unreadable"])[0]
        where = ""
        if mark is not None:  # the text starts on file line 2
            source = text.split("\n")
            snippet = source[mark.line].strip()[:60] if mark.line < len(source) else ""
            where = " at line %d (%s)" % (mark.line + 2, snippet)
        return None, ["frontmatter is not valid YAML%s: %s" % (where, reason)], set()
    if data is None:
        return None, ["frontmatter is empty"], set()
    if not isinstance(data, dict):
        return None, ["frontmatter must be a mapping of keys to values, not %s" % describe(data)], set()
    return data, [], set()


def load_yaml(use_pyyaml):
    """The PyYAML module when it may and can be used, else None."""
    if not use_pyyaml:
        return None
    try:
        import yaml
    except Exception:  # not installed, or a broken install: the built-in parser takes over
        return None
    return yaml


def parse_frontmatter(front_lines, use_pyyaml):
    yaml = load_yaml(use_pyyaml)
    if yaml is not None:
        return parse_with_pyyaml(yaml, "\n".join(front_lines))
    data, problems, bad = parse_simple_yaml(front_lines)
    return data, problems, bad


# --------------------------------------------------------------------------- field checks

def check_fields(data, bad, folder, where, report):
    def required_text(key):
        """The string in a required field, or None after reporting why it cannot be used."""
        value = data.get(key)
        if value is None:
            if key not in bad:  # a key that could not be parsed was reported already
                report.error(where, "missing required field '%s'" % key)
            return None
        if not isinstance(value, str):
            report.error(where, "'%s' must be a string, not %s" % (key, describe(value)))
            return None
        if not value.strip():
            report.error(where, "'%s' must not be empty" % key)
            return None
        return value

    name = required_text("name")
    if name is not None:
        if not NAME.match(name):
            report.error(where, "'name' %r must use only lowercase letters, digits and single hyphens "
                                "(no leading, trailing or doubled hyphen)" % name)
        if len(name) > MAX_NAME:
            report.error(where, "'name' is %d characters; the limit is %d" % (len(name), MAX_NAME))
        if name != folder:
            report.error(where, "'name' %r must equal the folder name %r" % (name, folder))

    description = required_text("description")
    if description is not None:
        if len(description) > MAX_DESCRIPTION:
            report.error(where, "'description' is %d characters; the limit is %d"
                         % (len(description), MAX_DESCRIPTION))
        if "<" in description or ">" in description:
            report.error(where, "'description' must not contain '<' or '>'")

    for key in ("license", "allowed-tools"):
        if key in data and key not in bad and not isinstance(data[key], str):
            report.error(where, "'%s' must be a string, not %s" % (key, describe(data[key])))

    if "compatibility" in data and "compatibility" not in bad:
        value = data["compatibility"]
        if not isinstance(value, str):
            report.error(where, "'compatibility' must be a string, not %s" % describe(value))
        elif len(value) > MAX_COMPATIBILITY:
            report.error(where, "'compatibility' is %d characters; the limit is %d"
                         % (len(value), MAX_COMPATIBILITY))

    if "metadata" in data and "metadata" not in bad:
        metadata = data["metadata"]
        if not isinstance(metadata, dict):
            report.error(where, "'metadata' must be a mapping of string keys to string values, not %s"
                         % describe(metadata))
        else:
            for key in sorted(metadata, key=str):
                value = metadata[key]
                if not isinstance(key, str):
                    report.error(where, "metadata key %r must be a string" % (key,))
                elif not isinstance(value, str):
                    report.error(where, "metadata.%s must be a string, not %s; quote it (for example "
                                        "version: \"1.0.0\")" % (key, describe(value)))

    for key in sorted(data, key=str):
        if key not in KNOWN_FIELDS:
            report.warn(where, "unknown frontmatter field %r (the specification defines %s)"
                        % (key, ", ".join(KNOWN_FIELDS)))


# --------------------------------------------------------------------------- body references

def iter_references(lines, first):
    """(line number, target) for every relative path candidate in the SKILL.md body."""
    in_fence, fence_char, fence_len = False, "", 0
    for index in range(first, len(lines)):
        line = lines[index]
        number = index + 1
        opener = FENCE.match(line)
        if in_fence:
            if re.match(r"^\s{0,3}%s{%d,}\s*$" % (re.escape(fence_char), fence_len), line):
                in_fence = False
            continue
        if opener:
            in_fence, fence_char, fence_len = True, opener.group(1)[0], len(opener.group(1))
            continue
        for span in CODE_SPAN.finditer(line):
            for word in span.group(2).split():
                word = word.rstrip(".,;:)'\"")
                if word.startswith(REFERENCE_PREFIXES):
                    yield number, word
        rest = CODE_SPAN.sub(" ", line)
        for link in LINK.finditer(rest):
            yield number, link.group(1)
        definition = LINK_DEFINITION.match(rest)
        if definition:
            yield number, definition.group(1)


def relative_target(target):
    """The relative filesystem path a link target or backticked word names, or None to skip it."""
    text = target.strip()
    if text.startswith("<") and text.endswith(">"):
        text = text[1:-1]
    if not text or text.startswith("#") or text.startswith("/"):
        return None
    if URL_SCHEME.match(text) or re.match(r"^[A-Za-z]:[\\/]", text):
        return None
    if any(ch in text for ch in PLACEHOLDER_CHARS) or "..." in text:
        return None
    text = unquote(re.split(r"[#?]", text, maxsplit=1)[0])
    return text or None


def lookup(base, rel):
    """'ok' when rel exists under base with the same letter case on every segment, 'case' when only the
    case differs (it works on Windows and macOS but breaks on Linux), else 'missing'."""
    if not os.path.exists(str(base / rel)):
        return "missing"
    current = base
    for part in rel.replace("\\", "/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            current = current.parent
            continue
        try:
            names = os.listdir(str(current))
        except OSError:
            return "ok"
        if part not in names:
            return "case"
        current = current / part
    return "ok"


def check_references(skill, lines, first, where, report):
    seen = set()
    for number, target in iter_references(lines, first):
        rel = relative_target(target)
        if rel is None or rel in seen:
            continue
        seen.add(rel)
        status = lookup(skill, rel)
        if status == "missing":
            report.error(where, "line %d: referenced path '%s' does not exist" % (number, rel))
        elif status == "case":
            report.error(where, "line %d: referenced path '%s' differs in letter case from the file on "
                                "disk (it would break on Linux)" % (number, rel))


# --------------------------------------------------------------------------- files in the skill folder

def walk_skill(skill):
    """(files sorted, __pycache__ folders sorted); __pycache__ is reported, not searched."""
    files, caches = [], []
    for dirpath, dirnames, filenames in os.walk(str(skill)):
        dirnames.sort()
        if "__pycache__" in dirnames:
            dirnames.remove("__pycache__")
            caches.append(Path(dirpath) / "__pycache__")
        for filename in sorted(filenames):
            files.append(Path(dirpath) / filename)
    return files, caches


def check_python(path, where, report):
    try:
        with open(str(path), "rb") as handle:
            source = handle.read()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            compile(source, str(path), "exec", dont_inherit=True)
    except SyntaxError as exc:
        report.error(where, "does not compile: %s (line %s)" % (exc.msg, exc.lineno))
        return
    except Exception as exc:  # null bytes, an unreadable file, or a pathological source
        report.error(where, "cannot be compiled: %s: %s" % (type(exc).__name__, exc))
        return
    for item in caught:
        if issubclass(item.category, (SyntaxWarning, DeprecationWarning)):
            report.warn(where, "compiles with a warning (line %s): %s" % (item.lineno, item.message))


def check_files(skill, base, report):
    files, caches = walk_skill(skill)
    for cache in caches:
        report.warn(cache.relative_to(base).as_posix(), "__pycache__ folder; delete it before publishing")
    for path in files:
        where = path.relative_to(base).as_posix()
        try:
            size = os.path.getsize(str(path))
        except OSError:
            continue
        if size > MAX_BYTES:
            report.warn(where, "file is %.1f MB; the recommended maximum is 1 MB" % (size / 1048576.0))
        if path.suffix == ".py":
            check_python(path, where, report)


# --------------------------------------------------------------------------- repository files

def load_json(path, where, report):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        report.error(where, "cannot be read: %s" % (exc.strerror or exc))
    except ValueError as exc:  # includes JSONDecodeError and UnicodeDecodeError
        report.error(where, "is not valid JSON: %s" % exc)
    return None


def non_empty(value):
    return isinstance(value, str) and bool(value.strip())


def check_marketplace(root, market, plugin_name, where, report):
    if not isinstance(market, dict):
        report.error(where, "must be a JSON object")
        return
    if not non_empty(market.get("name")):
        report.error(where, "missing required string field 'name'")
    owner = market.get("owner")
    if not isinstance(owner, dict) or not non_empty(owner.get("name")):
        report.error(where, "missing required 'owner' object with a string 'name'")
    plugins = market.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        report.error(where, "'plugins' must be a non-empty list")
        return
    root_resolved = root.resolve()
    for index, entry in enumerate(plugins):
        label = "plugins[%d]" % index
        if not isinstance(entry, dict):
            report.error(where, "%s must be an object" % label)
            continue
        for key in ("name", "description"):
            if not non_empty(entry.get(key)):
                report.error(where, "%s is missing a string '%s'" % (label, key))
        name = entry.get("name")
        if non_empty(name) and plugin_name is not None and name != plugin_name:
            report.error(where, "%s name %r must equal the plugin.json name %r" % (label, name, plugin_name))
        source = entry.get("source")
        if not (non_empty(source) or (isinstance(source, dict) and source)):
            report.error(where, "%s is missing 'source' (a ./relative folder, or an object for a remote one)"
                         % label)
        elif isinstance(source, str) and source.startswith("./"):
            target = (root / source).resolve()
            if target != root_resolved and root_resolved not in target.parents:
                report.error(where, "%s source %r points outside the repository" % (label, source))
            elif not target.is_dir():
                report.error(where, "%s source %r is not an existing folder" % (label, source))


def check_repo(root):
    """(Report, info) for .claude-plugin/*.json and CHANGELOG.md of one repository."""
    report = Report()
    info = {"plugin_version": None, "changelog": None}
    folder = root / ".claude-plugin"
    plugin_name = None
    plugin_file, market_file = folder / "plugin.json", folder / "marketplace.json"
    if plugin_file.is_file():
        where = plugin_file.relative_to(root).as_posix()
        plugin = load_json(plugin_file, where, report)
        if plugin is not None and not isinstance(plugin, dict):
            report.error(where, "must be a JSON object")
        elif plugin is not None:
            if non_empty(plugin.get("name")):
                plugin_name = plugin["name"]
            else:
                report.error(where, "missing required string field 'name'")
            if "version" in plugin:
                if non_empty(plugin["version"]):
                    info["plugin_version"] = plugin["version"]
                else:
                    report.error(where, "'version' must be a non-empty string")
    if market_file.is_file():
        where = market_file.relative_to(root).as_posix()
        market = load_json(market_file, where, report)
        if market is not None:
            check_marketplace(root, market, plugin_name, where, report)
    changelog = root / "CHANGELOG.md"
    if changelog.is_file():
        try:
            text = changelog.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            text = ""
        info["changelog"] = set(CHANGELOG_HEADING.findall(text))
    return report, info


def check_against_repo(version, repo_info, where, report):
    """Cross-checks that need the version in SKILL.md metadata."""
    if repo_info["plugin_version"] is not None and version != repo_info["plugin_version"]:
        report.error(".claude-plugin/plugin.json", "version %r must equal metadata.version %s in %s" % (
            repo_info["plugin_version"], "%r" % version if version else "(missing)", where))
    changelog = repo_info["changelog"]
    if changelog is not None and version and version.lstrip("v") not in changelog:
        report.warn("CHANGELOG.md", "no '## [%s]' heading for metadata.version in %s" % (version, where))


# --------------------------------------------------------------------------- one skill

def validate_skill(skill, base, repo_info, use_pyyaml):
    report = Report()
    skill_md = skill / "SKILL.md"
    where = skill_md.relative_to(base).as_posix()
    if not skill_md.is_file():
        report.error(where, "SKILL.md not found")
        return report
    try:
        text = skill_md.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        report.error(where, "is not valid UTF-8: %s" % exc.reason)
        return report
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()

    front, body_start, problem = split_frontmatter(lines)
    data, bad = None, set()
    if problem:
        report.error(where, problem)
    else:
        data, problems, bad = parse_frontmatter(front, use_pyyaml)
        for message in problems:
            report.error(where, message)
    if data is not None:
        check_fields(data, bad, skill.name, where, report)

    if len(lines) > MAX_LINES:
        report.warn(where, "SKILL.md has %d lines; keep it under %d and move detail to references/"
                    % (len(lines), MAX_LINES))
    check_references(skill, lines, body_start, where, report)
    check_files(skill, base, report)

    if repo_info is not None:
        metadata = data.get("metadata") if isinstance(data, dict) else None
        version = metadata.get("version") if isinstance(metadata, dict) else None
        check_against_repo(version if isinstance(version, str) else None, repo_info, where, report)
    return report


def repo_root_of(skill):
    """The repository a skill belongs to: <root>/skills/<name> belongs to <root>; any other folder inside
    the repository this script lives in belongs to that one; the rest belongs to none."""
    if skill.parent.name == "skills":
        return skill.parent.parent
    try:
        skill.relative_to(REPO)
    except ValueError:
        return None
    return REPO


def find_skills():
    folder = REPO / "skills"
    if not folder.is_dir():
        return []
    return sorted((p.resolve() for p in folder.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()),
                  key=lambda p: p.as_posix())


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="validate_skill.py",
        description="Validate Agent Skill folders against the Agent Skills specification.")
    parser.add_argument("skill_dirs", nargs="*", metavar="SKILL_DIR",
                        help="a skill folder (default: every folder under <repo>/skills/ that has a SKILL.md)")
    parser.add_argument("--strict", action="store_true", help="warnings fail the run too")
    parser.add_argument("--no-pyyaml", action="store_true",
                        help="parse the frontmatter with the built-in parser even when PyYAML is installed")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    def usage_error(message):
        parser.print_usage(sys.stderr)
        sys.stderr.write("validate_skill.py: error: %s\n" % message)
        return 2

    if args.skill_dirs:
        skills = []
        for raw in args.skill_dirs:
            path = Path(raw)
            if path.is_file() and path.name == "SKILL.md":
                path = path.parent
            if not path.is_dir():
                return usage_error("not a folder: %s" % raw)
            skills.append(path.resolve())
        skills = sorted(set(skills), key=lambda p: p.as_posix())
    else:
        skills = find_skills()
        if not skills:
            return usage_error("no skill folders (with a SKILL.md) found in %s" % (REPO / "skills"))

    errors = warnings_ = 0
    repos = {}
    for skill in skills:
        root = repo_root_of(skill)
        base = root if root is not None else skill.parent
        repo_info = None
        if root is not None:
            if root not in repos:
                repo_report, info = check_repo(root)
                repos[root] = info
                emit(repo_report)
                errors += repo_report.count("ERROR")
                warnings_ += repo_report.count("WARN")
            repo_info = repos[root]
        report = validate_skill(skill, base, repo_info, not args.no_pyyaml)
        emit(report)
        errors += report.count("ERROR")
        warnings_ += report.count("WARN")
        if not report.items:
            print("OK %s" % skill.name)
    return 1 if errors or (args.strict and warnings_) else 0


def emit(report):
    for level, path, message in report.items:
        print("%s %s: %s" % (level, path, message))


if __name__ == "__main__":
    sys.exit(main())
