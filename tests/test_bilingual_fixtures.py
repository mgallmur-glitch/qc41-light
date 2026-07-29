#!/usr/bin/env python3
"""Regression tests for English and Spanish blind fixtures."""
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/'scripts/validate_report.py'
RENDERER=ROOT/'scripts/render_report.py'
CASES=[
    ('en',ROOT/'tests/blind-english-call.txt',ROOT/'tests/blind-english-report.json',['Call-stage map','What to keep','Replay plan','Five-point checklist']),
    ('es',ROOT/'tests/blind-spanish-call.txt',ROOT/'tests/blind-spanish-report.json',['Mapa de etapas','Qué conservar','Plan de repetición','Checklist de cinco puntos']),
]

def quotes_in(obj):
    out=[]
    def walk(x):
        if isinstance(x,dict):
            if {'quote','speaker','timestamp'} <= set(x): out.append(x['quote'])
            for value in x.values(): walk(value)
        elif isinstance(x,list):
            for value in x: walk(value)
    walk(obj)
    return out

def main():
    for language,transcript_path,report_path,headings in CASES:
        check=subprocess.run([sys.executable,str(VALIDATOR),str(report_path)],capture_output=True,text=True)
        assert check.returncode==0, check.stderr
        data=json.loads(report_path.read_text())
        assert data['language']==language or data['language'].startswith(language+'-')
        transcript=transcript_path.read_text()
        quotes=quotes_in(data)
        missing=[quote for quote in quotes if quote not in transcript]
        assert not missing, f'{language}: missing exact quotes: {missing}'
        render=subprocess.run([sys.executable,str(RENDERER),str(report_path)],capture_output=True,text=True)
        assert render.returncode==0, render.stderr
        for heading in headings: assert heading in render.stdout, f'{language}: {heading}'
        print(f'PASS {language}: {len(quotes)} exact quotes, localized renderer, valid contract')

if __name__=='__main__': main()
