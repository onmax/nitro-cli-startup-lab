import subprocess,pathlib,json,os
r=pathlib.Path(__file__).resolve().parents[1];env={**os.environ,'CI':'1','NO_COLOR':'1'}
commands=[['--help'],['-h'],['--version'],['-v'],['build','--help'],['dev','--help'],['serve','--help'],['start','--help'],['preview','--help'],['deploy','--help'],['task','--help'],['task','list','--help'],['task','run','--help'],['create','--help'],['docs','--help'],['nonexistent'],['task','nonexistent'],['task','run']]
results=[]
for args in commands:
 outputs=[]
 for variant in ['baseline','recommended']:
  p=subprocess.run(['node',str(r/'variants'/variant/'dist/cli/index.mjs'),*args],capture_output=True,text=True,env=env,timeout=20)
  outputs.append((p.returncode,p.stdout,p.stderr))
 assert outputs[0]==outputs[1],(args,outputs)
 results.append({'args':args,'identical':True,'exitCode':outputs[0][0]})
(r/'results/cli-equivalence.json').write_text(json.dumps(results,indent=2));print(len(results),'identical CLI outputs and exit codes')
