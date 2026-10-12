"""Read-only appraisal of supplied evidence. No fitting, simulation, or new experiment."""
from pathlib import Path
import csv,json,math,statistics,hashlib,re,difflib,datetime

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw=list(csv.DictReader(open('inputs/inputs/measurements.csv')))
pred=list(csv.DictReader(open('inputs/inputs/results/test-predictions.csv')))
robust=json.load(open('inputs/evidence/robustness-results.json'))
train=[r for r in raw if r['split']=='train'];test=[r for r in raw if r['split']=='test']
cut=statistics.median(float(r['reference']) for r in train)
assert cut==14.1 and len(train)==80 and len(test)==40
for p in pred:
 r=raw[int(p['source_row'])-2];assert r['split']=='test'
 for k in ('batch','reference','sensor'):assert float(r[k])==float(p[k])
assert len({p['source_row'] for p in pred})==40
sections={}
for idx,name in enumerate(('low','high')):
 subset=[r for r in pred if (float(r['reference'])<=cut)==(name=='low')]; record=robust['strata'][idx]
 metrics={}
 for model in ('raw','offset','affine'):
  errors=[float(p[model])-float(p['reference']) for p in subset]
  m={'n':len(errors),'rmse':math.sqrt(sum(e*e for e in errors)/len(errors)),'mae':sum(abs(e) for e in errors)/len(errors),'bias':sum(errors)/len(errors)}
  for k,v in m.items():assert abs(v-record[model][k])<1e-12
  metrics[model]=m
 sections[name]={'definition':f'reference {"<=" if name=="low" else ">"} train median {cut}','source_rows':[int(p['source_row']) for p in subset],'metrics':metrics}
assert len(sections['low']['source_rows'])==14 and len(sections['high']['source_rows'])==26
reviewed=Path('inputs/manuscript-before-review.md').read_text();final=Path('manuscript.md').read_text()
# Preserve science exactly: compare every unchanged body segment, table, caption and reference.
def extract(t,start,end=None):
 s=t.split(start,1)[1];return s.split(end,1)[0] if end else s
checks={}
for label,start,end in [('abstract','## 摘要','## 引言'),('introduction','## 引言','## 方法'),('methods','## 方法','## 结果'),('discussion','## 讨论与结论','## 透明性与参考资料')]:
 checks[label]=extract(reviewed,start,end)==extract(final,start,end);assert checks[label]
checks['table']=extract(reviewed,'表1','共享batch2')==extract(final,'表1','共享batch2');assert checks['table']
checks['figure_caption']=extract(reviewed,'![图1','## 讨论与结论')==extract(final,'![图1','## 讨论与结论');assert checks['figure_caption']
checks['references']=extract(reviewed,'1. NIST/SEMATECH.')==extract(final,'1. NIST/SEMATECH.');assert checks['references']
old_results=extract(reviewed,'## 结果','## 讨论与结论');new_results=extract(final,'## 结果','## 讨论与结论')
normalized=new_results.replace('低参考区间(n=14)','低参考区间').replace('高区间(n=26)','高区间')
expected=old_results.replace('实测成本允许增加旧代理草案的两次拟合估计，不改变用户硬预算。','')
checks['results_except_declared_changes']=normalized==expected;assert checks['results_except_declared_changes']
assert '已复核' not in final and '待复核' not in final and '已完成本次同宿主快速全稿专业复核' not in final and '不改变用户硬预算' not in final
# Link existing full review to its actual, unchanged original receipts and bound inputs.
prior=Path('/Users/luca/Documents/ChatGPT/学术skill/validation-v3.5.3-20261012/independent-followup')
start=json.load(open(prior/'review-start.json'));finish=json.load(open(prior/'review-finish.json'))
matched={}
for p in ('manuscript-before-review.md','quick-review.md','numeric-review.json'):
 matched[p]={'provided':sha(Path('inputs')/p),'original':sha(prior/p)};assert matched[p]['provided']==matched[p]['original']
for p in ('figure1.png','figure1-grayscale.png'):
 matched['assets/'+p]={'provided':sha(Path('inputs/assets')/p),'original':sha(prior/'assets'/p)};assert matched['assets/'+p]['provided']==matched['assets/'+p]['original']
Path('prior-review-provenance.json').write_text(json.dumps({'prior_step_id':start['id'],'prior_capability':start['capability'],'prior_source':{k:start['source'][k] for k in ('id','repository','commit')},'receipt_paths':[str(prior/'review-start.json'),str(prior/'review-finish.json')],'receipt_hashes':{'started':sha(prior/'review-start.json'),'finished':sha(prior/'review-finish.json')},'current_check_command':'professional_flow.py check on the original start/finish: eligible_for_handoff; actions.jsonl','provided_inputs_identity':matched,'reused_scope':'unchanged abstract, introduction, methods, table, figure/caption, references, conclusions and scientific limitations','not_reused_scope':'n=14/26 additions and manuscript administrative/disclosure edits; assessed by this task focused review'},ensure_ascii=False,indent=2))
Path('affected-content-audit.json').write_text(json.dumps({'executed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'read-only counting/reaggregation and exact content comparison; no refits','cut_from_train_only':cut,'train_n':len(train),'test_n':len(test),'actual_test_batches':sorted({r['batch'] for r in test}),'source_rows_alignment':'all40checked','strata':sections,'unchanged_scientific_segments':checks,'final_manuscript_sha256':sha('manuscript.md'),'supplied_robustness_numbers_reproduced':True},ensure_ascii=False,indent=2))
print(json.dumps({'cut':cut,'low_n':len(sections['low']['source_rows']),'high_n':len(sections['high']['source_rows']),'low_offset_rmse':sections['low']['metrics']['offset']['rmse'],'low_affine_rmse':sections['low']['metrics']['affine']['rmse'],'high_offset_rmse':sections['high']['metrics']['offset']['rmse'],'high_affine_rmse':sections['high']['metrics']['affine']['rmse'],'unchanged_segments':checks,'final_sha256':sha('manuscript.md')},ensure_ascii=False,indent=2))
