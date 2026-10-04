import sys
from pathlib import Path
a=sys.argv[1]
with Path(__file__).with_name('repair-attempts.log').open('a') as f:f.write(a+'\n')
print('SOFTWARE_FIXTURE dependency unavailable through '+a)
raise SystemExit(3 if a=='local-cache' else 4)
