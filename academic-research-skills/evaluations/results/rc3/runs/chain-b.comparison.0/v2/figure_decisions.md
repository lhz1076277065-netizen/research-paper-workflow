# SYNTHETIC figure implementation

## Data and message

The source contains 43 rows, 41 distinct events and eight paired independent units. Conversion and validity-date metadata matching precede technical averaging. Four unit contrasts belong to each stratum. The authorised correction increases the last unit's B mean from 5 to 6 score and reduces its A−B contrast from 6 to 5; the other seven unit contrasts are unchanged. The stratum means now equal −1.00 and +2.75. The target contrast is −0.25, while the balanced sample diagnostic is +0.875. The figure exposes composition, all individual contrasts, heterogeneity and the conditional intervals together.

## SciPilot selection and actual production

`profile_data()` and `render_report()` ran on the corrected `pairs.csv`, grouped by stratum; their saved reports show n=4 per stratum. Column-type suggestions remain EDA hints: unit IDs are identifiers and technical-repeat counts are not independent sample sizes. The retained display combines horizontal composition bars, a unit-dot and mean-interval display and a continuous alternative-weight curve. Smooth density plots and mean-only score bars are inappropriate for four units per stratum.

`setup_style(journal='general', lang='en', use_sciplots=False)` and `add_panel_labels()` ran on the corrected figure. The explicit 180 × 103 mm canvas, 7–10 pt text, DejaVu Sans, blue/orange palette, hatching and redundant shapes retain the original design. The data-derived weight curve is now Δ(w)=2.75−3.75w; its crossing annotation and tick reflect 11/15≈73.33%. Target and sample markers derive from the recomputed results. The original label backgrounds and annotation positioning are retained.

`audit_layout()` returned no issues on the corrected figure. The corrected `render_preview()` output was inspected before final export. The final 600-dpi PNG and editable SVG were exported without a tight bounding-box crop. Final PNG and grayscale images were also inspected: all points, intervals, zero references and category cues remain legible; no clipping was observed. The SVG is 180 × 103 mm; PNG physical size differs only by pixel/DPI rounding (179.959 × 102.997 mm, 4251 × 2433 pixels). `check_figure()` and the independent physical/text/raster checks in `verify.py` pass. The corresponding audits are retained.

This workflow serves the actual main figure, caption and numerical explanation. Machine and Agent visual checks establish this local synthetic scope; they do not establish journal acceptance or real-world scientific validity.
