# Supplement S1 — version 3

SYNTHETIC developmental supporting material; not submitted.

## S1.1 Record and scope

The authoritative evidence.md version 2 reports eight independent paired units, four in each of g1 and g2. Both methods were measured on each unit. Technical repetitions were averaged within each unit and method after unit conversion. Independence is stipulated by the supplied record and has not been independently audited. Repetition counts, conversion details, numerical source observations and original analysis code are absent.

## S1.2 Aggregate values and arithmetic

All differences are A−B in score, with lower score better.

| Comparison | Independent units contributing | Composition weights g1/g2 | Mean A−B score | Supplied uncertainty |
| --- | --- | --- | --- | --- |
| g1 | 4 | g1 only | −1.00 | Not supplied |
| g2 | 4 | g2 only | +3.00 | Not supplied |
| Equal sampled mixture | 8 | 0.5/0.5 | +1.00 | Not supplied |
| Prespecified target mixture | 8 | 0.8/0.2 | −0.20 | 95% percentile bootstrap interval [−0.60, 0.20] |

The sampled result is 0.5×(−1.00)+0.5×3.00=+1.00. The target result is 0.8×(−1.00)+0.2×3.00=−0.20. These calculations reconcile the supplied aggregates; they do not reproduce the unit means or the bootstrap interval from raw data.

The two summaries estimate differently weighted mean paired differences. The target weights were fixed before measurement, according to the record. Equal stratum sample sizes do not establish that the equal sampled mixture is the intended population mixture.

## S1.3 Resampling object and unavailable details

The record reports paired-unit resampling within each stratum, with fixed target weights reapplied for each target-mean draw. It does not report treating technical repetitions as independent units. The supplied target interval is a 95% bootstrap percentile interval [−0.60, 0.20] score. Bootstrap draw count, seed, quantile implementation, realizations and original script were not supplied. The revised package retains the interval as reported and makes no claim of independent replication, appropriate coverage in every population, causal identification or equivalence.

## S1.4 Figure and package code

aggregate-results-v3.csv transcribes the four supplied aggregate means, weights and the single reported interval. Blank uncertainty cells mean not supplied, not zero. figure_1_v3.py reads that table and produces Figure 1 SVG, PNG and PDF. It is new local display code, not the unavailable analysis or bootstrap implementation. No per-unit values, identifiers, additional sample sizes, simulated observations or new experimental results are generated.

The run-level verification checks the frozen file hashes, arithmetic, retained g2, cross-file values, anonymous document properties and editable document contents. Those local checks do not validate unit independence, source data, the resampling procedure, ethics or author approval.

## S1.5 Data/code access draft

Aggregate-result and code sharing are permitted by the supplied fixture license. Redistribution of raw unit-level records and identifiers is prohibited. This package contains neither type of restricted material, and the original raw records were not supplied to the drafting agent. Requests concerning controlled materials must identify the purpose, requested fields and safeguards. The authors must confirm the data custodian, permitted lawful scope and an approved non-redistributive access mechanism, if one is permitted. The license does not authorize the agent to approve access. No access request has been sent and no approval is known. The authors must resolve a specific request route and actual sharing scope before submission under the chosen policy.

## S1.6 Interpretation and version record

The comparison shows opposing stratum directions and a composition-dependent aggregate direction. The target interval includes zero, with no recorded equivalence margin or registered equivalence test. The record contains no causal assignment, confounding measurements, causal adjustment or external validation. These absences limit interpretation rather than erase the diagnostic result.

Version 1 reported −0.30 for the target mixture; the authoritative version 2 memo and the displayed weighted arithmetic support −0.20. Version 3 uses −0.20 in the manuscript, caption, supporting material and figure. The preserved v1 snapshot remains unchanged, and a separate draft correction names both the numerical and interpretive changes.
