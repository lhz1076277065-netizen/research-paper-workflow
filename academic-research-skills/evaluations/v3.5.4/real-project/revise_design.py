from pathlib import Path
from datetime import datetime
import shutil
r=Path(__file__).resolve().parent
d=r/'refine-logs';d.mkdir(exist_ok=True)
suffix='20261013_232300'
p=(r/'research-plan-v1.md').read_text()
p=p.replace('# Experiment Plan v1','# Experiment Plan v2')
p=p.replace('This plan was written before downloading or fitting the datasets.','The scientific design was locked in v1 before downloading or fitting. This v2 preserves that design after official acquisition and before any fitting; it repairs missing pinned support-protocol coverage.')
p+='\n\n## Version 2 support-protocol repair\n\nThe fixed-commit output-versioning, output-manifest and output-language protocols have now been retrieved and read. This revision uses refine-logs, a timestamped plan plus latest copy, and a project output manifest because the real run already has more than 15 artifacts. Explicitly authorized English is retained. Earlier v1 files and errors remain preserved. Both datasets have already been downloaded completely; revalidate and reuse them without new transfers after re-binding the new plan/specification. Scientific hypotheses, methods, partitions and metrics are unchanged; no model has yet been fitted.\n'
pt=d/f'EXPERIMENT_PLAN_{suffix}.md';pt.write_text(p);shutil.copyfile(pt,d/'EXPERIMENT_PLAN.md')
t=(r/'experiment-tracker-v1.md').read_text().replace('# Experiment Tracker — pre-execution','# Experiment Tracker v2 — data acquired, no fitted models')
t=t.replace('| M0 | Whole-file acquisition, schema, class counts, duplicate and leakage setup | Wine and Iris complete official data | No fitting until both ready | planned |','| M0 | Both official complete tables acquired; subsequent QA pending | Wine and Iris | 178/150 rows, cumulative data download 9,776 bytes | downloaded; source rebinding and prep pending |')
t=t.split('The upstream design procedure')[0]+'Pinned shared output protocols were read and applied in this revision. No external/cross-model or human audit is claimed. All scientific analysis remains planned.\n'
tt=d/f'EXPERIMENT_TRACKER_{suffix}.md';tt.write_text(t);shutil.copyfile(tt,d/'EXPERIMENT_TRACKER.md')
paths=[x.relative_to(r).as_posix() for x in r.rglob('*') if x.is_file() and '__pycache__' not in str(x) and not x.name.startswith('.')]
manifest='# Research Output Manifest\n\n| Timestamp | Skill | File | Stage | Description |\n|---|---|---|---|---|\n'
for name in sorted(paths):manifest+=f'| 2026-10-13 | Current-host research workflow | {name} | implementation | Versioned artifact or preserved execution evidence |\n'
(r/'MANIFEST.md').write_text(manifest)
(d/f'MANIFEST_snapshot_{suffix}.md').write_text(manifest)
print(pt.relative_to(r),tt.relative_to(r))
