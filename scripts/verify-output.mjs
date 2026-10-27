import { readFile } from 'node:fs/promises';
const buildInfo=JSON.parse(await readFile('./.output/nitro.json','utf8'));
if (!buildInfo.versions?.nitro) throw new Error('Missing build metadata');
const {default:app}=await import(new URL(process.cwd()+'/.output/server/index.mjs','file:'));
const response=await app.fetch(new Request('http://localhost/'));
if (response.status!==200 || await response.text()!=='LAB_OK') throw new Error('Wrong built response');
for (let i=1;i<Number(process.argv[2]||1);i++) {
  const res=await app.fetch(new Request(`http://localhost/route-${i}`));
  if (res.status!==200 || await res.text()!==`route-${i}`) throw new Error(`Wrong route ${i}`);
}
console.log('LAB_OK');
