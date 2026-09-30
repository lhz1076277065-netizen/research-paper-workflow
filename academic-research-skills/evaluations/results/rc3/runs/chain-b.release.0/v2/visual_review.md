# SYNTHETIC corrected-figure inspection

The current Agent viewed the actual corrected `main_figure_preview.png` before export, then the exported `main_figure.png` and its derived grayscale PNG. This is a same-context inspection of the updated figure, not an external review. The full PNG is 2125 × 1181 pixels; the displayed review copies were resized to 2048 × 1138. The editable SVG dimensions and PNG metadata were checked independently by the retained figure workflow.

| Visual check | Actual observation | Judgment |
|---|---|---|
| Main argument | Target 80/20 and observed 50/50 bars sit above the opposing raw differences and aggregate rankings | Clear |
| Object and unit | Each raw point represents one independent paired unit; four in each stratum are visible, including the now +5 u08 difference | Correct |
| Chart structure | Bars represent composition only; common-axis forest represents score differences and intervals | Consistent |
| Axes and scale | All difference rows use the retained -2 to 6.5 axis and a zero reference; the same scale enables comparison with the preserved earlier figure | Correct |
| Uncertainty and baseline | Conditional interval header, fixed-weight resampling footer, target zero inclusion and sampled comparison are explicit | Correct |
| Numeric reconciliation | Stratum 2 +2.75 [+1.50,+4.25], target -0.25 [-0.65,+0.15], sampled +0.88 [+0.19,+1.62] match the two-decimal plotted annotations | Correct |
| Label/space integrity | No visible clipping, collisions or missing glyphs; header and right-hand interval text stay on the canvas | Pass |
| Grayscale | Composition hatch, circle/square shapes, row labels and numeric endpoints retain meaning; light second-stratum marks remain visible | Pass within supplied artifact scope |

The annotations use Python's two-decimal formatting; exact values and intervals are in `figure_source.csv` and the caption. The primary interval is conditional on the empirical strata and stipulated independence; no guaranteed real-population coverage or causal interpretation follows from the graphic. The related omission changes are reported separately in the manuscript and CSV, rather than relabeled as the main intervals.
