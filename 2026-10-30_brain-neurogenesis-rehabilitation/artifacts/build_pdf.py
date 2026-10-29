"""Print both complete local HTML articles to PDFs with bundled Playwright/Chrome.

Runtime and dependency locations are arguments or environment variables. Neither
the HTML nor PDF output contains host file paths, default browser print headers,
or browser-generated file URLs.
"""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import tempfile

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
const pages=[];
try {
 for(const lang of cfg.languages){
  const dir=path.join(cfg.root,'dist',lang==='ko'?'':'en');
  const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(pathToFileURL(path.join(dir,'index.html')).href,{waitUntil:'load'});
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForFunction(()=>[...document.images].every(image=>image.complete&&image.naturalWidth>0));
  const title=await page.title();
  const footer=`<div style="width:100%;margin:0 18mm;color:#66716f;font:8px Arial,sans-serif;border-top:1px solid #d9e1dc;padding-top:9px;display:flex;justify-content:space-between"><span>AI Tech Review Letters · 2026-10-30</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
  await page.pdf({path:path.join(dir,`review_${lang}.pdf`),format:'A4',preferCSSPageSize:true,printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:footer,margin:{top:'18mm',bottom:'20mm',left:'18mm',right:'18mm'},tagged:true,outline:true});
  await page.emulateMedia({media:'screen'});
  await page.screenshot({path:path.join(cfg.qa,`${lang}-desktop.png`),fullPage:false});
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:path.join(cfg.qa,`${lang}-mobile.png`),fullPage:false});
  const mobile=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth,badImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src')),h1:document.querySelector('h1').innerText,headings:document.querySelectorAll('h2').length}));
  if(mobile.document>mobile.viewport+1)throw Error(`Mobile overflow for ${lang}: ${JSON.stringify(mobile)}`);
  if(mobile.badImages.length||errors.length)throw Error(`Browser errors: ${JSON.stringify({mobile,errors})}`);
  pages.push({language:lang,title,mobile,pdf:`dist/${lang==='ko'?'':'en/'}review_${lang}.pdf`});
  await page.close();
 }
} finally {await browser.close()}
fs.writeFileSync(path.join(cfg.qa,'browser-checks.json'),JSON.stringify(pages,null,2)+'\n');
for(const record of pages)console.log(JSON.stringify(record));
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node', default=os.getenv('REVIEW_NODE') or shutil.which('node'))
    parser.add_argument('--modules', default=os.getenv('CODEX_PRIMARY_RUNTIME_NODE_MODULES'))
    parser.add_argument('--language', choices=['ko','en'])
    parser.add_argument('--qa-dir', type=Path, default=ROOT / 'tmp' / 'pdfs')
    args = parser.parse_args()
    if not args.node or not args.modules:
        parser.error('Set --node and --modules, or REVIEW_NODE and CODEX_PRIMARY_RUNTIME_NODE_MODULES.')
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    config = {'root':str(ROOT),'modules':str(Path(args.modules).resolve()),'qa':str(args.qa_dir.resolve()),'languages':[args.language] if args.language else ['ko','en']}
    env = {**os.environ, 'REVIEW_PRINT_CONFIG':json.dumps(config)}
    subprocess.run([args.node, '--input-type=module', '-e', NODE_PROGRAM], env=env, check=True)

if __name__ == '__main__':
    main()
