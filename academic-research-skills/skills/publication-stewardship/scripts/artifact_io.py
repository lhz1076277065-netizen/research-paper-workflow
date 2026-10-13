"""Bounded-memory content identities for local research artifacts."""
import hashlib
from pathlib import Path

def digest(path):
    p=Path(path)
    before=p.stat()
    h=hashlib.sha256()
    with p.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):h.update(chunk)
    after=p.stat()
    if (before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns):
        raise ValueError('Artifact changed while hashing: '+str(p))
    return h.hexdigest()

def output_text(path):
    # Large text attachments use the existing hash/observation action contract.
    # This representation choice is not a research budget or a stop condition.
    p=Path(path)
    if p.stat().st_size>8*1024*1024:return None
    try:return p.read_text(encoding='utf-8')
    except UnicodeDecodeError:return None
