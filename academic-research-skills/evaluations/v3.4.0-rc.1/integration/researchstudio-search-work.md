## ResearchStudio：检索与筛选

固定入口读取后调用真实 search_papers 函数：Crossref、2010–2026、最多3条、关键词 reproducible computational research。CLI 文档的 --json 不被解析器支持，第一次退出2；适配器只序列化函数返回值，未修改上游。

实际返回3条。Computational workflows for research students 是工具使用教育材料，保留为背景候选；Reproducible Science In Intelligent Transportation Research 是特定领域危机讨论，排除作为控制工具有效性证据；CDE: Automatically Package and Reproduce Computational Experiments 是复现封装相关候选，保留为概念对照。只依据返回元数据筛选，没有读全文、没有证明最近邻或创新。前两条年份和发布日期是null，保持未知，不冒称时间过滤已核实。全部3条及DOI见 search-results.json。

