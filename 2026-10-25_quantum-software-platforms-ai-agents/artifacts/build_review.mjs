/** Build a bilingual, self-contained public review with a strict asset allowlist. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifacts=path.join(root,'artifacts');
const dependencyRoots=[process.env.REVIEW_NODE_MODULES,process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,path.join(root,'node_modules'),path.join(process.cwd(),'node_modules')].filter(Boolean);
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
const cutoff='2026-10-25';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBase=(process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')||'https://infant83.github.io/AI_Tech_Review/reviews/2026-10-25_quantum-software-platforms-ai-agents/').replace(/\/?$/,'/');
const descriptors={ko:'양자 소프트웨어에서 고수준 합성과 회로 변환이 만나는 지점, AI 에이전트가 맡는 역할, 검증과 플랫폼 선택의 조건을 검토한다.',en:'High-level quantum synthesis and circuit transformation, the role of AI agents, and the conditions for verification and platform choice.'};
const titles={ko:'양자 소프트웨어의 두 경쟁 경로: 회로 합성, AI 에이전트와 생태계의 주도권',en:'Two Paths in Quantum Software: Circuit Synthesis, AI Agents, and Platform Power'};
// Optional stems are permitted, but only explicitly referenced assets are copied.
const figureStems=['program_paths','oracle_semantics','synthesis_tradeoff'];
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
for(const weight of ['regular','bold']){
 const file=`review-${weight}.woff2`;
 const encoded=fs.readFileSync(path.join(artifacts,file)).toString('base64');
 stylesheet=stylesheet.replaceAll(`url('${file}')`,`url('data:font/woff2;base64,${encoded}')`);
}
stylesheet='/* '+fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','')+' */\n'+stylesheet;

function disclosure(ko){
 const rows=ko?[
  ['책임 편집자','김현중'],['AI 보조','OpenAI Codex · 정확한 작성 모델 식별자: 미보존'],
  ['에이전트와 역할','root: 한국어 집필·원본 개념 표지·NumPy 교육 계산·생태계 조사·게시 통합; academic_sources: Qiskit의 현행 HLS·Target·에이전트 도구와 과학 감수; academic_sources/theory_crosscheck: LLM 벤치마크 분모와 주장 범위 감수; applications_sources: Classiq 논문·SDK·보장 범위·보고 데이터 대조와 영어 전문 번역; applications_sources/translation_audit: 한영 출처·기호·수식·조건의 독립 대응 감수; review_format: 원본 한영 설명 도표·수식·글꼴 조판·HTML/PDF 제작과 출력 검사; publish_audit: 독립 설명·개념 표지 감수와 출판 감사.'],
  ['입력과 산출물','공유 자료, 공개 논문·공식 SDK 문서와 코드, NumPy 교육 계산 → 한영 기술 리뷰·개념 표지·설명 도표·수식과 PDF.'],
  ['제작 요청 요약','Classiq와 Qiskit의 회로 합성·변환 접근, AI 에이전트의 도구 호출과 검증, 양자 소프트웨어 생태계의 선택 조건을 대조한 기술 리뷰 작성·공개.'],
  ['하네스','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a> · 과학 설명과 시각 전달 준칙 1.0(2026-10-22)'],
  ['검증 범위','공개 1차 출처·버전·SDK 문서와 논문 수치 대조, 3큐비트 위상 오라클과 한 번의 Grover 반복을 NumPy로 계산, 한영 수식·도표와 HTML/PDF 출력 검사. Classiq 보고 수치를 독립 합성하지 않았으며 계정·유료 API·QPU를 실행하지 않았다.'],
  ['사람 검토 수준','주제·작성·공개 게시 요청 확인; 문장 단위 사람 승인 없음.'],['근거 기준일',cutoff]
 ]:[
  ['Responsible editor','Hyun-Jung Kim'],['AI assistance','OpenAI Codex; exact authoring-model identifier not retained.'],
  ['Agents and roles','root: Korean writing, original conceptual cover, NumPy teaching calculation, ecosystem research and publication integration; academic_sources: current Qiskit HLS, Target, agent tools and scientific audit; academic_sources/theory_crosscheck: LLM benchmark denominators and claim-scope review; applications_sources: Classiq papers, SDK, guarantees, reported-data crosscheck and full English translation; applications_sources/translation_audit: independent bilingual audit of sources, notation, equations and conditions; review_format: original bilingual figures, equation/font typesetting, HTML/PDF production and output checks; publish_audit: independent explanation and conceptual-cover review, and publication audit.'],
  ['Inputs and outputs','Shared material, public papers, official SDK documentation/code and a NumPy teaching calculation → bilingual review, conceptual cover, explanatory figures/equations and PDFs.'],
  ['Production request','Review Classiq and Qiskit approaches to quantum synthesis and circuit transformation, agent tool use and verification, and choices in the quantum-software ecosystem.'],
  ['Harness','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>; Scientific Explanation and Visual Communication Principles 1.0 (2026-10-22)'],
  ['Verification scope','Primary sources, versions, SDK documentation and paper-reported values; a NumPy calculation of three-qubit phase oracles and one Grover iteration; bilingual equations, figures and HTML/PDF output. The Classiq synthesis results were not independently reproduced. No account, paid API or QPU execution.'],
  ['Human review','Topic, writing and public posting requested; no line-by-line human approval.'],['Evidence cutoff',cutoff]
 ];
 rows.push([ko?'문체 개정':'Prose revision',ko?"2026-10-26 문체 개정: 문체 감사 하네스의 10월 26일 보완에 따라 한국어 다섯 문단과 대응 영문을 퇴고했다. root는 편집·출력·게시 통합, english_update는 영문 대응 검토, publication_audit는 배포 정합성 검토를 맡았다. 수치·수식·도표·참고문헌과 근거 기준일은 유지했다.":"Prose revision, 2026-10-26: five Korean paragraphs and their English counterparts were edited using the October 26 prose-audit harness supplement. root handled editing, output and publication integration; english_update reviewed the English correspondence; publication_audit reviewed publication consistency. Numerical values, equations, figures, references and the evidence cutoff were retained."]);
 rows.push([ko?'참고문헌 개정':'Reference revision',ko?"2026-10-26 참고문헌 개정: APS의 번호식 인용·서지 형식을 적용했다. root는 인용 대응·조판·게시, aps_standard_audit는 공식 지침 대조, software_credit_metadata는 개발자 크레딧, bibliography_source_index는 공식 문서 원제 확인을 맡았다.":"APS reference revision, 2026-10-26: root handled citation mapping, typesetting and publication; aps_standard_audit checked the official style; software_credit_metadata checked software attribution; bibliography_source_index verified official documentation titles."]);
 return `<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">${ko?'작성·검증 정보':'How this review was made'}</h2><dl>${rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl><p>${ko?'교육용 상태벡터 계산, 저자 보고 합성 수치와 개념 도식을 구분한다. AI 생성 표지는 개념 일러스트이며 실제 장치·회로·벤치마크 데이터가 아니다.':'The teaching state-vector calculation, author-reported synthesis values and conceptual diagrams are distinguished. The AI-generated cover is conceptual, not an actual device, circuit or benchmark dataset.'}</p></section><!-- End AI Tech Review Authoring Disclosure -->`;
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
 const editor=`<p class="byline-disclosure">${ko?'책임 편집: 김현중 · AI 보조 작성: Codex · 근거 기준일: 2026년 10월 25일':'Responsible editor: Hyun-Jung Kim · AI assistance: Codex · Evidence cutoff: 25 October 2026'} · <a href="#authoring-disclosure">${ko?'작성·검증 범위':'Production and verification'}</a></p>`;
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
<header><a class="brand" href="https://infant83.github.io/AI_Tech_Review/">AI TECH REVIEW LETTERS</a><div class="topline-actions">${localBadge}<nav class="language-switcher" aria-label="${ko?'언어 선택':'Language'}"><span class="language-current" aria-current="page" lang="${lang}">${ko?'한국어':'English'}</span><a href="${other}" lang="${ko?'en':'ko'}" hreflang="${ko?'en':'ko'}">${ko?'English':'한국어'}</a></nav><a class="download" href="review_${lang}.pdf">PDF ↓</a></div></header>
<main class="paper"><div class="issue-meta"><span>RESEARCH LETTER</span><span>2026.10.25</span><span>${ko?'양자 합성 · AI 에이전트 · 소프트웨어 생태계':'QUANTUM SYNTHESIS · AI AGENTS · SOFTWARE ECOSYSTEMS'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">AI Tech Review Letters · ${cutoff}<br>${ko?'회로 구현과 의도 검증, 플랫폼 선택을 잇는 해설.':'Circuit implementation, specification checks and platform choice.'}</footer></main></body></html>\n`;
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
  fs.copyFileSync(asset,path.join(dir,filename));
 }
 for(const filename of fs.readdirSync(dir)){
  if(fs.statSync(path.join(dir,filename)).isFile()&&!assetNames.has(filename)&&!new Set(['index.html','review.css',`review_${lang}.pdf`]).has(filename))fs.unlinkSync(path.join(dir,filename));
 }
 outputFiles.push({language:lang,sections:count,equations:math.length,assets:assetNames.size,file:path.relative(root,path.join(dir,'index.html'))});
}
for(const result of outputFiles)console.log(JSON.stringify(result));
