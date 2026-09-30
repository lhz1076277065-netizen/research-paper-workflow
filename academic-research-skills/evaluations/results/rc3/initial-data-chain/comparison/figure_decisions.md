# SYNTHETIC figure implementation

## Data and message

The source has 43 rows but only 41 distinct events and eight independent unit pairs. After unit conversion and validity-date metadata matching, each stratum contains four unit contrasts. Their means have opposite signs. The standardized target contrast differs from the equally weighted sample contrast. The figure therefore needs to expose composition, individual unit variation, heterogeneity, and the conditional interval together.

## SciPilot selection and production

SciPilot's `profile_data()` actually ran on `pairs.csv`, grouped by stratum; its saved reports are `scipilot_profile.json` and `scipilot_profile.md`. The group summary confirms n=4 per stratum. Automated column-type suggestions were treated as EDA hints, not as the research design: unit IDs are identifiers; technical-repeat counts are not independent sample sizes. Based on the chart-selection reference, the chosen display is stacked horizontal composition bars plus a paired-difference dot/interval display. A continuous weight-sensitivity curve explains the reversal without connecting categorical means. Alternative: separate A/B paired slope plots, which would retain absolute scores but use more space. Alternative: contrast dots alone, which would leave the target/sample composition implicit. Smooth violin/KDE and mean-only score bars were rejected for n=4.

`setup_style(journal='general', lang='en', use_sciplots=False)` supplies the publication style; fixed physical layout, 7–10 pt text, DejaVu Sans and an Okabe–Ito blue/orange palette adapt it to the requested size. Hatching, circles/squares, and filled/open diamonds add redundant cues. `add_panel_labels()` is used on the actual figure. The target is 180 × 103 mm; no journal compliance is claimed.

`audit_layout()` ran on the actual figure and returned no issues. `render_preview()` produced the inspected PNG. The first inspection identified hatch strokes through percentage labels and the sample label near the sensitivity line. Solid label backgrounds and a moved annotation were applied; the updated preview was inspected. All unit points, intervals and zero references remain visible. Only after that inspection were the final editable SVG and 600-dpi PNG exported. The export uses the fixed canvas, without a tight bounding-box crop that would change physical dimensions. File audits and a grayscale preview are included. Numeric and physical checks are implemented in `verify.py`.

The professional workflow is adapted in the current Agent and serves this final figure; it is not an export-only demonstration. Machine checks are supplemented by image inspection, and neither is a journal acceptance certificate.
