#!/usr/bin/env python3
"""Check every item of the library: manifest fields, versions, and the tools' tests.

    python3 scripts/check.py            # manifests + tests (needs pytest, numpy, pandas)
    python3 scripts/check.py --no-tests

Each tool's tests run in their own pytest process (they all import `tool`).
"""
import os
import re
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = re.compile(r"^[a-z][a-z0-9_]{1,40}$")
TYPES = {"series", "dataframe", "number", "integer", "string", "boolean", "list", "dict", "timestamp", "any"}


def check_tool(name, folder):
    problems = []
    for f in ("tool.yaml", "tool.py", "test_tool.py"):
        if not os.path.exists(os.path.join(folder, f)):
            problems.append(f"{f} missing")
    if problems:
        return problems
    m = yaml.safe_load(open(os.path.join(folder, "tool.yaml"))) or {}
    if m.get("name") != name:
        problems.append("tool.yaml name differs from the folder name")
    if not isinstance(m.get("version"), int):
        problems.append("version: an integer")
    for key in ("purpose", "needs", "inputs", "outputs"):
        if not m.get(key):
            problems.append(f"{key} missing")
    for i in m.get("inputs") or []:
        if i.get("type") not in TYPES or not i.get("description"):
            problems.append(f"input {i.get('name')}: type and description")
    if not (m.get("outputs") or {}).get("description"):
        problems.append("outputs.description missing")
    if "def run(" not in open(os.path.join(folder, "tool.py")).read():
        problems.append("tool.py defines no run()")
    return problems


def check_skill(name, folder):
    text = open(os.path.join(folder, "SKILL.md")).read()
    if not text.startswith("---"):
        return ["SKILL.md without front matter"]
    m = yaml.safe_load(text.split("---", 2)[1]) or {}
    problems = [f"{k} missing" for k in ("title", "description") if not m.get(k)]
    if not isinstance(m.get("version"), int):
        problems.append("version: an integer")
    for t in m.get("tools") or []:
        if not os.path.isdir(os.path.join(ROOT, "tools", t)):
            problems.append(f"names unknown tool {t}")
    return problems


def main():
    tests = "--no-tests" not in sys.argv
    failed = 0
    for kind, check in (("tools", check_tool), ("skills", check_skill)):
        for name in sorted(os.listdir(os.path.join(ROOT, kind))):
            folder = os.path.join(ROOT, kind, name)
            if not os.path.isdir(folder) or name.startswith((".", "_")):
                continue
            problems = [] if NAME.match(name) else ["bad folder name"]
            problems += check(name, folder)
            if kind == "tools" and tests and not problems:
                r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=folder,
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    problems.append("tests failed:\n" + r.stdout[-2000:])
            print(f"{'FAIL' if problems else 'ok  '} {kind}/{name}" + "".join(f"\n     {p}" for p in problems))
            failed += bool(problems)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
