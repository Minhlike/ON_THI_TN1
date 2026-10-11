"""Isolated Playwright fixture. Fake time/gate are files, never product HTTP APIs."""
import argparse
import json
import time
from datetime import datetime as RealDatetime
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Condition
from study_app import server


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-dir',type=Path,required=True)
    parser.add_argument('--port',type=int,required=True)
    args=parser.parse_args()
    args.data_dir.mkdir(parents=True,exist_ok=True)
    clock=args.data_dir/'clock.json';gate=args.data_dir/'gate.json'
    class Clock(RealDatetime):
        @classmethod
        def now(cls,tz=None):
            if not clock.exists(): return RealDatetime.now(tz)
            value=RealDatetime.fromisoformat(json.loads(clock.read_text('utf-8'))['now'])
            return value.astimezone(tz) if tz else value.replace(tzinfo=None)
    class GatedStore(server.Store):
        def update_exam(self,p,finish=False,received=None):
            if not finish and gate.exists():
                (args.data_dir/'received.json').write_text(json.dumps({'received':received.isoformat(),'id':p['id']}),'utf-8')
                limit=time.monotonic()+15
                while gate.exists() and time.monotonic()<limit: time.sleep(.01)
                if gate.exists(): raise ValueError('Test gate timed out')
            return super().update_exam(p,finish,received)
    server.datetime=Clock
    http=ThreadingHTTPServer(('127.0.0.1',args.port),server.Handler)
    http.store=GatedStore(args.data_dir/'study.sqlite3')
    http.mutations=Condition();http.issued=0;http.serving=0
    print('QA fixture ready',flush=True)
    try: http.serve_forever()
    except KeyboardInterrupt: pass
    finally: http.server_close()


if __name__=='__main__': main()
