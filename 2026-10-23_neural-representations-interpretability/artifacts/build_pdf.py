"""Print complete local bilingual articles, and inspect desktop/mobile output."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]

NODE_PROGRAM = r'''
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const cfg=JSON.parse(process.env.REVIEW_PRINT_CONFIG);
const require=createRequire(path.join(cfg.modules,'_print.cjs'));
const {chromium}=require('playwright');
const browser=await chromium.launch({channel:'chrome',headless:true});
const results=[];
try {
 for(const language of cfg.languages){
  const dir=path.join(cfg.root,'dist',language==='ko'?'':'en');
  const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(pathToFileURL(path.join(dir,'index.html')).href,{waitUntil:'load'});
  await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(()=>{document.documentElement.style.scrollBehavior='auto'});
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0),undefined,{timeout:20000});
  const metadata=await page.evaluate(()=>({title:document.title,h1:document.querySelector('h1')?.textContent.trim(),og:document.querySelector('meta[property="og:title"]')?.content,lang:document.documentElement.lang,canonical:document.querySelector('link[rel="canonical"]')?.href}));
  if(metadata.title!==metadata.h1||metadata.og!==metadata.h1||metadata.lang!==language)throw Error(`Metadata mismatch: ${JSON.stringify(metadata)}`);
  // Keep local SVG inspection links on screen without leaking host file URIs to PDF annotations.
  await page.evaluate(()=>{for(const a of document.querySelectorAll('a.figure-zoom')){a.dataset.figureHref=a.getAttribute('href');a.removeAttribute('href')}});
  const footer='<div style="width:100%;margin:0 18mm;color:#66716f;font:8px Arial,sans-serif;border-top:1px solid #d9e1dc;padding-top:9px;display:flex;justify-content:space-between"><span>AI Tech Review Letters · 2026-10-23</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>';
  await page.pdf({path:path.join(dir,language==='ko'?'review.pdf':'review-en.pdf'),format:'A4',preferCSSPageSize:true,printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:footer,margin:{top:'18mm',bottom:'20mm',left:'18mm',right:'18mm'},tagged:true,outline:true});
  await page.evaluate(()=>{for(const a of document.querySelectorAll('a.figure-zoom'))a.setAttribute('href',a.dataset.figureHref)});
  await page.emulateMedia({media:'screen'});
  await page.screenshot({path:path.join(cfg.qa,`${language}-desktop.png`),fullPage:false});
  for(const [index,figure] of (await page.locator('figure').all()).entries())await figure.screenshot({path:path.join(cfg.qa,`${language}-desktop-figure-${index+1}.png`)});
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(()=>window.scrollTo({top:0,left:0,behavior:'instant'}));
  await page.screenshot({path:path.join(cfg.qa,`${language}-mobile.png`),fullPage:false});
  for(const [index,figure] of (await page.locator('figure').all()).entries())await figure.screenshot({path:path.join(cfg.qa,`${language}-mobile-figure-${index+1}.png`)});
  const mobile=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth,badImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src')),figures:document.querySelectorAll('figure').length}));
  if(mobile.document>mobile.viewport+1||mobile.badImages.length||errors.length)throw Error(`Browser checks failed: ${JSON.stringify({language,mobile,errors})}`);
  results.push({language,metadata,mobile,errors,pdf:language==='ko'?'dist/review.pdf':'dist/en/review-en.pdf'});
  await page.close();
 }
} finally {await browser.close()}
fs.writeFileSync(path.join(cfg.qa,'browser-checks.json'),JSON.stringify(results,null,2)+'\n');
for(const record of results)console.log(JSON.stringify(record));
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node', default=os.getenv('REVIEW_NODE') or shutil.which('node'))
    parser.add_argument('--modules', default=os.getenv('REVIEW_NODE_MODULES') or os.getenv('CODEX_PRIMARY_RUNTIME_NODE_MODULES'))
    parser.add_argument('--language', choices=['ko','en'])
    parser.add_argument('--qa-dir', type=Path, default=ROOT / 'tmp' / 'pdfs')
    args = parser.parse_args()
    if not args.node or not args.modules:
        parser.error('Set --node and --modules, or REVIEW_NODE and REVIEW_NODE_MODULES.')
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    config = {'root':str(ROOT),'modules':str(Path(args.modules).resolve()),'qa':str(args.qa_dir.resolve()),'languages':[args.language] if args.language else ['ko','en']}
    env = {**os.environ, 'REVIEW_PRINT_CONFIG':json.dumps(config)}
    subprocess.run([args.node, '--input-type=module', '-e', NODE_PROGRAM], env=env, check=True)

if __name__ == '__main__':
    main()
