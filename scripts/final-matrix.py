import pathlib,json,shutil
r=pathlib.Path(__file__).resolve().parents[1];cases=[]
for cmd in [['--help'],['--version'],['build','--help'],['dev','--help'],['serve','--help'],['task','--help'],['task','run','--help'],['deploy','--help']]:
 for v in ['baseline','recommended']:
  cases.append({'name':v+' / '+' '.join(cmd),'argv':['node',str(r/'variants'/v/'dist/cli/index.mjs'),*cmd],'contains':['3.0.260903' if cmd==['--version'] else 'USAGE']})
for size in [1,100]:
 for v in ['baseline','recommended']:
  d=r/'variants'/v;f=d/('fixture' if size==1 else 'fixture-100')
  if not f.exists():shutil.copytree(d/'fixture',f,ignore=shutil.ignore_patterns('.output','.nitro'))
  (f/'nitro.config.mjs').write_text('export default { serverDir: "server", preset: "standard", builder: "rolldown", compatibilityDate: "2026-10-26" };\n')
  if size==100:
   for i in range(1,100):(f/f'server/routes/route-{i}.ts').write_text(f'export default () => "route-{i}";\n')
  cases.append({'name':v+' / build '+str(size)+' routes','cwd':str(f),'argv':['node',str(d/'dist/cli/index.mjs'),'build'],'contains':['Server built'],'verify':['node',str(r/'scripts/verify-output.mjs'),str(size)]})
(r/'final-matrix.json').write_text(json.dumps(cases,indent=2))
