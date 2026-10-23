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
const cutoff='2026-10-23';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBase=(process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')||'https://infant83.github.io/AI_Tech_Review/reviews/2026-10-23_quantum-latent-generative-models/').replace(/\/?$/,'/');
const descriptors={ko:'광양자 샘플링을 생성모형의 출발 분포에 사용하는 연구를 검토하고, 분자 생성의 성과·비교 기준·양자 계산의 실행 범위를 설명한다.',en:'Photonic quantum sampling as a starting distribution for generative models: molecular-design results, matched classical comparisons and the scope of quantum execution.'};
const titles={ko:'광양자 샘플링과 생성형 AI: 출발 분포는 분자 설계를 바꾸는가',en:'Photonic Quantum Sampling and Generative AI: Can Starting Distributions Change Molecular Design?'};
// Optional stems are permitted, but only explicitly referenced assets are copied.
const figureStems=['sampling_pipeline','hom_interference','qm9_results','toy_latents'];
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
  ['에이전트와 역할','root: 1차 자료 종합·한국어 집필·원본 개념 표지·과학 편집·게시 통합; academic_sources: 원 논문·방법·보고 수치와 주장 범위의 과학 감수; applications_sources: 응용·고전 비교 기준·제한 CPU 학습 실행·확률의 정확 검사·설명 도표; academic_sources/theory_crosscheck: 수학 정리와 가정 교차 검토; review_format: 한영 수식·글꼴 조판·안정적인 수식 SVG·HTML/PDF 제작 및 게시 출력 검사; publish_audit: 독립 설명·개념 표지 감사, 영어 전문 번역, 공개 메타데이터·링크·자산·작성 공개 정보 감사.'],
  ['입력과 산출물','공유 자료, 공개 논문·공식 코드 및 문서 → 한영 기술 리뷰, 개념 표지, 설명용 도표·수식과 PDF.'],
  ['제작 요청 요약','광양자 샘플링을 생성모형에 사용하는 연구를 설명하고, 분자 설계의 보고 결과와 고전 기준선·실행 조건을 대조한 기술 리뷰를 작성·공개.'],
  ['하네스','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a> · 과학 설명과 시각 전달 준칙 1.0(2026-10-22)'],
  ['검증 범위','공개 1차 출처·서지·방법·보고 수치와 실행 범위, 한영 기호·수식·도표 및 HTML/PDF 출력 대조. 고전 CPU에서 한 훈련 시드의 합성 점 데이터 예제를 제한적으로 학습·실행했다. 논문 Figure 1의 세 루프 예제·QM9·단백질 생성·QPU 실험은 독립 재현하지 않았다.'],
  ['사람 검토 수준','주제·작성·공개 게시 요청 확인; 문장 단위 사람 승인 없음.'],['근거 기준일',cutoff]
 ]:[
  ['Responsible editor','Hyun-Jung Kim'],['AI assistance','OpenAI Codex; exact authoring-model identifier not retained.'],
  ['Agents and roles','root: primary-source synthesis, Korean writing, original conceptual cover, scientific editing and publication integration; academic_sources: scientific audit of the original paper, methods, reported values and claim scope; applications_sources: applications, classical comparators, limited CPU training runs, exact probability checks and explanatory figures; academic_sources/theory_crosscheck: independent theory and assumption crosscheck; review_format: bilingual equation/font typesetting, stable equation SVGs, HTML/PDF production and publication-output checks; publish_audit: independent explanation and conceptual-cover review, full English translation, publication metadata, link, asset and disclosure audit.'],
  ['Inputs and outputs','Shared material and public papers, official code/documentation → bilingual review, conceptual cover, explanatory figures/equations and PDFs.'],
  ['Production request','Explain research using photonic quantum sampling in generative models, and publish a technical review of reported molecular-design results, classical comparators and execution conditions.'],
  ['Harness','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>; Scientific Explanation and Visual Communication Principles 1.0 (2026-10-22)'],
  ['Verification scope','Public primary sources, bibliographic records, methods, reported values and execution boundaries; bilingual notation, equations, figures and HTML/PDF output. A synthetic point-data example was trained and run in a limited classical-CPU experiment with one training seed. The three-loop example in paper Figure 1, QM9, protein generation and QPU experiments were not independently reproduced.'],
  ['Human review','Topic, writing and public posting explicitly requested; no line-by-line human approval.'],['Evidence cutoff',cutoff]
 ];
 return `<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">${ko?'작성·검증 정보':'How this review was made'}</h2><dl>${rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl><p>${ko?'논문 보고 결과, 리뷰의 설명용 재구성과 응용 제안을 구분한다. 표지는 AI로 만든 개념 그림이며 실제 장치·분자 구조나 성능 데이터가 아니다.':'Reported results, teaching reconstructions and proposed applications are distinguished. The AI-generated cover is conceptual, not an actual device, molecular structure or performance dataset.'}</p></section><!-- End AI Tech Review Authoring Disclosure -->`;
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
 const editor=`<p class="byline-disclosure">${ko?'책임 편집: 김현중 · AI 보조 작성: Codex · 근거 기준일: 2026년 10월 23일':'Responsible editor: Hyun-Jung Kim · AI assistance: Codex · Evidence cutoff: 23 October 2026'} · <a href="#authoring-disclosure">${ko?'작성·검증 범위':'Production and verification'}</a></p>`;
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
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><meta name="description" content="${esc(description)}"><meta name="author" content="${ko?'김현중':'Hyun-Jung Kim'}"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(description)}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">${metadata}<link rel="stylesheet" href="review.css"></head><body>
<header><a class="brand" href="https://infant83.github.io/AI_Tech_Review/">AI TECH REVIEW LETTERS</a><div class="topline-actions">${localBadge}<nav class="language-switcher" aria-label="${ko?'언어 선택':'Language'}"><span class="language-current" aria-current="page" lang="${lang}">${ko?'한국어':'English'}</span><a href="${other}" lang="${ko?'en':'ko'}" hreflang="${ko?'en':'ko'}">${ko?'English':'한국어'}</a></nav><a class="download" href="review_${lang}.pdf">PDF ↓</a></div></header>
<main class="paper"><div class="issue-meta"><span>RESEARCH LETTER</span><span>2026.10.23</span><span>${ko?'광양자 샘플링 · 생성모형 · 분자 설계':'PHOTONIC SAMPLING · GENERATIVE MODELS · MOLECULAR DESIGN'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">AI Tech Review Letters · ${cutoff}<br>${ko?'출발 분포와 생성모형, 분자 설계를 연결하는 해설.':'Starting distributions, generative models and molecular design.'}</footer></main></body></html>\n`;
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
