/** Verify the actual browser widget against its analytic teaching examples. */
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(path.join(process.env.REVIEW_NODE_MODULES,'_widget_qa.cjs'));
const {chromium}=require('playwright');
const qa=path.join(root,'tmp','production-qa');fs.mkdirSync(qa,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
const records=[];
function near(a,b,label,tol=1e-12){if(Math.abs(a-b)>tol)throw Error(`${label}: ${a} != ${b}`)}
try{
 for(const lang of ['ko','en'])for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:1000}}),errors=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
  await page.goto(pathToFileURL(path.join(root,'dist',lang==='ko'?'':'en','index.html')).href);
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.fonts].map(f=>f.load()))});
  const widget=page.locator('[data-phase-widget]');await widget.locator('[data-rows] tr').first().waitFor();
  const snapshot=()=>page.evaluate(()=>{
   const host=document.querySelector('[data-phase-widget]'),gamma=+host.querySelector('[data-gamma]').value,beta=+host.querySelector('[data-beta]').value,graph=host.querySelector('[data-graph]').value,stage=+host.querySelector('[data-stage]').value;
   const model=window.QuantumPhaseModel.compute(graph,gamma,beta);return{gamma,beta,graph,stage,model,rows:host.querySelectorAll('tbody tr').length,summary:host.querySelector('[data-summary]').textContent,width:document.documentElement.scrollWidth,rangeSteps:[...host.querySelectorAll('input')].map(i=>i.step)};
  });
  let s=await snapshot();near(s.model.stages[2].expectedScore,1,'edge default');if(s.rows!==4||s.rangeSteps.some(x=>x!=='any'))throw Error('row/continuous-angle control mismatch');
  await widget.screenshot({path:path.join(qa,`${lang}-widget-${width}-edge.png`)});
  await widget.locator('[data-stage]').selectOption('1');s=await snapshot();for(const p of s.model.stages[1].probabilities)near(p,.25,'after-cost probability');
  await widget.locator('[data-graph]').selectOption('triangle');s=await snapshot();near(s.model.stages[2].expectedScore,.75,'triangle with edge angles');
  await widget.locator('[data-example]').click();s=await snapshot();const triangleGamma=Math.atan(1/Math.sqrt(2));near(s.gamma,triangleGamma,'DOM triangle gamma',1e-14);near(s.beta,triangleGamma/2,'DOM triangle beta',1e-14);near(s.model.stages[2].expectedScore,2,'triangle preset expected');near(s.model.stages[2].optimalProbability,1,'triangle preset optimal');if(s.rows!==8)throw Error('triangle rows missing');
  const trianglePreset={gamma:s.gamma,beta:s.beta,expectedScore:s.model.stages[2].expectedScore,optimalProbability:s.model.stages[2].optimalProbability,rows:s.rows};
  await widget.screenshot({path:path.join(qa,`${lang}-widget-${width}-triangle.png`)});
  await widget.locator('[data-reset]').click();s=await snapshot();if(s.graph!=='edge'||s.stage!==2||s.rows!==4)throw Error('reset failed');near(s.gamma,Math.PI/2,'reset gamma');near(s.beta,Math.PI/8,'reset beta');
  for(const field of ['gamma','beta']){
   await widget.locator(`[data-${field}]`).fill('0');await widget.locator(`[data-${field}]`).dispatchEvent('input');s=await snapshot();near(s.model.stages[2].expectedScore,.5,`zero ${field}`);await widget.locator('[data-reset]').click();
  }
  const before=await widget.locator('[data-gamma]').inputValue();await widget.locator('[data-gamma]').focus();await page.keyboard.press('ArrowRight');const after=await widget.locator('[data-gamma]').inputValue();if(before===after)throw Error('range keyboard action ineffective');await widget.locator('[data-reset]').click();
  const mathOverflow=await page.evaluate(()=>[...document.querySelectorAll('.math-block img,.math-inline')].map(i=>({alt:i.alt,b:i.getBoundingClientRect().toJSON()})).filter(x=>x.b.right>innerWidth+1||x.b.left< -1));
  if(s.width!==width||errors.length||requests.length||mathOverflow.length)throw Error(JSON.stringify({lang,width,s,errors,requests,mathOverflow}));
  await page.emulateMedia({media:'print'});const hidden=await widget.evaluate(x=>getComputedStyle(x).display==='none');if(!hidden)throw Error('interactive control is visible in print');
  records.push({lang,width,trianglePreset,keyboardRangeAction:true,reset:true,zeroAngleChecks:true,afterCostProbabilityInvariant:true,printWidgetHidden:true,displayedMathOverflow:mathOverflow,errors,externalRequests:requests});await page.close();
 }
}finally{await browser.close()}
fs.writeFileSync(path.join(qa,'widget-checks.json'),JSON.stringify(records,null,2)+'\n');
for(const r of records)console.log(JSON.stringify(r));
