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
const cutoff='2026-10-20';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBase=(process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')||'https://infant83.github.io/AI_Tech_Review/reviews/2026-10-20_jupiter-fault-tolerant-simulation/').replace(/\/?$/,'/');
const descriptors={ko:'JUPITER의 8,192개 GH200으로 수행한 104큐비트 매직상태 배양 프로토콜의 고전 모사를 살피고, 라이브 레지스터와 메모리·잡음·오류 허용 계산의 의미를 구분한다.',en:'A source-based review of the classical simulation of a 104-qubit magic-state cultivation protocol on JUPITER, separating live-register memory, noise models and fault-tolerant computation.'};
const titles={ko:'104큐비트 프로토콜의 고전 모사: JUPITER로 시험한 매직상태 배양',en:'Classical Simulation of a 104-Qubit Protocol: Testing Magic-State Cultivation on JUPITER'};
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
  ['에이전트와 역할','root: 1차 자료 종합·한국어와 영어 집필·과학 편집·게시 통합; jupiter_cover: 개념 표지 생성; jupiter_sources: 원 논문·기술 자료 조사와 수치·모형·주장 범위 대조; jupiter_production: 한영 설명 그림·교육용 메모리 계산·수식·글꼴 조판·HTML/PDF 제작과 출력 검증; mail_inventory: 수신 DQB 메일·첨부 파일 조사와 아카이브 목록 대조.'],
  ['입력과 산출물','수신 DQB 기사, 공개 논문·공식 기술 자료 → 한영 기술 리뷰, 개념 표지, 원본 설명 그림·수식과 PDF.'],
  ['제작 요청 요약','최근 DQB를 아카이브하고 율리히 연구소의 JUPITER 매직상태 배양 모사 결과를 별도 기술 리뷰로 편집·게재.'],
  ['하네스','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>'],
  ['검증 범위','공개 1차 출처·서지·큐비트 수와 메모리 단위·잡음 모형·주장 범위를 대조하고, 한영 수치·기호·그림과 HTML/PDF 출력을 확인했다. JUPITER 계산이나 실제 양자 프로세서 실험을 재실행하지 않았다.'],
  ['사람 검토 수준','주제·작성·공개 게시 요청 확인; 문장 단위 사람 검토 없음.'],['근거 기준일',cutoff]
 ]:[
  ['Responsible editor','Hyun-Jung Kim'],['AI assistance','OpenAI Codex; exact authoring-model identifier not retained.'],
  ['Agents and roles','root: primary-source synthesis, Korean and English writing, scientific editing and publication integration; jupiter_cover: conceptual cover generation; jupiter_sources: research on the original paper and technical sources, numerical/model/claim-scope checking; jupiter_production: bilingual original figures, teaching memory calculations, equation/font typesetting, HTML/PDF production and output validation; mail_inventory: received DQB and attachment inventory and archive comparison.'],
  ['Inputs and outputs','Received DQB article and public original/official sources → bilingual review, conceptual cover, original explanatory figures/equations and PDFs.'],
  ['Production request','Archive recent DQB issues and edit a separate technical review of the Jülich JUPITER magic-state cultivation simulation for publication.'],
  ['Harness','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>'],
  ['Verification scope','Public primary sources, bibliographic records, qubit counts and memory units, noise models and claim boundaries; bilingual values, symbols, figures and HTML/PDF output. The JUPITER computation and physical quantum-processor experiments were not independently rerun.'],
  ['Human review','Topic, writing and public posting explicitly requested; no line-by-line human review.'],['Evidence cutoff',cutoff]
 ];
 return `<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">${ko?'작성·검증 정보':'How this review was made'}</h2><dl>${rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl><p>${ko?'원문의 보고 내용, 독립적인 교육용 계산, 리뷰의 개념 설명을 구분한다. AI 개념 표지는 실제 장비 사진·회로도·성능 측정값이 아니다.':'Reported source results, independent teaching calculations and conceptual explanations are distinguished. The AI-generated conceptual cover is not a photograph, circuit schematic or performance measurement.'}</p></section><!-- End AI Tech Review Authoring Disclosure -->`;
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
 const source=fs.readFileSync(path.join(root,'reports',`review_${lang}.md`),'utf8').replace(/[\u2010-\u2015]/g,'-');
 const title=source.match(/^#\s+(.+)$/m)?.[1]?.trim()||titles[lang];
 const description=(source.match(/<p class=["']dek["']>([\s\S]*?)<\/p>/)?.[1]||descriptors[lang]).replace(/<[^>]*>/g,'').trim();
 const math=[];
 const safe=source.replace(/\*\*([^\n]+?)\*\*/g,'<strong>$1</strong>').replace(/\$\$([\s\S]*?)\$\$|\\\(([\s\S]*?)\\\)/g,(_,a,b)=>{
  const result=mathImage((a||b).trim(),a!==undefined);math.push(result);
  return a!==undefined?`\n\nMATHBLOCK${math.length-1}END\n\n`:`MATHINLINE${math.length-1}END`;
 });
 let body=marked.parse(safe,{gfm:true});
 if(publicBase){
  const links={'en/index.html':publicBase+'en/','en/review_en.pdf':publicBase+'en/review_en.pdf','../index.html':publicBase,'../review_ko.pdf':publicBase+'review_ko.pdf'};
  body=body.replace(/href="([^"]+)"/g,(match,href)=>links[href]?`href="${links[href]}"`:match);
 }
 body=body.replace(/<p>MATHBLOCK(\d+)END<\/p>/g,(_,i)=>math[+i].html).replace(/MATHINLINE(\d+)END/g,(_,i)=>math[+i].html);
 body=body.replace(/<img\b[^>]*\bsrc="((?:memory_register|cultivation_flow|noise_channels)_(?:ko|en)\.svg)"[^>]*>/g,(tag,filename)=>{
  const mobile=filename.replace(/_(ko|en)\.svg$/,'_mobile_$1.svg');
  return tag.replace('<img ','<img class="figure-desktop" ')+tag.replace(filename,mobile).replace('<img ','<img class="figure-mobile" ');
 });
 let count=0;const toc=[];
 body=body.replace(/<h2(?:\s[^>]*)?>(.*?)<\/h2>/g,(_,text)=>{const id=`section-${++count}`;toc.push(`<li><a href="#${id}">${text}</a></li>`);return `<h2 id="${id}">${text}</h2>`});
 body=body.replaceAll('<table>',`<div class="table-scroll" role="region" tabindex="0" aria-label="${ko?'비교와 응용 표':'Comparison and applications table'}"><table>`).replaceAll('</table>','</table></div>');
 const editor=`<p class="byline-disclosure">${ko?'책임 편집: 김현중 · AI 보조 작성: Codex · 근거 기준일: 2026년 10월 20일':'Responsible editor: Hyun-Jung Kim · AI assistance: Codex · Evidence cutoff: 20 October 2026'} · <a href="#authoring-disclosure">${ko?'작성·검증 범위':'Production and verification'}</a></p>`;
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
<main class="paper"><div class="issue-meta"><span>RESEARCH LETTER</span><span>2026.10.20</span><span>${ko?'양자 컴퓨팅 · HPC · 오류 허용':'QUANTUM COMPUTING · HPC · FAULT TOLERANCE'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">AI Tech Review Letters · ${cutoff}<br>${ko?'오류 허용 양자 프로토콜을 고전 초고성능 컴퓨팅으로 검증하는 방법과 한계.':'Methods and limits of testing fault-tolerant quantum protocols with classical high-performance computing.'}</footer></main></body></html>\n`;
 fs.writeFileSync(path.join(dir,'index.html'),html.split('\n').map(line=>line.trimEnd()).join('\n'));
 fs.writeFileSync(path.join(dir,'review.css'),stylesheet);
 const allowedFigures=new Set(['hero.webp',`memory_register_${lang}.svg`,`cultivation_flow_${lang}.svg`,`noise_channels_${lang}.svg`,`memory_register_mobile_${lang}.svg`,`cultivation_flow_mobile_${lang}.svg`,`noise_channels_mobile_${lang}.svg`]);
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
