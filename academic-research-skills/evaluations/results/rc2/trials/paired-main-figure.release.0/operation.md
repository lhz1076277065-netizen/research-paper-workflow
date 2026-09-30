The requested five files are `figure.svg`, `figure.png`, `figure.py`, `caption.md`, and this note. The SVG canvas is 180 × 104 mm with editable text and no embedded raster. The PNG is 300 dpi (2125 × 1228 pixels); `preview.png` is a 96 dpi target-size preview. Keep the figure at 180 mm width. `figure-results.csv` and MIT-licensed `scipilot/` helpers are included for rerunning the editable code:

```sh
'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' -B figure.py
```

Applied the request's scientific-visualization v3.2.0-rc.2 and [SciPilot](https://github.com/Haojae/scipilot-figure-skill/tree/43098ddb9e6a6d142218540c114f9ed38922fc42), reusing the supplied verified cache at commit `43098ddb9e6a6d142218540c114f9ed38922fc42`. The current agent adapted the paired error-bar and multi-panel recipes to this figure and invoked its profiler, style, panel labels, layout audit, export, and file audit. A difference forest plot directly answers the comparison question; plotting marginal A/B intervals would obscure the paired target. A raw-data dot plot is unavailable because only six aggregate rows were supplied. This was adapted in the current host, without another model or agent.

Verified the input hash, counts, weight sums, paired differences, all displayed endpoints, and derived values. Opened the actual target-size previews, final PNG, and grayscale preview; corrected crowded headers, panel spacing, and the footer. The code retains arithmetic assertions, the upstream layout audit, an added footer-versus-tick boundary check, SVG dimension/text checks, and PNG/DPI checks. The final upstream file audit reported no issues. Evidence and source identities are in `qa/` and `resource_reads.jsonl`.

The remaining limitation is inferential: weighted means and sensitivity changes have no estimable interval from these summaries. No marginal-endpoint averaging, raw observations, causal attribution, equivalence tests, or journal-specific submission checks were added. No new data were acquired and no paper was started.
