import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const bases=(process.env.REVIEW_NODE_MODULES||'').split(path.delimiter).filter(Boolean);
const {chromium}=require(require.resolve('playwright',{paths:bases.length?bases:[ROOT]}));
const qa=path.join(ROOT,'tmp','pdfs');await fs.mkdir(qa,{recursive:true});
const expectedFigures=JSON.parse(await fs.readFile(path.join(ROOT,'figures','manifest.json'),'utf8')).figures.length;
const output=path.join(ROOT,'output','pdf','classiq-talk-series-notes-ko.pdf');await fs.mkdir(path.dirname(output),{recursive:true});
const server=http.createServer(async(req,res)=>{try{const name=decodeURIComponent(new URL(req.url,'http://local').pathname);const f=path.resolve(ROOT,'dist',name==='/'?'index.html':name.slice(1));if(!f.startsWith(path.join(ROOT,'dist')+path.sep))throw Error();res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.css':'text/css','.woff2':'font/woff2','.pdf':'application/pdf','.svg':'image/svg+xml','.png':'image/png','.json':'application/json'})[path.extname(f)]||'application/octet-stream');res.end(await fs.readFile(f));}catch{res.statusCode=404;res.end('Not found');}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,channel:'chrome'});
try{
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const checks=[];
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await page.goto('http://127.0.0.1:'+server.address().port+'/',{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
  const check=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,font:document.fonts.check('14px QMLArchive'),mathErrors:document.querySelectorAll('[data-mjx-error],[data-mml-node="merror"]').length,chapters:document.querySelectorAll('.document').length,equations:document.querySelectorAll('.math-inline,.math-display').length,brokenAnchors:[...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href').slice(1)).filter(id=>!document.getElementById(id)),duplicateIds:[...document.querySelectorAll('[id]')].map(n=>n.id).filter((id,i,all)=>all.indexOf(id)!==i),badImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length}));checks.push(check);
  check.figures=await page.evaluate(()=>({count:document.querySelectorAll('figure.teaching-figure').length,missingAlt:[...document.images].filter(i=>!i.alt).length,missingCaptions:[...document.querySelectorAll('figure')].filter(f=>!f.querySelector('figcaption')).length,clipped:[...document.querySelectorAll('figure img')].filter(i=>i.getBoundingClientRect().width>i.closest('figure').getBoundingClientRect().width+1).map(i=>i.getAttribute('src')),empty:[...document.images].filter(i=>i.getBoundingClientRect().height<1).map(i=>i.getAttribute('src'))}));
  await page.screenshot({path:path.join(qa,'browser-'+width+'.png')});
  if(check.scrollWidth>width+1||!check.font||check.mathErrors||check.chapters!==9||check.brokenAnchors.length||check.duplicateIds.length||check.badImages||check.figures.count!==expectedFigures||check.figures.missingAlt||check.figures.missingCaptions||check.figures.clipped.length||check.figures.empty.length)throw Error('Layout verification failed '+JSON.stringify(check));
 }
 if(errors.length)throw Error(JSON.stringify(errors));
 await page.setViewportSize({width:1200,height:1000});
 for(const figure of await page.locator('figure.teaching-figure').all()){
  const id=await figure.getAttribute('id');await figure.screenshot({path:path.join(qa,id+'.png')});
 }
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({media:'print'});
 await page.evaluate(()=>document.querySelectorAll('a[href]').forEach(a=>{const h=a.getAttribute('href');if(!/^(https?:|#)/.test(h))a.removeAttribute('href');}));
 await page.pdf({path:output,format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,tagged:true,outline:true,headerTemplate:'<span></span>',footerTemplate:'<div style="width:100%;font-family:Arial;font-size:8px;color:#50666d;padding:0 16mm;display:flex;justify-content:space-between"><span>CLASSIQ REPLAY NOTES · 2026-10-22</span><span class="pageNumber"></span></div>'});
 await fs.copyFile(output,path.join(ROOT,'dist','notes.pdf'));
 await fs.writeFile(path.join(qa,'browser-qa.json'),JSON.stringify({checks,errors},null,2)+'\n');
 console.log(JSON.stringify({pdf:path.basename(output),bytes:(await fs.stat(output)).size,checks}));
}finally{await browser.close();await new Promise(r=>server.close(r));}
