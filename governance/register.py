"""AI risk register: validation, scoring, heat map and risk-appetite check.

Scores are likelihood x impact, each 1-5. Risk appetite (illustrative):
  residual 1-8   -> accepted by the risk owner
  residual 9-14  -> needs AI governance board sign-off
  residual 15-25 -> not acceptable: the system must not go live until it is reduced
"""

import csv

REQUIRED = ["id", "system", "risk", "category", "likelihood", "impact", "controls",
            "residual_likelihood", "residual_impact", "owner", "nist_function"]
NIST_FUNCTIONS = {"GOVERN", "MAP", "MEASURE", "MANAGE"}


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def score(row, residual=True):
    prefix = "residual_" if residual else ""
    return int(row[prefix + "likelihood"]) * int(row[prefix + "impact"])


def appetite(residual_score):
    if residual_score >= 15:
        return "BLOCK"
    if residual_score >= 9:
        return "BOARD SIGN-OFF"
    return "ACCEPTED"


def validate(rows):
    """Return a list of problems: missing fields, bad scores, unknown NIST functions, duplicates."""
    problems, seen = [], set()
    for i, row in enumerate(rows, start=2):
        where = f"line {i} ({row.get('id', '?')})"
        row_problems = []
        for field in REQUIRED:
            if not str(row.get(field, "")).strip():
                row_problems.append(f"{where}: missing {field}")
        for field in ("likelihood", "impact", "residual_likelihood", "residual_impact"):
            value = str(row.get(field, ""))
            if not value.isdigit() or not 1 <= int(value) <= 5:
                row_problems.append(f"{where}: {field} must be 1-5")
        if row.get("nist_function", "").upper() not in NIST_FUNCTIONS:
            row_problems.append(f"{where}: nist_function must be one of {sorted(NIST_FUNCTIONS)}")
        if row.get("id") in seen:
            row_problems.append(f"{where}: duplicate id")
        seen.add(row.get("id"))
        # Controls should reduce risk, never increase it (only checked when the scores are valid).
        if not row_problems and score(row) > score(row, residual=False):
            row_problems.append(f"{where}: residual score is higher than inherent score")
        problems += row_problems
    return problems


def heatmap(rows):
    """5x5 grid of residual risk counts: grid[impact][likelihood], both 1-5."""
    grid = {i: {l: 0 for l in range(1, 6)} for i in range(1, 6)}
    for row in rows:
        grid[int(row["residual_impact"])][int(row["residual_likelihood"])] += 1
    return grid
