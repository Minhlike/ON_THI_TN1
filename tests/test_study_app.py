import hashlib
import json
import tempfile
import unittest
from datetime import date as RealDate, timedelta
from pathlib import Path
from unittest.mock import patch

from study_app import server
from study_app.math_engine import PRESETS, calculate, add, mul, inv


class ContentTests(unittest.TestCase):
    def test_original_questions_and_sources_preserved(self):
        originals=[json.loads(s) for s in (server.ROOT/'knowledge/questions/questions.jsonl').read_text('utf-8').splitlines()]
        expected={q['question_id']:q for q in originals}
        for q in server.BANK['questions']+server.BANK['subquestions']:
            self.assertEqual(q,expected[q['question_id']])
        self.assertEqual(len(server.BANK['questions']),80)
        manifest=json.loads((server.ROOT/'knowledge/manifest.json').read_text('utf-8'))
        for kind in ['slide','outline']:
            self.assertEqual(hashlib.sha256((server.ROOT/manifest['sources'][kind]['file']).read_bytes()).hexdigest(),server.BANK[kind+'_sha256'])
        for c in server.CARDS.values():
            self.assertEqual(c['question'],expected[c['id']]['original_text'])
            for s in c['sources']: self.assertTrue(s['visual_reviewed']); self.assertEqual(s['sha256'],server.BANK['slide_sha256'])
    def test_calendar_and_week_one_coverage(self):
        plan=server.BANK['plan'];self.assertEqual(len(plan),51)
        self.assertEqual(plan[-1]['date'],'2026-12-01')
        ids=set()
        for i,p in enumerate(plan):
            self.assertEqual(p['date'],str(RealDate(2026,10,12)+timedelta(days=i)))
            self.assertEqual(sum(t['minutes'] for t in p['tasks']),p['minutes'])
            ids.update(p['card_ids'])
            if i<7: self.assertTrue(set(p['card_ids'])<=server.CARDS.keys())
        self.assertEqual(ids,set(server.QUESTIONS))
    def test_initial_answers_hidden(self):
        public=server.public_bank()
        for c in public['cards']:
            self.assertNotIn('answer',c);self.assertNotIn('rubric',c);self.assertNotIn('sources',c)


class ArithmeticTests(unittest.TestCase):
    def test_source_vectors(self):
        expected={'rsa':'280','elgamal':'145,140','dh':'3','ecc':'(7,9)','ecdh':'(5,2)'}
        for kind,value in expected.items(): self.assertEqual(calculate(kind,PRESETS[kind]['values'])['expected'],value)
        self.assertEqual(calculate('ecdh',{'p':19,'a':2,'b':7,'gx':6,'gy':8,'ka':4,'kb':7})['expected'],'(11,7)')
    def test_group_law_and_infinity(self):
        G=(2,7);self.assertEqual(mul(13,G,1,11),None)
        self.assertEqual(add(G,(2,4),1,11),None)
        for a in range(14):
            for b in range(14): self.assertEqual(add(mul(a,G,1,11),mul(b,G,1,11),1,11),mul(a+b,G,1,11))
    def test_invalid_and_missing_parameters(self):
        for kind,values in [('ecc',{'p':1,'a':5,'b':4,'gx':10,'gy':3,'k':5}),('rsa',{'p':17,'q':17,'e':7,'m':32}),('ecc',{'p':11,'a':1,'b':6,'gx':1,'gy':1,'k':5})]:
            with self.assertRaises(ValueError): calculate(kind,values)
        with self.assertRaises(KeyError): calculate('elgamal',{'p':113,'g':3,'x':86,'m':18})
        with self.assertRaises(ValueError): inv(0,11)


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'progress.sqlite3';self.store=server.Store(self.path)
        self.current=RealDate(2026,10,12)
        owner=self
        class Day(RealDate):
            @classmethod
            def today(cls): return owner.current
        self.mock=patch.object(server,'date',Day);self.mock.start()
    def tearDown(self): self.mock.stop();self.temp.cleanup()
    def grade(self,hints=0,checks=None,confidence=2):
        submitted=self.store.submit({'card_id':'TN1-Q002','answer':'Định danh khai tên; xác thực kiểm tra tính chân thực; hỗ trợ truy cập.','day':5,'hints':hints})
        return self.store.grade({'attempt_id':submitted['attempt_id'],'checks':checks if checks is not None else ['r1','r2','r3'],'confidence':confidence})
    def test_interval_ladder_and_no_same_day_mastery(self):
        first=self.grade();self.assertFalse(first['mastered']);self.assertEqual(first['due'],'2026-10-13')
        second=self.grade();self.assertFalse(second['mastered']);self.assertEqual(second['due'],'2026-10-13')
        for delta,gap in [(1,3),(3,7),(7,14),(14,30)]:
            self.current+=timedelta(days=delta);result=self.grade()
            self.assertEqual(result['due'],str(self.current+timedelta(days=gap)));self.assertTrue(result['mastered'])
    def test_hint_wrong_or_uncertain_resets(self):
        for kwargs in [{'hints':1},{'checks':['r2','r3']},{'confidence':1}]:
            result=self.grade(**kwargs);self.assertFalse(result['independent']);self.assertFalse(result['mastered']);self.assertEqual(result['due'],'2026-10-13')
            self.assertEqual(self.store.state()['progress']['TN1-Q002']['stage'],-1)
    def test_reopening_preserves_history(self):
        self.grade(checks=['r1']);state=server.Store(self.path).state();self.assertEqual(len(state['attempts']),1);self.assertLess(state['progress']['TN1-Q002']['score'],85);self.assertTrue(state['attempts'][0]['error'])
    def test_grade_exactly_once(self):
        submitted=self.store.submit({'card_id':'TN1-Q002','answer':'Một câu trả lời','day':1,'hints':0});payload={'attempt_id':submitted['attempt_id'],'checks':['r1']};self.store.grade(payload)
        with self.assertRaises(ValueError): self.store.grade(payload)
        self.assertEqual(len(self.store.state()['attempts']),1)
    def test_backup_merge_and_atomic_rejection(self):
        self.grade();snapshot=self.store.export();self.store.restore(snapshot);self.assertEqual(len(self.store.state()['attempts']),1)
        other=server.Store(Path(self.temp.name)/'restored.sqlite3');other.restore(snapshot);self.assertEqual(len(other.state()['attempts']),1)
        snapshot['tables']['progress'][0]['card_id']='FAKE'
        with self.assertRaises(ValueError): self.store.restore(snapshot)
        self.assertEqual(len(self.store.state()['attempts']),1)
    def test_backup_updates_grade_and_rejects_html_id(self):
        submitted=self.store.submit({'card_id':'TN1-Q002','answer':'Định danh và xác thực.','day':1,'hints':0})
        other=server.Store(Path(self.temp.name)/'other.sqlite3');other.restore(self.store.export())
        self.store.grade({'attempt_id':submitted['attempt_id'],'checks':['r1']})
        other.restore(self.store.export());self.assertIsNotNone(other.state()['attempts'][0]['graded'])
        snapshot=self.store.export();snapshot['tables']['attempts'][0]['id']='\" onclick=\"alert(1)'
        with self.assertRaises(ValueError): other.restore(snapshot)
        snapshot=self.store.export();snapshot['tables']['settings']=[{'key':'schedule','value':json.dumps({'1':'\" autofocus onfocus=\"alert(1)'})}]
        with self.assertRaises(ValueError): other.restore(snapshot)
    def test_unreviewed_cannot_be_graded(self):
        with self.assertRaises(ValueError): self.store.submit({'card_id':'TN1-Q053','answer':'Bài mẫu chưa có đáp án kiểm chứng.','day':36,'hints':0})


if __name__=='__main__': unittest.main()
