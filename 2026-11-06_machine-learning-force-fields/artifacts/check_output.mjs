/** Inspect final HTML at desktop/mobile widths; keep QA outside public outputs. */
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const modules=process.env.REVIEW_BROWSER_MODULES||process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
if(!modules)throw Error('Set REVIEW_BROWSER_MODULES or CODEX_PRIMARY_RUNTIME_NODE_MODULES.');
const {chromium}=createRequire(path.join(modules,'_check.cjs'))('playwright');
const qa=path.join(root,'tmp','html-qa');fs.mkdirSync(qa,{recursive:true});
const only=process.argv.find(x=>x.startsWith('--language='))?.split('=')[1];
const browser=await chromium.launch({channel:'chrome',headless:true});
const records=[];
try{
 for(const language of only?[only]:['ko','en']){
  const index=path.join(root,'dist',language==='ko'?'':'en','index.html');
  const source=fs.readFileSync(index,'utf8');
  if(/file:\/\/|\/Users\/|archive\/private|MATH(?:BLOCK|INLINE)\d+END/.test(source))throw Error('Nonpublic path or typesetting token in output.');
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(pathToFileURL(index).href,{waitUntil:'load'});
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  const content=await page.evaluate(()=>({title:document.title,h1:document.querySelector('h1')?.textContent.trim(),canonical:document.querySelector('link[rel=canonical]')?.href,figures:document.querySelectorAll('figure').length,tables:document.querySelectorAll('table').length,references:document.querySelectorAll('.reference-list>li').length,equations:document.querySelectorAll('.math-block').length,disclosures:document.querySelectorAll('.authoring-disclosure').length,disclosureParagraphs:document.querySelectorAll('.authoring-disclosure p').length,missingTargets:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash)}));
  if(content.title!==content.h1||content.figures!==5||content.tables!==5||content.references!==30||content.equations!==8||content.disclosures!==1||content.disclosureParagraphs<2||content.missingTargets.length)throw Error(JSON.stringify(content));
  await page.screenshot({path:path.join(qa,`${language}-desktop.png`)});
  const figures=await page.locator('figure').all();
  for(let i=0;i<figures.length;i++)await figures[i].screenshot({path:path.join(qa,`${language}-figure-${i+1}.png`)});
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';window.scrollTo(0,0)});
  const mobile=await page.evaluate(()=>({viewport:innerWidth,width:document.documentElement.scrollWidth,hero:[...document.querySelectorAll('figure.hero img')].map(i=>({width:i.width,height:i.height,ratio:i.width/i.height})),badImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src'))}));
  if(mobile.width>mobile.viewport+1||mobile.badImages.length||errors.length||Math.abs(mobile.hero[0].ratio-16/9)>.01)throw Error(JSON.stringify({mobile,errors}));
  await page.screenshot({path:path.join(qa,`${language}-mobile.png`)});
  records.push({language,content,mobile,errors});await page.close();
 }
}finally{await browser.close()}
fs.writeFileSync(path.join(qa,'checks.json'),JSON.stringify(records,null,2)+'\n');
for(const record of records)console.log(JSON.stringify(record));
