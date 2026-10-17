from pathlib import Path
import json,re,difflib
P=Path(__file__).resolve().parent
before=(P/'manuscript-v2.md').read_text();after=(P/'manuscript-final.md').read_text();checks=json.loads((P/'expression-meaning-checks.json').read_text())['meaning_checks']
def tokens(text):
 text=re.sub(r'(?m)^\s{0,3}#{1,6}\s+','',text)
 for pattern in (r'\*\*(.+?)\*\*',r'__(.+?)__',r'`([^`]+)`',r'(?<!\*)\*([^*\n]+)\*(?!\*)'):text=re.sub(pattern,r'\1',text,flags=re.S)
 return re.findall(r'\w+|[^\w\s]',text)
old=tokens(before);new=tokens(after);covered={}
for key,words in [('before',old),('after',new)]:
 mask=[False]*len(words)
 for check in checks:
  quote=tokens(check[key]);size=len(quote)
  for i,w in enumerate(words):
   if w==quote[0] and words[i:i+size]==quote:mask[i:i+size]=[True]*size
 covered[key]=mask
uncovered=[]
for tag,a,b,c,d in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes():
 if tag!='equal' and (not all(covered['before'][a:b]) or not all(covered['after'][c:d])):
  uncovered.append({'tag':tag,'before':' '.join(old[a:b]),'after':' '.join(new[c:d]),'before_context':' '.join(old[max(0,a-15):b+15]),'after_context':' '.join(new[max(0,c-15):d+15]),'before_uncovered':[w for j,w in enumerate(old[a:b],a) if not covered['before'][j]],'after_uncovered':[w for j,w in enumerate(new[c:d],c) if not covered['after'][j]]})
(P/'meaning-coverage-diagnosis.json').write_text(json.dumps(uncovered,indent=2));print(json.dumps(uncovered,indent=2))
