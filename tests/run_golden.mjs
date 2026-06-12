import { paiPan } from '../packages/hexagram-core/dist/index.mjs';
import fs from 'fs';
const snap = JSON.parse(fs.readFileSync('data/data-snapshot.json','utf8'));
const g1 = JSON.parse(fs.readFileSync('tests/golden/paipan_golden.json','utf8'));
const g2 = JSON.parse(fs.readFileSync('tests/golden/boundary_golden.json','utf8'));
const gold = {cases:[...g1.cases, ...g2.cases]};
const deep=(a,b,path='')=>{ if(a===b)return null;
 if(typeof a!=='object'||typeof b!=='object'||!a||!b) return `${path}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`;
 const keys=new Set([...Object.keys(a),...Object.keys(b)]);
 for(const k of keys){const r=deep(a[k],b[k],path+'.'+k); if(r)return r;} return null;};
let pass=0, fails=[];
for(const c of gold.cases){
  let got; try{ got=paiPan(c.input,snap);}catch(e){fails.push([c.id,'EXC '+e.message]);continue;}
  const diff=deep(c.expected,got);
  if(diff) fails.push([c.id+' '+c.desc, diff]); else pass++;
}
console.log(`黄金用例: ${pass}/${gold.cases.length} 通过`);
fails.slice(0,8).forEach(f=>console.log('FAIL',f[0],'->',f[1]));
process.exit(fails.length?1:0);
