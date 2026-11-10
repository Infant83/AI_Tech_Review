/** Publish bilingual Markdown with deterministic equations and explicit local assets. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifacts=path.join(root,'artifacts');
const moduleRoots=[process.env.REVIEW_NODE_MODULES,process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,path.join(root,'tmp','deps','node_modules'),path.join(root,'node_modules')].filter(Boolean);
const localRequire=createRequire(import.meta.url);
function resolveModule(name){
 for(const directory of moduleRoots){try{return createRequire(path.join(directory,'_build.cjs')).resolve(name)}catch{}}
 try{return localRequire.resolve(name)}catch{throw Error(`Missing ${name}; set REVIEW_NODE_MODULES or CODEX_PRIMARY_RUNTIME_NODE_MODULES.`)}
}
const {marked}=await import(pathToFileURL(resolveModule('marked')));
const module=name=>localRequire(resolveModule(name));
const {mathjax}=module('mathjax-full/js/mathjax.js');
const {TeX}=module('mathjax-full/js/input/tex.js');
const {SVG}=module('mathjax-full/js/output/svg.js');
const {liteAdaptor}=module('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=module('mathjax-full/js/handlers/html.js');
const {AllPackages}=module('mathjax-full/js/input/tex/AllPackages.js');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const mathDocument=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'local'})});
const esc=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const brand='Agentic Tech Review Letters';
const metadataPath=path.join(artifacts,'publication-metadata.json');
const meta=fs.existsSync(metadataPath)?JSON.parse(fs.readFileSync(metadataPath,'utf8')):{};
const date=meta.date||'2026-11-10',evidence=meta.evidence_cutoff||date;
for(const value of [date,evidence]){
 if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value)||new Date(`${value}T00:00:00Z`).toISOString().slice(0,10)!==value)throw Error('Invalid publication/evidence date.');
}
const language=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(language&&!['ko','en'].includes(language))throw Error('--language must be ko or en.');
const baseOption=process.argv.find(a=>a.startsWith('--public-base='));
const publicBase=(baseOption?baseOption.slice('--public-base='.length):(meta.public_base||'https://infant83.io/AI_Tech_Review/reviews/2026-11-10_qunova-hivqe-quantum-chemistry/')).replace(/\/?$/,'/');
if(!/^https:\/\/infant83\.io\/AI_Tech_Review\/reviews\/[a-zA-Z0-9_-]+\/$/.test(publicBase))throw Error('Public base must be this journal’s canonical review URL.');
const stems=['handover_workflow','support_and_energy'];
const figureAssets=new Set(['hero.webp',...stems.flatMap(stem=>[`${stem}.svg`,...['ko','en'].flatMap(lang=>[`${stem}_${lang}.svg`,`${stem}_mobile_${lang}.svg`])])]);
const publicData=new Set(['example-results.json']);
const sha=payload=>crypto.createHash('sha256').update(payload).digest('hex');

function normalizedMath(svg,hash){
 const ids=new Map();
 for(const match of svg.matchAll(/\bid="([^"]+)"/g))if(!ids.has(match[1]))ids.set(match[1],`math-${hash}-g${ids.size}`);
 return svg.replace(/\bid="([^"]+)"/g,(_,id)=>`id="${ids.get(id)}"`)
  .replace(/\b((?:xlink:)?href)="#([^"]+)"/g,(_,attr,id)=>`${attr}="#${ids.get(id)||id}"`)
  .replace(/url\(#([^)]+)\)/g,(_,id)=>`url(#${ids.get(id)||id})`)
  .replace(/\b(aria-labelledby|aria-describedby)="([^"]+)"/g,(_,attr,value)=>`${attr}="${value.split(/\s+/).map(id=>ids.get(id)||id).join(' ')}"`);
}
function renderMath(tex,display){
 const hash=sha((display?'display:':'inline:')+tex).slice(0,14),filename=`math_${hash}.svg`;
 const node=adaptor.outerHTML(mathDocument.convert(tex,{display,em:16,ex:8,containerWidth:760}));
 const svg=node.match(/<svg[\s\S]*<\/svg>/)?.[0];
 if(!svg||/data-mjx-error|merror/.test(svg))throw Error(`Math rendering failed: ${tex}`);
 const clean=normalizedMath(svg.replace(/<title>[\s\S]*?<\/title>/,''),hash).trimEnd()+'\n';
 const width=svg.match(/\bwidth="([\d.]+)ex"/)?.[1]||'1';
 const height=svg.match(/\bheight="([\d.]+)ex"/)?.[1]||'1';
 const valign=svg.match(/vertical-align:\s*([^;" ]+)/)?.[1]||'0';
 return {filename,svg:clean,html:display?`<div class="math-block"><img src="${filename}" alt="${esc(tex)}" style="width:${width}ex;height:auto"></div>`:`<img class="math-inline" src="${filename}" alt="${esc(tex)}" style="width:${width}ex;height:${height}ex;vertical-align:${valign}">`};
}
if(process.argv.includes('--check-math-stability')){
 for(const [tex,display] of [[String.raw`H_S\boldsymbol c=E_S\boldsymbol c`,true],[String.raw`\operatorname{Var}_{\Psi_S}(H)`,false]]){
  const a=renderMath(tex,display);renderMath(String.raw`x=\frac{1}{1+y}`,true);const b=renderMath(tex,display);
  if(a.svg!==b.svg||/\bid="MJX-\d+-/.test(b.svg))throw Error('Math IDs depend on render order.');
 }
 console.log('Deterministic equation SVG check passed.');process.exit(0);
}

const fontFiles=['regular','bold','symbols-regular','symbols-bold','math'].map(label=>`review-${label}.woff2`);
let css=fs.readFileSync(path.join(artifacts,'review.css'),'utf8');
for(const file of fontFiles)css=css.replaceAll(`url('${file}')`,`url('data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,file)).toString('base64')}')`);
const fontLicense=fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','');
css=`/* ${fontLicense} */\n${css}`;
function embeddedFigure(svg){
 if(!/<text\b/.test(svg)||svg.includes('data:font/woff2;base64,'))return svg;
 const rules=[['ReviewFigure','regular',400],['ReviewFigure','bold',700],['ReviewFigureSymbols','symbols-regular',400],['ReviewFigureSymbols','symbols-bold',700],['ReviewFigureMath','math',400]].map(([family,label,weight])=>`@font-face{font-family:${family};font-weight:${weight};src:url(data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,`review-${label}.woff2`)).toString('base64')}) format('woff2')}`).join('');
 // Explicit labels retain their geometry and acquire complete licensed glyph coverage.
 const prepared=svg.replace(/font-family="[^"]*"/g,'font-family="ReviewFigure,ReviewFigureSymbols,ReviewFigureMath,sans-serif"')
  .replace(/font-family:\s*[^;}]+/g,'font-family:ReviewFigure,ReviewFigureSymbols,ReviewFigureMath,sans-serif');
 return prepared.replace(/<svg\b[^>]*>/,tag=>tag+`<style><![CDATA[/* ${fontLicense} */\n${rules}]]></style>`);
}

function referenceNumbers(body){
 const order=[];
 for(const match of body.matchAll(/\[(\d+(?:[–-]\d+)?(?:,\s*\d+(?:[–-]\d+)?)*)\]/g)){
  for(const part of match[1].split(/,\s*/)){
   const values=part.split(/[–-]/).map(Number);
   for(let n=values[0];n<=(values[1]||values[0]);n++)if(!order.includes(n))order.push(n);
  }
 }
 return order;
}
const results=[];
for(const lang of language?[language]:['ko','en']){
 const ko=lang==='ko';
 const source=fs.readFileSync(path.join(root,'reports',`review_${lang}.md`),'utf8');
 if(/\/Users\/|file:\/\/|<script\b|\b(?:api_key|access_token)\s*=/i.test(source))throw Error(`Private path or executable input in ${lang} manuscript.`);
 const title=source.match(/^#\s+(.+)$/m)?.[1]?.trim();if(!title)throw Error(`Missing ${lang} H1.`);
 const afterH1=source.replace(/^#\s+[^\n]+\n+/,'');
 const sourceDekRaw=afterH1.match(/^([^\n]+)\n/)?.[1]?.trim();
 const sourceDek=sourceDekRaw?.replace(/^<p\s+class=["']dek["']>([\s\S]*)<\/p>$/,'$1');
 const dek=meta.deks?.[lang]||sourceDek;
 if(!dek||/^(?:<|#)/.test(dek))throw Error(`Missing plain ${lang} subtitle after H1.`);
 if(meta.deks?.[lang]&&sourceDek!==meta.deks[lang])throw Error(`Metadata and ${lang} manuscript subtitle differ.`);
 const description=meta.descriptions?.[lang]||dek;
 const disclosureMatch=source.match(/^##\s+(?:작성과 검증|Writing and verification|Preparation and verification|How this review was made)\s*\n([\s\S]*)$/im);
 let renderSource=disclosureMatch?source.slice(0,disclosureMatch.index).trimEnd():source.trimEnd();
 renderSource=renderSource.replace(sourceDekRaw,`<p class="dek">${esc(dek)}</p>`);
 const math=[];
 const safe=renderSource.replace(/\$\$([\s\S]*?)\$\$|\\\(([\s\S]*?)\\\)/g,(_,a,b)=>{
  const result=renderMath((a||b).trim(),a!==undefined);math.push(result);
  fs.writeFileSync(path.join(artifacts,result.filename),result.svg);
  return a!==undefined?`\n\nMATHBLOCK${math.length-1}END\n\n`:`MATHINLINE${math.length-1}END`;
 });
 let body=marked.parse(safe,{gfm:true});
 body=body.replace(/\b(src|href)="\.\.\/(?:artifacts|figs)\/([^"/]+)"/g,(_,attr,file)=>{
  if(!(attr==='src'?figureAssets:publicData).has(file))throw Error(`Unapproved ${attr} local asset ${file}`);
  return `${attr}="${file}"`;
 });
 body=body.replace(/<figure\b[\s\S]*?<\/figure>/g,figure=>figure.includes('src="hero.webp"')?figure.replace('<figure>','<figure class="hero">'):figure);
 body=body.replace(/<p>MATHBLOCK(\d+)END<\/p>/g,(_,i)=>math[+i].html).replace(/MATHINLINE(\d+)END/g,(_,i)=>math[+i].html);
 // Corresponding mobile diagrams are used only when an actual asset exists.
 body=body.replace(/<img\b[^>]*src="([^"]+\.svg)"[^>]*>/g,(tag,file)=>{
  const mobile=file.replace(/_(ko|en)\.svg$/,'_mobile_$1.svg');
  if(mobile===file||!figureAssets.has(mobile)||!fs.existsSync(path.join(artifacts,mobile)))return tag;
  return tag.replace('<img ','<img class="figure-desktop" ')+tag.replace(file,mobile).replace('<img ','<img class="figure-mobile" ');
 });
 // Figure captions provide an explicit, discoverable full-size original.
 body=body.replace(/<figure\b[\s\S]*?<\/figure>/g,figure=>{
  if(/class="hero"/.test(figure))return figure;
  const file=figure.match(/<img\b[^>]*src="([^"]+\.svg)"/)?.[1];
  if(!file)return figure;
  const number=figure.match(/<figcaption>\s*(?:그림|Figure)\s+(\d+)\./)?.[1];
  if(!number)throw Error(`Missing numbered caption for ${file}`);
  return figure.replace('</figcaption>',` <a class="figure-larger" href="${file}" target="_blank" rel="noopener" aria-label="${ko?`그림 ${number} 원본 크게 보기 (새 탭)`:`View Figure ${number} larger (opens in a new tab)`}">${ko?'크게 보기':'View larger'}</a></figcaption>`);
 });
 const referenceStart=body.search(/<h2[^>]*>(?:참고문헌|References)<\/h2>/);
 if(referenceStart<0)throw Error(`Missing ${lang} references.`);
 let main=body.slice(0,referenceStart),referenceBody=body.slice(referenceStart);
 const refs=[...referenceBody.matchAll(/<p>\[(\d+)\]\s*([\s\S]*?)<\/p>/g)];
 if(!refs.length||refs.some((r,i)=>Number(r[1])!==i+1))throw Error(`Non-contiguous ${lang} reference list.`);
 const order=referenceNumbers(main);
 if(order.join(',')!==refs.map(r=>r[1]).join(','))throw Error(`Reference first-use order differs from bibliography in ${lang}: ${order}`);
 main=main.replace(/\[(\d+(?:[–-]\d+)?(?:,\s*\d+(?:[–-]\d+)?)*)\]/g,(label,numbers)=>`<a class="citation" role="doc-biblioref" href="#ref-${numbers.match(/^\d+/)[0]}">${label}</a>`);
 const list=refs.map(r=>`<li id="ref-${r[1]}"><span class="reference-number">[${r[1]}]</span><span class="reference-text">${r[2]}</span></li>`).join('\n');
 referenceBody=referenceBody.replace(/(<h2[^>]*>[^<]*<\/h2>)[\s\S]*/,`$1<div class="references"><ol class="reference-list" role="list">${list}</ol></div>`);
 body=main+referenceBody;
 const toc=[];let section=0;
 body=body.replace(/<h2(?:\s[^>]*)?>([\s\S]*?)<\/h2>/g,(_,text)=>{const id=`section-${++section}`;toc.push(`<li><a href="#${id}">${text}</a></li>`);return `<h2 id="${id}">${text}</h2>`});
 body=body.replaceAll('<table>',`<div class="table-scroll" role="region" tabindex="0" aria-label="${ko?'비교 표':'Comparison table'}"><table>`).replaceAll('</table>','</table></div>');
 const byline=`<p class="byline-disclosure">${ko?'책임 편집: 김현중 · AI 보조 작성: Codex':'Responsible editor: Hyun-Jung Kim · AI assistance: Codex'} · ${date} · ${ko?'근거 기준일':'Evidence cutoff'} ${evidence} · <a href="#authoring-disclosure">${ko?'작성·검증 정보':'Production and verification'}</a></p>`;
 body=body.replace(/(<p class="dek">[\s\S]*?<\/p>)/,'$1'+byline);
 const tocHTML=`<details class="toc"><summary>${ko?'내용 살펴보기':'Contents'}</summary><ol>${toc.join('')}</ol></details>`;
 const heroEnd=body.indexOf('</figure>');
 if(heroEnd>=0)body=body.slice(0,heroEnd+9)+tocHTML+body.slice(heroEnd+9);else body=body.replace(byline,byline+tocHTML);
 const disclosureContent=meta.disclosure?.[lang]||disclosureMatch?.[1];
 if(!disclosureContent)throw Error(`Missing production disclosure for ${lang}.`);
 const disclosure=`<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">${ko?'작성·검증 정보':'How this review was made'}</h2>${marked.parse(disclosureContent,{gfm:true})}</section><!-- End AI Tech Review Authoring Disclosure -->`;
 const url=publicBase+(ko?'':'en/'),other=publicBase+(ko?'en/':'');
 const head=`<link rel="canonical" href="${url}"><link rel="alternate" hreflang="ko" href="${publicBase}"><link rel="alternate" hreflang="en" href="${publicBase}en/"><link rel="alternate" hreflang="x-default" href="${publicBase}"><meta property="og:url" content="${url}"><meta property="og:image" content="${publicBase}hero.webp"><meta property="article:published_time" content="${date}"><meta name="evidence-cutoff" content="${evidence}">`;
 const theme=`<script>(()=>{try{const t=localStorage.getItem('atr.reader.theme.v1');document.documentElement.dataset.theme=t==='dark'?'dark':'light'}catch{}})();</script>`;
 const html=`<!doctype html>\n<html lang="${lang}" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><meta name="description" content="${esc(description)}"><meta name="author" content="${ko?'김현중':'Hyun-Jung Kim'}"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(description)}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">${head}${theme}<link rel="stylesheet" href="review.css"></head><body>\n<header><a class="brand" href="https://infant83.io/AI_Tech_Review/">${brand.toUpperCase()}</a><div class="topline-actions"><a class="hub-link" href="https://infant83.github.io/AI_Tech_Review/">${ko?'리뷰 허브':'Review hub'}</a><nav class="language-switcher" aria-label="${ko?'언어 선택':'Language'}"><span aria-current="page" class="language-current" lang="${lang}">${ko?'한국어':'English'}</span><a href="${other}" lang="${ko?'en':'ko'}" hreflang="${ko?'en':'ko'}">${ko?'English':'한국어'}</a></nav><a class="download" href="review_${lang}.pdf">PDF ↓</a></div></header>\n<main class="paper"><div class="issue-meta"><span>RESEARCH LETTER</span><span>${date.replaceAll('-','.')}</span><span>${ko?'양자화학 · 샘플링 · 계산 비용':'QUANTUM CHEMISTRY · SAMPLING · COMPUTATIONAL COST'}</span></div><article>${body}${disclosure}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">${brand} · ${date}</footer></main></body></html>\n`;
 const dir=path.join(root,'dist',ko?'':'en');fs.mkdirSync(dir,{recursive:true});
 const used=new Set(math.map(x=>x.filename));
 for(const match of html.matchAll(/\bsrc="([^"#]+)"/g)){
  const file=match[1];if(/^(?:https?:|data:|\/)/.test(file))throw Error(`Figures must use approved local assets: ${file}`);
  if(!figureAssets.has(file)&&!/^math_[0-9a-f]{14}\.svg$/.test(file))throw Error(`Unapproved image: ${file}`);used.add(file);
 }
 for(const file of publicData)if(html.includes(`href="${file}"`))used.add(file);
 for(const file of used){
  if(path.basename(file)!==file)throw Error(`Nested public asset path: ${file}`);
  const sourceFile=path.join(artifacts,file);if(!fs.existsSync(sourceFile))throw Error(`Missing approved asset: ${file}`);
  if(file.endsWith('.svg')&&!file.startsWith('math_'))fs.writeFileSync(path.join(dir,file),embeddedFigure(fs.readFileSync(sourceFile,'utf8')));else fs.copyFileSync(sourceFile,path.join(dir,file));
 }
 fs.writeFileSync(path.join(dir,'index.html'),html.split('\n').map(line=>line.trimEnd()).join('\n'));
 fs.writeFileSync(path.join(dir,'review.css'),css);
 for(const file of fs.readdirSync(dir))if(fs.statSync(path.join(dir,file)).isFile()&&!used.has(file)&&!['index.html','review.css',`review_${lang}.pdf`].includes(file))fs.unlinkSync(path.join(dir,file));
 results.push({language:lang,title,date,evidence_cutoff:evidence,sections:section,references:refs.length,equations:math.length,figures:(html.match(/<figure\b/g)||[]).length,assets:[...used].sort(),html_sha256:sha(html),css_sha256:sha(css)});
}
for(const result of results)console.log(JSON.stringify(result));
