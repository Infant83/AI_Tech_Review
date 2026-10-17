/** Build a self-contained bilingual research letter; no public deployment. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifacts=path.join(root,'artifacts');
const dependencyRoots=[process.env.NOETHER_NODE_MODULES,process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,path.join(root,'node_modules'),path.join(process.cwd(),'node_modules')].filter(Boolean);
const localRequire=createRequire(import.meta.url);
function resolveDependency(spec){
  for(const directory of dependencyRoots){try{return createRequire(path.join(directory,'_build.cjs')).resolve(spec)}catch{}}
  try{return localRequire.resolve(spec)}catch{throw Error(`Missing ${spec}. Set NOETHER_NODE_MODULES and/or CODEX_PRIMARY_RUNTIME_NODE_MODULES to an installed dependency directory.`)}
}
const {marked}=await import(pathToFileURL(resolveDependency('marked')));
const requireModule=spec=>localRequire(resolveDependency(spec));
const {mathjax}=requireModule('mathjax-full/js/mathjax.js');
const {TeX}=requireModule('mathjax-full/js/input/tex.js');
const {SVG}=requireModule('mathjax-full/js/output/svg.js');
const {liteAdaptor}=requireModule('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=requireModule('mathjax-full/js/handlers/html.js');
const {AllPackages}=requireModule('mathjax-full/js/input/tex/AllPackages.js');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const mathDocument=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'local'})});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const cutoff='2026-10-17';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBase=process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')?.replace(/\/?$/,'/')||'';
const descriptors={ko:'노터 정리의 변분 원리와 연속대칭, 국소 게이지 대칭의 차이부터 구조 보존 계산과 과학기계학습의 응용까지.',en:'Variational principles, continuous symmetry, gauge identities, structure-preserving computation and scientific machine learning through Noether’s theorems.'};
const titles={ko:'대칭에서 보존법칙으로: 노터 정리와 과학 계산의 설계 원리',en:'From Symmetry to Conservation: Noether’s Theorems in Scientific Computing'};
const outputFiles=[];
// Embed openly licensed subsets so the public stylesheet has no sibling-font dependency.
let stylesheet=fs.readFileSync(path.join(artifacts,'review.css'),'utf8');
for(const weight of ['regular','bold']){
 const file=`review-${weight}.woff2`;
 const encoded=fs.readFileSync(path.join(artifacts,file)).toString('base64');
 stylesheet=stylesheet.replaceAll(`url('${file}')`,`url('data:font/woff2;base64,${encoded}')`);
}
stylesheet='/* '+fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','')+' */\n'+stylesheet;

function disclosure(ko){
 const rows=ko?[
  ['책임 편집자','김현중'],['AI 보조','OpenAI Codex · 정확한 작성 모델 식별자: 미보존'],
  ['에이전트와 역할','root: 자료 종합·한국어 작성·편집·설명 그림·계산 예제; academic_sources: 원 논문·수식·학술적 한계 확인; applications_sources: 계산·과학기계학습 응용과 1차 출처 조사·영어 번역; review_format: 저장소 형식 감사·한영 조판·HTML/PDF 생성과 출력 검사'],
  ['입력과 산출물','공유 LinkedIn 링크, 공개 논문·공식 자료 → 한영 기술 리뷰, 개념 표지, 설명용 도표·수식 및 PDF'],
  ['제작 요청 요약','공유 기사에서 출발해 노터 정리의 물리·수학적 의미를 설명하고, 관련 학술 연구와 계산·과학 AI의 응용을 1차 출처로 보강한 기술 리뷰 작성.'],
  ['하네스','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>'],
  ['검증 범위','공개 1차 출처·서지·핵심 수식과 해석의 범위, 한영 수치·기호, 로컬 자산·표·수식·페이지 출력 검사. 독립 실험 재현은 수행하지 않았다.'],
  ['사람 검토 수준','주제·작성·공개 게시 요청 확인; 문장 단위 사람 승인 없음.'],['근거 기준일',cutoff]
 ]:[
  ['Responsible editor','Hyun-Jung Kim'],['AI assistance','OpenAI Codex; exact authoring-model identifier not retained.'],
  ['Agents and roles','root: synthesis, Korean writing, editing, explanatory figures and numerical examples; academic_sources: original papers, formulas and scholarly limitations; applications_sources: computational/scientific-ML applications, primary-source research and English translation; review_format: repository-format audit, bilingual typesetting, HTML/PDF generation and output checks.'],
  ['Inputs and outputs','Shared LinkedIn link and public papers/documentation → bilingual review, conceptual cover, explanatory figures/equations and PDFs.'],
  ['Production request','Use the shared article to explain the physical and mathematical meaning of Noether’s theorems, and develop a technical review covering related scholarship and scientific-computing/AI applications using primary sources.'],
  ['Harness','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>'],
  ['Verification scope','Public primary sources, bibliographic records, central formulas and interpretation boundaries; bilingual values/symbols, local assets, tables, equations and page output. No independent experimental reproduction.'],
  ['Human review','Topic, writing and public posting explicitly requested; no line-by-line human approval.'],['Evidence cutoff',cutoff]
 ];
 return `<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">${ko?'작성·검증 정보':'How this review was made'}</h2><dl>${rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl><p>${ko?'원문의 보고 결과, 리뷰의 설명용 재구성과 후속 응용 제안을 구분한다. 표지는 AI로 만든 개념 그림이며 실험 영상이나 계산 데이터가 아니다.':'Reported results, teaching reconstructions and proposed applications are distinguished. The AI-generated cover is conceptual and contains no experimental image or numerical evidence.'}</p></section><!-- End AI Tech Review Authoring Disclosure -->`;
}

function mathImage(tex,display){
 const id=crypto.createHash('sha256').update((display?'display:':'inline:')+tex).digest('hex').slice(0,14);
 const filename=`math_${id}.svg`;
 const rendered=adaptor.outerHTML(mathDocument.convert(tex,{display,em:16,ex:8,containerWidth:760}));
 const svg=rendered.match(/<svg[\s\S]*<\/svg>/)?.[0];
 if(!svg||/data-mjx-error|merror/.test(svg))throw Error(`Math typesetting failed: ${tex}`);
 const clean=svg.replace(/<title>[\s\S]*?<\/title>/,'');
 fs.writeFileSync(path.join(artifacts,filename),clean);
 const width=svg.match(/\bwidth="([\d.]+)ex"/)?.[1]||'1';
 const height=svg.match(/\bheight="([\d.]+)ex"/)?.[1]||'1';
 const valign=svg.match(/vertical-align:\s*([^;" ]+)/)?.[1]||'0';
 return {filename,html:display?`<div class="math-block"><img src="${filename}" alt="${esc(tex)}" style="width:${width}ex;height:auto"></div>`:`<img class="math-inline" src="${filename}" alt="${esc(tex)}" style="width:${width}ex;height:${height}ex;vertical-align:${valign}">`};
}

for(const lang of onlyLanguage?[onlyLanguage]:['ko','en']){
 const ko=lang==='ko';
 const source=fs.readFileSync(path.join(root,'reports',`review_${lang}.md`),'utf8');
 const title=source.match(/^#\s+(.+)$/m)?.[1]?.trim()||titles[lang];
 const math=[];
 const safe=source.replace(/\$\$([\s\S]*?)\$\$|\\\(([\s\S]*?)\\\)/g,(_,a,b)=>{
  const result=mathImage((a||b).trim(),a!==undefined);math.push(result);
  return a!==undefined?`\n\nMATHBLOCK${math.length-1}END\n\n`:`MATHINLINE${math.length-1}END`;
 });
 let body=marked.parse(safe,{gfm:true});
 if(publicBase){
  const links={'en/index.html':publicBase+'en/','en/review_en.pdf':publicBase+'en/review_en.pdf','../index.html':publicBase,'../review_ko.pdf':publicBase+'review_ko.pdf'};
  body=body.replace(/href="([^"]+)"/g,(match,href)=>links[href]?`href="${links[href]}"`:match);
 }
 body=body.replace(/<p>MATHBLOCK(\d+)END<\/p>/g,(_,i)=>math[+i].html).replace(/MATHINLINE(\d+)END/g,(_,i)=>math[+i].html);
 let count=0;const toc=[];
 body=body.replace(/<h2(?:\s[^>]*)?>(.*?)<\/h2>/g,(_,text)=>{const id=`section-${++count}`;toc.push(`<li><a href="#${id}">${text}</a></li>`);return `<h2 id="${id}">${text}</h2>`});
 body=body.replaceAll('<table>',`<div class="table-scroll" role="region" tabindex="0" aria-label="${ko?'비교와 응용 표':'Comparison and applications table'}"><table>`).replaceAll('</table>','</table></div>');
 const editor=`<div class="editor-line">${ko?'책임 편집: 김현중 · AI 보조 작성: Codex · 근거 기준일: 2026년 10월 17일':'Responsible editor: Hyun-Jung Kim · AI assistance: Codex · Evidence cutoff: 17 October 2026'} · <a href="#authoring-disclosure">${ko?'작성·검증 범위':'Production and verification'}</a></div>`;
 const heroEnd=body.indexOf('</figure>');
 const tocHTML=`<details class="toc"><summary>${ko?'내용 살펴보기':'Contents'}</summary><ol>${toc.join('')}</ol></details>`;
 if(heroEnd>=0){
  const heroStart=body.lastIndexOf('<figure',heroEnd);
  body=body.slice(0,heroStart)+editor+body.slice(heroStart,heroEnd+9)+tocHTML+body.slice(heroEnd+9);
 }else{body=body.replace(/<\/h1>/,'</h1>'+editor+tocHTML)}
 body=body.replace(/(<h2[^>]*>(?:참고문헌[^<]*|References[^<]*)<\/h2>)([\s\S]*?)(?=<h2|$)/,(_,heading,content)=>heading+`<div class="references">${content}</div>`);
 const dir=path.join(root,'dist',ko?'':'en');fs.mkdirSync(dir,{recursive:true});
 const other=publicBase?publicBase+(ko?'en/':''):(ko?'en/index.html':'../index.html');
 const url=publicBase?publicBase+(ko?'':'en/'):'';
 const metadata=publicBase?`<link rel="canonical" href="${esc(url)}"><link rel="alternate" hreflang="ko" href="${esc(publicBase)}"><link rel="alternate" hreflang="en" href="${esc(publicBase)}en/"><link rel="alternate" hreflang="x-default" href="${esc(publicBase)}"><meta property="og:url" content="${esc(url)}"><meta property="og:image" content="${esc(publicBase)}hero.webp">`:'';
 const localBadge=publicBase?'':`<span class="local-status">${ko?'로컬 검토본':'Local review copy'}</span>`;
 const html=`<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><meta name="description" content="${esc(descriptors[lang])}"><meta name="author" content="${ko?'김현중':'Hyun-Jung Kim'}"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(descriptors[lang])}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">${metadata}<link rel="stylesheet" href="review.css"></head><body>
<header><a class="brand" href="https://infant83.github.io/AI_Tech_Review/">AI TECH REVIEW LETTERS</a><div class="topline-actions">${localBadge}<nav class="language-switcher" aria-label="${ko?'언어 선택':'Language'}"><span class="language-current" aria-current="page" lang="${lang}">${ko?'한국어':'English'}</span><a href="${other}" lang="${ko?'en':'ko'}" hreflang="${ko?'en':'ko'}">${ko?'English':'한국어'}</a></nav><a class="download" href="review_${lang}.pdf">PDF ↓</a></div></header>
<main class="paper"><div class="issue-meta"><span>RESEARCH LETTER</span><span>2026.10.17</span><span>${ko?'물리학 · 과학 계산 · 과학기계학습':'PHYSICS · SCIENTIFIC COMPUTING · SCIENTIFIC ML'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">AI Tech Review Letters · ${cutoff}<br>${ko?'연속대칭, 보존량과 계산의 구조를 연결하는 해설.':'An explainer connecting continuous symmetry, conservation and computational structure.'}</footer></main></body></html>\n`;
 fs.writeFileSync(path.join(dir,'index.html'),html);
 fs.writeFileSync(path.join(dir,'review.css'),stylesheet);
 const assetNames=new Set(['review-regular.woff2','review-bold.woff2','font-license.txt',...math.map(x=>x.filename)]);
 for(const match of html.matchAll(/\bsrc="([^"#]+)"/g)){
  if(!/^(?:https?:|data:|\/)/.test(match[1]))assetNames.add(match[1]);
 }
 for(const filename of assetNames){
  if(path.basename(filename)!==filename)throw Error(`Only flat local assets are allowed: ${filename}`);
  const asset=path.join(artifacts,filename);if(!fs.existsSync(asset))throw Error(`Missing asset: ${filename}`);
  fs.copyFileSync(asset,path.join(dir,filename));
 }
 for(const filename of fs.readdirSync(dir)){
  if(/^math_[0-9a-f]+\.svg$/.test(filename)&&!assetNames.has(filename))fs.unlinkSync(path.join(dir,filename));
 }
 outputFiles.push({language:lang,sections:count,equations:math.length,assets:assetNames.size,file:path.relative(root,path.join(dir,'index.html'))});
}
for(const result of outputFiles)console.log(JSON.stringify(result));
