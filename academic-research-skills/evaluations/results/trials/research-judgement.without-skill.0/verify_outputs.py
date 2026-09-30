"""Exact analytical/output check; no empirical simulation or model fitting."""
import hashlib
import itertools
import json
from pathlib import Path

REQUEST = Path("LOCAL_EVIDENCE_ROOT/evaluation-suite/requests/research-judgement.without-skill.0.json")
request = json.loads(REQUEST.read_text())
assert request["skill_entry"] is None
for item in request["material_files"]:
    path = Path(item["path"])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
    assert path.read_text().rstrip() in request["material"]

independent = [(r, y, 0.25) for r, y in itertools.product((-1, 1), repeat=2)]
dependent = [(r, r, 0.5) for r in (-1, 1)]

def observables(world):
    return {r: sum(p for a, _, p in world if a == r) for r in (-1, 1)}

def risks(world):
    return (sum(p * (r - y) ** 2 for r, y, p in world),
            sum(p * y ** 2 for _, y, p in world))

assert observables(independent) == observables(dependent) == {-1: 0.5, 1: 0.5}
assert risks(independent) == (2.0, 1.0)
assert risks(dependent) == (0.0, 1.0)
assert risks(independent)[0] - risks(independent)[1] == 1.0
assert risks(dependent)[0] - risks(dependent)[1] == -1.0

output = Path(__file__).resolve().parent
for name in ("judgement.md", "operation-note.md"):
    assert (output / name).is_file() and (output / name).stat().st_size > 0
print("PASS: frozen inputs; equal observables/opposite gains; requested deliverables")
