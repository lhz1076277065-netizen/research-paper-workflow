#!/usr/bin/env python3
"""Run the inherited v3 tests. Help does not execute or write test results."""
import argparse,runpy,sys
from pathlib import Path
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.parse_args()
    target=Path(__file__).with_name('_v300_run_all_original.py')
    sys.argv=[str(target)]
    runpy.run_path(str(target),run_name='__main__')
