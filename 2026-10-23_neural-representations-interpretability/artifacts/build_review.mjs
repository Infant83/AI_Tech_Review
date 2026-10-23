/** Render the bilingual local review; copy only explicitly approved final assets. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifacts=path.join(root,'artifacts');
const slug='2026-10-23_neural-representations-interpretability';
const cutoff='2026-10-23';
const publicBase=(process.argv.find(a=>a.startsWith('--public-base='))?.slice(14)||`https://infant83.github.io/AI_Tech_Review/reviews/${slug}/`).replace(/\/?$/,'/');
const language=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
const publicLinks=process.argv.includes('--public-links');
if(language&&!['ko','en'].includes(language))throw Error('--language must be ko or en.');
const localRequire=createRequire(import.meta.url);
const dependencyRoots=[process.env.REVIEW_NODE_MODULES,process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,path.join(root,'node_modules'),path.join(process.cwd(),'node_modules')].filter(Boolean);
function dependency(spec){
 for(const directory of dependencyRoots){try{return createRequire(path.join(directory,'_review.cjs')).resolve(spec)}catch{}}
 try{return localRequire.resolve(spec)}catch{throw Error(`Missing ${spec}; set REVIEW_NODE_MODULES to an installed dependency directory.`)}
}
const {marked}=await import(pathToFileURL(dependency('marked')));
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const plain=s=>String(s).replace(/<[^>]*>/g,'').replace(/\[([^\]]+)\]\([^)]*\)/g,'$1').replace(/[\*_`]/g,'').replace(/\s+/g,' ').trim();
let mathDocument,adaptor;
function renderMath(tex,display){
 if(!mathDocument){
  const requireModule=spec=>localRequire(dependency(spec));
  const {mathjax}=requireModule('mathjax-full/js/mathjax.js');
  const {TeX}=requireModule('mathjax-full/js/input/tex.js');
  const {SVG}=requireModule('mathjax-full/js/output/svg.js');
  const {liteAdaptor}=requireModule('mathjax-full/js/adaptors/liteAdaptor.js');
  const {RegisterHTMLHandler}=requireModule('mathjax-full/js/handlers/html.js');
  const {AllPackages}=requireModule('mathjax-full/js/input/tex/AllPackages.js');
  adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
  mathDocument=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'local'})});
 }
 const filename=`math_${crypto.createHash('sha256').update((display?'display:':'inline:')+tex).digest('hex').slice(0,14)}.svg`;
 const rendered=adaptor.outerHTML(mathDocument.convert(tex,{display,em:16,ex:8,containerWidth:760}));
 const svg=rendered.match(/<svg[\s\S]*<\/svg>/)?.[0];
 if(!svg||/data-mjx-error|merror/.test(svg))throw Error(`Math typesetting failed: ${tex}`);
 fs.writeFileSync(path.join(artifacts,filename),svg+'\n');
 const width=svg.match(/\bwidth="([\d.]+)ex"/)?.[1]||'1';
 const height=svg.match(/\bheight="([\d.]+)ex"/)?.[1]||'1';
 const valign=svg.match(/vertical-align:\s*([^;" ]+)/)?.[1]||'0';
 return {filename,html:display?`<div class="math-block"><img src="${filename}" alt="${escape(tex)}" style="width:${width}ex;height:auto"></div>`:`<img class="math-inline" src="${filename}" alt="${escape(tex)}" style="width:${width}ex;height:${height}ex;vertical-align:${valign}">`};
}

let stylesheet=fs.readFileSync(path.join(artifacts,'review.css'),'utf8');
for(const weight of ['regular','bold']){
 const filename=`review-${weight}.woff2`;
 stylesheet=stylesheet.replaceAll(`url('${filename}')`,`url('data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,filename)).toString('base64')}')`);
}
stylesheet='/* '+fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','')+' */\n'+stylesheet;
function selfContainedFigure(filename){
 let svg=fs.readFileSync(filename,'utf8');
 if(!/<text\b/.test(svg))return svg;
 const rules=['regular','bold'].map(weight=>`@font-face{font-family:ReviewFigure;src:url(data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,`review-${weight}.woff2`)).toString('base64')}) format('woff2');font-weight:${weight==='regular'?400:700}}`).join('');
 const license=fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','');
 svg=svg.replace(/<svg\b[^>]*>/,tag=>tag+`\n<style><![CDATA[/* ${license} */\n${rules}\ntext{font-family:ReviewFigure,sans-serif}]]></style>`);
 return svg.replace(/\bfont-family="[^"]*"/g,'font-family="ReviewFigure,sans-serif"');
}
const descriptions={ko:'신경망의 내부 표현을 뉴런·특징·개념·회로로 구분하고, 해독·개입·인과 검증의 차이를 원 연구와 함께 분석한다.',en:'An evidence-grounded review of neural representations, features and concepts: what decoding, intervention and causal tests establish about AI models.'};

function cleanOutput(dir,expected){
 for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
  if(entry.isDirectory()){
   if(entry.name==='en')continue;
   if(entry.name!=='figures')throw Error(`Unexpected output directory: ${entry.name}`);
   for(const asset of fs.readdirSync(path.join(dir,entry.name))){if(!expected.has(`figures/${asset}`))fs.unlinkSync(path.join(dir,entry.name,asset));}
  }else if(!expected.has(entry.name))fs.unlinkSync(path.join(dir,entry.name));
 }
}

for(const lang of language?[language]:['ko','en']){
 const ko=lang==='ko';
 const sourceFile=path.join(root,'reports',ko?'review.md':'review_en.md');
 const source=fs.readFileSync(sourceFile,'utf8').replace(/\r\n/g,'\n');
 const headings=[...source.matchAll(/^#\s+(.+)$/gm)];
 if(headings.length!==1)throw Error(`Expected exactly one H1 in ${path.basename(sourceFile)}.`);
 const title=plain(headings[0][1]);
 const description=plain(source.match(/<p class=["']dek["']>([\s\S]*?)<\/p>/)?.[1]||descriptions[lang]);
 const math=[];
 const safe=source.replace(/\$\$([\s\S]*?)\$\$|\\\(([\s\S]*?)\\\)/g,(_,a,b)=>{
  const result=renderMath((a||b).trim(),a!==undefined);math.push(result);
  return a!==undefined?`\n\nMATHBLOCK${math.length-1}END\n\n`:`MATHINLINE${math.length-1}END`;
 });
 let body=marked.parse(safe,{gfm:true});
 // Preserve intended bold terms when a closing parenthesis is followed by a Korean particle.
 body=body.replace(/(?<=>)([^<]+)(?=<)/g,(_,text)=>text.replace(/\*\*([^*\n]+\))\*\*(?=[가-힣])/g,'<strong>$1</strong>'));
 body=body.replace(/<p>MATHBLOCK(\d+)END<\/p>/g,(_,i)=>math[+i].html).replace(/MATHINLINE(\d+)END/g,(_,i)=>math[+i].html);
 // Manuscripts may use source-package paths; public output always uses a local final path.
 body=body.replace(/\b(src|href)="(?:\.\.\/)?artifacts\/figures\/([^"/]+\.svg)"/g,'$1="figures/$2"').replace(/\bsrc="(?:\.\.\/)?artifacts\/hero\.webp"/g,'src="hero.webp"');
 body=body.replace(/<img\b[^>]*\bsrc="(figures\/[^"/]+\.svg)"[^>]*>/g,(tag,name)=>`<a class="figure-zoom" href="${name}" aria-label="${ko?'설명 도식 원본을 열어 확대 보기':'Open the full-size explanatory diagram'}">${tag}</a>`);
 let section=0;const toc=[];
 body=body.replace(/<h2(?:\s[^>]*)?>([\s\S]*?)<\/h2>/g,(_,text)=>{
  const label=plain(text);
  const id=/작성|제작|How (?:this review|the review)|Production and verification/i.test(label)?'authoring-disclosure':`section-${++section}`;
  toc.push(`<li><a href="#${id}">${text}</a></li>`);
  return `<h2 id="${id==='authoring-disclosure'?'authoring-disclosure-heading':id}">${text}</h2>`;
 });
 body=body.replaceAll('<table>',`<div class="table-scroll" role="region" tabindex="0" aria-label="${ko?'비교 표':'Comparison table'}"><table>`).replaceAll('</table>','</table></div>');
 body=body.replace(/(<h2[^>]*>(?:참고문헌[^<]*|References[^<]*)<\/h2>)([\s\S]*?)(?=<h2|$)/,(_,heading,content)=>heading+`<div class="references">${content}</div>`);
 body=body.replace(/(<h2 id="authoring-disclosure-heading">[\s\S]*?)(?=<h2|$)/,(_,content)=>`<!-- AI Tech Review Authoring Disclosure -->\n<section class="authoring-disclosure" id="authoring-disclosure">${content}</section>\n<!-- End AI Tech Review Authoring Disclosure -->`);
 const disclosureAnchor=body.includes('id="authoring-disclosure"')?'#authoring-disclosure':`${publicBase}#authoring-disclosure`;
 const byline=`<p class="byline-disclosure">${ko?'책임 편집: 김현중 · AI 보조 작성: OpenAI Codex · 근거 기준일: 2026년 10월 23일':'Responsible editor: Hyun-Jung Kim · AI assistance: OpenAI Codex · Evidence cutoff: 23 October 2026'} · <a href="${disclosureAnchor}">${ko?'작성·검증 범위':'Production and verification'}</a></p>`;
 body=body.replace(/<\/h1>/,'</h1>'+byline);
 const contents=`<details class="toc"><summary>${ko?'내용 살펴보기':'Contents'}</summary><ol>${toc.join('')}</ol></details>`;
 const heroEnd=body.indexOf('</figure>');
 body=heroEnd>=0?body.slice(0,heroEnd+9)+contents+body.slice(heroEnd+9):body.replace(byline,byline+contents);
 const url=publicBase+(ko?'':'en/');
 const other=publicLinks?(ko?`${publicBase}en/`:publicBase):(ko?'en/index.html':'../index.html');
 const pdf=ko?'review.pdf':'review-en.pdf';
 const html=`<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><meta name="description" content="${escape(description)}"><meta name="author" content="${ko?'김현중':'Hyun-Jung Kim'}"><meta property="og:title" content="${escape(title)}"><meta property="og:description" content="${escape(description)}"><meta property="og:type" content="article"><meta property="og:url" content="${escape(url)}"><meta property="og:image" content="${escape(publicBase)}hero.webp"><meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="${escape(url)}"><link rel="alternate" hreflang="ko" href="${escape(publicBase)}"><link rel="alternate" hreflang="en" href="${escape(publicBase)}en/"><link rel="alternate" hreflang="x-default" href="${escape(publicBase)}"><link rel="stylesheet" href="review.css"></head><body>
<header><a class="brand" href="https://infant83.github.io/AI_Tech_Review/">AI TECH REVIEW LETTERS</a><div class="topline-actions"><nav class="language-switcher" aria-label="${ko?'언어 선택':'Language'}"><span class="language-current" aria-current="page" lang="${lang}">${ko?'한국어':'English'}</span><a href="${escape(other)}" lang="${ko?'en':'ko'}" hreflang="${ko?'en':'ko'}">${ko?'English':'한국어'}</a></nav><a class="download" href="${pdf}">PDF ↓</a></div></header>
<main class="paper"><div class="issue-meta"><span>TECH REVIEW</span><span>2026.10.23</span><span>${ko?'AI 연구 · 신경망 표현과 해석 가능성':'AI RESEARCH · REPRESENTATIONS AND INTERPRETABILITY'}</span></div><article>${body}</article><div class="downloads"><a href="${pdf}">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${escape(other)}">${ko?'English version':'한국어판'}</a></div><footer class="footer">AI Tech Review Letters · ${cutoff}</footer></main></body></html>\n`;
 const dir=path.join(root,'dist',ko?'':'en');fs.mkdirSync(dir,{recursive:true});
 const expected=new Set(['index.html','review.css',pdf]);
 const assets=new Set();
 for(const match of html.matchAll(/\b(?:src|poster)="([^"#]+)"/g)){
  const name=match[1];if(/^(?:https?:|data:)/.test(name))throw Error(`Image must be a local approved asset: ${name}`);
  const isHero=name==='hero.webp';
  const isFigure=/^figures\/[a-zA-Z0-9_-]+\.svg$/.test(name);
  const isMath=/^math_[0-9a-f]{14}\.svg$/.test(name);
  if(!isHero&&!isFigure&&!isMath)throw Error(`Asset outside final figure allowlist: ${name}`);
  const origin=path.join(artifacts,name);if(!fs.existsSync(origin))throw Error(`Missing asset: ${name}`);
  const target=path.join(dir,name);fs.mkdirSync(path.dirname(target),{recursive:true});
  if(isFigure)fs.writeFileSync(target,selfContainedFigure(origin));else fs.copyFileSync(origin,target);
  expected.add(name);assets.add(name);
 }
 const firstImage=html.match(/<img\b[^>]*\bsrc="([^"]+)"/)?.[1];
 if(firstImage!=='hero.webp')throw Error(`The first article image must be hero.webp; got ${firstImage||'none'}.`);
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
 if(new Set(ids).size!==ids.length)throw Error('Duplicate HTML id.');
 for(const match of html.matchAll(/\bhref="#([^"]+)"/g)){if(!ids.includes(match[1]))throw Error(`Missing fragment: #${match[1]}`);}
 fs.writeFileSync(path.join(dir,'index.html'),html);
 fs.writeFileSync(path.join(dir,'review.css'),stylesheet);
 cleanOutput(dir,expected);
 console.log(JSON.stringify({language:lang,title,sections:toc.length,equations:math.length,assets:assets.size,file:path.relative(root,path.join(dir,'index.html'))}));
}
