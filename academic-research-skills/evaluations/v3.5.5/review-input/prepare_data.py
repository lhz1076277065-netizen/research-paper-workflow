from pathlib import Path
import csv,json,hashlib
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
spec=json.loads((P/'dataset-spec-v1.json').read_text());cols=spec['datasets'][0]['files'][0]['columns']
raw=P/'raw/wine.data'
assert raw.stat().st_size<1000000 and not raw.is_symlink()
with raw.open(newline='') as f:rows=list(csv.reader(f,strict=True))
assert len(rows)==178 and all(len(r)==14 for r in rows)
a=np.array(rows,dtype=float);assert np.isfinite(a).all()
d=pd.DataFrame(a,columns=cols);d['class']=d['class'].astype(int)
assert d['class'].value_counts().sort_index().to_dict()=={1:59,2:71,3:48}
(P/'derived').mkdir(exist_ok=True)
d.to_csv(P/'derived/wine.csv',index=False,float_format='%.12g')
report={'rows':len(d),'columns':list(d.columns),'class_counts':{str(k):int(v) for k,v in d['class'].value_counts().sort_index().items()},'missing_cells':int(d.isna().sum().sum()),'nonfinite_cells':int((~np.isfinite(a)).sum()),'duplicate_complete_rows':int(d.duplicated().sum()),'all_raw_fields_parsed':True,'exclusions':0,'imputation':False,'train_test_split':'not applicable: descriptive complete fixed dataset','sampling_unit':'one wine record; replication/batch/independence not documented','units':'not supplied in official dictionary; use recorded units','class_names':'numeric codes only, no cultivar name mapping supplied','sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'software':{'numpy':np.__version__,'pandas':pd.__version__},'summaries':d[['alcohol','color_intensity']].describe().to_dict()}
(P/'preparation-report-v1.json').write_text(json.dumps(report,indent=2,allow_nan=False))
(P/'data-dictionary-v1.md').write_text('# Data dictionary and validity\nOriginal headerless CSV: first column cultivar class 1/2/3, next 13 feature columns in official wine.names order. Alcohol = first feature; color_intensity = tenth feature. All fields parsed; 178 rows, 14 numeric columns; class counts 59/71/48; no missing/nonfinite cells, no exact duplicate complete rows. No records excluded, no imputation, no transformation, no train/test split. One observation is a recorded wine; sampling frame, instrument, batch, repeated measurements and collection dates are not documented. Unit fields are blank, so no percentage or absorbance unit is invented. No direct identifiers. Derived CSV adds verified names only and preserves numerical values. Whole-file profile limit is 1000 rows, above actual 178; raw rows sorted in class order. Preplanned Q1/Q2 remain descriptive.\n')
print(json.dumps(report,indent=2))
