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
const cutoff='2026-11-12';
const issueDate='2026-11-09';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBaseValue=process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')||'';
const publicBase=publicBaseValue?publicBaseValue.replace(/\/?$/,'/'):'';
const articleDescriptions={"ko":"논문을 읽다 생긴 질문이 조사·계산·집필·감수를 거쳐 한 편의 설명으로 자랍니다. ATRL 공방에서는 사람의 기획 아래 에이전틱 편집팀과 에이전틱 개발운영팀이 협력하고, 그 과정에서 얻은 판단을 바탕으로 역할과 도구의 연결을 다시 설계합니다. 그 협업 구조를 설계하고 검토하는 일도 연구와 창작의 일부가 되는 변화를 따라갑니다.","en":"A question arising while reading a paper grows through investigation, calculation, writing and review into an explanation. At the ATRL atelier, an agentic editorial team and an agentic development and operations team work under human direction, revising how roles and tools connect as findings and feedback return. This essay follows how designing and examining that collaborative structure becomes part of research and creative practice."};
const descriptors={"ko": "에이전틱 시대의 지식 흐름과 연구 공방의 탄생", "en": "Knowledge Flows in the Agentic Era: The Emergence of a Research Atelier"};
const titles={ko:'ATRL: Agentic Atelier for Tech Review Letters',en:'ATRL: Agentic Atelier for Tech Review Letters'};
// Optional stems are permitted, but only explicitly referenced assets are copied.
// Revision 27 corrects the repository reference while retaining the revision 26 figures.
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
 const rows=ko?[["책임 편집자", "김현중"], ["AI 시스템", "OpenAI Codex; 정확한 모델 식별자는 보존되지 않음"], ["확인 가능한 에이전트 역할", "개정 26에서 harness_graph_visuals는 그림 3·7·8의 한영 PC·모바일 벡터 12종을 개정했다. harness_visual_editorial은 실제 그림에 맞춰 대체 설명·캡션과 인접 문장을 다듬고 관계의 의미를 감수했다. harness_visual_production은 작성 정보·한영 웹·PDF 제작과 출력·보존 검사를 맡았다. root는 편집 방향을 통합하고 선택한 실제 그림과 본문을 대조했다. 개정 27에서 root는 참고문헌 [4]의 저장소 대표 주소와 기존 commit 링크를 확인하고 정정했다. harness_visual_production은 해당 한영 웹·PDF와 변경된 쪽, 보존 범위를 확인했다."], ["편집 하네스", "<a href=\"https://infant83.io/AI_Tech_Review/methods/\">AI Tech Review Editorial Harness</a> 기본판 2026.08, 2026-11-06 과학 설명·문체 보완과 2026-11-11 독자 친화적 설명 보완을 이번 편집에 적용했다. 2026-11-12 원고 개정 26은 하네스·루프·그래프의 관계를 기존 조직·인계·교육 예제 그림의 구조로 표현한다. 개정 27은 같은 방법서 아래 참고문헌 [4]의 저장소 링크와 확인일을 수정했다."], ["검증 범위", "개정 26에서 그림 3은 공유 하네스와 역할 사이의 관계를, 그림 7은 통과·불일치·미완료에 따른 진행·수정·재개를, 그림 8은 설명과 운영의 두 루프를 같은 판본·확인 범위로 연결한다. 개정한 벡터 12종과 한영 설명을 대조했다. 기존 18개 참고문헌, 교육모형·CSV·공개 통계, 다른 그림 24종과 대표 이미지를 유지했다. 이번 실제 웹·PDF의 조판과 그림 판독, 보존 검사는 별도 출력 기록에 남긴다. 개정 27은 참고문헌 [4]의 대표 주소와 별도 commit 주소, 인용 번호와 실제 출력을 대조했다. 나머지 설명·그림·관찰 자료는 보존했다."], ["사람 검토 기록", "책임 편집자는 하네스·루프·그래프로 해석한 공방의 구조를 기존 그림에도 반영해 달라는 방향을 제시했다. 벡터 제작과 문장·의미·한영 출력 검토는 에이전트가 수행했다. 문장 단위의 사람 재독이나 별도 사람 독자 조사는 기록하지 않았다. 이번 개정 27은 GitHub 저장소를 참고문헌에 연결해 달라는 요청을 반영했다."], ["근거 기준일", "2026-11-12. 개정 25의 문헌·운영 근거와 기존 조직 자료·55편 관찰의 고정판을 유지했다."], ["적용 판본과 감수", "기본 방법서·보완판과 원고 개정 26·27을 구별한다. 현재의 조직 규약·공유 기록·도구로 연결된 관계를 하네스와 반복·협업 경로의 관점으로 시각화했다. 그림 8의 기존 AI 개념 원화와 과학 곡선을 보존하고 표기·되돌림 경로·모바일 구성을 벡터로 개정했다."]]:[["Responsible editor", "Hyun-Jung Kim"], ["AI system", "OpenAI Codex; exact model identifier not retained"], ["Verifiable agent roles", "For revision 26, harness_graph_visuals revised twelve Korean/English desktop/mobile vector variants of Figures 3, 7 and 8. harness_visual_editorial aligned alternative descriptions, captions and adjacent prose with the actual figures and reviewed their relationships. harness_visual_production handled disclosure, bilingual web/PDF production and output/preservation checks. root integrated the editorial direction and compared selected actual figures with the manuscript. For revision 27, root checked and corrected the repository home and existing commit links in reference [4]. harness_visual_production checked the bilingual web/PDF outputs, changed pages and preservation scope."], ["Editorial harness", "<a href=\"https://infant83.io/AI_Tech_Review/methods/\">AI Tech Review Editorial Harness</a>, base edition 2026.08, with scientific-explanation/prose supplements dated 2026-11-06 and the reader-friendly explanation supplement dated 2026-11-11, applied to this edit. Manuscript revision 26, prepared on 2026-11-12, expresses harness, loop and graph relationships through the structure of the existing organization, handoff and educational-example figures. Revision 27 corrects the repository link and access date in reference [4] under the same method."], ["Verification scope", "In revision 26, Figure 3 shows the shared harness and relationships among roles; Figure 7 distinguishes progression, revision and resumption after passing checks, a mismatch or unfinished work; Figure 8 connects explanation and operations loops through the same version and checking scope. The twelve revised vector variants were compared with the bilingual explanation. The eighteen existing references, educational model, CSV, public statistics, other twenty-four figure variants and hero were retained. Actual web/PDF layout, figure reading and preservation checks are recorded separately. Revision 27 checks the repository home and separate commit links in reference [4], citation numbering and actual outputs. Other explanations, figures and observational materials are preserved."], ["Human review record", "The responsible editor asked for the atelier structure interpreted through harnesses, loops and graphs to be incorporated into the existing figures. Agents performed vector production and wording, meaning and bilingual output review. Line-by-line human rereading and a separate human-reader study were not recorded. Revision 27 follows the request to cite the GitHub repository in the bibliography."], ["Evidence cutoff", "2026-11-12. Revision 25 literature and operational evidence, and the existing organizational and 55-review snapshots, retain their identities."], ["Applied versions and review", "The base method and supplements are distinguished from manuscript revisions 26 and 27. Relationships connected through current organizational conventions, shared records and tools are visualized as a harness with iterative and collaborative paths. Figure 8 retains its existing AI conceptual artwork and scientific curves; inscriptions, return paths and mobile composition were revised as vectors."]];
 const note=ko?"2026-11-12 개정 26. 원 발행 표기는 2026-11-09다. 그림 3·7·8의 바깥 작업 환경과 역할별 연결, 조건별 되돌림·재개, 두 반복의 접점을 실제 구성에 반영하고 한영 본문·캡션을 맞췄다. 새로운 외부 근거나 과학 수치 계산, 원화 생성은 추가하지 않았다. 기존 자료의 감수와 이번 개정·출력의 실제 검토 범위를 구분해 기록한다. 2026-11-12 개정 27은 참고문헌 [4]에 저장소 대표 링크를 두고 55편 관찰의 기존 commit 링크를 함께 보존했다. 확인일을 갱신하고 한영 실제 출력과 판본의 동일성을 대조했다.":"Revision 26, prepared on 2026-11-12. The original issue date remains 2026-11-09. Figures 3, 7 and 8 now express the surrounding working environment and role relationships, conditional return/resumption and the junction between two loops, with aligned bilingual prose and captions. No new external evidence, scientific numerical calculation or artwork generation was added. Earlier source review and actual current revision/output checks are recorded according to their respective scope. Revision 27, prepared on 2026-11-12, gives reference [4] a repository-home link while preserving the existing commit link for the 55-review observation. The access date was updated, with actual bilingual outputs and edition preservation checked.";
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
<main class="paper"><div class="issue-meta"><span>EDITORIAL ESSAY</span><span>2026.11.09</span><span>${ko?'지식 아카이빙 · 협업 · 공유':'KNOWLEDGE ARCHIVING · COLLABORATION · SHARING'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">Agentic Tech Review Letters · ${issueDate}<br>${ko?'연구를 함께 읽고 연결하며 나누는 방식.':'Reading, connecting, and sharing research.'}</footer></main></body></html>\n`;
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
