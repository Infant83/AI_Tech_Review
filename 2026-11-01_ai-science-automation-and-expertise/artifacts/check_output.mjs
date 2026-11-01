/** Read-only checks and private screenshots of final bilingual publication files. */
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(path.join(process.env.REVIEW_NODE_MODULES,'_qa.cjs'));
const {chromium}=require('playwright');
const qa=path.resolve(process.argv.find(a=>a.startsWith('--qa-dir='))?.slice('--qa-dir='.length)||path.join(root,'tmp/pdfs'));
const expectedRefs=Number(process.argv.find(a=>a.startsWith('--expected-refs='))?.split('=')[1]||13);
const expectedCitations=Number(process.argv.find(a=>a.startsWith('--expected-citations='))?.split('=')[1]||29);
fs.mkdirSync(qa,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});const records=[];
try{
 for(const lang of ['ko','en']){
  const dir=path.join(root,'dist',lang==='ko'?'':'en');
  const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[],network=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
  await page.goto(pathToFileURL(path.join(dir,'index.html')).href);await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.fonts].map(f=>f.load()))});
  await page.evaluate(()=>{document.documentElement.style.scrollBehavior='auto'});
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  const info=await page.evaluate(()=>({
   title:document.title,h1:document.querySelector('h1').textContent,og:document.querySelector('meta[property="og:title"]').content,lang:document.documentElement.lang,
   canonical:document.querySelector('link[rel=canonical]').href,
   alternate:[...document.querySelectorAll('link[rel=alternate]')].map(x=>[x.hreflang,x.href]),
   fonts:[...document.fonts].map(x=>({family:x.family,weight:x.weight,status:x.status})),
   references:[...document.querySelectorAll('.reference-list>li')].map(x=>x.id),
   citationTargets:[...document.querySelectorAll('.citation')].map(x=>({href:x.href,label:x.textContent})),
   figures:[...document.querySelectorAll('figure')].map(f=>({src:[...f.querySelectorAll('img')].map(i=>i.getAttribute('src')),alt:[...f.querySelectorAll('img')].map(i=>i.alt),caption:f.querySelector('figcaption')?.textContent})),
   disclosureCount:document.querySelectorAll('#authoring-disclosure').length,
   disclosureFields:[...document.querySelectorAll('#authoring-disclosure dt')].map(x=>x.textContent),
   mathImages:document.querySelectorAll('img[src^="math_"]').length,
   desktop:{viewport:innerWidth,width:document.documentElement.scrollWidth},
   verificationSection:[...document.querySelectorAll('h2')].some(h=>/연구자가 검증을 설계하는 방법|How researchers can design verification/.test(h.textContent)),
   pauliTest:['|0⟩','Pauli Z','Pauli Y'].map(s=>({text:s,present:document.body.textContent.includes(s)})),
   rawBold:document.body.textContent.includes('**'),replacement:document.body.textContent.includes('\uFFFD'),
   privateStrings:['/Users/','file://','localhost','127.0.0.1','chain-of-thought'].filter(s=>document.documentElement.outerHTML.includes(s)),
   missingFragments:[...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href').slice(1)).filter(id=>!document.getElementById(id))
  }));
  const base='https://infant83.io/AI_Tech_Review/reviews/2026-11-01_ai-science-automation-and-expertise/';
  if(info.title!==info.h1||info.og!==info.h1||info.lang!==lang||info.canonical!==base+(lang==='ko'?'':'en/'))throw Error('metadata mismatch');
  if(info.references.length!==expectedRefs||info.citationTargets.length!==expectedCitations||!info.verificationSection||info.pauliTest.some(t=>!t.present))throw Error('Revision contents or counts mismatch: '+JSON.stringify(info));
  if(info.desktop.width!==info.desktop.viewport)throw Error('Desktop overflow');
  if(info.figures.length!==4||info.figures[0].src[0]!=='hero.webp'||info.figures.some(f=>!f.caption||f.alt.some(a=>!a))||info.disclosureCount!==1||info.disclosureFields.length!==7||info.rawBold||info.replacement||info.privateStrings.length||info.missingFragments.length||info.fonts.some(f=>f.status!=='loaded'))throw Error(JSON.stringify(info));
  for(const c of info.citationTargets){const target=c.href.match(/#(ref-\d+)$/)?.[1];if(!target||!info.references.includes(target))throw Error('citation has no reference '+JSON.stringify(c))}
  await page.screenshot({path:path.join(qa,`${lang}-desktop-final.png`)});
  await page.locator('p').filter({hasText:'Pauli Z'}).screenshot({path:path.join(qa,`${lang}-pauli-desktop.png`)});
  await page.locator('#authoring-disclosure').screenshot({path:path.join(qa,`${lang}-disclosure-desktop.png`)});
  await page.setViewportSize({width:390,height:844});await page.goto(pathToFileURL(path.join(dir,'index.html')).href);await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.fonts].map(f=>f.load()))});await page.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';window.scrollTo(0,0)});
  await page.screenshot({path:path.join(qa,`${lang}-mobile-fresh.png`)});
  await page.locator('p').filter({hasText:'Pauli Z'}).screenshot({path:path.join(qa,`${lang}-pauli-mobile.png`)});
  for(const [i,f] of (await page.locator('figure').all()).entries())await f.screenshot({path:path.join(qa,`${lang}-mobile-final-figure-${i+1}.png`)});
  await page.locator('#authoring-disclosure').screenshot({path:path.join(qa,`${lang}-disclosure-mobile.png`)});
  info.mobile=await page.evaluate(()=>({viewport:innerWidth,width:document.documentElement.scrollWidth,visibleFigures:[...document.querySelectorAll('figure')].map(f=>[...f.querySelectorAll('img')].filter(i=>getComputedStyle(i).display!=='none').map(i=>i.getAttribute('src'))),badImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length}));
  if(info.mobile.width!==390||info.mobile.badImages||info.mobile.visibleFigures.some(f=>f.length!==1)||errors.length||network.length)throw Error(JSON.stringify({info,errors,network}));
  const svgs=[];
  for(const f of info.figures.flatMap(f=>f.src).filter(f=>f.endsWith('.svg'))){
   const raw=fs.readFileSync(path.join(dir,f),'utf8');const m=raw.match(/width="(\d+)" height="(\d+)"/);if(!m)throw Error('no SVG size');await page.setViewportSize({width:+m[1],height:+m[2]});await page.goto(pathToFileURL(path.join(dir,f)).href);await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.fonts].map(f=>f.load()))});
   const bounds=await page.evaluate(()=>{const v=document.documentElement.viewBox.baseVal;return{fonts:[...document.fonts].map(f=>({family:f.family,status:f.status})),bad:[...document.querySelectorAll('text')].map(t=>({text:t.textContent,b:t.getBBox()})).filter(o=>o.b.x<12||o.b.y<12||o.b.x+o.b.width>v.width-12||o.b.y+o.b.height>v.height-12).map(o=>o.text)}});
   if(bounds.bad.length||bounds.fonts.some(f=>f.status!=='loaded'))throw Error(JSON.stringify({f,bounds}));
   await page.screenshot({path:path.join(qa,f.replace('.svg','-embedded.png'))});svgs.push({file:f,...bounds});
  }
  records.push({lang,info,svgs,errors,network});await page.close();
 }
}finally{await browser.close()}
fs.writeFileSync(path.join(qa,'html-asset-checks.json'),JSON.stringify(records,null,2)+'\n');
for(const r of records)console.log(JSON.stringify({lang:r.lang,refs:r.info.references.length,math:r.info.mathImages,mobile:r.info.mobile,svgCount:r.svgs.length,errors:r.errors,externalRequests:r.network}));
