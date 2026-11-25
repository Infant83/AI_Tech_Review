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
const qa=path.join(root,'..','output','quantum-review-production-20261125','publication-production');fs.mkdirSync(qa,{recursive:true});
const results=[];
try{
 const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
 if(process.argv.includes('--figures')){
  const files=['','en'].flatMap(lang=>{const dir=path.join(root,'dist',lang);return fs.readdirSync(dir).filter(n=>/^fig[1-3]_.*\.svg$/.test(n)).map(name=>({dir,name}));});
  const all=[];
  for(const {dir,name} of files){
   const svg=fs.readFileSync(path.join(dir,name),'utf8');
   const w=Number(svg.match(/width="(\d+)"/)[1]),h=Number(svg.match(/height="(\d+)"/)[1]);
   await page.setViewportSize({width:w,height:h});
   await page.setContent('<html><body style="margin:0">'+svg+'</body></html>');
   await page.evaluate(()=>document.fonts.ready);
   const box=await page.evaluate(name=>{
    const s=document.querySelector('svg'),v=s.viewBox.baseVal;
    const text=[...s.querySelectorAll('text')].map(e=>{const b=e.getBBox();return {text:e.textContent,x:b.x,y:b.y,width:b.width,height:b.height,anchorX:Number(e.getAttribute('x'))};});
    const columns=name.startsWith('fig1_desktop')?text.filter(t=>t.anchorX===551||t.anchorX===895).map(t=>({text:t.text,x:t.x,end:t.x+t.width,limit:t.anchorX===551?827:1156})):[];
    return {width:v.width,height:v.height,overflow:text.filter(b=>b.x<0||b.x+b.width>v.width||b.y<0||b.y+b.height>v.height),columns,columnOverflow:columns.filter(t=>t.end>t.limit+.25)};
   },name);
   await page.setViewportSize({width:box.width,height:box.height});
   await page.screenshot({path:path.join(qa,name.replace('.svg','.png')),fullPage:true});
   all.push({file:name,...box});
  }
  fs.writeFileSync(path.join(qa,'all-figure-bounds.json'),JSON.stringify(all,null,2));
  const failures=all.filter(r=>r.overflow.length||r.columnOverflow.length);
  if(failures.length)throw Error('Figure text bounds failed: '+JSON.stringify(failures));
  console.log(JSON.stringify(all.map(r=>({file:r.file,overflow:r.overflow.length,columnOverflow:r.columnOverflow.length}))));
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
   await page.pdf({path:pdf,format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-family:Arial,sans-serif;font-size:8px;color:#586865;width:100%;text-align:center">Agentic Tech Review Letters · 2026-11-24 · <span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
   await page.emulateMedia({media:'screen'});
   const desktop=await page.evaluate(()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),imageCount:document.images.length,references:document.querySelectorAll('[id^="ref-"]').length,citationTargets:[...document.querySelectorAll('[role="doc-biblioref"]')].every(a=>document.getElementById(a.hash.slice(1))),disclosures:document.querySelectorAll('.authoring-disclosure').length,tableRegions:document.querySelectorAll('.table-scroll').length,language:document.documentElement.lang,canonical:document.querySelector('link[rel="canonical"]').href,selectedLanguage:document.querySelector('[aria-current="page"]').lang,privatePaths:/\/Users\/|file:\/\//.test(document.body.textContent),scripts:document.scripts.length}));
   if(desktop.overflow||!desktop.images||desktop.imageCount!==4||desktop.references!==27||!desktop.citationTargets||desktop.disclosures!==1||desktop.tableRegions!==3||desktop.language!==lang||desktop.selectedLanguage!==lang||desktop.privatePaths||desktop.scripts)throw Error('Desktop structural verification failed: '+JSON.stringify(desktop));
   await page.screenshot({path:path.join(qa,`${lang}-desktop.png`)});
   await page.setViewportSize({width:390,height:844});
   await page.waitForFunction(()=>[...document.querySelectorAll('picture img')].every(i=>i.currentSrc.includes('mobile')));
   await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
   const mobile=await page.evaluate(()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),mobileFigures:[...document.querySelectorAll('picture img')].every(i=>i.currentSrc.includes('mobile'))}));
   if(mobile.overflow||!mobile.images||!mobile.mobileFigures)throw Error('Mobile verification failed');
   await page.screenshot({path:path.join(qa,`${lang}-mobile.png`)});
   results.push({language:lang,pdf:pdf.slice(root.length+1),bytes:fs.statSync(pdf).size,desktop,mobile});
  }
  const fix=spawnSync(process.env.REVIEW_PYTHON||'python3',[path.join(root,'artifacts','fix_pdf_text.py')],{encoding:'utf8'});
  if(fix.status!==0)throw Error('PDF text-layer verification failed: '+fix.stderr);
  for(const result of results)result.bytes=fs.statSync(path.join(root,result.pdf)).size;
  fs.writeFileSync(path.join(qa,'render-results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results));
 }
}finally{await browser.close();}
