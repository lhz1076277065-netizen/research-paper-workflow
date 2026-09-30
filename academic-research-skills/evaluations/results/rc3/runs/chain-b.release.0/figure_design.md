# SYNTHETIC main-figure design

The figure's one argument is that the same paired-unit contrasts produce different descriptive rankings at the stipulated and sampled compositions. Readers must also see the disagreement between strata and the uncertainty of the target summary.

SciPilot's chart-selection axes give: two categorical strata; continuous paired score differences; four units per stratum; comparison, composition, and uncertainty as connected parts of the argument. A stacked horizontal composition display above a common-scale difference forest with every raw unit contrast below it keeps all decisive evidence in one figure. The composition bars show proportions, not outcome means. Open circles show the eight unit differences; solid markers and capped segments show means and conditional percentile intervals. Different marker shapes and a hatched second stratum preserve meaning in grayscale.

A paired A/B absolute-score plot is a reasonable alternative but makes readers subtract scores and compute two weighted averages. A mean-only outcome bar chart would conceal the four-unit samples and the second-stratum counterexample. A violin/KDE would imply distributional resolution unavailable with four units. The selected difference display avoids these problems.

Target specification: exactly 180 × 100 mm, editable SVG text, 300 dpi PNG. All difference rows use one score axis. Target and sampled rows retain the same paired-unit resampling draws, changing only the stated fixed composition. Intervals are labeled as conditional 95% percentile bootstrap intervals rather than standard deviations, standard errors, causal intervals, or guaranteed population coverage.

No journal is selected. User dimensions control the canvas; a generic SciPilot style supplies readable typography and vector-text settings. Numeric checks compare every displayed estimate/endpoint with `results.json`. The final PNG and grayscale PNG will be inspected using the eight-item SciPilot visual-review checklist.
