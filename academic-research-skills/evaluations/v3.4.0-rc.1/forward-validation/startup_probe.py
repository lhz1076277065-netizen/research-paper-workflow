from pathlib import Path
Path(__file__).with_name('COMPUTATION_STARTED.marker').write_text('software probe started\n')
print('software probe started')
