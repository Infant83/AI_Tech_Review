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
const cutoff='2026-11-02';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBase=(process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')||'https://infant83.io/AI_Tech_Review/reviews/2026-11-02_chiral-amplification-nobel-chemistry/').replace(/\/?$/,'/');
const descriptors={ko:'거울상 혼합물의 작은 편향이 선택적 활성과 자가촉매 반응망에서 커지는 원리를 살피고, 고체의 광학 선택성 계산으로 질문을 잇는다.',en:'Selective activity and autocatalytic reaction networks amplify small imbalances between mirror-image molecules, leading to questions about optical selectivity in solids.'};
const titles={ko:'거울상 분자의 작은 불균형을 키우는 화학',en:'How Chemistry Amplifies a Small Enantiomeric Imbalance'};
// Optional stems are permitted, but only explicitly referenced assets are copied.
const figureStems=['chiral_pool','frank_feedback','optical_selectivity'];
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
    "root — 한국어 집필·기작 종합·개념 표지·편집 및 게시 통합; dqb_fermiscope — 화학 원전·지표·서지 대조 및 원고의 독립 과학·문맥 감수; cuantico_source — 공개 연구 이력·CDW 광학·VASPBERRY 기여 대조 및 고체물리 원고 감수; journal_dataset — 영어 전문 번역 및 한영 논증·조건·참고문헌 대응 검토; agent_standards — 원본 교육 도식·수치 검산·글꼴 및 HTML/PDF 제작·전체 출력 검사"
  ],
  [
    "편집 하네스",
    "<a href=\"https://infant83.io/AI_Tech_Review/methods/\">AI Tech Review Editorial Harness 2026.08</a> · 과학 설명과 시각 전달 준칙 1.0 · APS 번호식 인용"
  ],
  [
    "검증 범위",
    "2026년 화학상 공식 발표와 IUPAC 용어; Kagan 1986 서지·공식 해설, Noyori 1989 소속기관 초록, Soai 1995 공개 초록, Sato 2003 공개 초록·각주·보충자료 대조; Athavale 2020 저자 원고·Kalek-Fu 2017 전문, Mohler 2025 공개 초록·색인 본문, Gallarati 2026 저자 공개 출판승인본·최종 서지, PRB 2020 초록·PRL 2022 출판 본문과 보충자료, VASPBERRY 1.6.6 commit 60efa4cf1eaca1e9d34450ce527017f57973569d 대조; 리뷰 계산: 무작위 짝지음 활성 집단 모형과 무차원 Frank형 반응망; 광학 전이 설명 도식; 지표·과학·문맥·한영 독립 감수와 참고문헌·그림 문구·글꼴·HTML/PDF·모바일·아카이브 해시·공개 링크 검사"
  ],
  [
    "사람 검토 기록",
    "편집자가 주제와 자신의 공개 연구 이력에 대한 연결을 지정했다. 전체 과학·문맥·한영·출력 감수는 AI 에이전트가 수행했으며, 문장 단위 사람 승인과 독자 이해도 실험은 수행하지 않았다."
  ],
  [
    "근거 기준일",
    "2026-11-02"
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
    "root — Korean writing, mechanistic synthesis, conceptual cover, editorial and publication integration; dqb_fermiscope — chemistry primary-source, metric and bibliographic audit; independent manuscript scientific and contextual review; cuantico_source — public research-career, CDW optics and VASPBERRY attribution audit; independent solid-state manuscript review; journal_dataset — complete English translation and bilingual argument, condition and reference correspondence review; agent_standards — original educational figures and numerical checks, font and HTML/PDF production and complete output inspection"
  ],
  [
    "Editorial harness",
    "<a href=\"https://infant83.io/AI_Tech_Review/methods/\">AI Tech Review Editorial Harness 2026.08</a>; Scientific Explanation and Visual Communication Principles 1.0; APS numbered references."
  ],
  [
    "Verification scope",
    "Official 2026 chemistry-prize announcement and IUPAC terminology; Kagan 1986 bibliography and official background; Noyori 1989 institutional abstract; Soai 1995 public abstract; Sato 2003 public abstract, notes and supplementary information; Athavale 2020 author manuscript and Kalek-Fu 2017 full text; Mohler 2025 public abstract and indexed passages; Gallarati 2026 accepted author preview with final bibliographic record; PRB 2020 abstract, PRL 2022 published text and supplement, and VASPBERRY 1.6.6 at commit 60efa4cf1eaca1e9d34450ce527017f57973569d; Review computations: random-pair active-pool model and dimensionless Frank-type reaction network; explanatory optical-transition diagram; independent metric, scientific, contextual and bilingual review; references, SVG text, fonts, HTML/PDF, mobile output, archive hashes and live links"
  ],
  [
    "Human review record",
    "The editor selected the topic and requested the connection to his published research. Full scientific, contextual, bilingual and output reviews were performed by AI agents; line-by-line human approval and reader-comprehension testing were not performed."
  ],
  [
    "Evidence cutoff",
    "2026-11-02"
  ]
];
 const note=ko?"말미에서 책임 편집자가 공저한 CDW 논문과 개발에 참여한 VASPBERRY를 다룹니다. 원논문의 반응·DFT 결과를 소개하고, 리뷰에서는 조합 모형과 최소 반응망의 교육 계산을 수행했습니다. 표지는 AI 생성 개념 그림입니다.":"The final section discusses CDW papers coauthored by the responsible editor and VASPBERRY software he develops. Research reaction and DFT results are attributed to their authors; computations for this review comprise educational pairing and minimal reaction-network models. The cover is an AI-generated conceptual illustration.";
 return `<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">${ko?'작성·검증 정보':'How this review was made'}</h2><dl>${rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl><p>${note}</p></section><!-- End AI Tech Review Authoring Disclosure -->`;
}

function embedFigureFonts(svg){
 const rules=['regular','bold'].flatMap(weight=>[['ReviewFigure',`review-${weight}.woff2`],['ReviewFigureSymbols',`review-symbols-${weight}.woff2`]].map(([family,file])=>`@font-face{font-family:${family};src:url(data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,file)).toString('base64')}) format('woff2');font-weight:${weight==='regular'?400:700}}`)).join('')+`@font-face{font-family:ReviewFigureMath;src:url(data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,'review-math.woff2')).toString('base64')}) format('woff2');font-weight:400}`;
 const license=fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','');
 return svg.replace('font-family:ReviewFigure,','font-family:ReviewFigure,ReviewFigureSymbols,ReviewFigureMath,').replace(/<svg\b[^>]*>/,tag=>tag+`<style><![CDATA[/* ${license} */\n${rules}]]></style>`);
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
 const editor=`<p class="byline-disclosure">${ko?'책임 편집: 김현중 · AI 보조 작성: Codex · 근거 기준일: 2026년 11월 2일':'Responsible editor: Hyun-Jung Kim · AI assistance: Codex · Evidence cutoff: 2 November 2026'} · <a href="#authoring-disclosure">${ko?'작성·검증 범위':'Production and verification'}</a></p>`;
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
<main class="paper"><div class="issue-meta"><span>RESEARCH LETTER</span><span>2026.11.02</span><span>${ko?'카이랄 증폭 · 자가촉매 · 고체 광학':'CHIRAL AMPLIFICATION · AUTOCATALYSIS · SOLID-STATE OPTICS'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">AI Tech Review Letters · ${cutoff}<br>${ko?'거울상 조성의 증폭과 고체의 광학 선택성.':'Chiral amplification and optical selectivity in solids.'}</footer></main></body></html>\n`;
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
