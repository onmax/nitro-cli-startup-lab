"""Run from an extracted lab with a clean, installed Nitro checkout at source/."""
import pathlib,subprocess,shutil,json
r=pathlib.Path(__file__).resolve().parents[1];s=r/'source';sha='5b5bd219397eb50c854eb1240ec844ac5d401b41'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=s,text=True).strip()==sha
assert not subprocess.check_output(['git','diff','--name-only'],cwd=s,text=True).strip(), 'Use a clean dedicated source checkout'
(r/'results').mkdir(exist_ok=True)
for name in ['baseline','recommended']:
 if name=='recommended':subprocess.run(['git','apply',str(r/'patches/recommended.patch')],cwd=s,check=True)
 subprocess.run(['pnpm','build'],cwd=s,check=True)
 d=r/'variants'/name;d.mkdir(parents=True,exist_ok=True)
 for x in ['dist','lib']:shutil.copytree(s/x,d/x,dirs_exist_ok=True)
 shutil.copy(s/'package.json',d/'package.json')
 (d/'node_modules').symlink_to(s/'node_modules',target_is_directory=True)
 f=d/'fixture';(f/'server/routes').mkdir(parents=True,exist_ok=True)
 (f/'package.json').write_text('{"type":"module","private":true}')
 (f/'server/routes/index.ts').write_text('export default () => "LAB_OK";\n')
 (f/'nitro.config.mjs').write_text('export default {serverDir:"server",preset:"standard",builder:"rolldown",compatibilityDate:"2026-10-26"};\n')
subprocess.run(['python3',str(r/'scripts/final-matrix.py')],check=True)
subprocess.run(['python3',str(r/'scripts/bench.py'),str(r/'final-matrix.json'),'15'],check=True)
subprocess.run(['python3',str(r/'scripts/verify-cli.py')],check=True)
