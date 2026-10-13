# Experiment Plan v2 — fixed training-only preprocessing

Date: 2026-10-13. The scientific design was locked in v1 before downloading or fitting. This v2 preserves that design after official acquisition and before any fitting; it repairs missing pinned support-protocol coverage. Scope: teaching replication on the complete UCI Wine and Iris tables, not novel method research or a general model competition.

## Claim map and four-part storyline

| Claim | Minimum evidence | Block |
|---|---|---|
| C1: Feature standardization can change fixed distance-classifier performance; the direction and size are dataset-specific empirical questions. | Paired raw-versus-scaled predictions on the same prespecified partitions in each dataset. | B1 |
| C2: Results require reporting partition sensitivity and the restricted evaluation scope. | Full per-split results, train-only preprocessing check, independent metric recomputation and a second fixed test fraction. | B2 |

Anti-claims: These experiments do not show population causality, a universally best preprocessing rule, the superiority of a new method, or independent repeated test samples. The gap is a transparent teaching demonstration; existing methods already supply the relevant algorithms. No LLM, frontier component or GPU is scientifically needed. A simple centroid rule tests whether local-neighbor complexity is essential under this protocol.

## Prespecified methods and evaluation

Required datasets: All rows and all feature columns in the authoritative UCI Wine and Iris tables, their labels and official dictionaries. Keep the supplied versions unchanged. Metadata will determine exact schema; data defects will be documented rather than silently repaired. No optional external population is necessary for the deliberately dataset-specific descriptive question.

Fixed arms: majority-class predictor; nearest centroid without scaling; nearest centroid after training-mean/population-standard-deviation scaling; Euclidean k-nearest-neighbor with k=5 without scaling; the same k=5 after training-only scaling. Uniform votes, deterministic smallest-label tie break. Zero training standard deviations map to scale 1. No hyperparameter selection, classifier selection or tuning on test information.

B1 (must run): 30 stratified random 80/20 train/test holdouts, seeds 0 through 29, classwise independent permutations with NumPy default_rng(seed). For each class, test count = max(1, round(0.2*n_class)); remaining observations train. All arms share exact partitions. Primary metric balanced accuracy = mean class recall; secondary accuracy. Save split indices, all test predictions, per-class confusion counts, balanced accuracy and accuracy. Compare scaled minus raw within each method and split, report average paired differences and observed ranges. Repeated holdouts share observations: report descriptive means and split standard deviations, not independent-sample confidence intervals or p-values. Main table: all arms by dataset. Main figure: balanced accuracy and paired scaling differences.

B2 (must run): Recompute confusion and metrics independently from saved predictions, rerun deterministic code to a separate destination and compare prediction/result hashes. Repeat the same five arms on 70/30 partitions with seeds 0 through 29 as prespecified sensitivity. Report disagreements and changes in the qualitative comparison rather than choosing whichever split looks best. Check that scaler parameters exactly match the training data and train/test indices are disjoint; record test means separately only as diagnostics, never fit transforms on them.

Pilot: After BOTH datasets are completely local and validated, fit the first planned partition once on both, validate shapes, metrics and resource cost; a tiny hand-calculated classifier/metric check can test implementation but will not count as research evidence. If code fails, diagnose and correct implementation before full runs, preserving failures. Pilot values will not change seeds, methods or metrics.

## Run order, costs and choices

1. Finish plan, enumerate data needs, verify UCI metadata and download only complete needed tables plus small dictionaries (archives only if the official package requires it).
2. Verify all required file hashes, schemas, row counts, labels, missingness and duplicate records. Preserve original rows; duplicate feature records can cross splits, so explicitly quantify this and limit the independence claim.
3. Prepare immutable arrays and fixed partitions; run pilot then full B1 and B2 locally.
4. Reproduce from raw files and independently recompute metrics. Produce vector scientific figures and their exact CSV values. Assemble report, audit citations and methods, polish expression and check the factual diff.

Estimated data: Two small tabular datasets and small metadata, expected download below 100 kB for data archives, conservatively allocate 2 MB including source-page/dictionary receipts. Expected peak including code, source evidence, prediction CSV, figures, Word/PDF and receipts below 30 MB; initial capacity plan reserves 50 MB. One study receipt, 200 GB cumulative transfer and project occupancy hard caps, default 10 GB free-disk floor. CPU only, <100 MB analysis arrays, expected seconds to a minute of actual computation; elapsed documentation time is separately adjustable. Existing NumPy/pandas, Pillow, reportlab and docx are available; sklearn/scipy/matplotlib are absent. Implement simple algorithms transparently in NumPy and render vector SVG/PDF using installed tools, so no new scientific dependencies or model weights are needed.

## Risks, mitigations and completion

Official endpoints may move: inspect official links and choose an authorized official mirror or supported archive without changing required data. Unexpected size: update estimated plan before transfer and keep hard study quotas. Missing/wrong rows or units: inspect dictionary and exact source, fix acquisition, then recheck all required data. Strong differences may reflect historical dataset geometry and shared samples, not generalizable domain performance. Negative differences remain valid results. Small-sample and duplicate limitations stay visible.

Complete after both datasets pass local readiness, planned fits and prediction-level checks run, all professional source gates pass and the report with figures/Word/PDF and exact reproduction instructions is delivered. Extra methods, exhaustive literature search, inferential claims from correlated splits and novelty inflation are intentionally excluded.


## Version 2 support-protocol repair

The fixed-commit output-versioning, output-manifest and output-language protocols have now been retrieved and read. This revision uses refine-logs, a timestamped plan plus latest copy, and a project output manifest because the real run already has more than 15 artifacts. Explicitly authorized English is retained. Earlier v1 files and errors remain preserved. Both datasets have already been downloaded completely; revalidate and reuse them without new transfers after re-binding the new plan/specification. Scientific hypotheses, methods, partitions and metrics are unchanged; no model has yet been fitted.
