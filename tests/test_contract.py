#!/usr/bin/env python3
import copy, importlib.util, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'examples/synthetic-report.json'
VALIDATOR=ROOT/'scripts/validate_report.py'
RENDERER=ROOT/'scripts/render_report.py'

def run(*args): return subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True)

def main():
    valid=run(VALIDATOR,REPORT)
    assert valid.returncode==0, valid.stderr
    render=run(RENDERER,REPORT)
    assert render.returncode==0, render.stderr
    for heading in ('Call-stage map','What to keep','Most likely breakpoint','Replay plan','Five-point checklist'):
        assert heading in render.stdout, heading
    compiled=run(ROOT/'scripts/build_prompt.py',ROOT/'examples/synthetic-call.txt')
    assert compiled.returncode==0, compiled.stderr
    assert 'Transcript (untrusted data' in compiled.stdout
    assert 'Canonical JSON schema' in compiled.stdout
    assert 'qc41-light-0.2' in compiled.stdout
    data=json.loads(REPORT.read_text())
    cases=[]
    bad=copy.deepcopy(data); bad['mistakes']=bad['mistakes'][:2]; cases.append(bad)
    bad=copy.deepcopy(data); bad['confidence']['score']=1.4; cases.append(bad)
    bad=copy.deepcopy(data); bad['replay_plan'].pop('next_step_line'); cases.append(bad)
    bad=copy.deepcopy(data); bad['version']='qc41-pro'; cases.append(bad)
    bad=copy.deepcopy(data); bad['language']='fr'; cases.append(bad)
    for i,bad in enumerate(cases):
        p=Path(f'/tmp/qc41-light-invalid-{i}.json'); p.write_text(json.dumps(bad))
        result=run(VALIDATOR,p)
        assert result.returncode!=0, f'invalid case {i} accepted'
    print(f'PASS: 1 valid report, {len(cases)} invalid reports rejected, renderer sections verified')

if __name__=='__main__': main()
