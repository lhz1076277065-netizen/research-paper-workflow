# Data profile: LOCAL_EVIDENCE_ROOT/runs/chain-b.comparison.0/pairs.csv

**Shape:** 8 rows × 8 cols

## Columns

| Column | Type | n | missing | summary |
|---|---|---|---|---|
| `unit_id` | unknown | 8 | 0 |  |
| `stratum` | unknown | 8 | 0 |  |
| `observed_at` | unknown | 8 | 0 |  |
| `A` | continuous | 8 | 0 | mean=7.5, sd=2.45, range=[4, 11], skew=0.00 (approximately symmetric) |
| `B` | continuous | 8 | 0 | mean=6.5, sd=0.964, range=[5, 8], skew=-0.10 (approximately symmetric) |
| `difference_A_minus_B` | continuous | 8 | 0 | mean=1, sd=2.58, range=[-1.5, 6], skew=0.72 (moderately skewed) |
| `n_A_technical` | ordinal | 8 | 0 | 3 levels: 2(3), 3(3), 1(2); min_group_n=2 |
| `n_B_technical` | ordinal | 8 | 0 | 3 levels: 4(3), 2(3), 3(2); min_group_n=2 |

## Group structure
- Grouped by: `stratum`
- Number of groups: 2
- Group size: min=4, median=4, max=4
- **WARN**: at least one group has n<10 — use box/violin + stripplot rather than mean-only bar chart.

## Correlations (Pearson, sorted by |r|)
- `A` ↔ `difference_A_minus_B` : r = 0.928 (very strong)
- `B` ↔ `difference_A_minus_B` : r = -0.316 (moderate)
- `A` ↔ `B` : r = 0.061 (negligible)

## Warnings
- 列 'n_A_technical' 至少有一个类别 n<10 — 小样本必须展示原始数据点，不要只画均值柱状图。
- 列 'n_B_technical' 至少有一个类别 n<10 — 小样本必须展示原始数据点，不要只画均值柱状图。

## Chart suggestions (preliminary)
- 分类 vs 连续，小样本（每组 n<10）→ **箱线图/小提琴图 + stripplot 叠加原始点**；**避免**只画均值柱状图，会掩盖分布。
- ≥3 个连续变量 → 相关性热力图（['A', 'B', 'difference_A_minus_B']）或 pairplot 散点矩阵

> 这是基于数据形态的**初步建议**。最终图型选择必须结合**论证目标**（你想说什么）—— 详见 `references/chart_selection.md`。