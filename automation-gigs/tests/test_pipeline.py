import email, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from fulfill import parse_files_json, write_files, validate_all
from intake import platform_for, ingest, connect_db
from validate_n8n import validate

class PipelineTests(unittest.TestCase):
    def test_sender_spoof(self):
        for sender in ['Fiverr <fake@evil.test>','a@fiverr.com.evil.test','fiverr.com <a@evil.test>']:
            self.assertIsNone(platform_for(sender))
        self.assertEqual(platform_for('Order <a@notify.fiverr.com>'),'fiverr')
    def test_duplicate_notification_is_one_candidate(self):
        raw=b'From: orders@fiverr.com\nSubject: You have a new order\nMessage-ID: <unique@fiverr.com>\n\nBrief'
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);db=connect_db(root)
            folder=ingest(raw,root,db);self.assertIsNotNone(folder)
            self.assertIsNone(ingest(raw,root,db))
            status=json.loads((folder/'STATUS.json').read_text())
            self.assertFalse(status['funding_verified']);self.assertEqual(status['state'],'NEEDS_ORDER_REVIEW');db.close()
    def test_output_cannot_escape(self):
        with tempfile.TemporaryDirectory() as td:
            for name in ['../escape','/tmp/escape','x/../../escape','x\\..\\escape']:
                with self.assertRaises(ValueError):write_files({name:'bad'},td)
    def test_no_workflow_not_success(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertFalse(validate_all(td)[0])
    def test_missing_status_rejected(self):
        with self.assertRaises(ValueError):parse_files_json('{"files":{}}')
    def test_secret_in_readme_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'README.md').write_text('sk-ant-'+'a'*25)
            self.assertTrue(any('credential' in x for x in validate_all(p)[1]))
    def test_malformed_node_does_not_crash(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'a.json';p.write_text(json.dumps({'name':'x','nodes':[5],'connections':{}}))
            self.assertTrue(validate(p))
if __name__=='__main__':unittest.main()
