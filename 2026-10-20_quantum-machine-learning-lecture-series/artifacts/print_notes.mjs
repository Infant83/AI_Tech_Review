#!/usr/bin/env node
// REVIEW_NODE_MODULES locates playwright. Optional REVIEW_CHROME gives an
// executable; otherwise installed Google Chrome is selected by channel.
import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const bases=(process.env.REVIEW_NODE_MODULES||'').split(path.delimiter).filter(Boolean);
const {chromium}=require(require.resolve('playwright',{paths:bases.length?bases:[ROOT]}));
const output=path.join(ROOT,'output','pdf','quantum-machine-learning-lecture-notes-ko.pdf');
const qa=path.join(ROOT,'tmp','pdfs'); await fs.mkdir(qa,{recursive:true});await fs.mkdir(path.dirname(output),{recursive:true});
const server=http.createServer(async(req,res)=>{try{const name=decodeURIComponent(new URL(req.url,'http://local').pathname);const rel=name==='/'?'index.html':name.slice(1);const file=path.resolve(ROOT,'dist',rel);if(!file.startsWith(path.join(ROOT,'dist')+path.sep))throw new Error('outside dist');const type=({'.html':'text/html; charset=utf-8','.css':'text/css','.woff2':'font/woff2','.json':'application/json','.pdf':'application/pdf','.svg':'image/svg+xml'})[path.extname(file)]||'text/plain';res.setHeader('Content-Type',type);res.end(await fs.readFile(file));}catch{res.statusCode=404;res.end('Not found');}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const url='http://127.0.0.1:'+server.address().port+'/';
const browser=await chromium.launch(process.env.REVIEW_CHROME?{headless:true,executablePath:process.env.REVIEW_CHROME}:{headless:true,channel:'chrome'});
try{
const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
const consoleErrors=[];page.on('pageerror',e=>consoleErrors.push(String(e)));
await page.goto(url,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
await page.screenshot({path:path.join(qa,'desktop.png')});
const inspect=()=>page.evaluate(()=>({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
  overflow:document.documentElement.scrollWidth>innerWidth+1,
  overflowingContent:[...document.querySelectorAll('.document p,.document li,.document .math-inline,.document .math-display,.document h1,.document h2,.document h3')].filter(n=>n.getBoundingClientRect().right>innerWidth+1&&!n.closest('table')).map(n=>({tag:n.tagName,source:n.closest('.document').dataset.source,text:(n.getAttribute('aria-label')||n.textContent).slice(0,160),right:n.getBoundingClientRect().right})).slice(0,20),
  mathErrors:document.querySelectorAll('[data-mjx-error],[data-mml-node="merror"]').length,
  equations:document.querySelectorAll('.math-inline,.math-display').length,
  images:[...document.images].map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0})),
  clippedFigures:[...document.images].filter(i=>i.getBoundingClientRect().width>i.parentElement.getBoundingClientRect().width+1).map(i=>i.getAttribute('src')),
  clippedMath:[...document.querySelectorAll('.math-display')].filter(i=>i.getBoundingClientRect().width>i.closest('.document').getBoundingClientRect().width+1).map(i=>i.getAttribute('aria-label')),
  fonts:document.fonts.check('14px QMLArchive'),
  glossaryEntries:document.querySelectorAll('.term-entry').length,
  duplicateIds:[...document.querySelectorAll('[id]')].map(n=>n.id).filter((id,index,all)=>all.indexOf(id)!==index),
  brokenAnchors:[...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href').slice(1)).filter(id=>!document.getElementById(id))}));
const desktop=await inspect();
await page.setViewportSize({width:390,height:844});await page.reload({waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
await page.screenshot({path:path.join(qa,'mobile.png')});const mobile=await inspect();
await page.locator('#term-query').fill('G056');
const termSearch=await page.locator('.term-entry:visible').count();
await page.locator('#term-query').fill('존재하지않는용어xx');
const emptySearch=await page.locator('.term-entry:visible').count();
await page.locator('#term-query').fill('');
const resetSearch=await page.locator('.term-entry:visible').count();
if(desktop.overflow||mobile.overflow||desktop.mathErrors||mobile.mathErrors||!desktop.fonts||!mobile.fonts||desktop.brokenAnchors.length||mobile.brokenAnchors.length||desktop.duplicateIds.length||mobile.duplicateIds.length||desktop.glossaryEntries!==144||mobile.glossaryEntries!==144||termSearch!==1||emptySearch!==0||resetSearch!==144||[...desktop.images,...mobile.images].some(i=>!i.loaded)||desktop.clippedFigures.length||mobile.clippedFigures.length||desktop.clippedMath.length||mobile.clippedMath.length||consoleErrors.length)throw new Error('Browser QA failed: '+JSON.stringify({desktop,mobile,termSearch,emptySearch,resetSearch,consoleErrors}));
await page.setViewportSize({width:1440,height:1100});await page.emulateMedia({media:'print'});
// Downloadable local files have no portable URL in a standalone PDF. Keep
// their visible labels while removing only those link annotations for print.
await page.evaluate(()=>{document.querySelectorAll('a[href]').forEach(a=>{const h=a.getAttribute('href');if(!h.startsWith('#')&&!/^https?:|^mailto:/.test(h))a.removeAttribute('href');});});
await page.pdf({path:output,format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,tagged:true,outline:true,
  headerTemplate:'<span></span>',footerTemplate:'<div style="width:100%;font-family:Arial,sans-serif;font-size:8px;color:#5a7278;padding:0 16mm;display:flex;justify-content:space-between"><span>QML LECTURE NOTES · 2026-10-20</span><span class="pageNumber"></span></div>'});
await fs.copyFile(output,path.join(ROOT,'dist','notes.pdf'));
await fs.writeFile(path.join(qa,'browser-qa.json'),JSON.stringify({desktop,mobile,termSearch,emptySearch,resetSearch,consoleErrors},null,2)+'\n');
console.log(JSON.stringify({pdf:path.basename(output),bytes:(await fs.stat(output)).size,desktop,mobile}));
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
