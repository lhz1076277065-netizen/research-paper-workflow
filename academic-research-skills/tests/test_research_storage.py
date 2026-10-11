"""Real local HTTP/ZIP/TAR operations at small quotas; never downloads research data."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/common/scripts'))
import research_storage as S
import phase_control as P

class HTTP(BaseHTTPRequestHandler):
    requests=[]
    def log_message(self,*args):pass
    def do_GET(self):
        self.requests.append((self.path,self.headers.get('Authorization')))
        if self.path.startswith('/redirect'):
            self.send_response(302);self.send_header('Location',f'http://localhost:{self.server.server_port}/data');self.end_headers();return
        if self.path.startswith('/denied'):
            self.send_response(401);self.end_headers();return
        self.send_response(200)
        body=b'<html>login</html>' if self.path=='/login' else b'x'*300 if self.path=='/stream' else b'evidence'
        if self.path!='/stream':self.send_header('Content-Length','99999' if self.path=='/huge' else '99' if self.path=='/short' else str(len(body)))
        self.send_header('Content-Type','text/html' if self.path=='/login' else 'application/octet-stream')
        self.end_headers();self.wfile.write(body);self.close_connection=True

class Storage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),HTTP)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup);HTTP.requests.clear()
        proxy=patch.dict(os.environ,{'no_proxy':'localhost,127.0.0.1'})
        proxy.start();self.addCleanup(proxy.stop)
        self.spec={'needs':[{'purpose':'test a scientific claim','subset':'required observations only','access':'free official subset'}],
                   'expected_download_bytes':1000,'expected_peak_project_bytes':1000}
    def plan(self,limit=4096):return S.plan(self.root,self.spec,limit,0)
    def url(self,path):return f'http://127.0.0.1:{self.server.server_port}{path}'
    def acquire(self,path='/data',name='raw/data',bound=100,**kw):return S.download(self.root,self.url(path),name,bound,0,**kw)
    def test_default_decimal_200gb_and_disk_reserve(self):
        result=S.plan(self.root,self.spec)
        self.assertEqual(result['limit_bytes'],200_000_000_000);self.assertEqual(result['reserve_bytes'],10_000_000_000)
    def test_upper_limit_cannot_be_raised(self):
        with self.assertRaises(S.StorageError):S.plan(self.root,self.spec,S.LIMIT+1,0)
    def test_nonintegral_limits_and_negative_estimates(self):
        for value in [True,1.5,-1]:
            with self.subTest(value=value),self.assertRaises(S.StorageError):S.plan(self.root,self.spec,value,0)
    def test_need_without_subset_or_purpose_rejected(self):
        self.spec['needs']=[{'access':'public'}]
        with self.assertRaises(S.StorageError):self.plan()
    def test_existing_inputs_count_in_peak(self):
        (self.root/'input').write_bytes(b'x'*1100)
        with self.assertRaises(S.StorageError):self.plan()
    def test_peak_and_future_transfer_estimates_must_fit(self):
        with self.assertRaises(S.StorageError):self.plan(500)
        self.assertFalse((self.root/S.NAME).exists())
    def test_free_space_checked_before_plan_and_download(self):
        with patch.object(S.shutil,'disk_usage',return_value=type('Disk',(),{'free':999})()):
            with self.assertRaises(S.StorageError):self.plan()
        self.plan()
        with patch.object(S.shutil,'disk_usage',return_value=type('Disk',(),{'free':50})()):
            with self.assertRaises(S.StorageError):self.acquire()
        self.assertEqual(HTTP.requests,[])
    def test_actual_download_identity_and_only_planned_need(self):
        self.plan();r=self.acquire();self.assertEqual((self.root/'raw/data').read_bytes(),b'evidence')
        self.assertEqual(r['bytes'],8);self.assertEqual(S.read(self.root)['downloaded_bytes'],8)
        with self.assertRaises(S.StorageError):S.download(self.root,self.url('/data'),'unplanned',100,1)
    def test_no_plan_refuses_before_contact(self):
        with self.assertRaises(S.StorageError):self.acquire()
        self.assertEqual(HTTP.requests,[])
    def test_header_bound_rejects_without_payload_written(self):
        self.plan()
        with self.assertRaises(S.StorageError):self.acquire('/huge')
        self.assertEqual(S.read(self.root)['downloaded_bytes'],0);self.assertFalse((self.root/'raw/data').exists())
    def test_no_length_stream_cannot_exceed_bound(self):
        self.plan()
        with self.assertRaises(S.StorageError):self.acquire('/stream',bound=32)
        state=S.read(self.root);self.assertEqual(state['downloaded_bytes'],32)
        partial=self.root/state['operations'][0]['partial'];self.assertEqual(partial.stat().st_size,32)
    def test_retry_and_deletion_never_reset_transfer(self):
        self.plan();self.acquire();(self.root/'raw/data').unlink()
        self.acquire(name='raw/retry');self.assertEqual(S.read(self.root)['downloaded_bytes'],16)
        S.plan(self.root,self.spec,4096,0);self.assertEqual(S.read(self.root)['downloaded_bytes'],16)
    def test_replan_preserves_original_ceiling(self):
        self.plan()
        with self.assertRaises(S.StorageError):S.plan(self.root,self.spec,8192,0)
    def test_cumulative_limit_rejects_new_contact_even_after_cleanup(self):
        self.plan();s=S.read(self.root);s['downloaded_bytes']=4090;S.save(self.root,s)
        with self.assertRaises(S.StorageError):self.acquire(bound=7)
        self.assertEqual(HTTP.requests,[])
    def test_truncation_counts_received_bytes_and_preserves_partial(self):
        self.plan()
        with self.assertRaises(S.StorageError):self.acquire('/short')
        self.assertEqual(S.read(self.root)['downloaded_bytes'],8)
    def test_login_and_denial_are_recoverable_without_false_data(self):
        self.plan()
        for path in ['/login','/denied']:
            with self.subTest(path=path),self.assertRaises(S.StorageError):self.acquire(path)
        self.acquire();self.assertEqual(S.read(self.root)['operations'][-1]['status'],'completed')
    def test_no_overwrite_or_path_escape(self):
        self.plan();self.acquire()
        for path in ['raw/data','../escape','/absolute']:
            with self.subTest(path=path),self.assertRaises(S.StorageError):self.acquire(name=path)
        self.assertEqual((self.root/'raw/data').read_bytes(),b'evidence')
    def test_cross_origin_redirect_does_not_leak_bearer(self):
        self.plan()
        with patch.dict(os.environ,{'STUDY_TEST_TOKEN':'secret-value'}):
            self.acquire('/redirect?token=query-secret',token_env='STUDY_TEST_TOKEN')
        self.assertEqual(HTTP.requests[0][1],'Bearer secret-value');self.assertIsNone(HTTP.requests[1][1])
        receipt=(self.root/S.NAME).read_text();self.assertNotIn('secret-value',receipt);self.assertNotIn('query-secret',receipt)
    def test_missing_secret_uses_no_network(self):
        self.plan()
        with patch.dict(os.environ,{},clear=True),self.assertRaises(S.StorageError):self.acquire(token_env='STUDY_TEST_TOKEN')
        self.assertEqual(HTTP.requests,[])
    def test_project_copy_cannot_reset_a_quota_identity(self):
        self.plan();s=S.read(self.root);s['root']='/elsewhere';S.save(self.root,s)
        with self.assertRaises(S.StorageError):self.acquire()
    def test_concurrent_operation_cannot_start(self):
        self.plan()
        with S.locked(self.root),self.assertRaises(S.StorageError):self.acquire()
    def test_paused_phase_prevents_contact(self):
        self.plan();phase=self.root/'phase.json';state=P.init('focused','test');state['status']='paused';P.save(phase,state)
        with self.assertRaises(S.StorageError):self.acquire(phase=str(phase))
        self.assertEqual(HTTP.requests,[])
    def test_phase_cannot_switch_to_a_new_data_quota(self):
        self.plan();phase=self.root/'phase.json';state=P.init('focused','test');P.save(phase,state)
        with self.assertRaises(S.StorageError):self.acquire(phase=str(phase))
        self.assertEqual(HTTP.requests,[])
    def test_linked_phase_guard_refuses_storage_growth_without_closing_goal(self):
        self.plan();state=P.init('focused','test');receipt=S.read(self.root)
        state['storage']={'root':str(self.root),'id':receipt['id']};deadline=state['project_deadline']
        result=P.enforce(state,storage=True,estimated_bytes=4097)
        self.assertFalse(result['allowed']);self.assertEqual(state['status'],'active');self.assertEqual(state['project_deadline'],deadline)
    def test_compact_resume_keeps_complete_state_and_latest_actions(self):
        state=P.init('full','test');state['artifacts']=[{'path':str(i)} for i in range(200)]
        full=P.resume(state);small=P.resume(state,compact=True)
        self.assertEqual(len(full['artifacts']),200);self.assertEqual(small['artifacts_count'],200)
        self.assertEqual([x['path'] for x in small['artifacts']],['197','198','199']);self.assertEqual(len(state['artifacts']),200)
    def archive(self,entries):
        path=self.root/'bundle.zip'
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            for name,body in entries:z.writestr(name,body)
        return path
    def test_bulk_archive_extracts_only_needed_member(self):
        self.archive([('needed.csv',b'a,b\n1,2\n'),('unneeded.csv',b'x'*1000)])
        self.plan();before=S.footprint(self.root);r=S.extract(self.root,'bundle.zip',['needed.csv'],'derived')
        self.assertEqual(r['bytes'],8);self.assertFalse((self.root/'derived/unneeded.csv').exists())
        self.assertEqual(S.footprint(self.root),before+8)
    def test_archive_expansion_is_bounded_before_writing(self):
        self.archive([('large',b'x'*8000)]);self.plan()
        with self.assertRaises(S.StorageError):S.extract(self.root,'bundle.zip',['large'],'derived')
        self.assertFalse((self.root/'derived').exists())
    def test_archive_traversal_and_symlink_rejected(self):
        path=self.archive([('../escape',b'x')])
        with zipfile.ZipFile(path,'a') as z:
            info=zipfile.ZipInfo('link');info.external_attr=(0o120777<<16);z.writestr(info,'elsewhere')
        self.plan()
        for member in ['../escape','link']:
            with self.subTest(member=member),self.assertRaises(S.StorageError):S.extract(self.root,'bundle.zip',[member],'out')
    def test_duplicate_archive_members_rejected(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore');self.archive([('same',b'a'),('same',b'b')])
        self.plan()
        with self.assertRaises(S.StorageError):S.extract(self.root,'bundle.zip',['same'],'out')
    def test_tar_regular_subset_no_links(self):
        with tarfile.open(self.root/'bundle.tar','w') as t:
            info=tarfile.TarInfo('needed');info.size=8;t.addfile(info,io.BytesIO(b'evidence'))
            link=tarfile.TarInfo('link');link.type=tarfile.SYMTYPE;link.linkname='/outside';t.addfile(link)
        self.spec['expected_peak_project_bytes']=20000;self.plan(30000)
        S.extract(self.root,'bundle.tar',['needed'],'out');self.assertEqual((self.root/'out/needed').read_bytes(),b'evidence')
        with self.assertRaises(S.StorageError):S.extract(self.root,'bundle.tar',['link'],'bad')
    def test_external_symlinks_cannot_hide_storage(self):
        self.plan();(self.root/'external').symlink_to('/tmp',target_is_directory=True)
        with self.assertRaises(S.StorageError):S.check(self.root)
    def test_check_accounts_for_derived_and_model_files(self):
        self.plan();(self.root/'model').write_bytes(b'x'*4000)
        self.assertFalse(S.check(self.root,extra=97)['allowed'])
    def test_unknown_historical_transfers_are_not_zero(self):
        (self.root/'old-input').write_bytes(b'old');self.plan()
        self.assertIsNone(S.check(self.root)['preplan_download_bytes'])
    def test_external_receipt_counts_once_and_retains_already_incurred_excess(self):
        self.plan();e=self.root/'nonsecret-receipt.json';e.write_text('{"bytes":5000,"request_id":"one"}')
        r=S.record_transfer(self.root,5000,e.name,0);self.assertFalse(r['allowed'])
        self.assertEqual(S.read(self.root)['downloaded_bytes'],5000)
        with self.assertRaises(S.StorageError):S.record_transfer(self.root,5000,e.name,0)
    def test_estimated_transfer_must_be_replanned_before_larger_acquisition(self):
        self.spec['expected_download_bytes']=10;self.plan()
        with self.assertRaises(S.StorageError):self.acquire(bound=100)
        self.assertEqual(HTTP.requests,[])
        self.spec['expected_download_bytes']=100;self.plan();self.acquire()
    def test_files_named_like_metadata_do_not_hide_capacity(self):
        self.plan();(self.root/(S.NAME+'-dataset')).write_bytes(b'x'*5000)
        self.assertFalse(S.check(self.root)['allowed']);self.assertEqual(S.footprint(self.root),5000)

if __name__=='__main__':unittest.main()
