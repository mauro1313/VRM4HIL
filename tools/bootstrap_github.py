#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 VRM4-HIL authors (see NOTICE)
# SPDX-License-Identifier: Apache-2.0
"""Creates GitHub labels, milestones, and issues from docs/requirements.yaml.

Performs step 1 of § 8.2 of the specification: one issue per milestone and one
per requirement (by default only the MUST ones). Uses the `gh` CLI, already
authenticated, and must be run from the root of a repository clone.

By default it writes NOTHING: it prints the commands it would run. To actually
run them, add --apply. Rerunning it is safe: it skips what already exists.

Examples:
    python tools/bootstrap_github.py --start 2026-11-02
    python tools/bootstrap_github.py --start 2026-11-02 --apply
    python tools/bootstrap_github.py --start 2026-11-02 --apply --prio MUST SHOULD
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / "docs" / "requirements.yaml"

AREAS = {
    "PLT": ("area:plant", "HIL plant on PYNQ-Z1"),
    "CTL": ("area:ctrl", "Controller on iCE40UP5K"),
    "IF": ("area:if", "Interfaces"),
    "PRF": ("area:prf", "Performance"),
    "VER": ("area:ver", "Verification and quality"),
    "DOC": ("area:doc", "Documentation"),
}

LABELS = {
    "prio:MUST": ("b60205", "Mandatory requirement"),
    "prio:SHOULD": ("d93f0b", "Expected requirement"),
    "prio:COULD": ("c5def5", "Optional requirement"),
    "owner:A": ("0e8a16", "Owner A (analog/power)"),
    "owner:D": ("1d76db", "Owner D (digital/FPGA)"),
    "owner:A+D": ("5319e7", "Shared responsibility"),
    "type:requirement": ("ededed", "Issue generated from a requirement"),
    "type:milestone": ("fbca04", "Exit criteria for a milestone"),
    **{label: ("bfdadc", desc) for label, desc in AREAS.values()},
}

# Milestone exit criteria (table 7.2), as a checklist.
EXIT_CRITERIA = {
    "M0": [
        "Toolchains installed and versions written in tools/versions",
        "Repository scaffolded with green CI on a sample module",
        "An LED blinks on both boards",
        "Cables verified with continuity and loopback tests",
        "D0 completed",
    ],
    "M1": [
        "Average, switched, and small-signal Python models, with tests",
        "Derived quantities from § 3.5 and budget",
        "D1 in draft",
        "DR1 review (Appendix D.1)",
    ],
    "M2": [
        "ICD frozen (D2)",
        "PYNQ-Z1 -> iCE40 link working in PRBS",
        "DPWM on the iCE40 with P1-P6 demonstrated",
        "TC-03, TC-04, and TC-17 passed for the available part",
    ],
    "M3": [
        "Plant v1 with API, capture, and internal generator",
        "TC-01 and TC-02 passed",
        "Controller v1 in co-simulation with soft-start and load step (VER-04)",
    ],
    "M4": [
        "First closed loop on hardware",
        "TC-05, TC-06, TC-07, TC-18 at the MUST level",
        "DR2 review (Appendix D.2)",
        "Feature list frozen",
    ],
    "M5": [
        "AVP, balancing, protections, FRA, Zout, line transients, and VID",
        "TC-08 ... TC-16 at the MUST level",
        "SHOULD items started in priority order",
    ],
    "M6": [
        "Full acceptance test campaign in a single session",
        "D5 and D6 delivered",
        "Public repository and v1.0 release",
        "Final DR3 review (Appendix D.3)",
    ],
}


def gh(args: list[str], apply: bool, read: bool = False) -> str:
    """Runs `gh`. Reads always happen; writes only with --apply."""
    if not apply and not read:
        print("  [dry-run] gh " + " ".join(_quote(a) for a in args))
        return ""
    res = subprocess.run(["gh", *args], text=True, capture_output=True)
    if res.returncode != 0:
        sys.exit(f"gh {' '.join(args)}\n{res.stderr.strip()}")
    return res.stdout


def _quote(s: str) -> str:
    return s if s and all(c.isalnum() or c in "-_:/.=+" for c in s) else repr(s)


def due_date(start: dt.date, week: int) -> str:
    """End of week `week` (Sunday), format required by the API."""
    day = start + dt.timedelta(days=7 * week - 1)
    return f"{day.isoformat()}T23:59:59Z"


def requirement_body(r: dict) -> str:
    area = AREAS[r["id"].split("-")[0]][1]
    verify = ", ".join(str(v) for v in r["verify"])
    return (
        f"**{r['id']}** · {r['prio']} · {area}\n\n"
        f"{r['title']}.\n\n"
        f"Binding text: VRM4-HIL v1.0 specification, § 4.\n\n"
        f"| Field | Value |\n|---|---|\n"
        f"| Verify | {verify} |\n"
        f"| Milestone | {r['ms']} |\n"
        f"| Owner (proposed) | {r['owner']} |\n\n"
        f"### Done when\n"
        f"- [ ] Implemented and passed review (linked PR)\n"
        f"- [ ] Verification ({verify}) performed\n"
        f"- [ ] Evidence archived (results file in `reports/` or reference to the report)\n"
    )


def milestone_body(key: str) -> str:
    items = "\n".join(f"- [ ] {c}" for c in EXIT_CRITERIA[key])
    return (
        "Exit criteria (specification, table 7.2). The milestone is reached "
        "when all items are checked, not when the week runs out.\n\n" + items + "\n"
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", required=True, type=dt.date.fromisoformat,
                   help="Monday of week 1 (YYYY-MM-DD)")
    p.add_argument("--prio", nargs="+", default=["MUST"], choices=["MUST", "SHOULD", "COULD"],
                   help="priorities to create issues for (default: MUST)")
    p.add_argument("--apply", action="store_true", help="actually execute (default: dry-run)")
    a = p.parse_args()

    if a.start.weekday() != 0:
        sys.exit(f"--start {a.start} is not a Monday")

    data = yaml.safe_load(REQ_FILE.read_text(encoding="utf-8"))
    milestones: dict = data["milestones"]
    reqs = [r for r in data["requirements"] if r["prio"] in a.prio]

    # Current state of the repository (reads: done even in dry-run).
    existing_ms = set()
    existing_issues = set()
    if a.apply:
        existing_ms = {m["title"] for m in json.loads(
            gh(["api", "repos/{owner}/{repo}/milestones?state=all&per_page=100"], a.apply, read=True))}
        existing_issues = {i["title"] for i in json.loads(
            gh(["issue", "list", "--state", "all", "--limit", "1000", "--json", "title"], a.apply, read=True))}

    print("== Labels")
    for name, (color, desc) in LABELS.items():
        gh(["label", "create", name, "--color", color, "--description", desc, "--force"], a.apply)

    print("== Milestones")
    for key, m in milestones.items():
        if m["title"] in existing_ms:
            print(f"  already exists: {m['title']}")
            continue
        gh(["api", "repos/{owner}/{repo}/milestones", "-f", f"title={m['title']}",
            "-f", f"due_on={due_date(a.start, m['week'])}",
            "-f", f"description=End of week {m['week']}"], a.apply)

    print("== Milestone issues")
    for key, m in milestones.items():
        title = f"{m['title']}: exit criteria"
        if title in existing_issues:
            print(f"  already exists: {title}")
            continue
        gh(["issue", "create", "--title", title, "--body", milestone_body(key),
            "--label", "type:milestone", "--milestone", m["title"]], a.apply)

    print(f"== Requirement issues ({', '.join(a.prio)}: {len(reqs)})")
    for r in reqs:
        title = f"{r['id']}: {r['title']}"
        if title in existing_issues:
            print(f"  already exists: {title}")
            continue
        labels = ["type:requirement", f"prio:{r['prio']}", AREAS[r["id"].split("-")[0]][0], f"owner:{r['owner']}"]
        args = ["issue", "create", "--title", title, "--body", requirement_body(r),
                "--milestone", milestones[r["ms"]]["title"]]
        for lab in labels:
            args += ["--label", lab]
        gh(args, a.apply)

    if not a.apply:
        print("\nDry-run: nothing was written. Rerun with --apply to execute.")


if __name__ == "__main__":
    main()
