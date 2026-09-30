# SYNTHETIC main-figure visual review

SciPilot's full main-figure workflow was applied to the actual paired-unit data: profile → argument-based selection → production at final size → programmed layout audit → PNG inspection → source revision → reinspection → SVG/PNG export → format and dimension checks → final PNG and grayscale inspection. The first preview is preserved as `main_figure_preview.v1.png`; the final numeric data are unchanged by the visual revision.

The first preview had a long open/filled-symbol explanation approaching the interval-column header and hatch strokes crossing the stratum-2 text. The explanation was shortened, and the direct composition label received a matching solid text background. The second preview and exported final figure were read again. No element was manually edited in a bitmap.

| SciPilot item | Final artifact observation |
|---|---|
| Glyphs | All English labels, minus signs, percentages, and mathematical direction symbols render clearly |
| Clipping | Title, row labels, endpoint column, footer, and score-axis label remain inside the final canvas |
| Overlap/occlusion | Endpoint header and symbol explanation are separated; no legend covers contrasts; duplicate -1 units are separated vertically |
| Panel labels | a/b share the same left figure coordinate, typography, and weight |
| Panel spacing | Composition and difference displays have distinct headings and no invading labels |
| Color/grayscale | Blue circles and gold squares identify strata; hatching and marker shapes remain distinct in grayscale; aggregate diamonds have direct labels |
| Data completeness | All eight raw paired differences are visible, including +6; all interval endpoints and zero reference are in range |
| Cross-panel meaning | Stratum color mapping is consistent; difference rows share one score scale; sample and target compositions are directly labeled |

The exported SVG is 179.999999833 × 100.000000025 mm because points are serialized to six decimal places, agreeing with the 180 × 100 mm canvas within one micrometre. PNG is 2125 × 1181 pixels at nominal 300 dpi. SVG text remains editable and contains no embedded raster image. `figure_qa.json` records the actual final metadata and the absence of programmed layout issues.

The reader can answer the three required questions directly: target composition is 80/20 while observed units are 50/50; the strata oppose each other; the displayed segments are conditional within-stratum paired-unit percentile intervals, with the target segment crossing zero. No external human readability assessment or journal compliance certification was performed.
