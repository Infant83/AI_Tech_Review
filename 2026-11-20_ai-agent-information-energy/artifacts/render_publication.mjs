/** Render the reviewed publication, including closed theory notes in print. */
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const modules=process.env.REVIEW_NODE_MODULES||process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
if(!modules)throw Error('Set REVIEW_NODE_MODULES to an installed Playwright dependency directory.');
const require=createRequire(path.join(modules,'_render.cjs'));
const {chromium}=require('playwright');
const browser=await chromium.launch({channel:'chrome',headless:true});
const qa=path.join(root,'tmp','publication-production');fs.mkdirSync(qa,{recursive:true});
const results=[];
try{
 const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
 if(process.argv.includes('--figures')){
  const names=fs.readdirSync(path.join(root,'dist','en')).filter(n=>/^fig[1-5]_.*\.svg$/.test(n));
  const all=[];
  for(const name of names){
   const svg=fs.readFileSync(path.join(root,'dist','en',name),'utf8');
   const w=Number(svg.match(/width="(\d+)"/)[1]),h=Number(svg.match(/height="(\d+)"/)[1]);
   await page.setViewportSize({width:w,height:h});
   await page.setContent('<html><body style="margin:0">'+svg+'</body></html>');
   await page.evaluate(()=>document.fonts.ready);
   const box=await page.evaluate(()=>{const s=document.querySelector('svg');const v=s.viewBox.baseVal;return {width:v.width,height:v.height,overflow:[...s.querySelectorAll('text')].map(e=>({text:e.textContent,...(()=>{const b=e.getBBox();return {x:b.x,y:b.y,width:b.width,height:b.height}})()})).filter(b=>b.x<0||b.x+b.width>v.width||b.y<0||b.y+b.height>v.height)}});
   await page.setViewportSize({width:box.width,height:box.height});
   await page.screenshot({path:path.join(qa,name.replace('.svg','.png')),fullPage:true});
   all.push({file:name,...box});
  }
  fs.writeFileSync(path.join(qa,'english-figure-bounds.json'),JSON.stringify(all,null,2));
  console.log(JSON.stringify(all));
 }else{
  for(const lang of ['ko','en']){
   const dir=path.join(root,'dist',lang==='ko'?'':'en');
   const url='https://infant83.io/AI_Tech_Review/reviews/'+path.basename(root)+'/'+(lang==='ko'?'':'en/');
   await page.setViewportSize({width:1440,height:1100});
   await page.goto(pathToFileURL(path.join(dir,'index.html')).href);
   await page.evaluate(()=>document.fonts.ready);
   await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
   await page.locator('details').evaluateAll(nodes=>nodes.forEach(n=>n.open=true));
   await page.evaluate(base=>{for(const a of document.querySelectorAll('a[href]')){const h=a.getAttribute('href');if(h&&!h.startsWith('#'))a.href=new URL(h,base).href;}},url);
   await page.emulateMedia({media:'print'});
   const pdf=path.join(dir,`review_${lang}.pdf`);
   await page.pdf({path:pdf,format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-family:Arial,sans-serif;font-size:8px;color:#586865;width:100%;text-align:center">Agentic Tech Review Letters · 2026-11-22 · <span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
   await page.emulateMedia({media:'screen'});
   const desktop=await page.evaluate(()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0)}));
   await page.screenshot({path:path.join(qa,`${lang}-desktop.png`)});
   await page.setViewportSize({width:390,height:844});
   await page.waitForFunction(()=>[...document.querySelectorAll('picture img')].every(i=>i.currentSrc.includes('mobile')));
   await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
   const mobile=await page.evaluate(()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),mobileFigures:[...document.querySelectorAll('picture img')].every(i=>i.currentSrc.includes('mobile'))}));
   await page.screenshot({path:path.join(qa,`${lang}-mobile.png`)});
   results.push({language:lang,pdf:pdf.slice(root.length+1),bytes:fs.statSync(pdf).size,desktop,mobile});
  }
  const fix=spawnSync(process.env.REVIEW_PYTHON||'python3',[path.join(root,'artifacts','fix_pdf_text.py')],{encoding:'utf8'});
  if(fix.status!==0)throw Error('PDF text-layer verification failed: '+fix.stderr);
  for(const result of results)result.bytes=fs.statSync(path.join(root,result.pdf)).size;
  fs.writeFileSync(path.join(qa,'render-results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results));
 }
}finally{await browser.close();}
