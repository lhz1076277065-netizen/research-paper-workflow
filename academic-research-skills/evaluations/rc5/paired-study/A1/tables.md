| Method | Mean loss | False alarms / 120 | Hits / 60 | Mean delay among hits | Runtime, s |
|---|---:|---:|---:|---:|---:|
| baseline | 22.692 | 4 | 44 | 25.07 | 0.0069 |
| initial | 20.883 | 3 | 49 | 25.43 | 0.0067 |
| refined | 20.825 | 5 | 52 | 27.29 | 0.2482 |
| ablation | 47.675 | 53 | 37 | 18.41 | 0.0369 |

| Condition, n=30 | Baseline loss | Initial loss | Refined loss | Ablation loss |
|---|---:|---:|---:|---:|
| bursts | 27.000 | 29.800 | 21.967 | 47.300 |
| clean | 25.067 | 21.400 | 20.000 | 33.333 |
| gaps | 19.967 | 17.867 | 21.367 | 50.833 |
| heavy | 18.733 | 14.467 | 19.967 | 59.233 |

| Refined minus comparator | Mean paired loss delta | Descriptive SE | Better / tie / worse | Common-hit delay delta |
|---|---:|---:|---:|---:|
| baseline | -1.867 | 2.074 | 24 / 69 / 27 | 0.68, n=44 |
| initial | -0.058 | 1.874 | 24 / 65 / 31 | 1.67, n=46 |
| ablation | -26.850 | 3.966 | 46 / 37 / 37 | 9.51, n=35 |
