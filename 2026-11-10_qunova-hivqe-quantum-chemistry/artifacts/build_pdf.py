"""Render local review HTML to PDFs; UI verification is a separate CUA task."""
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
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const cfg=JSON.parse(process.env.REVIEW_PRINT_CONFIG);
const require=createRequire(path.join(cfg.modules,'_print.cjs'));
const {chromium}=require('playwright');
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const browser=await chromium.launch({channel:'chrome',headless:true});
const results=[];
try {
 for(const language of cfg.languages){
  const dir=path.join(cfg.root,'dist',language==='ko'?'':'en');
  const input=path.join(dir,'index.html');
  const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(pathToFileURL(input).href,{waitUntil:'load'});
  await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(()=>{for(const image of document.images)image.loading='eager'});
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0),undefined,{timeout:20000});
  const metadata=await page.evaluate(()=>({title:document.title,h1:document.querySelector('h1')?.textContent.trim(),og:document.querySelector('meta[property="og:title"]')?.content,lang:document.documentElement.lang,canonical:document.querySelector('link[rel="canonical"]')?.href,published:document.querySelector('meta[property="article:published_time"]')?.content,evidence:document.querySelector('meta[name="evidence-cutoff"]')?.content,brand:document.querySelector('header .brand')?.textContent.trim()}));
  if(metadata.title!==metadata.h1||metadata.og!==metadata.h1||metadata.lang!==language||metadata.brand!=='AGENTIC TECH REVIEW LETTERS')throw Error(`Print metadata mismatch: ${JSON.stringify(metadata)}`);
  // Resolve only approved publication support links against the clean public canonical.
  // This affects the print document, never the saved source HTML. Unexpected relative
  // destinations are rejected, so a chemical label cannot silently become a dead link.
  const printLinks=await page.evaluate(({language,canonical})=>{
   const base=new URL(canonical);
   if(base.protocol!=='https:'||base.hostname!=='infant83.io'||!base.pathname.startsWith('/AI_Tech_Review/reviews/'))throw Error('Invalid print canonical URL.');
   const allowed=new Set(['example-results.json','hero.webp',`review_${language}.pdf`,...['handover_workflow','support_and_energy'].flatMap(stem=>[`${stem}_${language}.svg`,`${stem}_mobile_${language}.svg`])]);
   const converted=[];
   for(const a of document.querySelectorAll('a[href]')){
    const raw=a.getAttribute('href');
    if(!raw||raw.startsWith('#'))continue;
    if(/^(?:file:|\/|\\|~)/i.test(raw)||/\/Users\/|\/tmp\//i.test(raw))throw Error('Private or absolute local link in print input.');
    if(/^[A-Za-z][A-Za-z0-9+.-]*:/.test(raw)){
     if(!/^(?:https?:|mailto:)/i.test(raw))throw Error('Unsupported URI scheme in print input.');
     continue;
    }
    if(!allowed.has(raw))throw Error(`Unexpected relative publication link: ${raw}`);
    const publicUrl=new URL(raw,base).href;
    a.setAttribute('href',publicUrl);converted.push({source:raw,url:publicUrl});
   }
   return converted;
  },{language,canonical:metadata.canonical});
  const footer=`<div style="width:100%;margin:0 18mm;color:#66716f;font:8px Arial,sans-serif;border-top:1px solid #d9e1dc;padding-top:9px;display:flex;justify-content:space-between"><span>Agentic Tech Review Letters · ${metadata.published}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
  const pdf=path.join(dir,`review_${language}.pdf`);
  await page.pdf({path:pdf,format:'A4',preferCSSPageSize:true,printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:footer,margin:{top:'18mm',bottom:'20mm',left:'18mm',right:'18mm'},tagged:true,outline:true});
  if(errors.length)throw Error(`Local document rendering error: ${errors.join('; ')}`);
  results.push({language,metadata,source_html_sha256:sha(input),stylesheet_sha256:sha(path.join(dir,'review.css')),pdf:path.relative(cfg.root,pdf),pdf_bytes:fs.statSync(pdf).size,pdf_sha256:sha(pdf),approved_print_links:printLinks,document_render_errors:errors});
  await page.close();
 }
} finally {await browser.close()}
fs.writeFileSync(path.join(cfg.qa,'print-manifest.json'),JSON.stringify(results,null,2)+'\n');
for(const result of results)console.log(JSON.stringify(result));
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node', default=os.getenv('REVIEW_NODE') or shutil.which('node'))
    parser.add_argument('--modules', default=os.getenv('CODEX_PRIMARY_RUNTIME_NODE_MODULES') or os.getenv('REVIEW_NODE_MODULES'))
    parser.add_argument('--language', choices=['ko', 'en'])
    parser.add_argument('--qa-dir', type=Path, default=ROOT / 'tmp' / 'pdfs')
    args = parser.parse_args()
    if not args.node or not args.modules:
        parser.error('Set --node and --modules, or REVIEW_NODE and CODEX_PRIMARY_RUNTIME_NODE_MODULES.')
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    config = {'root': str(ROOT), 'modules': str(Path(args.modules).resolve()),
              'qa': str(args.qa_dir.resolve()), 'languages': [args.language] if args.language else ['ko', 'en']}
    env = {**os.environ, 'REVIEW_PRINT_CONFIG': json.dumps(config)}
    subprocess.run([args.node, '--input-type=module', '-e', NODE_PROGRAM], env=env, check=True)


if __name__ == '__main__':
    main()
