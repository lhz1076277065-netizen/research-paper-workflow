# Research Question Card

Question: For the complete UCI Wine and Iris teaching datasets, how does standardization fitted exclusively on each training partition affect small fixed distance classifiers under identical stratified train/test partitions?
Type: exploratory teaching replication; no originality claim.
Hypothesis: Standardization may change distance-based classification differently on the two datasets; a raw-feature classifier may remain competitive. No direction or winning model is guaranteed.
Why it matters: A compact reproducible comparison makes preprocessing scope and evaluation leakage inspectable.
Current evidence: The user fixes two official UCI datasets and local computation. Scientific metadata have not yet been downloaded or verified in this project.
Missing evidence: Official data dictionaries and versions, complete raw files, actual schema and class balance, fixed-split predictions, scale effects, execution cost and sensitivity.
What would support it: A consistent paired difference between scaled and unscaled variants across prespecified partitions within each dataset.
What would falsify it: Near-zero differences or changes dominated by partition variation; reversal across datasets would refute a universal scaling benefit.
Minimal next action: Complete a locked analysis plan and data requirements, then verify official UCI metadata and acquire both complete required data tables before any model fitting.
Decision: run experiment after source verification and full local readiness.

## Four-part route board

Gap: This teaching replication lacks directly observed results under a transparent fixed local protocol; it does not assert an unresolved scientific field gap.
Limitations/competitors: Raw and training-standardized distances, k-nearest-neighbor versus nearest-centroid decision rules, and a majority-class reference are plausible explanations of performance changes.
Contribution and discriminating evidence: An auditable download-to-report teaching example with matched partitions, per-observation predictions, training-only transforms and reproducible comparisons.
Knowledge and boundary: The outcome describes these two historical datasets and these fixed classifiers; it does not establish a best general-purpose model, population causality, independence of repeated holdouts, or publication novelty.

## Resources and evidence boundary

Local runtime check found sklearn unavailable. Use transparent NumPy implementations if NumPy is present, with unit checks on toy calculations only after the real-data readiness gate. This avoids unnecessary dependency downloads. Existing scientific claims remain speculative until actual official metadata and experiment artifacts exist. No polished literature review is warranted at intake.
Budget: No user hard time limit. Plan tens of minutes for tiny CPU experiments and source-gated reporting, adjust self-planned stage time as required. All acquisitions and project occupancy remain within the same 200 GB receipt; target peak is orders of magnitude smaller.
