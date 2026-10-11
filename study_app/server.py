"""Loopback-only study application, stdlib HTTP and SQLite storage."""
import argparse
import hashlib
import json
import mimetypes
import os
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote

from study_app.math_engine import PRESETS, calculate, normalized_answer

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'study_app'
BANK = json.loads((APP / 'content/bank.json').read_text('utf-8'))
CARDS = {c['id']: c for c in BANK['cards']}
QUESTIONS = {q['question_id']: q for q in BANK['questions']}
for preset in PRESETS.values():
    preset['page'] = QUESTIONS[preset['question_id']]['pdf_page']
INTERVALS = [1,3,7,14,30]


def today(): return date.today().isoformat()
def stamp(): return datetime.now(timezone.utc).isoformat()


def validate_setting(key, value):
    if key not in ['schedule','tasks'] or not isinstance(value,dict): raise ValueError('Thiết lập không hợp lệ.')
    if key=='schedule':
        for day,when in value.items():
            if not 1<=int(day)<=51: raise ValueError('Ngày học không hợp lệ.')
            date.fromisoformat(when)
    elif any(not isinstance(v,bool) or not re.fullmatch(r'\d{1,2}-\d',k) for k,v in value.items()): raise ValueError('Nhiệm vụ không hợp lệ.')


def validate_practice(kind, payload):
    if kind not in ['math','diagram','code'] or not isinstance(payload,dict): raise ValueError('Bài luyện không hợp lệ.')
    if kind=='math' and payload.get('kind') not in PRESETS: raise ValueError('Thuật toán không hợp lệ.')
    if kind=='code' and payload.get('question_id') not in ['TN1-Q028','TN1-Q029']: raise ValueError('Bài mã không hợp lệ.')


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS attempts(id TEXT PRIMARY KEY,card_id TEXT NOT NULL,answer TEXT NOT NULL,day INTEGER NOT NULL,hints INTEGER NOT NULL,created TEXT NOT NULL,graded TEXT,score INTEGER,checks TEXT,confidence INTEGER,error TEXT,passed INTEGER);
                CREATE TABLE IF NOT EXISTS progress(card_id TEXT PRIMARY KEY,stage INTEGER NOT NULL,due TEXT NOT NULL,streak INTEGER NOT NULL,score INTEGER NOT NULL,mastered INTEGER NOT NULL,updated TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS drafts(key TEXT PRIMARY KEY,answer TEXT NOT NULL,updated TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS practices(id TEXT PRIMARY KEY,kind TEXT NOT NULL,payload TEXT NOT NULL,created TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS exams(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
            ''')
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path, timeout=10)
        db.row_factory=sqlite3.Row
        try:
            db.execute('PRAGMA journal_mode=WAL')
            with db:
                yield db
        finally:
            db.close()
    def state(self):
        with self.connect() as db:
            exams=[json.loads(r['payload']) for r in db.execute('SELECT * FROM exams')]
            # A backup contains learner state, never authoritative model answers or HTML.
            for exam in exams:
                if exam.get('report'):
                    for cid,report in exam['report'].items():
                        report['card']=CARDS.get(cid)
            return { 'progress':{r['card_id']:dict(r) for r in db.execute('SELECT * FROM progress')},
                'attempts':[dict(r) for r in db.execute('SELECT * FROM attempts ORDER BY created DESC LIMIT 500')],
                'drafts':{r['key']:r['answer'] for r in db.execute('SELECT * FROM drafts')},
                'practices':[dict(r) for r in db.execute('SELECT * FROM practices ORDER BY created DESC LIMIT 500')],
                'settings':{r['key']:json.loads(r['value']) for r in db.execute('SELECT * FROM settings')},
                'exams':exams}
    def submit(self, p):
        cid=p.get('card_id'); answer=str(p.get('answer','')).strip()
        if cid not in CARDS: raise ValueError('Câu này chưa có đáp án kiểm chứng.')
        if len(answer)<3 or len(answer)>50000: raise ValueError('Hãy viết câu trả lời trước khi mở đáp án (3–50000 ký tự).')
        day=int(p.get('day',1)); hints=int(p.get('hints',0))
        if not 1<=day<=51 or not 0<=hints<=len(CARDS[cid]['hints']): raise ValueError('Dữ liệu phiên học không hợp lệ.')
        aid=uuid.uuid4().hex
        with self.connect() as db:
            db.execute('INSERT INTO attempts(id,card_id,answer,day,hints,created) VALUES(?,?,?,?,?,?)',(aid,cid,answer,day,hints,stamp()))
        return {'attempt_id':aid,'card':CARDS[cid]}
    def grade(self, p):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM attempts WHERE id=?',(p.get('attempt_id'),)).fetchone()
            if row is None or row['graded']: raise ValueError('Bài làm không tồn tại hoặc đã chấm. Hãy tạo lần ôn mới.')
            rubric=CARDS[row['card_id']]['rubric']; valid={r['id'] for r in rubric}; checks=p.get('checks',[])
            if not isinstance(checks,list) or not set(checks)<=valid: raise ValueError('Rubric không hợp lệ.')
            checks=set(checks); score=round(100*len(checks)/len(rubric)); conf=int(p.get('confidence',2))
            if conf not in [1,2,3]: raise ValueError('Mức tự tin không hợp lệ.')
            passed=score>=85 and all(r['id'] in checks for r in rubric if r['essential']) and not p.get('critical_error',False)
            old=db.execute('SELECT * FROM progress WHERE card_id=?',(row['card_id'],)).fetchone()
            independent=passed and not row['hints'] and conf>=2
            mature = not old or old['due'] <= today()
            stage=(min(old['stage']+1,4) if old else 0) if independent and mature else old['stage'] if independent and old else -1
            # A hinted or incorrect recall resets the ladder; it never establishes mastery.
            gap=INTERVALS[stage] if independent else 1
            streak=(old['streak']+1 if old else 1) if independent and mature else old['streak'] if independent and old else 0
            due=(date.today()+timedelta(days=gap)).isoformat() if mature or not independent else old['due']
            mastered=int(independent and streak>=2)
            error=str(p.get('error','')).strip()[:5000]
            if not passed and not error: error='Cần bổ sung: '+'; '.join(r['label'] for r in rubric if r['id'] not in checks)
            db.execute('UPDATE attempts SET graded=?,score=?,checks=?,confidence=?,error=?,passed=? WHERE id=?',(stamp(),score,json.dumps(sorted(checks)),conf,error,int(passed),row['id']))
            db.execute('INSERT INTO progress VALUES(?,?,?,?,?,?,?) ON CONFLICT(card_id) DO UPDATE SET stage=excluded.stage,due=excluded.due,streak=excluded.streak,score=excluded.score,mastered=excluded.mastered,updated=excluded.updated',(row['card_id'],stage,due,streak,score,mastered,stamp()))
        return {'score':score,'passed':passed,'independent':bool(independent),'mastered':bool(mastered),'due':due,'missing':[r['label'] for r in rubric if r['id'] not in checks]}
    def practice(self, kind, payload):
        validate_practice(kind,payload)
        with self.connect() as db:
            db.execute('INSERT INTO practices VALUES(?,?,?,?)',(uuid.uuid4().hex,kind,json.dumps(payload,ensure_ascii=False),stamp()))
    def export(self):
        with self.connect() as db:
            return {'format':'TN1-progress-v1','exported':stamp(),'tables':{table:[dict(r) for r in db.execute('SELECT * FROM '+table)] for table in ['attempts','progress','drafts','practices','settings','exams']}}
    def restore(self, data):
        if data.get('format')!='TN1-progress-v1': raise ValueError('Định dạng bản sao lưu không phù hợp.')
        tables=data.get('tables',{})
        # Validate everything before entering the transaction; merge, never delete existing history.
        schema={'attempts':['id','card_id','answer','day','hints','created','graded','score','checks','confidence','error','passed'], 'progress':['card_id','stage','due','streak','score','mastered','updated'],'drafts':['key','answer','updated'],'practices':['id','kind','payload','created'],'settings':['key','value'],'exams':['id','payload']}
        for table,cols in schema.items():
            rows=tables.get(table,[])
            if not isinstance(rows,list) or len(rows)>20000: raise ValueError('Bản sao lưu vượt giới hạn.')
            for r in rows:
                if not isinstance(r,dict) or set(r)!=set(cols): raise ValueError('Cấu trúc bản sao lưu không hợp lệ.')
                if 'id' in r and not re.fullmatch(r'[a-f0-9]{32}',str(r['id'])): raise ValueError('Mã bản ghi không hợp lệ.')
                if 'card_id' in r and r['card_id'] not in CARDS: raise ValueError('Bản sao lưu có mã câu chưa được hỗ trợ.')
                if table=='progress':
                    date.fromisoformat(r['due']); datetime.fromisoformat(r['updated'])
                    if not isinstance(r['stage'],int) or not -1<=r['stage']<=4 or not isinstance(r['score'],int) or not 0<=r['score']<=100 or not isinstance(r['streak'],int) or not 0<=r['streak']<=10000 or r['mastered'] not in [0,1]: raise ValueError('Lịch ôn trong bản sao lưu không hợp lệ.')
                if table=='attempts':
                    if not isinstance(r['answer'],str) or len(r['answer'])>50000 or not isinstance(r['day'],int) or not 1<=r['day']<=51: raise ValueError('Bài làm trong bản sao lưu không hợp lệ.')
                    if r['score'] is not None and (not isinstance(r['score'],int) or not 0<=r['score']<=100): raise ValueError('Điểm không hợp lệ.')
                    datetime.fromisoformat(r['created'])
                    if r['graded'] is not None: datetime.fromisoformat(r['graded'])
                for c in ['payload','value','checks']:
                    if c in r and r[c] is not None: json.loads(r[c])
                if table=='settings': validate_setting(r['key'],json.loads(r['value']))
                if table=='practices': validate_practice(r['kind'],json.loads(r['payload']))
                if table=='exams':
                    exam=json.loads(r['payload'])
                    if exam.get('id')!=r['id'] or exam.get('kind') not in EXAMS: raise ValueError('Phiên thi không hợp lệ.')
                    datetime.fromisoformat(exam['started']);datetime.fromisoformat(exam['deadline'])
                    allowed=set(EXAMS[exam['kind']])
                    if not isinstance(exam.get('answers'),dict) or not set(exam['answers'])<=allowed or any(not isinstance(v,str) or len(v)>50000 for v in exam['answers'].values()): raise ValueError('Bài thi trong bản sao lưu không hợp lệ.')
                    report=exam.get('report')
                    if report is not None and (not isinstance(report,dict) or not set(report)<=allowed or any(not isinstance(v,dict) or not isinstance(v.get('answer'),str) for v in report.values())): raise ValueError('Báo cáo thi không hợp lệ.')
        with self.connect() as db:
            for table,cols in schema.items():
                for r in tables.get(table,[]):
                    if table=='attempts':
                        old=db.execute('SELECT * FROM attempts WHERE id=?',(r['id'],)).fetchone()
                        if old:
                            if any(old[k]!=r[k] for k in ['card_id','answer','day','hints','created']): raise ValueError('Trùng mã bài làm nhưng khác dữ liệu gốc; hủy khôi phục.')
                            if r['graded'] and (not old['graded'] or r['graded']>old['graded']):
                                fields=['graded','score','checks','confidence','error','passed']
                                db.execute('UPDATE attempts SET '+','.join(k+'=?' for k in fields)+' WHERE id=?',[r[k] for k in fields]+[r['id']])
                            continue
                    if table in ['progress','drafts']:
                        key=cols[0]; old=db.execute(f'SELECT updated FROM {table} WHERE {key}=?',(r[key],)).fetchone()
                        if old and old['updated']>=r['updated']: continue
                        if old: db.execute(f'DELETE FROM {table} WHERE {key}=?',(r[key],))
                    db.execute(f'INSERT OR IGNORE INTO {table} ({",".join(cols)}) VALUES ({",".join("?" for _ in cols)})',[r[c] for c in cols])


EXAMS={'baseline':['TN1-Q032','TN1-Q002','TN1-Q069','TN1-Q001','TN1-Q009'], 'week1':['TN1-Q033','TN1-Q003','TN1-Q010','TN1-Q073','TN1-Q035'], 'sample1':[f'TN1-Q{i:03}' for i in range(53,58)],'sample2':[f'TN1-Q{i:03}' for i in range(58,63)],'sample3':[f'TN1-Q{i:03}' for i in range(63,68)]}


def public_bank():
    cards=[{k:v for k,v in c.items() if k not in ['answer','rubric','sources','note','derivations']} for c in BANK['cards']]
    return {'cards':cards,'questions':BANK['questions'],'subquestions':BANK['subquestions'],'plan':BANK['plan'],'start':BANK['start'],'end':BANK['end'],'reviewed':len(cards),'total':len(QUESTIONS),'sha':BANK['slide_sha256']}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt,*args): pass
    def reply(self,status,data):
        raw=json.dumps(data,ensure_ascii=False).encode('utf-8')
        self.send_response(status); self.common_headers(); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def common_headers(self):
        self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Referrer-Policy','same-origin')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; script-src 'self'; connect-src 'self'; font-src 'self'; object-src 'none'; frame-ancestors 'none'")
    def allowed(self, mutation=False):
        host=self.headers.get('Host','')
        allowed={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
        if host not in allowed: return False
        origin=self.headers.get('Origin')
        return not mutation or origin is None or origin in {'http://'+s for s in allowed}
    def do_GET(self):
        if not self.allowed(): return self.reply(403,{'error':'Chỉ chấp nhận truy cập localhost.'})
        path=unquote(urlsplit(self.path).path)
        if path=='/api/bootstrap': return self.reply(200,{'bank':public_bank(),'state':self.server.store.state(),'today':today(),'math':PRESETS,'exam_sets':EXAMS})
        if path=='/api/export': return self.reply(200,self.server.store.export())
        if path.startswith('/api/'): return self.reply(404,{'error':'Không có đường dẫn này.'})
        if path=='/sources/slide.pdf': file=ROOT/'CSATTT_SLIDE_FULL.pdf'
        elif path=='/sources/outline.pdf':
            manifest=json.loads((ROOT/'knowledge/manifest.json').read_text('utf-8')); file=ROOT/manifest['sources']['outline']['file']
        else:
            file=(APP/'static'/('index.html' if path=='/' else path.lstrip('/'))).resolve()
            if not file.is_relative_to((APP/'static').resolve()): return self.reply(403,{'error':'Đường dẫn không hợp lệ.'})
        if not file.is_file(): return self.reply(404,{'error':'Không tìm thấy tệp.'})
        raw=file.read_bytes(); self.send_response(200); self.common_headers(); self.send_header('Content-Type',mimetypes.guess_type(file.name)[0] or 'application/octet-stream'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_POST(self):
        if not self.allowed(True): return self.reply(403,{'error':'Nguồn yêu cầu không hợp lệ.'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if self.headers.get('Content-Type','').split(';')[0]!='application/json' or not 0<size<=8_000_000: raise ValueError('Cần dữ liệu JSON trong giới hạn 8 MB.')
            p=json.loads(self.rfile.read(size)); path=urlsplit(self.path).path; store=self.server.store
            if not isinstance(p,dict): raise ValueError('Cần một đối tượng JSON.')
            if path=='/api/submit': result=store.submit(p)
            elif path=='/api/resume':
                with store.connect() as db: row=db.execute('SELECT * FROM attempts WHERE id=?',(p.get('attempt_id'),)).fetchone()
                if row is None or row['graded']: raise ValueError('Bài làm không còn chờ chấm.')
                result={'attempt_id':row['id'],'card':CARDS[row['card_id']]}
            elif path=='/api/grade': result=store.grade(p)
            elif path=='/api/draft':
                key=str(p['key']); answer=str(p.get('answer',''))
                if len(key)>200 or len(answer)>100000: raise ValueError('Bản nháp quá dài.')
                with store.connect() as db: db.execute('INSERT INTO drafts VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET answer=excluded.answer,updated=excluded.updated',(key,answer,stamp()))
                result={'saved':True}
            elif path=='/api/settings':
                value=p.get('value');validate_setting(p.get('key'),value)
                with store.connect() as db: db.execute('INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(p['key'],json.dumps(value),))
                result={'saved':True}
            elif path=='/api/math':
                kind=p['kind']; result=calculate(kind,p['values']); mode=p.get('mode','worked')
                if mode not in ['worked','faded','solo']: raise ValueError('Chế độ không hợp lệ.')
                answer=str(p.get('answer','')); correct=normalized_answer(answer)==normalized_answer(result['expected'])
                result['correct']=correct if answer.strip() else None
                if mode=='solo' and not answer.strip(): raise ValueError('Chế độ tự giải cần câu trả lời trước khi xem kết quả.')
                if answer.strip(): store.practice('math',{'kind':kind,'mode':mode,'question_id':PRESETS[kind]['question_id'],'values':p['values'],'answer':answer,'correct':correct,'expected':result['expected']})
            elif path=='/api/practice':
                if p.get('kind') not in ['diagram','code']: raise ValueError('Loại thực hành không hợp lệ.')
                # This API records self-assessed mechanisms separately from machine checked math.
                store.practice(p['kind'],p.get('payload',{})); result={'saved':True}
            elif path=='/api/exam/start':
                kind=p.get('kind','baseline')
                if kind not in EXAMS: raise ValueError('Đề thi không hợp lệ.')
                minutes=45 if kind in ['baseline','week1'] else 180; eid=uuid.uuid4().hex
                result={'id':eid,'kind':kind,'started':stamp(),'deadline':(datetime.now(timezone.utc)+timedelta(minutes=minutes)).isoformat(),'answers':{},'finished':False,'report':None}
                with store.connect() as db: db.execute('INSERT INTO exams VALUES(?,?)',(eid,json.dumps(result,ensure_ascii=False)))
            elif path in ['/api/exam/save','/api/exam/finish']:
                with store.connect() as db:
                    db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT payload FROM exams WHERE id=?',(p.get('id'),)).fetchone()
                    if not row: raise ValueError('Không tìm thấy phiên thi.')
                    result=json.loads(row['payload'])
                    if result['finished']: raise ValueError('Phiên thi đã kết thúc.')
                    answers=p.get('answers',{})
                    if not isinstance(answers,dict) or any(k not in EXAMS[result['kind']] or not isinstance(v,str) or len(v)>50000 for k,v in answers.items()): raise ValueError('Bài thi không hợp lệ.')
                    expired=datetime.now(timezone.utc)>datetime.fromisoformat(result['deadline'])
                    if not expired: result['answers']=answers
                    if path.endswith('finish') or expired:
                        result['finished']=True; result['finished_at']=stamp(); result['report']={cid:{'card':CARDS.get(cid),'answer':result['answers'].get(cid,''),'status':'SELF_ASSESS' if cid in CARDS else 'AWAITING_REVIEW'} for cid in EXAMS[result['kind']]}
                        for cid, report in result['report'].items():
                            if cid in CARDS and len(report['answer'].strip())>=3:
                                aid=uuid.uuid4().hex
                                db.execute('INSERT INTO attempts(id,card_id,answer,day,hints,created) VALUES(?,?,?,?,?,?)',(aid,cid,report['answer'],1 if result['kind']=='baseline' else 7,0,stamp()))
                                report['attempt_id']=aid
                    db.execute('UPDATE exams SET payload=? WHERE id=?',(json.dumps(result,ensure_ascii=False),result['id']))
            elif path=='/api/restore': store.restore(p); result={'restored':True}
            else: return self.reply(404,{'error':'Không có đường dẫn này.'})
            self.reply(200,result)
        except (ValueError,KeyError,TypeError,OverflowError,json.JSONDecodeError) as exc:
            self.reply(400,{'error':str(exc)})


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765); parser.add_argument('--data-dir',type=Path); args=parser.parse_args()
    data=args.data_dir or Path(os.environ.get('LOCALAPPDATA',str(ROOT/'.local')))/'ON_THI_TN1'
    manifest=json.loads((ROOT/'knowledge/manifest.json').read_text('utf-8'))
    for key,expected in [('slide',BANK['slide_sha256']),('outline',BANK['outline_sha256'])]:
        source=ROOT/manifest['sources'][key]['file']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=expected: raise SystemExit('Nguồn đã thay đổi; cần kiểm chứng lại ngân hàng câu hỏi: '+key)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler); server.store=Store(data/'study.sqlite3')
    print(f'TN1: http://127.0.0.1:{args.port} | Progress: {server.store.path}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__=='__main__': main()
