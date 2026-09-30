# SYNTHETIC — Fact, semantic, and figure checks

`check.py` is the runnable local check. Its latest execution result and UTC time are saved in `check_results.json`. A machine or Agent check is not human scientific approval.

| Check | Evidence and finding |
|---|---|
| Input identity | Selected original ZIP matches SHA256 `078a354c60fa96ee7ceedca955517176765f7406bd409dec7512337f59018ef4`; copied archive and extracted member bytes match the identity receipt. Mirror bytes match the same archive digest and add no independent information. The proxy was not used. |
| Preparation | 43 input rows → 41 unique events after two exact event copies are removed. Conflicting duplicate events, unsupported units, non-finite values, missing active metadata, overlapping active metadata, and incomplete pairs are rejected by runnable checks. Inclusive metadata boundaries are tested. |
| Measurement unit | Subscore values are divided by 1,000 before averaging; unit-level B scores for g2 are 7, 7, 7, and 5 score. |
| Independent unit | Technical repetitions are averaged separately for each unit/method, then A and B are paired. There are 8 independent units, not 41 events: 4 per stratum. A has 17 and B 24 technical events, so raw-row weighting would misrepresent units. |
| Primary estimand | Fixed target weights are 0.8/0.2; mean differences are −1 and +3. Target difference = −0.2 score; target A/B means = 6.3/6.5. Sample-mix difference = +1, explicitly labeled a different descriptive composition. |
| Stratum disagreement | Every g1 paired difference is negative and every g2 paired difference is positive. The report does not say that strata agree or infer universal A superiority. |
| Conditional interval | Whole paired units are resampled within strata. All 256 ordered resamples per stratum and 65,536 joint combinations are represented. Approximate percentile interval = [−0.65, 0.25] score. Enumeration is exact for the empirical resampling distribution, not for population confidence coverage. |
| Robustness | Eight fixed-target leave-one-unit-out computations give [−0.4, −0.0666667] and retain a negative point estimate. The weight sensitivity crosses zero at g1 weight 0.75. An alternative Welch–Satterthwaite interval [−0.8747594, 0.4747594] also crosses zero. |
| Interpretation | Lower scores are favorable, so A−B < 0 favors A. Point-estimate sign stability is not evidence that sampling uncertainty disappears. An interval crossing zero is not proof of equality. No causal design was provided; no causal conclusion is asserted. |
| Prespecification | The target and weights were supplied before measurements. The interval and three sensitivity choices were selected in this analysis and are labeled descriptive/exploratory. |
| Unknown inputs | Fixture independence and equal precision are stipulated. Real target provenance, real sampling and selection, representativeness, calibration, real independence, real measurement uncertainty, and transportability are not established. |
| Prose consistency | The abstract, result table, result text, and caption repeat matching target and sample-mix values. All 17 claim blocks map to evidence IDs and have text hashes. Human verification and scientific approval remain unknown. |

## Actual PNG and grayscale inspection

The Agent inspected `main_figure.png` and `main_figure_grayscale.png` after rendering. This was a direct image review of the generated files, in addition to the professional layout checker.

1. All title, axis, numerical, and footer characters are legible; no missing-glyph boxes were observed.
2. Titles, tick labels, composition percentages, legend, and footer are inside the canvas.
3. Legends do not cover data. The repeated −1 g1 values are offset so both unit points remain visible. Unit markers, mean diamonds, and whiskers are separated.
4. Panel labels a and b use the same font/style and align on the same title line.
5. Panels and the contrast row labels do not invade each other's content.
6. Blue/orange colors remain distinguishable in grayscale through brightness, hatches, circles/squares, and direct stratum labels. The sample-mix diamond is open and the target diamond filled.
7. All eight unit points and all interval endpoints are visible. The g2 unit at +6 and negative g1 points are inside the x-axis limits.
8. Stratum colors agree between the composition and contrast panels. Contrast rows share one score axis, a labeled A−B orientation, and a visible zero reference.

`figure_machine_qa.json` records zero layout/glyph warnings and zero PNG/SVG file issues. Nominal figure size is 180 mm × 100 mm; SVG dimensions are 179.9999998 mm × 100.0000000 mm. The 600 dpi PNG has 4,251 × 2,362 pixels, with rounding yielding approximately 179.9594 mm × 99.9915 mm. SVG text remains editable and no raster images are embedded. Minimum designed figure font size is 7 pt. No image retouching was used.

## Evidence workflow scope

The professional writing workflow was adapted into a source manifest, 17 hashed claim/evidence bindings, a method/result consistency record, and runnable numerical/text checks. Only local fixture and computed artifacts support the scientific claims. The source manifest explicitly distinguishes Agent/machine checks from unknown human verification. No scholarly bibliography, author contribution, ethics approval, funding, conflict declaration, or journal acceptance was invented.
