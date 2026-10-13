# Experiment Tracker — pre-execution

| Run | Purpose | Data | Setting | Status |
|---|---|---|---|---|
| M0 | Whole-file acquisition, schema, class counts, duplicate and leakage setup | Wine and Iris complete official data | No fitting until both ready | planned |
| M1 | Pilot correctness/resource check | Both | Seed 0, 20% test, 5 fixed arms | planned |
| B1 | Main matched comparison | Both | Seeds 0–29, 20% test, 5 fixed arms | planned |
| B2 | Sensitivity and independent reproduction | Both | Seeds 0–29, 30% test; duplicate complete run; metric recomputation | planned |
| M2 | Figures, report, citation/science review, polishing and factual differences | Saved actual results | No new claims from formatting | planned |

The upstream design procedure is adapted in the current host. No separate external or cross-model reviewer has been run. Source output-versioning support references are not present in the prepared cache; explicit v1 immutable files and this tracker supply local versioned outputs, while their missing optional support is recorded in the validation log.
