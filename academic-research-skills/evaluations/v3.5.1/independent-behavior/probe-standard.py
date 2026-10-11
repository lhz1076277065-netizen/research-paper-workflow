import csv, json, sys
from decimal import Decimal
import numpy as np
from PIL import Image
with open('measurements.csv', newline='') as f:
    reader=csv.DictReader(f); rows=list(reader)
    assert reader.fieldnames == ['case_id','scale','truth','method_a','method_b']
assert len(rows)==24
r=rows[0]
a=abs(Decimal(r['method_a'])-Decimal(r['truth']))
b=abs(Decimal(r['method_b'])-Decimal(r['truth']))
assert a==Decimal('0.35') and b==Decimal('0.22')
print(json.dumps({'python':sys.version,'numpy':np.__version__,'rows':len(rows),'first_abs_error_A':str(a),'first_abs_error_B':str(b),'Pillow_available':True},ensure_ascii=False))
