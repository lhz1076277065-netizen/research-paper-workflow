"""Offline check of the delivered revision against the frozen request."""
from pathlib import Path
from decimal import Decimal
import csv
import hashlib
import io
import json
import re

OUT = Path(__file__).resolve().parent
REQUEST = OUT.parents[1] / "suite/requests/long-revision.comparison.0.json"
request = json.loads(REQUEST.read_text())
manuscript = (OUT / "manuscript.md").read_text()
csv_text = request["material"].split("## fixtures/rc2/figure-results.csv\n", 1)[1].strip()
rows = list(csv.DictReader(io.StringIO(csv_text)))
assert len(rows) == 6
for item in request["material_files"]:
    assert hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"]
assert hashlib.sha256(Path(request["skill_entry"]).read_bytes()).hexdigest() == request["skill_entry_sha256"]

def number(value, signed=False):
    return format(Decimal(value), "+.1f" if signed else ".1f").replace("-", "−")

for row in rows:
    assert Decimal(row["loss_A"]) - Decimal(row["loss_B"]) == Decimal(row["difference_A_minus_B"])
    cells = [row["condition"], row["group"], row["n_clusters"], row["target_weight"]]
    for mean, low, high in (("loss_A", "A_low", "A_high"), ("loss_B", "B_low", "B_high"), ("difference_A_minus_B", "diff_low", "diff_high")):
        cells.append(f"{number(row[mean], mean == 'difference_A_minus_B')} [{number(row[low])}, {number(row[high])}]")
    assert manuscript.count("| " + " | ".join(cells) + " |") == 1, row

summaries = {}
c1_weights = {r["group"]: Decimal(r["target_weight"]) for r in rows if r["condition"] == "C1"}
for label, condition, fixed in (("C1", "C1", False), ("C2", "C2", False), ("C2_fixed_C1", "C2", True)):
    group_rows = [r for r in rows if r["condition"] == condition]
    assert sum(int(r["n_clusters"]) for r in group_rows) == 30
    weights = [c1_weights[r["group"]] if fixed else Decimal(r["target_weight"]) for r in group_rows]
    assert sum(weights) == 1
    a = sum(w * Decimal(r["loss_A"]) for w, r in zip(weights, group_rows))
    b = sum(w * Decimal(r["loss_B"]) for w, r in zip(weights, group_rows))
    summaries[label] = {"A": str(a.quantize(Decimal("0.01"))), "B": str(b.quantize(Decimal("0.01"))), "A_minus_B": str((a-b).quantize(Decimal("0.01")))}
assert summaries == {"C1": {"A": "7.40", "B": "6.72", "A_minus_B": "0.68"}, "C2": {"A": "6.74", "B": "7.58", "A_minus_B": "-0.84"}, "C2_fixed_C1": {"A": "7.34", "B": "7.46", "A_minus_B": "-0.12"}}
for old in ("5.1", "7.61", "7.49", "−0.87", "−0.15"):
    assert old not in manuscript, old
for heading in ("Abstract", "Figure 1 caption", "Conclusion"):
    section = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", manuscript, re.M | re.S)
    assert section and all(value in section.group(1) for value in ("+0.68", "−0.84", "−0.12")), heading
for required in ("clusters are independent between conditions", "paired 95%", "[−0.6, 0.2]", "does not resolve the direction or establish equivalence", "not replaced by observed cluster proportions", "cross-condition interaction test", "equivalence margin", "out-of-domain validation", "not published citations", "not submission-ready", "No human research was conducted"):
    assert required in manuscript, required
digest = hashlib.sha256((OUT / "manuscript.md").read_bytes()).hexdigest()
if (OUT / "factual-semantic-diff.md").exists():
    assert digest in (OUT / "factual-semantic-diff.md").read_text(), "comparison subject hash mismatch"
print(json.dumps({"status": "passed", "manuscript_sha256": digest, "frozen_rows_checked": len(rows), "weighted_summaries": summaries}, indent=2))
