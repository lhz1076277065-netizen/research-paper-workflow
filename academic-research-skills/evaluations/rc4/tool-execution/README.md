# rc.4 tool execution acceptance

These are actual implementation-stage installation, backend and professional API records on the recorded project machine. Manufactured examples do not establish scientific novelty or biological/prediction claims.

- `first-install-environment.json` and its referenced `setup-runs/749001799e97` preserve the actual missing-package install, pip report/check, imports and distribution snapshot. `environment.json` records later reuse.
- `acceptance.stdout.log` retains the first failed follow-up caused by the managed-reuse guard; `retry.stdout.log` and individual receipts show the repaired successful runs.
- CPU, NumPy and MLX CPU/GPU calibration files contain actual checksums, precise compute timing, process peak RSS and available device allocation. The workload and precision are explicitly limited.
- `professional_chain.py` produced exact symbolic results, 8 molecule descriptors and editable/reload-checked SDF, plus a local research_model trained on 40 manufactured points and evaluated on 40 fixed holdout points. `reload_model.py` reloaded saved coefficients and exactly reproduced predictions.
- `test-research-tools.stderr.log` records 18 passing source-level regressions, including the actual audit CLI, missing outputs and compiled C execution.
- Live upstream discovery/read/fetch records freeze commit/tree/blob; source availability is separate from native Skill research completion. No full figure operation is claimed.
- `official-version-findings.json` separates documentation/support/license findings from actual installed versions and exercised APIs.

`SHA256SUMS` binds every archived input/script/result/receipt/log. Original absolute execution paths stay in receipts as historical provenance; runtime environments and caches are omitted. The original `run_acceptance.py` is retained unchanged as the executed driver.

To reproduce on a compatible platform, run the repository's `src/common/scripts/environment.py ensure --task task.json --workspace . --apply --allow-network --isolated`, then use `run --task task.json --workspace . --script professional_chain.py` and `run --task task.json --workspace . --script reload_model.py`. Backend tests use `calibrate` with the selected backend. Choose actual compatible dependencies on another platform rather than treating this project recipe as universal. New run receipts must be saved separately.

Implementation-stage receipts retain the VERSION present at execution; the final engineering validation records the release identity.
