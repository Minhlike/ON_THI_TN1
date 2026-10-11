"""Reviewer P0 regressions: fake clock, backup merge, atomicity, deadline."""
import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from study_app import server


class ExamRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = server.Store(Path(self.tmp.name)/'learner.sqlite3')
        self.now = datetime(2026,10,12,10,tzinfo=timezone.utc)
        owner = self
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None):
                return owner.now if tz else owner.now.replace(tzinfo=None)
        self.clock = patch.object(server,'datetime',Clock)
        self.clock.start()
    def tearDown(self):
        self.clock.stop()
        self.tmp.cleanup()
    def test_new_backup_updates_existing_exam_without_regression(self):
        exam = self.store.start_exam({'kind':'baseline'})
        p = {'id':exam['id'],'answers':{'TN1-Q032':'Câu trả lời A'},'revision':1}
        self.store.update_exam(p)
        old = self.store.export()
        target = server.Store(Path(self.tmp.name)/'restored.sqlite3')
        target.restore(old)
        self.now += timedelta(seconds=1)
        p['answers']['TN1-Q002']='Câu trả lời B';p['revision']=2
        final = self.store.update_exam(p,finish=True)
        target.restore(self.store.export())
        restored=target.state()['exams']
        self.assertEqual(len(restored),1)
        self.assertTrue(restored[0]['finished'])
        self.assertEqual(restored[0]['answers'],final['answers'])
        self.assertEqual(len(target.state()['attempts']),2)
        target.restore(old)
        self.assertEqual(target.state()['exams'][0]['answers'],final['answers'])
        self.assertTrue(target.state()['exams'][0]['finished'])
    def test_predeadline_received_save_survives_delayed_processing(self):
        exam=self.store.start_exam({'kind':'baseline'})
        received=datetime.fromisoformat(exam['deadline'])-timedelta(milliseconds=100)
        # Request already received; worker/DB is pending when the clock crosses zero.
        self.now=received+timedelta(seconds=1)
        p={'id':exam['id'],'revision':1,'answers':{'TN1-Q032':'Ý cuối gõ trước khi hết giờ'}}
        saved=self.store.update_exam(p,received=received)
        self.assertEqual(saved['answers'],p['answers'])
        final=self.store.update_exam({'id':exam['id']},finish=True)
        self.assertEqual(final['answers'],p['answers'])
        # Reload and repeated automatic/manual finish never submit twice.
        again=server.Store(self.store.path).update_exam({'id':exam['id']},finish=True)
        self.assertEqual(again,final)
        self.assertEqual(len(self.store.state()['attempts']),1)
        late={'id':exam['id'],'revision':2,'answers':{'TN1-Q032':'Sửa sau giờ'}}
        self.store.update_exam(late,received=self.now)
        self.assertEqual(self.store.state()['exams'][0]['answers'],p['answers'])
    def test_invalid_exam_backup_is_atomic(self):
        exam=self.store.start_exam({'kind':'baseline'})
        self.store.update_exam({'id':exam['id'],'revision':1,'answers':{'TN1-Q032':'Bài làm gốc'}})
        before=self.store.state()
        bad=copy.deepcopy(self.store.export())
        bad['tables']['drafts'].append({'key':'should-rollback','answer':'new','updated':self.now.isoformat()})
        payload=json.loads(bad['tables']['exams'][0]['payload'])
        payload['started']=(self.now-timedelta(days=1)).isoformat()
        bad['tables']['exams'][0]['payload']=json.dumps(payload)
        with self.assertRaises(ValueError): self.store.restore(bad)
        self.assertEqual(self.store.state(),before)
    def test_settings_newer_wins_and_legacy_does_not_regress(self):
        self.store.setting('schedule',{'1':'2026-10-12'})
        old=self.store.export()
        target=server.Store(Path(self.tmp.name)/'settings.sqlite3');target.restore(old)
        self.now+=timedelta(seconds=1)
        self.store.setting('schedule',{'1':'2027-01-01'})
        target.restore(self.store.export())
        self.assertEqual(target.state()['settings']['schedule'],{'1':'2027-01-01'})
        target.restore(old)
        self.assertEqual(target.state()['settings']['schedule'],{'1':'2027-01-01'})
        old['format']='TN1-progress-v1'
        for r in old['tables']['settings']: r.pop('updated')
        target.restore(old)
        self.assertEqual(target.state()['settings']['schedule'],{'1':'2027-01-01'})
    def test_revision_order_and_deadline_reject_late_changes(self):
        exam=self.store.start_exam({'kind':'baseline'})
        fresh={'id':exam['id'],'revision':2,'answers':{'TN1-Q032':'Bản mới nhất'}}
        self.store.update_exam(fresh)
        self.store.update_exam({'id':exam['id'],'revision':1,'answers':{'TN1-Q032':'Bản cũ'}})
        self.now=datetime.fromisoformat(exam['deadline'])
        self.store.update_exam({'id':exam['id'],'revision':3,'answers':{'TN1-Q032':'Sau hạn'}})
        self.assertEqual(self.store.state()['exams'][0]['answers'],fresh['answers'])
        self.store.update_exam({'id':exam['id']},finish=True)
        self.store.update_exam({'id':exam['id']},finish=True)
        self.assertEqual(len(self.store.state()['attempts']),1)
    def test_conflicting_submission_rolls_back_all_tables(self):
        exam=self.store.start_exam({'kind':'baseline'})
        self.store.update_exam({'id':exam['id'],'answers':{'TN1-Q032':'Nội dung gốc'}},finish=True)
        before=self.store.state();bad=self.store.export()
        bad['tables']['drafts'].append({'key':'rollback','answer':'pending','updated':self.now.isoformat()})
        e=json.loads(bad['tables']['exams'][0]['payload'])
        e['answers']['TN1-Q032']='Bản nộp xung đột';e['report']['TN1-Q032']['answer']='Bản nộp xung đột'
        bad['tables']['exams'][0]['payload']=json.dumps(e)
        with self.assertRaises(ValueError): self.store.restore(bad)
        self.assertEqual(before,self.store.state())


class ContentMilestoneTests(unittest.TestCase):
    def test_day_eight_and_selective_final_preserve_bank_scope(self):
        self.assertTrue(set(server.BANK['plan'][7]['card_ids'])<=server.CARDS.keys())
        self.assertEqual(len(server.BANK['plan'][50]['card_ids']),8)
        self.assertEqual(server.BANK['plan'][50]['minutes'],150)
        self.assertEqual(set().union(*(set(p['card_ids']) for p in server.BANK['plan'])),set(server.QUESTIONS))
    def test_children_have_explicit_status_rubric_and_steps(self):
        children={q['question_id']:q for q in server.BANK['subquestions']}
        coverage=server.BANK['child_coverage']
        self.assertEqual(len(coverage),43)
        self.assertEqual({c['id'] for c in coverage},set(children))
        for c in coverage:
            self.assertEqual(c['question'],children[c['id']]['original_text'])
            self.assertTrue(c['required_steps'])
            if c['status']=='REVIEWED':
                self.assertTrue(c['slide_pages']);self.assertTrue(c['rubric_ids'])
                self.assertTrue(set(c['rubric_ids'])<={r['id'] for r in server.CARDS[c['parent_id']]['rubric']})
            else: self.assertEqual(c['rubric_ids'],[])
        lookup={c['id']:c for c in coverage}
        self.assertIn('thiếu',lookup['TN1-Q048-d']['note'].lower())
        self.assertIn('mod 1',lookup['TN1-Q049-a']['note'])
    def test_new_cards_have_real_excerpts_and_separate_derivations(self):
        for n in range(12,17):
            c=server.CARDS[f'TN1-Q{n:03}']
            self.assertGreaterEqual(len(c['hints']),2);self.assertTrue(c['derivations'])
            for s in c['sources']:
                raw=(server.ROOT/f"knowledge/slide/pages/p{s['page']:04}.md").read_text('utf-8').split('-->',1)[-1].strip()
                self.assertEqual(s['excerpt'],raw)


if __name__=='__main__': unittest.main()
