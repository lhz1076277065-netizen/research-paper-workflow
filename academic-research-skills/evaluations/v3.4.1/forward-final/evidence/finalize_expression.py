from pathlib import Path
import json,csv,hashlib,re
r=Path(__file__).resolve().parent.parent
original=(r/'outputs/requested-draft.zh.md').read_text()
old=original.split('\n\n')[1]
paragraph='本组合成数据中，A组12条预约有2条未到场，B组12条预约有5条未到场，A组的未到场记录比例低于B组。上述计数呈现了两组预约记录的描述性差异。由于未开展随机分组、显著性检验或因果识别，现有材料不足以判断该方法的因果效果、统计显著性及在其他学校的适用性。'
line=paragraph+' <!-- [claim:C001] [evidence:E001] -->'
final=original.replace(old,line)
(r/'outputs/result-and-three-checks.zh.md').write_text(final)
clean=re.sub(r'\[claim:[^]]+\]|\[evidence:[^]]+\]','',line)
with (r/'evidence/final-claims.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['claim_id','section','claim_kind','claim_text_sha256','evidence_ids','verification_status','uncertainty','analysis_intent']);w.writerow(['C001','结果段落','result',hashlib.sha256(' '.join(clean.split()).encode()).hexdigest(),'E001','unverified','not_estimated','descriptive'])
(r/'evidence/expression-note.md').write_text('最终表达先报给定计数，再说明描述性差异与证据边界。删去重复的“不能据此认定/也不能推断”和“仅”，保留所有会改变解释的未实施步骤。没有将A/B重命名为干预/对照组，没有添加百分比或显著性。逐字复核：A为12/2，B为12/5；合成数据标签、预约单位和三项检查未变。来源的宣传性语言不能压过专业路由中保留实质不确定性的边界，因此没有编造优势、价值或学校推广支持。最终段落的证据标记使用HTML注释，正文显示保持清洁，映射及人工待核验状态保存在final-claims.csv。\n')
s=json.loads((r/'evidence/expression-start.json').read_text())
a=[]
for p,quote,excerpt,applied in [('outputs/result-and-three-checks.zh.md','只提出证据能牢固支撑的主张。','上述计数呈现了两组预约记录的描述性差异。','围绕现有计数写出描述性记忆点，不增加显著性、因果或推广论断。'),('evidence/expression-note.md','只有在无法回避且确实影响核心结论时,才进行必要说明。','保留所有会改变解释的未实施步骤。','保留无随机化/检验/识别的实质限制；将语言建议置于证据边界内。'),('evidence/final-claims.csv','说服力来自主张与证据高度一致，而不是比较项目数量最多。','unverified,not_estimated,descriptive','重新核对措辞及计数后记录本段新哈希，人工核验仍待完成。')]:
 a.append({'source_file':'skills/anti-defensive-writing/SKILL.md','source_excerpt':quote,'applied':applied,'output':str(r/p),'output_excerpt':excerpt})
(r/'evidence/expression-work.json').write_text(json.dumps({'step_id':s['id'],'scope':'requested_step','omitted_required_work':[],'functions_run':False,'actions':a},ensure_ascii=False,indent=2))
print(final)
