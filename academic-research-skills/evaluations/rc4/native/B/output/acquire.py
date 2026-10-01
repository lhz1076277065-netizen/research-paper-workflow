from pathlib import Path
import csv, hashlib, io, json, time, urllib.request, zipfile

ROOT = Path(__file__).resolve().parent
log = []
def get(url, path):
    start = time.monotonic()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Research acceptance pilot'}), timeout=35) as response:
            body = response.read()
            item = {'url':url, 'status':response.status, 'content_type':response.headers.get('Content-Type'), 'etag':response.headers.get('ETag')}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        item.update(path=str(path), bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), seconds=time.monotonic()-start)
        log.append(item)
        return body
    except Exception as e:
        log.append({'url':url, 'error':str(e), 'seconds':time.monotonic()-start})
        return None

def extract_members(body, dest, names):
    if body is None: return
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        for member in archive.namelist():
            if Path(member).name in names:
                # Only exact selected basenames; no archive paths become output paths.
                dest.mkdir(parents=True, exist_ok=True)
                (dest / Path(member).name).write_bytes(archive.read(member))

if __name__ == '__main__':
    bike=ROOT/'direction-no-data'
    body=get('https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip', bike/'raw.zip')
    extract_members(body,bike,{'hour.csv','day.csv','Readme.txt'})
    get('https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset',bike/'source.html')
    human=ROOT/'human-collection'
    for v in ['28_0','29_0']:
        body=get(f'https://www.onetcenter.org/dl_files/database/db_{v}_text.zip',human/f'raw_{v}.zip')
        extract_members(body,human/v,{'Task Statements.txt','Occupation Data.txt'})
        get(f'https://www.onetcenter.org/dictionary/{v.replace("_",".")}/text/task_statements.html',human/f'dictionary_{v}.html')
    get('https://www.onetcenter.org/license_db.html',human/'license.html')
    get('https://www.onetcenter.org/db_releases.html',human/'releases.html')
    (ROOT/'download_log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
    print(json.dumps(log,ensure_ascii=False,indent=2))
