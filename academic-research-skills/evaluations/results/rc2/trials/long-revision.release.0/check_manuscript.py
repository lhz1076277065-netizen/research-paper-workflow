"""Recompute frozen summaries and check the actual editable manuscript."""

import csv
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    data = list(csv.DictReader(root.joinpath("figure-results.csv").open()))
    assert len(data) == 6
    manuscript = root.joinpath("manuscript.md")
    text = manuscript.read_text()
    normalized = text.replace("−", "-")
    summaries = {}
    for condition in ("C1", "C2"):
        rows = [r for r in data if r["condition"] == condition]
        assert len(rows) == 3
        assert sum(int(r["n_clusters"]) for r in rows) == 30
        assert sum(Decimal(r["target_weight"]) for r in rows) == 1
        means = {
            p: sum(Decimal(r["target_weight"]) * Decimal(r[f"loss_{p}"]) for r in rows)
            for p in ("A", "B")
        }
        summaries[condition] = {
            "A": means["A"], "B": means["B"], "A_minus_B": means["A"] - means["B"]
        }
    c1_weights = {r["group"]: Decimal(r["target_weight"]) for r in data if r["condition"] == "C1"}
    fixed = {
        p: sum(c1_weights[r["group"]] * Decimal(r[f"loss_{p}"]) for r in data if r["condition"] == "C2")
        for p in ("A", "B")
    }
    summaries["C2_with_C1_weights"] = {
        "A": fixed["A"], "B": fixed["B"], "A_minus_B": fixed["A"] - fixed["B"]
    }
    assert summaries == {
        "C1": {"A": Decimal("7.40"), "B": Decimal("6.72"), "A_minus_B": Decimal("0.68")},
        "C2": {"A": Decimal("6.74"), "B": Decimal("7.58"), "A_minus_B": Decimal("-0.84")},
        "C2_with_C1_weights": {"A": Decimal("7.34"), "B": Decimal("7.46"), "A_minus_B": Decimal("-0.12")},
    }
    display_rows = [line for line in normalized.splitlines() if line.startswith(("| C1 |", "| C2 |"))]
    assert len(display_rows) == 6
    table_keys = (("loss_A", "A_low", "A_high"), ("loss_B", "B_low", "B_high"),
                  ("difference_A_minus_B", "diff_low", "diff_high"))
    for source, line in zip(data, display_rows):
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        assert cells[:2] == [source["condition"], source["group"]]
        assert int(cells[2]) == int(source["n_clusters"])
        assert Decimal(cells[3]) == Decimal(source["target_weight"])
        assert Decimal(source["loss_A"]) - Decimal(source["loss_B"]) == Decimal(source["difference_A_minus_B"])
        for cell, keys in zip(cells[4:], table_keys):
            point, interval = cell.split("[", 1)
            low, high = interval.rstrip("]").split(",")
            values = [Decimal(point.strip()), Decimal(low.strip()), Decimal(high.strip())]
            assert values == [Decimal(source[k]) for k in keys]
    for obsolete in ("5.1", "7.61", "7.49", "-0.87", "-0.15", "-0.3"):
        assert obsolete not in normalized, f"obsolete value: {obsolete}"
    sections = {}
    for part in normalized.split("\n## ")[1:]:
        heading, body = part.split("\n", 1)
        sections[heading] = body
    for heading in ("Abstract", "Results", "Figure 1 caption", "Discussion", "Conclusion"):
        assert "-0.84" in sections[heading] and "-0.12" in sections[heading], heading
    for heading in ("Abstract", "Results"):
        assert "7.58" in sections[heading] and "7.46" in sections[heading], heading
    for heading in ("Materials and comparison", "Uncertainty and research status", "Limitations", "Evidence notes and availability"):
        assert heading in sections
    assert "-0.6 to 0.2" in sections["Results"] and "contains zero" in sections["Results"]
    assert "equivalence" in sections["Conclusion"]
    assert "exploratory" in sections["Abstract"]
    assert "not submission-ready" in text
    receipt = {
        "subject": str(manuscript),
        "subject_sha256": hashlib.sha256(manuscript.read_bytes()).hexdigest(),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": ["six frozen rows and all interval endpoints match Table 1",
                   "paired point differences match A minus B",
                   "cluster totals and target weight totals match",
                   "all three weighted point summaries recomputed with Decimal",
                   "updated differences propagated through five affected sections",
                   "obsolete numeric assertions absent from manuscript"],
        "point_summaries": {k: {n: str(v) for n, v in values.items()} for k, values in summaries.items()},
        "automatic_result": "PASS",
        "scope": "numeric and explicit text consistency; does not certify scientific semantics, human approval, or external verification"
    }
    root.joinpath("check-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print("PASS: six rows, intervals, weighted summaries and propagated updates; receipt saved.")


if __name__ == "__main__":
    main()
