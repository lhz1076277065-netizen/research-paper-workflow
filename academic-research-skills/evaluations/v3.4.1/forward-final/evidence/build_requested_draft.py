from pathlib import Path
import json,csv,hashlib,re
r=Path(__file__).resolve().parent.parent
paragraph='在本组合成预约记录中，A组12条预约有2条未到场，B组12条预约有5条未到场。A组的未到场记录比例低于B组；由于未进行随机分组、显著性检验或因果识别，这一差异仅作描述，不能据此认定该方法降低了学生未到场率，也不能推断其适用于所有学校。'
checks=['核对计数、分母与分析单位，保持“预约记录”的表述，不能将记录条数直接写成独立学生人数。','在结果、摘要及结论中统一保留合成数据与描述性分析标签，删除未经检验的显著性、因果及跨学校推广表述。','投稿前由负责作者核验本段证据与措辞，并按目标期刊要求确认合成数据说明和AI辅助写作披露；当前段落不标为投稿就绪。']
text='## 结果段落\n\n'+paragraph+' <!-- [claim:C001] [evidence:E001] -->\n\n## 投稿前检查项\n\n'+'\n'.join('- '+v for v in checks)+'\n'
(r/'outputs/requested-draft.zh.md').write_text(text)
source={'schema_version':'1.0','sources':[{'authors':[],'confidentiality':'public','evidence_id':'E001','identifiers':{'doi':'','isbn':'','pmcid':'','pmid':'','url':''},'locator':'inputs/materials.json: groups、synthetic、not_performed；inputs/request.md','source_type':'other','title':'用户提供的合成预约汇总与未开展步骤','verification':{'source_opened':True,'status':'unverified','verified_by':'','verified_on':''},'year':None}]}
(r/'evidence/source_manifest.json').write_text(json.dumps(source,ensure_ascii=False,indent=2))
line=paragraph+' <!-- [claim:C001] [evidence:E001] -->'
clean=re.sub(r'\[claim:[^]]+\]|\[evidence:[^]]+\]','',line)
with (r/'evidence/claims.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['claim_id','section','claim_kind','claim_text_sha256','evidence_ids','verification_status','uncertainty','analysis_intent']);w.writerow(['C001','结果段落','result',hashlib.sha256(' '.join(clean.split()).encode()).hexdigest(),'E001','unverified','not_estimated','descriptive'])
(r/'evidence/writing-note.md').write_text('范围：仅一段结果与三项未来投稿检查，不创建全稿或投稿包。E001支持给定计数、合成属性及三个未开展步骤。当前Agent已打开材料并逐字核对计数和单位；具名人工核验仍unverified。未增加百分比、效应估计、检验、文献主张或推广依据。明确A/B无提醒/对照含义，不擅自命名干预。检查项是待执行建议，不假称已经投稿审批。\n来源要求的全稿作者/指南/注册/披露准入不属于局部改写；未指定期刊，当前规则未查验。软件来源：KDense scientific-writing缓存commit 154988403bb5a18e9d3c0ce4e6d5e2e4b184a298。来源缓存所列参考为Kassis等(2026), Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents, arXiv:2609.00065；未联网核验，仅记录归属，不用作本主题实证证据。\n')
s=json.loads((r/'evidence/writing-start.json').read_text())
a=[]
for p,quote,excerpt,applied in [('outputs/requested-draft.zh.md','Do not convert association into causation or non-significance into equivalence.','这一差异仅作描述','把原句中的未经检验显著性、因果、学生单位和普遍推广改为预约记录描述；按用户要求给三项检查。'),('evidence/source_manifest.json','Do not mark a source verified until an accountable human has opened it and confirmed','"status": "unverified"','为本次唯一来源保留人工未核验状态。'),('evidence/claims.csv','Store a hash of claim text in CSV rather than raw claim text.','unverified,not_estimated,descriptive','按真实模板字段及枚举记录本段主张哈希，未建立全稿准入文件。'),('evidence/writing-note.md','Keep conclusions within the observed design, population, and uncertainty.','明确A/B无提醒/对照含义，不擅自命名干预。','提纲和人工语义核对限定在已有A/B汇总，不添加干预标签或数据。')]:
 a.append({'source_file':'skills/scientific-writing/SKILL.md','source_excerpt':quote,'applied':applied,'output':str(r/p),'output_excerpt':excerpt})
(r/'evidence/writing-work.json').write_text(json.dumps({'step_id':s['id'],'scope':'requested_step','omitted_required_work':[],'functions_run':False,'actions':a},ensure_ascii=False,indent=2))
print('Saved requested draft and only its local claim provenance.')
