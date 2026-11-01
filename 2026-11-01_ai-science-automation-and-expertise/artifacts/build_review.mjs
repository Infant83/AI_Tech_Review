/** Build a bilingual, self-contained public review with a strict asset allowlist. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifacts=path.join(root,'artifacts');
const dependencyRoots=[process.env.REVIEW_NODE_MODULES,process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,path.join(root,'tmp','deps','node_modules'),path.join(root,'node_modules'),path.join(process.cwd(),'node_modules')].filter(Boolean);
const localRequire=createRequire(import.meta.url);
function resolveDependency(spec){
  for(const directory of dependencyRoots){try{return createRequire(path.join(directory,'_build.cjs')).resolve(spec)}catch{}}
  try{return localRequire.resolve(spec)}catch{throw Error(`Missing ${spec}. Set REVIEW_NODE_MODULES and/or CODEX_PRIMARY_RUNTIME_NODE_MODULES to an installed dependency directory.`)}
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
const cutoff='2026-11-01';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBase=(process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')||'https://infant83.io/AI_Tech_Review/reviews/2026-11-01_ai-science-automation-and-expertise/').replace(/\/?$/,'/');
const descriptors={ko:'양자와 재료 연구의 AI 자동화 사례, 공개 계산 자료와 심사 대조군을 따라 과학적 판단과 전문성의 역할을 검토한다.',en:'AI automation in quantum and materials research, public computational records, and review controls illuminate the role of scientific judgment and expertise.'};
const titles={ko:'양자와 재료 연구의 AI 자동화와 과학적 판단',en:'AI Automation and Scientific Judgment in Quantum and Materials Research'};
// Optional stems are permitted, but only explicitly referenced assets are copied.
const figureStems=['h2_energy','density_gap','referee_controls'];
const outputFiles=[];
// This check needs no manuscripts/fonts and creates no artifact files.
if(process.argv.includes('--check-math-stability')){
 const examples=[['x^2+y^2=1',true],[String.raw`\sum_{n=1}^{N}p_n=1`,true],[String.raw`\boldsymbol\theta`,false]];
 for(const [tex,display] of examples){
  const before=renderMath(tex,display);
  renderMath(String.raw`z=\frac{1}{1+x}`,false);
  const after=renderMath(tex,display);
  if(before.svg!==after.svg)throw Error(`Equation IDs depend on rendering order: ${tex}`);
  if(/\bid="MJX-\d+-/.test(after.svg))throw Error('Unnormalized MathJax global ID.');
 }
 console.log('Equation SVG bytes are stable when unrelated formulas are inserted.');
 process.exit(0);
}
// Embed openly licensed subsets so the public stylesheet has no sibling-font dependency.
let stylesheet=fs.readFileSync(path.join(artifacts,'review.css'),'utf8');
for(const weight of ['regular','bold','symbols-regular','symbols-bold','math']){
 const file=`review-${weight}.woff2`;
 const encoded=fs.readFileSync(path.join(artifacts,file)).toString('base64');
 stylesheet=stylesheet.replaceAll(`url('${file}')`,`url('data:font/woff2;base64,${encoded}')`);
}
stylesheet='/* '+fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','')+' */\n'+stylesheet;

function disclosure(ko){
 const rows=ko?[
  ['책임 편집자','김현중'],
  ["AI 시스템", "OpenAI Codex; 정확한 작성 모델 식별자 미보존."],
  ['확인 가능한 에이전트 역할','root: 한국어 집필·표지 기획·편집과 게시 통합; cuantico_source: El Agente Cuántico·AutoMat와 공개 데이터 대조·과학 감수; dqb_fermiscope: FermiScope·INCAR와 재료 계산 조건 대조·과학 감수; journal_dataset: JCCM 공개 집계·대조군·인간–AI 협력 문헌 대조와 영어 전문 번역; agent_standards: 공개 보고값 재도표·교육 모형 도식·수식·글꼴·HTML/PDF 제작과 출력 검사.'],
  ['편집 하네스','<a href="https://infant83.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a> · 과학 설명과 시각 전달 준칙 1.0 · APS 번호식 인용'],
  ["검증 범위", "El Agente Cuántico의 기술 근거는 2026-11-01에 확인한 arXiv v3 PDF이며, 관측량·초기분포 사례는 논문 보고를 대조했다. 공개 논문·공식 코드·데이터·서지를 읽고 주장과 조건, 판본을 확인했다. 그림 1·3은 Borealis V6의 H₂ 19점과 JCCM 집계의 재도식이며, 그림 2는 리뷰의 고정 직교 기저 교육 모형이다. 이번 리뷰에서 실행한 계산은 교육 모형과 별도 Pauli 검사 입력의 2×2 행렬 기대값 검산이다. 연구실 적용절은 V&V·DFT 참조 자료·PPI·능동 통계 추론을 바탕으로 한 검증 설계 제안이다. 한영 본문·그림·인용·HTML/PDF·모바일 출력을 대조했다."],
  ["사람 검토 기록", "편집자의 주제·논의 방향과 구체적 문체 교정 지적을 반영했다. 전체 원고의 과학·문맥·한영 감수는 AI 에이전트가 수행했다. 문장 단위 사람 승인·독자 이해도 평가는 수행하지 않았다."],
  ['근거 기준일',cutoff]
 ]:[
  ['Responsible editor','Hyun-Jung Kim'],
  ["AI system", "OpenAI Codex; exact authoring-model identifier not retained."],
  ['Verifiable agent roles','root: Korean writing, conceptual-cover planning, editorial and publication integration; cuantico_source: El Agente Cuántico, AutoMat, public-data crosschecks and scientific audit; dqb_fermiscope: FermiScope, INCAR and materials-calculation conditions, scientific audit; journal_dataset: JCCM aggregates and controls, human–AI collaboration literature and full English translation; agent_standards: reported-data redrawing, teaching-model diagrams, equation/font typesetting, HTML/PDF production and output checks.'],
  ['Editorial harness','<a href="https://infant83.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>; Scientific Explanation and Visual Communication Principles 1.0; APS numbered references.'],
  ["Verification scope", "Technical claims about El Agente Cuántico use the arXiv v3 PDF checked on 2026-11-01; observable and initial-distribution cases are attributed to the paper. Papers, official code, data and bibliographic records were checked for claims, conditions and versions. Figures 1 and 3 redraw the 19 Borealis V6 hydrogen results and JCCM aggregates; Figure 2 is the review’s fixed-orthonormal-basis teaching model. Computation performed for this review comprised the teaching-model check and two-by-two-matrix expectation values for the separate Pauli input. The laboratory section proposes verification designs using V&V, DFT references, PPI and active statistical inference. Bilingual prose, figures, citations, HTML/PDF and mobile output were checked."],
  ["Human review record", "Editorial direction and specific prose corrections were incorporated. Whole-manuscript scientific, contextual and bilingual reviews were performed by AI agents. No line-by-line human approval or reader-comprehension study was performed."],
  ['Evidence cutoff',cutoff]
 ];
 return `<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">${ko?'작성·검증 정보':'How this review was made'}</h2><dl>${rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl><p>${ko?'표지는 AI로 생성한 개념 일러스트이며, 본문 그림은 공개 보고값의 재도식과 리뷰의 교육 모형으로 제작했다.':'The cover is an AI-generated conceptual illustration. Article figures redraw public reported values or present the review’s teaching model.'}</p></section><!-- End AI Tech Review Authoring Disclosure -->`;
}

function embedFigureFonts(svg){
 const rules=['regular','bold'].flatMap(weight=>[['ReviewFigure',`review-${weight}.woff2`],['ReviewFigureSymbols',`review-symbols-${weight}.woff2`]].map(([family,file])=>`@font-face{font-family:${family};src:url(data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,file)).toString('base64')}) format('woff2');font-weight:${weight==='regular'?400:700}}`)).join('');
 const license=fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','');
 return svg.replace('font-family:ReviewFigure,','font-family:ReviewFigure,ReviewFigureSymbols,').replace(/<svg\b[^>]*>/,tag=>tag+`<style><![CDATA[/* ${license} */\n${rules}]]></style>`);
}

function normalizeEquationIds(svg,hash){
 const replacements=new Map();
 for(const match of svg.matchAll(/\bid="([^"]+)"/g)){
  if(!replacements.has(match[1]))replacements.set(match[1],`math-${hash}-g${replacements.size}`);
 }
 return svg
  .replace(/\bid="([^"]+)"/g,(_,id)=>`id="${replacements.get(id)}"`)
  .replace(/\b((?:xlink:)?href)="#([^"]+)"/g,(_,attribute,id)=>`${attribute}="#${replacements.get(id)||id}"`)
  .replace(/url\(#([^)]+)\)/g,(_,id)=>`url(#${replacements.get(id)||id})`)
  .replace(/\b(aria-labelledby|aria-describedby)="([^"]+)"/g,(_,attribute,ids)=>`${attribute}="${ids.split(/\s+/).map(id=>replacements.get(id)||id).join(' ')}"`);
}

function renderMath(tex,display){
 const id=crypto.createHash('sha256').update((display?'display:':'inline:')+tex).digest('hex').slice(0,14);
 const filename=`math_${id}.svg`;
 const rendered=adaptor.outerHTML(mathDocument.convert(tex,{display,em:16,ex:8,containerWidth:760}));
 const svg=rendered.match(/<svg[\s\S]*<\/svg>/)?.[0];
 if(!svg||/data-mjx-error|merror/.test(svg))throw Error(`Math typesetting failed: ${tex}`);
 const clean=normalizeEquationIds(svg.replace(/<title>[\s\S]*?<\/title>/,''),id).trimEnd()+'\n';
 const width=svg.match(/\bwidth="([\d.]+)ex"/)?.[1]||'1';
 const height=svg.match(/\bheight="([\d.]+)ex"/)?.[1]||'1';
 const valign=svg.match(/vertical-align:\s*([^;" ]+)/)?.[1]||'0';
 return {filename,svg:clean,html:display?`<div class="math-block"><img src="${filename}" alt="${esc(tex)}" style="width:${width}ex;height:auto"></div>`:`<img class="math-inline" src="${filename}" alt="${esc(tex)}" style="width:${width}ex;height:${height}ex;vertical-align:${valign}">`};
}

function mathImage(tex,display){
 const result=renderMath(tex,display);
 const target=path.join(artifacts,result.filename);
 if(!fs.existsSync(target)||fs.readFileSync(target,'utf8')!==result.svg)fs.writeFileSync(target,result.svg);
 return result;
}

for(const lang of onlyLanguage?[onlyLanguage]:['ko','en']){
 const ko=lang==='ko';
 const source=fs.readFileSync(path.join(root,'reports',`review_${lang}.md`),'utf8');
 const title=source.match(/^#\s+(.+)$/m)?.[1]?.trim()||titles[lang];
 const description=(source.match(/<p class=["']dek["']>([\s\S]*?)<\/p>/)?.[1]||descriptors[lang]).replace(/<[^>]*>/g,'').trim();
 const math=[];
 const safe=source.replace(/\$\$([\s\S]*?)\$\$|\\\(([\s\S]*?)\\\)/g,(_,a,b)=>{
  const result=mathImage((a||b).trim(),a!==undefined);math.push(result);
  return a!==undefined?`\n\nMATHBLOCK${math.length-1}END\n\n`:`MATHINLINE${math.length-1}END`;
 });
 let body=marked.parse(safe,{gfm:true});
 body=body.replace(/(?<=>)([^<]+)(?=<)/g,(_,text)=>text.replace(/\*\*([^*\n]+\))\*\*(?=[가-힣])/g,'<strong>$1</strong>'));
 if(publicBase){
  const links={'en/index.html':publicBase+'en/','en/review_en.pdf':publicBase+'en/review_en.pdf','../index.html':publicBase,'../review_ko.pdf':publicBase+'review_ko.pdf'};
  body=body.replace(/href="([^"]+)"/g,(match,href)=>links[href]?`href="${links[href]}"`:match);
 }
 body=body.replace(/<p>MATHBLOCK(\d+)END<\/p>/g,(_,i)=>math[+i].html).replace(/MATHINLINE(\d+)END/g,(_,i)=>math[+i].html);
 if(figureStems.length){
  const figurePattern=new RegExp('<img\\b[^>]*\\bsrc="(('+figureStems.join('|')+')_(?:ko|en)\\.svg)"[^>]*>','g');
  body=body.replace(figurePattern,(tag,filename)=>{
   const mobile=filename.replace(/_(ko|en)\.svg$/,'_mobile_$1.svg');
   return tag.replace('<img ','<img class="figure-desktop" ')+tag.replace(filename,mobile).replace('<img ','<img class="figure-mobile" ');
  });
 }
 let count=0;const toc=[];
 body=body.replace(/<h2(?:\s[^>]*)?>(.*?)<\/h2>/g,(_,text)=>{const id=`section-${++count}`;toc.push(`<li><a href="#${id}">${text}</a></li>`);return `<h2 id="${id}">${text}</h2>`});
 body=body.replaceAll('<table>',`<div class="table-scroll" role="region" tabindex="0" aria-label="${ko?'비교와 응용 표':'Comparison and applications table'}"><table>`).replaceAll('</table>','</table></div>');
 const editor=`<p class="byline-disclosure">${ko?'책임 편집: 김현중 · AI 보조 작성: Codex · 근거 기준일: 2026년 11월 1일':'Responsible editor: Hyun-Jung Kim · AI assistance: Codex · Evidence cutoff: 1 November 2026'} · <a href="#authoring-disclosure">${ko?'작성·검증 범위':'Production and verification'}</a></p>`;
 const heroEnd=body.indexOf('</figure>');
 const tocHTML=`<details class="toc"><summary>${ko?'내용 살펴보기':'Contents'}</summary><ol>${toc.join('')}</ol></details>`;
 if(heroEnd>=0){
  const heroStart=body.lastIndexOf('<figure',heroEnd);
  body=body.slice(0,heroStart)+editor+body.slice(heroStart,heroEnd+9)+tocHTML+body.slice(heroEnd+9);
 }else{body=body.replace(/<\/h1>/,'</h1>'+editor+tocHTML)}
 const referenceStart=body.search(/<h2[^>]*>(?:참고문헌[^<]*|References[^<]*)<\/h2>/);
 if(referenceStart>=0){
  const main=body.slice(0,referenceStart).replace(/\[(\d+(?:[–-]\d+)?(?:,\s*\d+(?:[–-]\d+)?)*)\]/g,(label,numbers)=>{
   const first=numbers.match(/^\d+/)[0];
   const href=publicBase?publicBase+(ko?'':'en/')+`#ref-${first}`:`#ref-${first}`;
   return `<a class="citation" role="doc-biblioref" href="${esc(href)}">${label}</a>`;
  });
  body=main+body.slice(referenceStart);
 }
 body=body.replace(/(<h2[^>]*>(?:참고문헌[^<]*|References[^<]*)<\/h2>)([\s\S]*?)(?=<h2|$)/,(_,heading,content)=>{
  let reference=0;
  const list=content.replace('<ol>','<ol class="reference-list" role="list">').replace(/<li>([\s\S]*?)<\/li>/g,(_,entry)=>{
   const number=++reference;
   return `<li id="ref-${number}"><span class="reference-number">[${number}]</span><span class="reference-text">${entry}</span></li>`;
  });
  return heading+`<div class="references">${list}</div>`;
 });
 const dir=path.join(root,'dist',ko?'':'en');fs.mkdirSync(dir,{recursive:true});
 const other=publicBase?publicBase+(ko?'en/':''):(ko?'en/index.html':'../index.html');
 const url=publicBase?publicBase+(ko?'':'en/'):'';
 const metadata=publicBase?`<link rel="canonical" href="${esc(url)}"><link rel="alternate" hreflang="ko" href="${esc(publicBase)}"><link rel="alternate" hreflang="en" href="${esc(publicBase)}en/"><link rel="alternate" hreflang="x-default" href="${esc(publicBase)}"><meta property="og:url" content="${esc(url)}"><meta property="og:image" content="${esc(publicBase)}hero.webp">`:'';
 const localBadge=publicBase?'':`<span class="local-status">${ko?'로컬 검토본':'Local review copy'}</span>`;
 const html=`<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><meta name="description" content="${esc(description)}"><meta name="author" content="${ko?'김현중':'Hyun-Jung Kim'}"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(description)}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">${metadata}<link rel="stylesheet" href="review.css"></head><body>
<header><a class="brand" href="https://infant83.io/AI_Tech_Review/">AI TECH REVIEW LETTERS</a><div class="topline-actions">${localBadge}<nav class="language-switcher" aria-label="${ko?'언어 선택':'Language'}"><span class="language-current" aria-current="page" lang="${lang}">${ko?'한국어':'English'}</span><a href="${other}" lang="${ko?'en':'ko'}" hreflang="${ko?'en':'ko'}">${ko?'English':'한국어'}</a></nav><a class="download" href="review_${lang}.pdf">PDF ↓</a></div></header>
<main class="paper"><div class="issue-meta"><span>RESEARCH LETTER</span><span>2026.11.01</span><span>${ko?'양자·재료 연구 · AI 자동화 · 과학적 판단':'QUANTUM AND MATERIALS RESEARCH · AI AND SCIENTIFIC JUDGMENT'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">AI Tech Review Letters · ${cutoff}<br>${ko?'연구의 자동화와 과학적 판단을 잇는 해설.':'Research automation and scientific judgment.'}</footer></main></body></html>\n`;
 fs.writeFileSync(path.join(dir,'index.html'),html.split('\n').map(line=>line.trimEnd()).join('\n'));
 fs.writeFileSync(path.join(dir,'review.css'),stylesheet);
 const allowedFigures=new Set(['hero.webp',...figureStems.flatMap(stem=>[`${stem}_${lang}.svg`,`${stem}_mobile_${lang}.svg`])]);
 const assetNames=new Set(math.map(x=>x.filename));
 for(const match of html.matchAll(/\bsrc="([^"#]+)"/g)){
  if(!/^(?:https?:|data:|\/)/.test(match[1])){
   if(!allowedFigures.has(match[1])&&!/^math_[0-9a-f]+\.svg$/.test(match[1]))throw Error(`Asset is outside the explicit figure allowlist: ${match[1]}`);
   assetNames.add(match[1]);
  }
 }
 for(const filename of assetNames){
  if(path.basename(filename)!==filename)throw Error(`Only flat local assets are allowed: ${filename}`);
  const asset=path.join(artifacts,filename);if(!fs.existsSync(asset))throw Error(`Missing asset: ${filename}`);
  if(filename.endsWith('.svg')&&!filename.startsWith('math_'))fs.writeFileSync(path.join(dir,filename),embedFigureFonts(fs.readFileSync(asset,'utf8')));else fs.copyFileSync(asset,path.join(dir,filename));
 }
 for(const filename of fs.readdirSync(dir)){
  if(fs.statSync(path.join(dir,filename)).isFile()&&!assetNames.has(filename)&&!new Set(['index.html','review.css',`review_${lang}.pdf`]).has(filename))fs.unlinkSync(path.join(dir,filename));
 }
 outputFiles.push({language:lang,sections:count,equations:math.length,assets:assetNames.size,file:path.relative(root,path.join(dir,'index.html'))});
}
for(const result of outputFiles)console.log(JSON.stringify(result));
