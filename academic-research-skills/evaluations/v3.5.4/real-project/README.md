# Wine and Iris teaching reanalysis

Start with manuscript-final.md or the Word/PDF files in delivery/. This is a complete small empirical teaching report, not a novel algorithm or a submission-ready paper. The authoritative raw sources, actual results and limitations are retained. File provenance and professional step receipts are in the project root; final-validation.md describes this skill acceptance run.

## Data and storage

The complete required original Wine and Iris tables and dictionaries are local in raw/. Official UCI archive URLs are https://archive.ics.uci.edu/static/public/109/wine.zip and https://archive.ics.uci.edu/static/public/53/iris.zip. The managed downloads totaled 9,776 bytes. Both datasets are CC BY 4.0; see references.bib and sources/. Only required archive members were extracted. No sklearn bundled dataset or synthetic table substitutes for the real inputs.

## Reproduce the numerical study

Use Python 3.12.14 and NumPy 2.3.5 for byte-level replay. Figure export also uses Pillow and reportlab; the plotting script records the macOS Arial font path. These are the versions and environment actually used, not a requirement to install a large scientific distribution. The exact bundled interpreter on the test host was:

```sh
PYTHON=/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
```

From this project root, reuse the validated derived tables and locked splits and create a NEW output directory. experiment.py refuses to overwrite an existing output directory.

```sh
"$PYTHON" experiment.py --fraction 0.2 --out rerun-main
"$PYTHON" experiment.py --fraction 0.3 --out rerun-sensitivity
```

Compare results.csv, predictions.csv, scaler-parameters.json and summary.json from rerun-main to results/; runtime.json changes with host timing and is not expected to match. replay/ already contains an actually executed byte-identical main replication. verify_results.py independently recomputes stored main/sensitivity metrics and scalers; it writes robustness-verification.json. To preserve this acceptance archive, run the complete rebuild below in a COPY of the minimal project, not in the original receipt-bound folder.

```sh
mkdir rebuild
cp prepare_data.py experiment.py verify_results.py plot_figures.py dataset-spec-v2.json rebuild/
cp -R raw rebuild/
cd rebuild
"$PYTHON" prepare_data.py
"$PYTHON" experiment.py --pilot --fraction 0.2 --out pilot
"$PYTHON" experiment.py --fraction 0.2 --out results
"$PYTHON" experiment.py --fraction 0.3 --out sensitivity
"$PYTHON" experiment.py --fraction 0.2 --out replay
"$PYTHON" verify_results.py
"$PYTHON" plot_figures.py
"$PYTHON" plot_figures.py --final
```

The original full pipeline was executed in this order. The command list itself is a run guide, not evidence of an additional executed rebuild. Read each output's provenance before reuse. Figure PNGs require visual inspection; editable SVG and vector PDF exports are included. The final report generator and Word rendering instructions are in export_documents.py and document-render.py. Exporting does not validate a scientific claim.

## Interpretation

Training-only standardization improved Wine mean balanced accuracy for both fixed distance rules and decreased Iris means. Partitions reuse observations; reported split spread is descriptive and is not an inferential confidence interval. Historical source imperfections, duplicates, small data and limited algorithms constrain generalization. No human source approval, independent external peer review or journal readiness is claimed.
