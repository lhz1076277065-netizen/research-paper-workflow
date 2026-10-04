## Nature：源文问题与术语一致

source_format=pasted-text/Markdown。问题：autoresearch 的固定5分钟是否代表整个研究会在5分钟结束？

结论：不是。program.md 的 Experimentation 节限定每次训练5分钟，排除启动与编译；The experiment loop 节指示继续循环直至人类中断。因此它不能直接继承为总研究预算。这里将有限试验记账思想适配到软件试验，整体循环受阶段预算约束。原文没有说明如何保障 Codex 宿主预算，不能据此推断保障。

原文依据：已校验的 autoresearch program.md 的 Experimentation、Logging results、The experiment loop 三节。没有纸本文本或页码，不造 page/block IDs。

术语：fixed time budget=固定时长预算；wall clock training time=训练墙钟时间；baseline=基线；val_bpb=上游训练验证指标，本测试不测；keep/discard=保留/弃用方案，不是科学接受/拒稿。

