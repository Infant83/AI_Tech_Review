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
const cutoff='2026-10-21';
const heroFilename='hero.webp';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBase=(process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')||'https://infant83.github.io/AI_Tech_Review/reviews/2026-10-21_sparse-reference-quantum-chemistry/').replace(/\/?$/,'/');
const descriptors={ko:'희소 기준상태와 잔차로 양자화학 에너지를 읽는 원리와 성립 조건을 유도하고, 두 준위 예제와 Helios 측정 결과를 통해 정밀도·정확도·전체 비용을 살펴본다.',en:'How sparse references and residuals enable mixed energy estimation in quantum chemistry: derivations, two-level examples and a critical reading of Helios measurements, precision, accuracy and total cost.'};
const titles={ko:'양자화학의 에너지 차이를 읽는 법: 희소 기준상태와 혼합 추정량',en:'Reading Energy Differences in Quantum Chemistry: Sparse References and Mixed Estimators'};
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
  ['에이전트와 역할','root: 1차 자료 종합·한영 심층 리뷰 집필 및 주제 중심 도입 편집·과학 편집·게시 통합; seminar_science: 원 논문·부록·수치·모형·주장 범위 대조 및 독립 원고 감수; seminar_production: 한영 설명 그림·독립 2준위 계산·인터랙티브 실습·수식·글꼴·HTML/PDF 제작과 출력 검증; seminar_cover: 과학 표지 기획·생성·시각 검수; seminar_translation: 한국어 정본의 전체 영어 번역과 언어 간 수식·수치·조건 보존; implicit_structure_review: 주제 중심 구성·독자용 표현의 독립 편집 감수; revision_production: 개정 한영 HTML/PDF 재생성과 출력 검수.'],
  ['입력과 산출물','공개 논문·부록·공식 자료 → 한영 심층 기술 리뷰, 개념 표지, 원본 교육 도표·수식·합성 실습과 PDF.'],
  ['제작 요청 요약','양자화학 에너지 측정의 문제에서 시작해 유도·예제·반례·실험 해석으로 이어지는 심층 리뷰를 작성하고 공개 리뷰 허브에 게재.'],
  ['하네스','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>'],
  ['검증 범위','원 논문·부록의 식·활성공간·측정 조건·오차와 주장 범위 및 별도 SVD-THC 논리 자원 추정을 대조하고, 독립적인 합성 2준위 항등식·분산·최적 측정 배분, 한영 수식·도표·HTML/PDF 출력을 확인했다. 원 논문의 분자 계산이나 QPU 실험을 재실행하지 않았다.'],
  ['사람 검토 수준','주제 중심의 도입·표현에 대한 편집 피드백 반영; 전체 원고의 문장 단위 사람 검토 없음.'],['근거 기준일',cutoff]
 ]:[
  ['Responsible editor','Hyun-Jung Kim'],['AI assistance','OpenAI Codex; exact authoring-model identifier not retained.'],
  ['Agents and roles','root: primary-source synthesis, bilingual in-depth review writing and topic-led revision, scientific editing and publication integration; seminar_science: original-paper and supplement research, numerical/model/claim-scope checking and independent manuscript audit; seminar_production: bilingual original diagrams, independent two-level calculation, interactive lab, equation/font typesetting and HTML/PDF production and validation; seminar_cover: scientific cover planning, generation and visual review; seminar_translation: full English translation of the Korean canonical text, preserving formulas, numerical values and conditions; implicit_structure_review: independent editorial audit of topic-led framing and reader-facing wording; revision_production: revised bilingual HTML/PDF regeneration and output checks.'],
  ['Inputs and outputs','Public paper, supplement and official material → bilingual in-depth technical review, conceptual cover, original teaching figures/equations, synthetic lab and PDFs.'],
  ['Production request','Develop an in-depth review of quantum-chemical energy measurement through derivations, examples, counterexamples and experimental interpretation, then publish it in the review hub.'],
  ['Harness','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>'],
  ['Verification scope','Original-paper and supplement formulas, active spaces, measurement conditions, errors, claim boundaries and the separate SVD-THC logical-resource estimates; independent synthetic two-level identity, variance and optimal allocation; bilingual equations/figures and HTML/PDF output. The original molecular calculations and QPU experiments were not independently rerun.'],
  ['Human review','Editorial feedback on topic-led framing and wording incorporated; no line-by-line human review of the full manuscript.'],['Evidence cutoff',cutoff]
 ];
 return `<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">${ko?'작성·검증 정보':'How this review was made'}</h2><dl>${rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl><p>${ko?'논문 보고값과 독립 교육용 계산을 구분한다. 2준위 실습은 리뷰의 합성 모형이며, 표지는 실제 분자·장비 사진이나 정량 결과가 아니다.':'Reported source values and independent teaching calculations are distinguished. The two-level lab is a synthetic review model; the cover is not a photograph of a molecule or device, or a quantitative result.'}</p></section><!-- End AI Tech Review Authoring Disclosure -->`;
}

function teachingLab(ko){
 const label=(a,b)=>ko?a:b;
 return `<section class="teaching-lab" data-two-level-lab aria-label="${label('합성 2준위 실습','Synthetic two-level lab')}">
 <p class="lab-kicker">${label('리뷰의 교육용 재구성 · 논문 기본값 없음','SYNTHETIC TEACHING MODEL · NO PAPER DEFAULTS')}</p>
 <h3>${label('직접 조절하기: 기준 중첩과 측정 배분','Explore reference overlap and shot allocation')}</h3>
 <p>${label('Δ = 100 mHa, H = diag(0, Δ), 정확한 목표 상태 |0⟩. 독립적인 Bernoulli 투영 측정과 1차 분산 근사를 사용한다. 장치 잡음·누설·오류 완화·계산시간은 포함하지 않는다.','Δ = 100 mHa, H = diag(0, Δ), exact target |0⟩. Independent Bernoulli projector measurements and a first-order variance approximation; excludes device noise, leakage, mitigation and runtime.')}</p>
 <p>${label('이 모형은 pΛ+pΦ=1이지만 두 회로의 배분을 배우기 위해 각각 따로 표본추출한다. 이 특별한 관계를 이용한 단일 확률 추정은 더 적은 측정으로 가능하며, 아래 최적 배분은 두 회로라는 제약 안에서의 결과다.','Although pΛ+pΦ=1 in this model, the lab samples them separately to teach two-circuit allocation. A single-probability estimator can exploit this special relation; the optimum below is constrained to the two-circuit scheme.')}</p>
 <div class="lab-controls">
 <label for="toy-theta">${label('기준상태 각도 θ (도)','Reference angle θ (degrees)')} <output data-value="theta" for="toy-theta">30°</output><input id="toy-theta" data-theta type="range" min="1" max="89" step="1" value="30"></label>
 <label for="toy-shots">${label('채택된 총 측정 횟수 N','Total accepted shots N')} <output data-value="shots" for="toy-shots">10,000</output><input id="toy-shots" data-shots type="range" min="1000" max="50000" step="1000" value="10000"></label>
 <label for="toy-fraction">${label('잔차 측정에 배분할 비율 (%)','Fraction allocated to residual measurements (%)')} <output data-value="fraction" for="toy-fraction">75%</output><input id="toy-fraction" data-fraction type="range" min="1" max="99" step="1" value="75"></label>
 <div class="lab-buttons"><button type="button" data-lab-optimal>${label('최적 비율 적용','Apply optimal fraction')}</button><button type="button" data-lab-reset>${label('교육용 기본값으로 초기화','Reset teaching defaults')}</button></div></div>
 <svg class="lab-bars" viewBox="0 0 420 92" role="img" aria-label="${label('기준 에너지와 음의 보정 항의 크기는 같다','Reference energy and negative correction have equal magnitudes')}"><text x="0" y="21">${label('기준 에너지','Reference energy')}</text><rect x="170" y="6" width="60" height="22" fill="#11666d" data-energy-bar></rect><text x="0" y="65">${label('음의 보정 항','Negative correction')}</text><rect x="170" y="50" width="60" height="22" fill="#b77b30" data-correction-bar></rect></svg>
 <table><caption>${label('기본값 θ = 30°, N = 10,000회. 값은 모형에서 결정론적으로 계산한다.','Defaults: θ = 30°, N = 10,000. Values are calculated deterministically from the model.')}</caption><tbody>
 <tr><th>${label('기준 에너지 EΦ','Reference energy EΦ')}</th><td data-value="reference">25.0000 mHa</td><th>${label('잔차 크기 r','Residual norm r')}</th><td data-value="r">43.3013 mHa</td></tr>
 <tr><th>${label('보정 항','Correction term')}</th><td data-value="correction">-25.0000 mHa</td><th>${label('혼합 추정량','Mixed estimator')}</th><td data-value="energy">0.0000 mHa</td></tr>
 <tr><th>pΛ</th><td data-value="p">0.2500</td><th>pΦ</th><td data-value="q">0.7500</td></tr>
 <tr><th>${label('잔차 측정 횟수','Residual shots')}</th><td data-value="residual-shots">7,500</td><th>${label('기준 측정 횟수','Reference shots')}</th><td data-value="reference-shots">2,500</td></tr>
 <tr><th>${label('현재 배분의 근사 SE','Approximate SE for current allocation')}</th><td data-value="se">0.2887 mHa</td><th>${label('최적 잔차 비율','Optimal residual fraction')}</th><td data-value="optimal-fraction">75.0%</td></tr>
 <tr><th>${label('최적 배분의 근사 SE','Approximate SE at optimal allocation')}</th><td data-value="optimal-se">0.2887 mHa</td><td colspan="2">${label('단위: mHa · 측정 횟수는 채택 후 기준','Units: mHa; shot counts are after acceptance')}</td></tr>
 </tbody></table>
 <p class="lab-warning" data-rare-event hidden>${label('일부 기대 빈도가 30회 미만이다. 비선형 비율 추정량에서 이 1차 근사로 신뢰구간을 보장할 수 없다.','Some expected event counts are below 30. This first-order approximation does not guarantee a confidence interval for a nonlinear ratio estimator.')}</p>
 <p class="lab-status" data-lab-status aria-live="polite">${label('교육용 기본값에서 혼합 추정량은 0 mHa다.','At the teaching defaults, the mixed estimator is 0 mHa.')}</p>
 <noscript><p>${label('JavaScript가 꺼져 있어 교육용 기본값을 표시한다.','JavaScript is disabled; teaching defaults are shown.')}</p></noscript>
 <p class="caption">${label('0°에서 잔차는 불필요하고 90°에서 참조 중첩은 0이다. 슬라이더는 두 끝점을 제외한다. 최적화는 잔차 비율을 1% 단위로 반올림한다. 논문의 분자·회로·측정 성능을 재현한 자료가 아니다.','At 0° the residual is unnecessary; at 90° the reference overlap is zero. The slider excludes both endpoints. The optimal-fraction control rounds to 1% steps. This does not reproduce the paper’s molecules, circuits or measurement performance.')}</p></section>`;
}

function mathImage(tex,display){
 const id=crypto.createHash('sha256').update((display?'display:':'inline:')+tex).digest('hex').slice(0,14);
 const filename=`math_${id}.svg`;
 const rendered=adaptor.outerHTML(mathDocument.convert(tex,{display,em:16,ex:8,containerWidth:760}));
 const svg=rendered.match(/<svg[\s\S]*<\/svg>/)?.[0];
 if(!svg||/data-mjx-error|merror/.test(svg))throw Error(`Math typesetting failed: ${tex}`);
 const clean=svg.replace(/<title>[\s\S]*?<\/title>/,'');
 fs.writeFileSync(path.join(artifacts,filename),clean+'\n');
 const width=svg.match(/\bwidth="([\d.]+)ex"/)?.[1]||'1';
 const height=svg.match(/\bheight="([\d.]+)ex"/)?.[1]||'1';
 const valign=svg.match(/vertical-align:\s*([^;" ]+)/)?.[1]||'0';
 return {filename,html:display?`<div class="math-block"><img src="${filename}" alt="${esc(tex)}" style="width:${width}ex;height:auto"></div>`:`<img class="math-inline" src="${filename}" alt="${esc(tex)}" style="width:${width}ex;height:${height}ex;vertical-align:${valign}">`};
}

for(const lang of onlyLanguage?[onlyLanguage]:['ko','en']){
 const ko=lang==='ko';
 const source=fs.readFileSync(path.join(root,'reports',`2026-10-21_sparse-reference-quantum-chemistry_final_review${ko?'':'_en'}.md`),'utf8').replace(/[\u2010-\u2015]/g,'-');
 const title=source.match(/^#\s+(.+)$/m)?.[1]?.trim()||titles[lang];
 const description=(source.match(/<p class=["']dek["']>([\s\S]*?)<\/p>/)?.[1]||descriptors[lang]).replace(/<[^>]*>/g,'').trim();
 const math=[];
 const safe=source.replace(/\*\*([^\n]+?)\*\*/g,'<strong>$1</strong>').replace(/\$\$([\s\S]*?)\$\$|\\\(([\s\S]*?)\\\)/g,(_,a,b)=>{
  const result=mathImage((a||b).trim(),a!==undefined);math.push(result);
  return a!==undefined?`\n\nMATHBLOCK${math.length-1}END\n\n`:`MATHINLINE${math.length-1}END`;
 });
 let body=marked.parse(safe,{gfm:true});
 const hasLab=body.includes('<!-- TWO_LEVEL_EXPLORER -->');
 body=body.replace('<!-- TWO_LEVEL_EXPLORER -->',teachingLab(ko));
 if(publicBase){
  const links={'en/index.html':publicBase+'en/','en/review-en.pdf':publicBase+'en/review-en.pdf','../index.html':publicBase,'../review.pdf':publicBase+'review.pdf'};
  body=body.replace(/href="([^"]+)"/g,(match,href)=>links[href]?`href="${links[href]}"`:match);
 }
 body=body.replace(/<p>MATHBLOCK(\d+)END<\/p>/g,(_,i)=>math[+i].html).replace(/MATHINLINE(\d+)END/g,(_,i)=>math[+i].html);
 body=body.replace(/<img\b[^>]*\bsrc="((?:projection_residual|evidence_conditions|cost_chain|two_level_model)_(?:ko|en)\.svg)"[^>]*>/g,(tag,filename)=>{
  const mobile=filename.replace(/_(ko|en)\.svg$/,'_mobile_$1.svg');
  return tag.replace('<img ','<img class="figure-desktop" ')+tag.replace(filename,mobile).replace('<img ','<img class="figure-mobile" ');
 });
 let count=0;const toc=[];
 body=body.replace(/<h2(?:\s[^>]*)?>(.*?)<\/h2>/g,(_,text)=>{const id=`section-${++count}`;toc.push(`<li><a href="#${id}">${text}</a></li>`);return `<h2 id="${id}">${text}</h2>`});
 body=body.replaceAll('<table>',`<div class="table-scroll" role="region" tabindex="0" aria-label="${ko?'비교와 응용 표':'Comparison and applications table'}"><table>`).replaceAll('</table>','</table></div>');
 const countNotePrefix=ko?'표의 오차는 원문 보고의 1 standard error다.':'The uncertainties are one standard error as reported in the paper.';
 if(!body.includes('<p>'+countNotePrefix))throw Error('Missing Helios accepted-count note for the targeted print keep-together rule.');
 body=body.replace('<p>'+countNotePrefix,'<p class="helios-count-note">'+countNotePrefix);
 const editor=`<p class="byline-disclosure">${ko?'책임 편집: 김현중 · AI 보조 작성: Codex · 근거 기준일: 2026년 10월 21일':'Responsible editor: Hyun-Jung Kim · AI assistance: Codex · Evidence cutoff: 21 October 2026'} · <a href="#authoring-disclosure">${ko?'작성·검증 범위':'Production and verification'}</a></p>`;
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
 const metadata=publicBase?`<link rel="canonical" href="${esc(url)}"><link rel="alternate" hreflang="ko" href="${esc(publicBase)}"><link rel="alternate" hreflang="en" href="${esc(publicBase)}en/"><link rel="alternate" hreflang="x-default" href="${esc(publicBase)}"><meta property="og:url" content="${esc(url)}"><meta property="og:image" content="${esc(publicBase)}${heroFilename}">`:'';
 const localBadge=publicBase?'':`<span class="local-status">${ko?'로컬 검토본':'Local review copy'}</span>`;
 const html=`<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><meta name="description" content="${esc(description)}"><meta name="author" content="${ko?'김현중':'Hyun-Jung Kim'}"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(description)}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">${metadata}<link rel="stylesheet" href="review.css"></head><body>
<header><a class="brand" href="https://infant83.github.io/AI_Tech_Review/">AI TECH REVIEW LETTERS</a><div class="topline-actions">${localBadge}<nav class="language-switcher" aria-label="${ko?'언어 선택':'Language'}"><span class="language-current" aria-current="page" lang="${lang}">${ko?'한국어':'English'}</span><a href="${other}" lang="${ko?'en':'ko'}" hreflang="${ko?'en':'ko'}">${ko?'English':'한국어'}</a></nav><a class="download" href="${ko?'review.pdf':'review-en.pdf'}">PDF ↓</a></div></header>
<main class="paper"><div class="issue-meta"><span>TECH REVIEW</span><span>2026.10.21</span><span>${ko?'양자화학 · 양자 측정':'QUANTUM CHEMISTRY · QUANTUM MEASUREMENT'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="${ko?'review.pdf':'review-en.pdf'}">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">AI Tech Review Letters · ${cutoff}<br>${ko?'희소 기준상태와 혼합 추정량으로 읽는 양자화학의 에너지 차이.':'Reading quantum-chemistry energy differences with sparse references and mixed estimators.'}</footer></main>${hasLab?'<script src="two_level_explorer.js" defer></script>':''}</body></html>\n`;
 fs.writeFileSync(path.join(dir,'index.html'),html.split('\n').map(line=>line.trimEnd()).join('\n'));
 fs.writeFileSync(path.join(dir,'review.css'),stylesheet);
 const allowedFigures=new Set([heroFilename,'two_level_explorer.js',...['projection_residual','evidence_conditions','cost_chain','two_level_model'].flatMap(name=>[`${name}_${lang}.svg`,`${name}_mobile_${lang}.svg`])]);
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
  if(fs.statSync(path.join(dir,filename)).isFile()&&!assetNames.has(filename)&&!new Set(['index.html','review.css',ko?'review.pdf':'review-en.pdf']).has(filename))fs.unlinkSync(path.join(dir,filename));
 }
 outputFiles.push({language:lang,sections:count,equations:math.length,assets:assetNames.size,file:path.relative(root,path.join(dir,'index.html'))});
}
for(const result of outputFiles)console.log(JSON.stringify(result));
