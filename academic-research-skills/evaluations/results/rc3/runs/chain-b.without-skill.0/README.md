# SYNTHETIC reproduction bundle

The materials and manuscript are manufactured development artifacts, not a real study.

Run these three commands using the shared Python environment:

```sh
PYTHONDONTWRITEBYTECODE=1 'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/runs/chain-b.without-skill.0/prepare.py'
PYTHONDONTWRITEBYTECODE=1 'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/runs/chain-b.without-skill.0/analysis.py'
PYTHONDONTWRITEBYTECODE=1 'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/runs/chain-b.without-skill.0/check.py'
```

The archive and professional cache are read-only inputs. All generated files and the Matplotlib cache stay in this bundle. `prepare.py` verifies and copies the original archive, checks the matching mirror, extracts original members, and copies four byte-identical professional scripts with their license. `analysis.py` reconstructs event preparation, paired-unit scores, numeric results, bootstrap distributions, robustness checks, and the 180 mm × 100 mm main figure. `check.py` tests malformed inputs, inclusive temporal joins, numeric identities, file dimensions, editable SVG structure, and manuscript/caption consistency; it regenerates evidence records.

Read `manuscript.md`, `caption.md`, and `main_figure.png`/`main_figure.svg` for the scientific presentation. `paired_units.csv`, `flow.json`, `results.json`, and both `robustness_*.csv` files contain the principal numbers. `checks.md` distinguishes numerical, semantic, visual, and human-review status. `operation.md` records the actual process and source versions separately from the scientific content. No global installation is needed; the shared environment supplies NumPy, pandas, SciPy, Matplotlib, and Pillow.
