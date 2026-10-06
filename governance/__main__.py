"""Command line:
  python -m governance classify    assessment/systems.json        EU AI Act triage per system
  python -m governance register    assessment/risk_register.csv   validate, score, heat map
"""

import argparse
import json
import sys
from pathlib import Path

from . import register as reg
from .classify import classify


def cmd_classify(a):
    systems = json.loads(Path(a.systems).read_text(encoding="utf-8"))["systems"]
    for s in systems:
        result = classify(s)
        print(f"## {s['name']}\n")
        print("Tier(s): " + "; ".join(result["tiers"]) + "\n")
        print("| Ref | Obligation | Applies from |")
        print("|---|---|---|")
        for o in result["obligations"]:
            print(f"| {o['ref']} | {o['text']} | {o['applies_from']} |")
        for n in result["notes"]:
            print(f"\n- {n}")
        print()


def cmd_register(a):
    rows = reg.load(a.register)
    problems = reg.validate(rows)
    if problems:
        for p in problems:
            print(f"INVALID: {p}")
        sys.exit(1)

    print("| ID | System | Risk | Inherent | Residual | Decision | Owner |")
    print("|---|---|---|---:|---:|---|---|")
    for row in sorted(rows, key=lambda r: reg.score(r), reverse=True):
        residual = reg.score(row)
        print(f"| {row['id']} | {row['system']} | {row['risk']} | {reg.score(row, residual=False)} "
              f"| {residual} | {reg.appetite(residual)} | {row['owner']} |")

    print("\nResidual risk heat map (rows = impact, columns = likelihood):\n")
    grid = reg.heatmap(rows)
    print("| Impact \\ Likelihood | 1 | 2 | 3 | 4 | 5 |")
    print("|---|---|---|---|---|---|")
    for impact in range(5, 0, -1):
        cells = " | ".join(str(grid[impact][l]) if grid[impact][l] else "." for l in range(1, 6))
        print(f"| {impact} | {cells} |")

    blocked = [r["id"] for r in rows if reg.appetite(reg.score(r)) == "BLOCK"]
    board = [r["id"] for r in rows if reg.appetite(reg.score(r)) == "BOARD SIGN-OFF"]
    print(f"\n{len(rows)} risks; board sign-off needed: {', '.join(board) or 'none'}; "
          f"blocking: {', '.join(blocked) or 'none'}")
    if blocked:
        sys.exit(2)


def main(argv=None):
    p = argparse.ArgumentParser(prog="governance", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("classify")
    c.add_argument("systems", nargs="?", default="assessment/systems.json")
    c.set_defaults(func=cmd_classify)
    r = sub.add_parser("register")
    r.add_argument("register", nargs="?", default="assessment/risk_register.csv")
    r.set_defaults(func=cmd_register)
    a = p.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
