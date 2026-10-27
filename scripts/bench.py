import json, os, pathlib, random, subprocess, time, statistics, sys, shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
ENV = {**os.environ, 'CI':'1', 'NO_COLOR':'1', 'NITRO_COMPATIBILITY_DATE':'2026-10-26'}
ENV.pop('NODE_OPTIONS', None)
ENV.pop('NODE_COMPILE_CACHE', None)

def run(case, iteration):
    if case.get('reset'):
        shutil.rmtree(case['reset'], ignore_errors=True)
    env = {**ENV, **case.get('env', {})}
    start = time.perf_counter_ns()
    p = subprocess.run(case['argv'], cwd=case.get('cwd', str(ROOT)), env=env, capture_output=True, text=True, timeout=90)
    wall = (time.perf_counter_ns()-start)/1e6
    output = p.stdout + p.stderr
    valid = p.returncode == case.get('exit', 0) and all(s in output for s in case.get('contains', []))
    if case.get('verify') and valid:
        q = subprocess.run(case['verify'], cwd=case['cwd'], env=env, capture_output=True, text=True, timeout=20)
        valid = q.returncode == 0 and 'LAB_OK' in q.stdout
        output += q.stdout + q.stderr
    result = {'name':case['name'], 'iteration':iteration, 'ms':wall, 'code':p.returncode, 'valid':valid, 'load':os.getloadavg(), 'output':output}
    if not valid:
        print(json.dumps(result), flush=True)
        raise RuntimeError('Failed work validation')
    return result

def main():
    manifest = pathlib.Path(sys.argv[1])
    cases = json.loads(manifest.read_text())
    n = int(sys.argv[2]) if len(sys.argv)>2 else 11
    rows=[]
    for case in cases:
        run(case, -1)
    for i in range(n):
        order = cases[:] if i % 2 == 0 else list(reversed(cases))
        for case in order:
            r=run(case, i); rows.append(r)
            print(f"{r['name']} {i}: {r['ms']:.1f} ms", flush=True)
            (OUT / f'{manifest.stem}-raw.json').write_text(json.dumps(rows, indent=2))
    summary=[]
    for case in cases:
        values=[r['ms'] for r in rows if r['name']==case['name']]
        summary.append({'name':case['name'], 'n':len(values), 'median':statistics.median(values), 'min':min(values), 'max':max(values), 'errors':0})
    (OUT / f'{manifest.stem}-summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

if __name__=='__main__': main()
