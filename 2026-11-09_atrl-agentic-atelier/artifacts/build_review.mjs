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
const articleDescriptions={"ko":"논문을 읽다 생긴 질문이 조사·계산·집필·감수를 거쳐 한 편의 설명으로 자랍니다. ATRL 공방에서는 사람의 기획 아래 에이전틱 편집팀과 에이전틱 개발운영팀이 협력하고, 그 과정에서 얻은 판단을 바탕으로 역할과 도구의 연결을 다시 설계합니다. 그 협업 구조를 설계하고 검토하는 일도 연구와 창작의 일부가 되는 변화를 따라갑니다.","en":"A question arising while reading a paper grows through investigation, calculation, writing and review into an explanation. At the ATRL atelier, an agentic editorial team and an agentic development and operations team work under human direction, revising how roles and tools connect as findings and feedback return. This essay follows how designing and examining that collaborative structure becomes part of research and creative practice."};
const descriptors={"ko": "에이전틱 시대의 지식 흐름과 연구 공방의 탄생", "en": "Knowledge Flows in the Agentic Era: The Emergence of a Research Atelier"};
const titles={ko:'ATRL: Agentic Atelier for Tech Review Letters',en:'ATRL: Agentic Atelier for Tech Review Letters'};
// Optional stems are permitted, but only explicitly referenced assets are copied.
// Revision 24 clarifies team roles before names; all current figures are retained.
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
    "개정 24에서 root는 요약·본문·게시 정보를 통합했다. atrl_reader_terms는 독자의 진입 순서와 팀 이름의 소개 위치를 검토했다. atrl_plain_terms_production은 한영 웹·PDF 제작과 출력·보존 검사를 맡았다. 앞선 개정 23의 그림 9는 gate_article_editorial·gate_article_physics·agent_standards와 root가 문장·의미·벡터·원화를 제작하고 감수한 산출물이다."
  ],
  [
    "편집 하네스",
    "<a href=\"https://infant83.io/AI_Tech_Review/methods/\">AI Tech Review Editorial Harness</a> 기본판 2026.08과 2026-11-06 과학 설명·문체 보완을 적용했다. 2026-11-10 개정 24는 요약에서 팀의 역할로 먼저 소개하고, 본문에서 팀 이름과 약어를 그림 3 앞에 정의하며 그 협업 구조를 설계하는 의미를 연결했다."
  ],
  [
    "검증 범위",
    "구조·운영의 8개 자료는 e5a8ac6, 55편 관찰은 f347836 고정판을 유지했다. 14개 참고문헌·수학 조건·교육용 CSV·통계 자료와 그림 36종을 보존했다. 이번 개정은 요약·팀 소개의 순서·하네스 설계 설명과 작성 정보를 다듬고, 한영 실제 출력과 이전 판본의 동일한 쪽·자산을 대조했다. 새 외부 연구·실험·과학 수치 계산은 추가하지 않았다."
  ],
  [
    "사람 검토 기록",
    "책임 편집자는 요약에 설명 없이 팀 약어가 등장하면 독자의 진입을 방해할 수 있음을 지적했다. 먼저 일반적인 에이전틱 편집팀·개발운영팀으로 소개하고 본문에서 팀 이름을 정의하며, 하네스 자체도 설계할 수 있음을 보여 달라는 방향을 제시했다. 문장·한영·출력 검토는 에이전트가 수행했다. 문장 단위의 사람 재독이나 별도 사람 독자 조사는 기록하지 않았다."
  ],
  [
    "근거 기준일",
    "2026-11-09"
  ],
  [
    "적용 판본과 감수",
    "기본 방법서와 2026-11-06 보완판의 정체를 유지한다. 개정 24의 요약·이름 소개·실제 출력 검토를 앞선 원고·그림·자료 감수와 구분했다. 사람과 에이전트의 역할, 도구·권한·공유 기록·인계 방식을 연결하는 일을 하네스 설계의 대상으로 설명한다. 조직의 소속과 기존 권한, 연구 근거와 계산 조건은 유지한다."
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
    "For revision 24, root integrated the summaries, manuscript and publication information. atrl_reader_terms reviewed the reader’s entry and the point at which team names are introduced. atrl_plain_terms_production handled bilingual web/PDF production and output/preservation checks. Figure 9 retains the revision 23 work of gate_article_editorial, gate_article_physics, agent_standards and root on prose, meaning, vectors and artwork."
  ],
  [
    "Editorial harness",
    "<a href=\"https://infant83.io/AI_Tech_Review/methods/\">AI Tech Review Editorial Harness</a>, base edition 2026.08 with scientific-explanation and prose supplements dated 2026-11-06. Revision 24, prepared on 2026-11-10, introduces teams by function in the summary, defines their full names and acronyms before Figure 3, and connects their organization to the design of the harness."
  ],
  [
    "Verification scope",
    "The eight structural/operational sources retain e5a8ac6 and the 55-review observation retains f347836. Fourteen references, mathematical conditions, educational CSV, statistical materials and all thirty-six figure variants were retained. The revision refines summaries, the order of team introductions, harness-design explanation and disclosure, with actual bilingual output and prior-edition page/asset comparisons. No new external study, experiment or scientific numerical calculation was added."
  ],
  [
    "Human review record",
    "The responsible editor observed that unexplained team acronyms in the summary could obstruct the reader’s entry. The requested direction was to introduce an agentic editorial team and a development/operations team by function, define their names in the body, and show that the harness itself can be designed. Agents performed wording, bilingual and output checks. Line-by-line human rereading and a separate human-reader study were not recorded."
  ],
  [
    "Evidence cutoff",
    "2026-11-09"
  ],
  [
    "Applied versions and review",
    "The base method and supplements dated 2026-11-06 retain their identities. Revision 24 summary, team-introduction and actual-output checks are distinguished from earlier manuscript, figure and data review. Arranging people and agents, tools, permissions, shared records and hand-offs is explained as part of harness design. Team membership, existing authority, research evidence and calculation conditions are retained."
  ]
];
 const note=ko?"2026-11-10 개정 24. 발행 표기·근거 기준일은 2026-11-09다. 요약에서는 에이전틱 편집팀·개발운영팀의 역할을 소개하고, 본문에서는 정식 이름과 약어를 그림 3보다 먼저 정의했다. 원고의 중심 논지와 과학적 근거를 유지하며 이번 문장·한영 출력과 최종 파일의 정체를 기록했다. 그림 9는 개정 23에서 기존 무문자 원화를 내장 image_gen 도구로 1회 편집하고 모형·코드·CSV·감수 기록을 정확한 벡터로 구성한 산출물이다. 개정 24에서는 새 원화 생성·편집 없이 그림 36종과 B3 대표 이미지·기존 자료를 보존했다. 실제 출력의 시각 판독과 동일한 쪽·자산의 보존 비교는 각각 수행한 범위로 구분한다.":"Revision 24, prepared on 2026-11-10. Displayed publication date and evidence cutoff remain 2026-11-09. The summary introduces the functions of the agentic editorial and development/operations teams; the body defines their full names and acronyms before Figure 3. The central argument and scientific evidence are retained, while current wording, bilingual outputs and final file identities are recorded. Figure 9 retains revision 23’s single built-in image_gen edit of the earlier text-free artwork, with exact model, code, CSV and review inscriptions authored as vectors. Revision 24 generates or edits no new artwork and preserves all thirty-six figure variants, the B3 hero and existing data. Actual visual reading is distinguished from comparisons establishing identical pages and assets.";
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
