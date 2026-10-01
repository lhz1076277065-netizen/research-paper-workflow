"""Fail closed when source material needed for manuscript synchronization is absent."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
def audit(manifest):
    missing=[name for name in ['source','frozen_results','figures','pdf'] if not manifest.get(name)]
    return {'missing_artifacts':missing,'caption_status':'not_checked','abstract_numbers_status':'not_checked','pdf_source_sync_status':'not_checked','scientific_completion':'reported_in_synthetic_request_only','authors':'pending_human_confirmation','declarations':'pending_human_confirmation','delivery_status':'not_submission_ready','reason':'No manuscript, figures, frozen result table or PDF was supplied in B/cases.json or B top-level files.'}

if __name__=='__main__':
    folder=ROOT/'author-pending';folder.mkdir(exist_ok=True)
    manifest={'source':None,'frozen_results':None,'figures':None,'pdf':None}
    report=audit(manifest)
    assert set(report['missing_artifacts'])=={'source','frozen_results','figures','pdf'}
    assert report['delivery_status']=='not_submission_ready'
    (folder/'sync_input.json').write_text(json.dumps(manifest,indent=2))
    (folder/'sync_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
