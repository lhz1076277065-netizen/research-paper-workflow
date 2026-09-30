# Operation and actual review

Produced `plot_main_figure.py`, `main-figure.svg`, `main-figure.pdf`, `main-figure.png`, the grayscale preview, and `caption.md` from the two frozen input files. Their SHA-256 values and the assigned Skill entry matched the request. The input CSV is copied unchanged. This is a manufactured evaluation example.

## Professional operation

Used scientific-visualization 3.2.0-rc.1 and [SciPilot's current main branch](https://github.com/Haojae/scipilot-figure-skill/tree/43098ddb9e6a6d142218540c114f9ed38922fc42), pinned to commit `43098ddb9e6a6d142218540c114f9ed38922fc42` (README reports v2.1.0). Its [chart-selection framework](https://github.com/Haojae/scipilot-figure-skill/blob/43098ddb9e6a6d142218540c114f9ed38922fc42/references/chart_selection.md) contributed distinct visual channels for condition, stratum, method and uncertainty; its [errorbar and multi-panel recipes](https://github.com/Haojae/scipilot-figure-skill/blob/43098ddb9e6a6d142218540c114f9ed38922fc42/references/plot_recipes.md) informed the capped intervals, common loss scale and consistent method encoding. The final figure uses its actual profiling, style, layout, panel-label, preview, layout-audit, export and format-audit functions. Its visual-review checklist guided inspection of the final color, grayscale and PDF-rendered files.

Adapted in this Codex host: the eight table rows are summaries, so profiler row counts and raw-data distribution recommendations are not observation-level evidence. The n column determines weights. Supplied interval endpoints replace recipe SEM calculations; no simulations, bootstrap or tests were run. The fixed brief supplied the argument and allowed source selection without further confirmation. A general 180×132 mm layout is used; no particular journal's acceptance requirements are claimed. SVG text remains editable. Exact-size export disables tight cropping; grayscale is generated separately because the upstream grayscale helper rewrites its color PNG with tight cropping. Upstream source files remain unchanged and retain their MIT license.

## Numeric review

Eight actual Matplotlib point/interval artists were read back and asserted equal to the supplied loss, lo and hi (absolute tolerance 1e−12); see `plotted-row-review.json`. No row was omitted. All derived values use exact Decimal arithmetic and runnable assertions in the plotting source.

| Condition | Stratum | n per method | A loss [95% interval] | B loss [95% interval] | B−A |
|---|---|---:|---|---|---:|
| Reference | S1 | 80 | 4.0 [3.7, 4.3] | 3.2 [2.9, 3.5] | −0.8 |
| Reference | S2 | 20 | 8.0 [7.5, 8.5] | 9.0 [8.4, 9.6] | +1.0 |
| Changed | S1 | 20 | 5.0 [4.5, 5.5] | 4.8 [4.3, 5.3] | −0.2 |
| Changed | S2 | 80 | 7.0 [6.6, 7.4] | 8.2 [7.7, 8.7] | +1.2 |

Weighted loss is `w(S1) × loss(S1) + w(S2) × loss(S2)`, using a separate n=100 total for each method; A and B counts are not added.

| Loss rows | S1:S2 weights | A | B | B−A |
|---|---|---:|---:|---:|
| Reference | 80:20 observed | 4.80 | 4.36 | −0.44 |
| Changed | 20:80 observed | 6.60 | 7.52 | +0.92 |
| Changed | 80:20 fixed reference | 5.40 | 5.48 | +0.08 |

The fixed-weight row is a re-expression of the supplied results, not a new observation or a chosen target-population estimate. Both stratum losses and composition differ between conditions; the reversal cannot be causally attributed to composition. Row-level interval overlap or separation is not used as a significance test. Interval endpoints are not averaged into aggregate intervals.

## Actual visual and format review

Opened the 150 dpi pre-export color and grayscale previews, then the final 300 dpi color/grayscale PNG and the independent 150 dpi PDF rendering. At the designed 180 mm width, the eight row values, interval caps, n labels, weight proportions and −0.44/+0.92/+0.08 comparisons are readable. The supplied interval extremes (2.9–9.6) all lie within the common 0–10.4 loss range.

| Checklist item | Actual observation |
|---|---|
| Glyphs | Letters, numbers and minus signs are intact; no boxes. |
| Clipping | Titles, axis labels, data and footer are inside the canvas. |
| Occlusion | Legends occupy vacant space; numeric labels do not cover points or caps. |
| Panel labels | a/b and c/d share row heights; a/c and b/d share left alignments. |
| Panel spacing | Axis labels and titles do not intrude into adjacent panels. |
| Color/grayscale | Blue-circle/orange-square redundancy distinguishes A/B; light-solid/dark-hatched bars distinguish strata. |
| Completeness | All eight supplied point/interval pairs and all three derived differences are visible. |
| Consistency | Methods retain colors/markers across a/b and share the same loss range; c uses percentages and d explicitly uses B−A. |

The provider layout audit returned no issues. Initial execution needed native-scalar JSON serialization for profiler output and correction of the plotting script's layout rectangle height after an audit flagged top-label clipping; the final figure was regenerated and reopened after these fixes.

Final PNG: 2125×1559 px at 300 dpi (stored metadata 299.9994 dpi). PDF: one 180×132 mm page, 97 vector drawing objects, no raster images, all three font subsets embedded as CID TrueType. SVG: 68 editable text elements and no image elements. The provider skipped its optional pypdf check because pypdf was unavailable; existing Poppler `pdffonts`/`pdfinfo` and PyMuPDF independently verified the PDF size, embedding and render. See `independent-format-review.json` for actual outputs.

Rebuild the checked final figure with the supplied interpreter:

```bash
LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python plot_main_figure.py --stage final
```

Scope: descriptive figure and review only. No raw samples, significance tests, aggregate uncertainty, causal identification or mechanism experiment were added. Token use, fees and exact model identity are unknown.
