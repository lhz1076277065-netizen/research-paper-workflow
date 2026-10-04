import csv,json,re,shutil,hashlib
from pathlib import Path
out=Path(__file__).parent
rows=list(csv.DictReader((out/'launch-results.csv').open()))
with (out/'results.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['trial','state','method','started','wall_seconds','status','description'],delimiter='\t');w.writeheader()
 for r in rows:w.writerow({k:r[k] for k in ['trial','state','method','started','wall_seconds']}|{'status':'baseline' if r['method']=='direct' else ('keep' if int(r['started'])==int(r['expected_controlled_start']) else 'discard'),'description':'local software fixture; fixed evaluation'})
(out/'tracker.md').write_text('# 执行追踪\n\n| 块 | 实际证据 | 结果 |\n|---|---|---|\n| 过期/活动对照 | launch-results.csv、launch-fixture/* | 24行，拒绝0/6与接受6/6成立 |\n| 核心控制边界 | regression-v340-green.log、forward-validation/actions.jsonl | 详见行为报告，不推断科研质量 |\n| 来源专业处理 | prepared、receipts、professional-work.md | 逐来源边界见集成报告 |\n\n没有GPU训练、额外种子、领域课题或论文投稿。\n')
(out/'before-after.md').write_text('''# 证据保持表达记录\n\n## 原稿\n我们先创建了测试场景，然后做了多项核验。遗憾的是只能在本机测试，可能还有很多问题。过期时直接启动6/6，控制启动0/6，活动时都是6/6。这个工具可能改善研究，但无法证明长任务不会出错。\n\n## 整理稿\n阶段控制在本机配对软件场景中拒绝了6次过期启动，并接受了6次活动启动。与直接启动对照相比，它把预算出口落实为命令执行条件。结论限于经控制工具启动的命令；本次测试不证明长期Agent行为或科研质量，也不能消除平台容量及压缩故障。\n\n保留：6/6、0/6、活动对照、本机范围、长期/科研/平台限制。删除执行流水账与泛化的自我削弱句。没有隐藏失败或新增结果。\n''')
(out/'final-report.md').write_text('''# 阶段控制与专业来源软件验收\n\n阶段控制在本机软件场景中把预算出口落实为命令执行条件。14个固定来源的指定入口被准备、实施或按能力边界验证，下载与成功标签不作为专业工作完成证据。\n\n## 方法\n预先固定两条主张、12个场景和评价标准。6个过期、6个活动状态分别比较direct与phase_control；每条调用只尝试写本地标记。结果不靠人工状态标签推断。数据为24行，trial为配对标识，不作独立科研样本。\n\n## 结果与范围\n过期状态direct启动6/6、phase_control启动0/6；活动状态两者启动均6/6。文件标记与拒绝记录对应。CSV核心剖析、图及结果绑定检查器把实际输入接到了交付；文献检索实际返回3条元数据，筛选后保留2条候选，没有完成综述。\n\n主图见launch-figure.png；数值见launch-results.csv和figure-values.json。图型为零基线计数条图，无p值、置信区间或性能加速主张。\n\n## 限制\n只约束经过guard/run的动作，不能拦截所有宿主API、Agent采样或平台目标。当前Agent对专业协议的适配不等于原生所有工具链或独立跨模型评审。H100训练、外部模型审查及全图生成PPT未完成；已有图像组装只是函数验收。短软件fixture不证明多小时科研质量提升，也不保证消除平台容量及远程压缩失败。\n\n## 交付判断\n可交付为本机软件维护与集成报告。现有软件证据足够，停止增加课题、模型训练或原创性搜索；本报告不是科研论文。\n''')
# Copy the real OpenDesign template structure/runtime, replacing all demo content.
uid='open-design-deck';r=json.loads((out/'prepared'/f'{uid}.json').read_text());src=Path(r['root'])/'design-templates/html-ppt';deck=out/'deck';deck.mkdir(exist_ok=True)
shutil.copytree(src/'assets',deck/'assets',dirs_exist_ok=True);shutil.copy2(src/'templates/full-decks/tech-sharing/style.css',deck/'style.css');shutil.copy2(src/'LICENSE',deck/'LICENSE')
html=(src/'templates/full-decks/tech-sharing/index.html').read_text();html=html.replace('../../../assets/','assets/').replace('Rust 异步运行时内部机制 · Tech Sharing','学术 Skill 软件验收')
slides='''<section class="slide" data-title="Bounded work"><p class="kicker">academic skills / local validation</p><h1 class="h1">阶段出口<br>进入真实执行</h1><p class="lede mt-m">维护、局部写作与完整研究按范围进入；完成后保留可恢复收据。</p><div class="deck-footer"><span>3.4.0-rc.1 · 软件维护验收</span></div><aside class="notes">这次交付是 Skill 软件更新，目标是减少没有阶段出口的持续工作。原测试会话没有被续接或修改。范围是本机软件行为验证，不能把版本更新直接说成长期科研质量已经改善。</aside></section>
<section class="slide" data-title="Evidence"><p class="kicker">actual launch markers</p><h2 class="h2">过期拒绝 0/6<br>活动接受 6/6</h2><div class="grid g2 mt-l"><div class="card card-accent"><h4>过期状态</h4><p>直接启动 6/6<br>阶段控制 0/6</p></div><div class="card card-accent"><h4>活动状态</h4><p>直接启动 6/6<br>阶段控制 6/6</p></div></div><p class="dim mt-m">同一台Mac的确定性软件场景，无推断统计。</p><aside class="notes">评价标准在测试前固定。24行对应12个配对场景。通过真实文件标记确认是否执行，活动对照检查没有把所有启动一律禁用。结果不代表任意宿主动作都被拦截，也不是科研效果实验。</aside></section>
<section class="slide" data-title="Sources"><p class="kicker">14 pinned sources</p><h2 class="h2">按真实能力接入</h2><div class="stack mt-l"><div class="agenda-row"><span class="num">01</span><span class="t">源码身份、入口、依赖与专业输入输出</span></div><div class="agenda-row"><span class="num">02</span><span class="t">检索 → 剖析 → 图 → 复核 → 报告</span></div><div class="agenda-row"><span class="num">03</span><span class="t">区分协议实施、函数运行和参考使用</span></div></div><aside class="notes">来源下载不代表专业任务完成。每项收据绑定具体输入、输出和动作；报告保留原生阻碍。整篇研究按需选择实现，无需调用全部14库。未启动专用GPU训练、完整工作台或外部图像生成。</aside></section>
<section class="slide" data-title="Limits"><p class="kicker">delivery decision</p><h2 class="h2">可回退更新<br>保留验证边界</h2><div class="grid g2 mt-l"><div class="card"><h4>交付</h4><p>维护源码、独立skills、安装包、行为与集成证据</p></div><div class="card"><h4>限制</h4><p>经控制工具的本地动作；长期Agent、多宿主和科研质量尚未证明</p></div></div><aside class="notes">本次不发布GitHub，也不恢复旧科研题。更新前保留安装备份，恢复不重置阶段预算。平台容量与压缩故障属于外部系统问题，skill可以收束与恢复但不能保证消除它们。</aside></section>'''
a=html.index('<div class="deck">')+len('<div class="deck">');b=html.index('</div>\n<script',a) if '</div>\n<script' in html[a:] else html.rindex('</div>')
html=html[:a]+'\n'+slides+'\n'+html[b:];(deck/'index.html').write_text(html)
# Reject any copied in-tree paths or leftover Rust demo.
assert '../../../assets/' not in html and 'Future::poll' not in html
for rel in re.findall(r'(?:src|href)="([^"]+)"',html):
 if not rel.startswith(('http','#')):assert (deck/rel).is_file(),rel
(out/'deck-plan.md').write_text('受众：Skill维护用户；决策：核验交付及边界。4页依次解释阶段出口、实际计数、来源接入、交付边界。保留模板布局和runtime。备注隐藏在aside.notes。没有Rust示例/新增科研结论。\n')
print('artifact writing and local deck dependencies verified')
