from pathlib import Path
Path(__file__).with_name('CONTROL_STARTED.marker').write_text('software positive control started\n')
print('software positive control started')
