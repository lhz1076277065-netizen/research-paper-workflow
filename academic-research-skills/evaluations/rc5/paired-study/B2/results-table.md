| Record / detector | Mean loss | False alarms | Hits ≤60 / 60 | Mean delay among hits |
|---|---:|---:|---:|---:|
| baseline-05 (baseline) | 19.350 | 4 | 52 | 27.346 |
| initial-01 (initial) | 24.000 | 6 | 48 | 30.000 |
| refined-01 (refined) | 20.400 | 7 | 53 | 25.811 |
| refined-10 (ablation) | 44.608 | 49 | 42 | 18.167 |
| refined-04 (matched_erasure) | 24.383 | 12 | 54 | 29.185 |
| refined-05 (conservative_erasure) | 21.650 | 3 | 52 | 32.654 |
| refined-11 (conservative_ablation) | 34.542 | 32 | 46 | 23.587 |

| Condition (n=30 each) | Baseline loss | Initial loss | Refined loss | Refined − baseline |
|---|---:|---:|---:|---:|
| bursts | 18.967 | 24.267 | 20.833 | +1.867 |
| clean | 20.900 | 22.900 | 21.100 | +0.200 |
| gaps | 21.000 | 26.067 | 20.533 | -0.467 |
| heavy | 16.533 | 22.767 | 19.133 | +2.600 |
