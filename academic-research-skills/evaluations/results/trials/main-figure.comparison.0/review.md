The actual main figure is `main-figure.pdf`, with editable vector text in `main-figure.svg`, a 300 dpi preview in `main-figure.png`, and reproducible plotting source in `plot_main_figure.py`. Inputs are copied unchanged into `inputs/`; both material hashes and the v3.1.0 Skill entry hash matched the frozen request. This is a synthetic evidence discussion, not an empirical research result.

The selected professional implementation is [SciPilot, main at 43098ddb9e6a6d142218540c114f9ed38922fc42](https://github.com/Haojae/scipilot-figure-skill/tree/43098ddb9e6a6d142218540c114f9ed38922fc42). Its chart-selection framework and point-interval recipe contributed the main design: retain stratum counterexamples beside the condition-specific mixtures, with supplied uncertainty only where available. Shared 0–10 loss axes and consistent circle/square markers support direct and grayscale comparison. Actual upstream profiling, style, panel-label, layout-audit, export and file-check functions operated on this figure. Profiling counts describe summary rows, not sampling units; raw-data distribution/correlation suggestions were not used. A table is a feasible alternative; box/violin plots would require unavailable raw distributions. The neutral 7.2 × 4.5 in canvas is a design choice, not verified compliance with a named journal.

The exact weighted arithmetic and the plotted point/interval coordinates were checked against the supplied rows (`numeric-review.json`):

| Condition | S1:S2 weights | A | B | B − A |
|---|---:|---:|---:|---:|
| Reference | 80:20 | 4.80 | 4.36 | −0.44 |
| Changed | 20:80 | 6.60 | 7.52 | +0.92 |

Stratum B − A differences are −0.80 and +1.00 for reference S1/S2, and −0.20 and +1.20 for changed S1/S2. B's lower point loss is limited to S1 and the reference mixture. Supplied intervals cannot supply uncertainty for aggregates or paired differences. No test, causal or mechanism claim was added.

Actual visual review used rendered color and grayscale PNGs. Round 1 found main/panel title overlap and footer/tick overlap that the layout auditor missed; moving the plotting rectangle after upstream layout finalization corrected both. Round 2 and the final PDF rasterization passed all eight checks: glyphs, clipping, text/data occlusion, panel-label alignment, panel separation, grayscale identification, complete interval visibility, and consistent axes/encodings. Labels remain at least 8 pt at the intended size. This was screen review; no physical print, external reader test or color-vision simulation was performed.

The upstream strict file checker exited 0: SVG and PNG passed, while its optional PDF font check reported INFO because pypdf was absent. An independent PyMuPDF check confirmed embedded TrueType fonts, one 518.4 × 324 pt page, all numeric labels, and no raster images. SVG contains 47 editable text nodes and no image elements; PNG is 2160 × 1350 pixels at approximately 300 dpi (`file-review.json`). The source is adapted in the current host; no other assistant/model host or field study was used.

Rebuild from this directory with the shared Python interpreter and `plot_main_figure.py --export`. Its assertions check the frozen input hash, all plotted endpoints, the weighted values and the ranking reversal.
