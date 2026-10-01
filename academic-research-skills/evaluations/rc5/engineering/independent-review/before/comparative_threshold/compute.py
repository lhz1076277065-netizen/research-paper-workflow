import json,sys
from decimal import Decimal
from pathlib import Path
x=json.loads(Path(sys.argv[1]).read_text())
print(json.dumps({"value":str(sum(map(Decimal,x))/len(x))}))
