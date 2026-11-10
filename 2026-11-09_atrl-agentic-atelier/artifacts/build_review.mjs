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
const cutoff='2026-11-09';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBaseValue=process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')||'';
const publicBase=publicBaseValue?publicBaseValue.replace(/\/?$/,'/'):'';
const articleDescriptions={"ko":"논문을 읽다 생긴 질문이 조사·계산·집필·감수를 거쳐 한 편의 설명으로 자라고, 그 과정의 문제는 공통 기준과 게시 도구의 수리로 돌아옵니다. ATRL 공방을 사례로 사람의 기획과 AEDAUT 편집·저술, ADOPT 개발운영이 하나의 에이전틱 워크플로를 이루는 구조를 살핍니다. 글을 만드는 협업 아키텍처 자체가 연구와 창작의 대상이 되는 변화를 따라갑니다.","en":"A question arising while reading a paper grows through investigation, calculation, writing and review into an explanation; problems encountered along the way return as changes to shared criteria and publishing tools. Using the ATRL atelier as a case, this essay follows how human direction, AEDAUT editorial work and ADOPT operations form one agentic workflow, making the collaborative architecture itself an object of research and creation."};
const descriptors={"ko": "에이전틱 시대의 지식 흐름과 연구 공방의 탄생", "en": "Knowledge Flows in the Agentic Era: The Emergence of a Research Atelier"};
const titles={ko:'ATRL: Agentic Atelier for Tech Review Letters',en:'ATRL: Agentic Atelier for Tech Review Letters'};
// Optional stems are permitted, but only explicitly referenced assets are copied.
// Revision 23 replaces Figure 9 only; larger-view links reuse current desktop SVGs.
const figureStems=["research_agent_evidence","harness_configuration","atelier_architecture","editorial_workflow","hub_observation","explanation_design","collaboration_mechanism","coupled_cycles","reusable_archive"];
// Only these assembled, public-safe records may be linked as local data downloads.
const reproductionAssets=['hub-publication-topics-v15.json','hub-publication-topics-v15.csv'];
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
  [
    "책임 편집자",
    "김현중"
  ],
  [
    "AI 시스템",
    "OpenAI Codex; 정확한 모델 식별자는 보존되지 않음"
  ],
  [
    "확인 가능한 에이전트 역할",
    "gate_article_editorial은 그림 9와 인접 설명의 한영 문장·캡션을 개정했다. gate_article_physics는 출판물·세 기록층·후속 질문의 의미와 예제 조건을 감수했다. agent_standards는 그림 9의 정확한 벡터 자료와 한영 PC·모바일 구성, 웹·PDF 제작·검수를 맡았다. root는 내장 이미지 생성 도구로 원화를 편집하고 본문·원본·출력·판본 기록을 대조했다."
  ],
  [
    "편집 하네스",
    "<a href=\"https://infant83.io/AI_Tech_Review/methods/\">AI Tech Review Editorial Harness</a> 기본판 2026.08과 2026-11-06 과학 설명·문체 보완을 적용했다. 2026-11-10 개정 23은 완성된 출판물과 그 설명을 이루는 근거·방법·편집 판단을 그림 9에서 함께 읽도록 다듬었다."
  ],
  [
    "검증 범위",
    "구조·운영의 8개 자료는 e5a8ac6, 55편 관찰은 f347836 고정판을 유지했다. 14개 참고문헌·수학 조건·교육용 CSV·통계 자료를 보존했다. 그림 9는 기존 교육모형과 기록을 펼쳐 보는 설계 예다. 새 외부 연구·실험·성능 측정·과학 수치 계산은 추가하지 않았다."
  ],
  [
    "사람 검토 기록",
    "책임 편집자는 그림 9의 위쪽이 완성된 책 표지로 읽히고 아래 기록층의 실제 내용이 그 설명을 함께 이루도록 개정 방향을 제시했다. 에이전트들이 새 원화·자료·한영 설명·출력을 감수했다. 책임 편집자는 2026-11-10 게재를 요청했다. 문장 단위의 사람 감수나 별도 사람 독자 조사는 수행하지 않았다."
  ],
  [
    "근거 기준일",
    "2026-11-09"
  ],
  [
    "적용 판본과 감수",
    "기본 방법서와 2026-11-06 보완판의 정체를 유지한다. 이번 그림 9의 원화·벡터·표면 배치·한영 설명과 실제 출력 검토를 앞선 원고·그림·자료 감수와 구분했다. 새로운 모형 실험이나 기존 55편의 품질 효과를 측정한 기록으로 쓰지 않는다."
  ]
]:[
  [
    "Responsible editor",
    "Hyun-Jung Kim"
  ],
  [
    "AI system",
    "OpenAI Codex; exact model identifier not retained"
  ],
  [
    "Verifiable agent roles",
    "gate_article_editorial revised bilingual prose and captions for Figure 9 and its adjacent explanation. gate_article_physics reviewed the meaning of the publication, three supporting record layers and follow-up question, with the example’s conditions. agent_standards authored exact vector contents and desktop/mobile arrangements and handled web/PDF production and checks. root edited the bare artwork with the built-in image tool and compared prose, sources, outputs and edition records."
  ],
  [
    "Editorial harness",
    "<a href=\"https://infant83.io/AI_Tech_Review/methods/\">AI Tech Review Editorial Harness</a>, base edition 2026.08 with scientific-explanation and prose supplements dated 2026-11-06. Revision 23, produced on 2026-11-10, refines Figure 9 so a finished publication can be read together with the evidence, methods and editorial judgments behind its explanation."
  ],
  [
    "Verification scope",
    "The eight structural/operational sources retain e5a8ac6 and the 55-review observation retains f347836. Fourteen references, mathematical conditions, educational CSV and statistical materials were preserved. Figure 9 unfolds an existing teaching model and records as a design example. No new external study, experiment, performance measurement or scientific numerical calculation was added."
  ],
  [
    "Human review record",
    "The responsible editor asked for Figure 9’s top to read as a finished book cover and the concrete contents of its supporting layers to form that explanation together. Agents reviewed the new artwork, materials, bilingual explanation and outputs. The responsible editor requested publication on 2026-11-10. Line-by-line human review and a separate human-reader study were not performed."
  ],
  [
    "Evidence cutoff",
    "2026-11-09"
  ],
  [
    "Applied versions and review",
    "The base method and supplements dated 2026-11-06 retain their identities. Current Figure 9 artwork, vectors, surface placement, bilingual explanation and actual-output review are distinguished from earlier manuscript, figure and data review. They are not recorded as a new model experiment or measurement of quality effects across the 55 reviews."
  ]
];
 const note=ko?"2026-11-10 게재용 개정 23. 발행 표기·근거 기준일은 2026-11-09다. 그림 9의 제본 표지와 세 내용층, 후속 질문을 시각화하고 인접 한영 설명을 맞췄다. 나머지 논지와 근거를 유지하며 실제 검토 범위·입력·최종 출력의 정체를 기록했다. 책임 편집자의 2026-11-10 게재 요청에 따라 공개용 판본을 준비했다. 기존 무문자 그림 9 원화를 내장 image_gen 도구로 1회 편집하고, 새 제본 책 장면에 모형·코드·CSV·감수 기록을 정확한 벡터로 구성했다. 한영 PC·모바일 4종을 바꾸고 다른 32개 SVG·B3 대표 이미지·기존 자료는 보존했다. 단순 WebP 인코딩과 SVG 화면 재배치를 창작적 래스터 편집과 구분했다.":"Revision 23, prepared for publication on 2026-11-10. Displayed publication date and evidence cutoff remain 2026-11-09. Figure 9’s bound cover, three content layers and follow-up question were redrawn and its adjacent bilingual explanation aligned. The remaining argument and evidence retain their identities; actual review scope, inputs and final outputs were recorded. The public edition was prepared following the responsible editor’s publication request on 2026-11-10. The earlier text-free Figure 9 artwork was edited once with the built-in image_gen tool. Exact model, code, CSV and review records were authored as vectors on the new bound-book scene. Four desktop/mobile language variants changed; the other thirty-two SVGs, B3 hero and existing data were retained. Encoding-only WebP conversion and SVG presentation are distinguished from creative raster editing.";
 return '<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">'+(ko?'작성·검증 정보':'How this review was made')+'</h2><dl>'+rows.map(([a,b])=>'<div><dt>'+a+'</dt><dd>'+b+'</dd></div>').join('')+'</dl><p>'+note+'</p></section><!-- End AI Tech Review Authoring Disclosure -->';
}

// Reader access to dense native details; the picture and source SVG remain unchanged.
function addLargerFigureLinks(body,lang){
 const selected=['atelier_architecture','collaboration_mechanism','coupled_cycles','reusable_archive'];
 return body.replace(/<figure\b[\s\S]*?<\/figure>/g,figure=>{
  const stem=selected.find(value=>figure.includes(`src="${value}_${lang}.svg"`));
  if(!stem)return figure;
  const number=figure.match(/<figcaption>\s*(?:그림|Figure)\s+(\d+)\./)?.[1];
  if(!number)throw Error(`Missing numbered caption for ${stem}`);
  const label=lang==='ko'?'크게 보기':'View larger';
  const accessible=lang==='ko'?`그림 ${number} 원본 크게 보기 (새 탭)`:`View Figure ${number} larger (opens in a new tab)`;
  const control=` <a class="figure-larger" href="${stem}_${lang}.svg" target="_blank" rel="noopener" aria-label="${esc(accessible)}">${label}</a>`;
  return figure.replace('</figcaption>',control+'</figcaption>');
 });
}

function embedFigureFonts(svg){
 if(!/<text\b/.test(svg))return svg; // Outlined labels need no unused font definitions.
 if(svg.includes('data:font/woff2;base64,'))return svg;
 const rules=['regular','bold'].flatMap(weight=>[['ReviewFigure',`review-${weight}.woff2`],['ReviewFigureSymbols',`review-symbols-${weight}.woff2`]].map(([family,file])=>`@font-face{font-family:${family};src:url(data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,file)).toString('base64')}) format('woff2');font-weight:${weight==='regular'?400:700}}`)).join('')+`@font-face{font-family:ReviewFigureMath;src:url(data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,'review-math.woff2')).toString('base64')}) format('woff2');font-weight:400}`;
 const license=fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','');
 return svg.replace(/<svg\b[^>]*>/,tag=>tag+`<style><![CDATA[/* ${license} */\n${rules}]]></style>`);
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
 // Manuscripts retain their production record; the output uses one structured disclosure below.
 const renderSource=source.replace(/^##\s+(?:작성과 검증|Writing and verification|Preparation and verification)\s*\n[\s\S]*$/im,'').trimEnd();
 const title=source.match(/^#\s+(.+)$/m)?.[1]?.trim()||titles[lang];
 const description=articleDescriptions[lang];
 const math=[];
 const safe=renderSource.replace(/\$\$([\s\S]*?)\$\$|\\\(([\s\S]*?)\\\)/g,(_,a,b)=>{
  const result=mathImage((a||b).trim(),a!==undefined);math.push(result);
  return a!==undefined?`\n\nMATHBLOCK${math.length-1}END\n\n`:`MATHINLINE${math.length-1}END`;
 });
 let body=marked.parse(safe,{gfm:true});
 body=body.replace(/\b(src|srcset|href)="\.\.\/(?:figs|artifacts)\/([^"/]+)"/g,(match,attribute,filename)=>{
  const approved=new Set(['hero.webp',...reproductionAssets,...figureStems.flatMap(stem=>[`${stem}_${lang}.svg`,`${stem}_mobile_${lang}.svg`])]);
  if(!approved.has(filename))throw Error(`Unapproved local asset ${filename}`);
  return `${attribute}="${filename}"`;
 });
 body=body.replace(/(?<=>)([^<]+)(?=<)/g,(_,text)=>text.replace(/\*\*([^*\n]+\))\*\*(?=[가-힣])/g,'<strong>$1</strong>'));
 if(publicBase){
  const links={'en/index.html':publicBase+'en/','en/review_en.pdf':publicBase+'en/review_en.pdf','../index.html':publicBase,'../review_ko.pdf':publicBase+'review_ko.pdf'};
  body=body.replace(/href="([^"]+)"/g,(match,href)=>links[href]?`href="${links[href]}"`:match);
 }
 body=body.replace(/<p>MATHBLOCK(\d+)END<\/p>/g,(_,i)=>math[+i].html).replace(/MATHINLINE(\d+)END/g,(_,i)=>math[+i].html);
 body=addLargerFigureLinks(body,lang);
 let count=0;const toc=[];
 body=body.replace(/<h2(?:\s[^>]*)?>(.*?)<\/h2>/g,(_,text)=>{const id=`section-${++count}`;toc.push(`<li><a href="#${id}">${text}</a></li>`);return `<h2 id="${id}">${text}</h2>`});
 body=body.replaceAll('<table>',`<div class="table-scroll" role="region" tabindex="0" aria-label="${ko?'비교와 응용 표':'Comparison and applications table'}"><table>`).replaceAll('</table>','</table></div>');
 const editor='';
 body=body.replace(/(<p class="byline">)([\s\S]*?)(<\/p>)/,(_,open,content,close)=>`${open}${content} · <a href="#authoring-disclosure">${ko?'작성·검증 정보':'Production and verification'}</a>${close}`);
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
  const normalized=content.replace(/<p>\[(\d+)\]\s*([\s\S]*?)<\/p>/g,'<li>$2</li>');
  const prepared=/<ol>/.test(normalized)?normalized:(/<li>/.test(normalized)?`<ol>${normalized}</ol>`:normalized);
  const list=prepared.replace('<ol>','<ol class="reference-list" role="list">').replace(/<li>([\s\S]*?)<\/li>/g,(_,entry)=>{
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
<header><a class="brand" href="https://infant83.io/AI_Tech_Review/">AGENTIC TECH REVIEW LETTERS</a><div class="topline-actions">${localBadge}<nav class="language-switcher" aria-label="${ko?'언어 선택':'Language'}"><span class="language-current" aria-current="page" lang="${lang}">${ko?'한국어':'English'}</span><a href="${other}" lang="${ko?'en':'ko'}" hreflang="${ko?'en':'ko'}">${ko?'English':'한국어'}</a></nav><a class="download" href="review_${lang}.pdf">PDF ↓</a></div></header>
<main class="paper"><div class="issue-meta"><span>EDITORIAL ESSAY</span><span>2026.11.09</span><span>${ko?'지식 아카이빙 · 협업 · 공유':'KNOWLEDGE ARCHIVING · COLLABORATION · SHARING'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">Agentic Tech Review Letters · ${cutoff}<br>${ko?'연구를 함께 읽고 연결하며 나누는 방식.':'Reading, connecting, and sharing research.'}</footer></main></body></html>\n`;
 fs.writeFileSync(path.join(dir,'index.html'),html.split('\n').map(line=>line.trimEnd()).join('\n'));
 fs.writeFileSync(path.join(dir,'review.css'),stylesheet);
 const allowedFigures=new Set(['hero.webp',...reproductionAssets,...figureStems.flatMap(stem=>[`${stem}_${lang}.svg`,`${stem}_mobile_${lang}.svg`])]);
 const assetNames=new Set(math.map(x=>x.filename));
 for(const match of html.matchAll(/\b(?:src|srcset)="([^"#]+)"/g)){
  if(!/^(?:https?:|data:|\/)/.test(match[1])){
   if(!allowedFigures.has(match[1])&&!/^math_[0-9a-f]+\.svg$/.test(match[1]))throw Error(`Asset is outside the explicit figure allowlist: ${match[1]}`);
   assetNames.add(match[1]);
  }
 }
 for(const filename of reproductionAssets)if(html.includes(`href="${filename}"`))assetNames.add(filename);
 for(const filename of assetNames){
  if(path.basename(filename)!==filename)throw Error(`Only flat local assets are allowed: ${filename}`);
  const asset=path.join(figureStems.some(stem=>filename.startsWith(stem+'_'))?path.join(root,'figs'):artifacts,filename);if(!fs.existsSync(asset))throw Error(`Missing asset: ${filename}`);
  if(filename.endsWith('.svg')&&!filename.startsWith('math_'))fs.writeFileSync(path.join(dir,filename),embedFigureFonts(fs.readFileSync(asset,'utf8')));else fs.copyFileSync(asset,path.join(dir,filename));
 }
 for(const filename of fs.readdirSync(dir)){
  if(fs.statSync(path.join(dir,filename)).isFile()&&!assetNames.has(filename)&&!new Set(['index.html','review.css',`review_${lang}.pdf`]).has(filename))fs.unlinkSync(path.join(dir,filename));
 }
 outputFiles.push({language:lang,sections:count,equations:math.length,assets:assetNames.size,file:path.relative(root,path.join(dir,'index.html'))});
}
for(const result of outputFiles)console.log(JSON.stringify(result));
