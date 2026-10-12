# Data profile: results/test-predictions.csv

**Shape:** 40 rows × 7 cols

## Columns

| Column | Type | n | missing | summary |
|---|---|---|---|---|
| `source_row` | continuous | 40 | 0 | mean=102, sd=11.7, range=[82, 121], skew=-0.00 (approximately symmetric) |
| `batch` | ordinal | 40 | 0 | 2 levels: 3(30), 2(10); min_group_n=10 |
| `reference` | continuous | 40 | 0 | mean=16.9, sd=6.22, range=[5, 25.3], skew=-0.40 (approximately symmetric) |
| `sensor` | continuous | 40 | 0 | mean=18.4, sd=6.18, range=[6.61, 27], skew=-0.40 (approximately symmetric) |
| `raw` | continuous | 40 | 0 | mean=18.4, sd=6.18, range=[6.61, 27], skew=-0.40 (approximately symmetric) |
| `offset` | continuous | 40 | 0 | mean=16.8, sd=6.18, range=[4.98, 25.3], skew=-0.40 (approximately symmetric) |
| `affine` | continuous | 40 | 0 | mean=16.8, sd=6.19, range=[4.97, 25.3], skew=-0.40 (approximately symmetric) |

## Group structure
- Grouped by: `batch`
- Number of groups: 2
- Group size: min=10, median=20, max=30

## Correlations (Pearson, sorted by |r|)
- `sensor` ↔ `raw` : r = 1.000 (very strong)
- `sensor` ↔ `offset` : r = 1.000 (very strong)
- `raw` ↔ `offset` : r = 1.000 (very strong)
- `sensor` ↔ `affine` : r = 1.000 (very strong)
- `raw` ↔ `affine` : r = 1.000 (very strong)
- `offset` ↔ `affine` : r = 1.000 (very strong)
- `reference` ↔ `offset` : r = 0.999 (very strong)
- `reference` ↔ `sensor` : r = 0.999 (very strong)
- `reference` ↔ `raw` : r = 0.999 (very strong)
- `reference` ↔ `affine` : r = 0.999 (very strong)
- ... +5 more pairs

## Chart suggestions (preliminary)
- 分类 vs 连续，样本量充足 → 箱线图 / 小提琴图，或带误差棒的柱状图（误差棒说明 SD/SEM/CI）
- ≥3 个连续变量 → 相关性热力图（['source_row', 'reference', 'sensor', 'raw', 'offset']）或 pairplot 散点矩阵

> 这是基于数据形态的**初步建议**。最终图型选择必须结合**论证目标**（你想说什么）—— 详见 `references/chart_selection.md`。
