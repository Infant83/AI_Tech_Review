/** Build the bilingual public review with a strict, flat local-asset allowlist. */
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifacts=path.join(root,'artifacts');
const localRequire=createRequire(import.meta.url);
const dependencyRoots=[process.env.REVIEW_NODE_MODULES,process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,path.join(root,'node_modules'),path.join(process.cwd(),'node_modules')].filter(Boolean);
function resolveDependency(spec){
 for(const directory of dependencyRoots){try{return createRequire(path.join(directory,'_build.cjs')).resolve(spec)}catch{}}
 try{return localRequire.resolve(spec)}catch{throw Error(`Missing ${spec}. Set REVIEW_NODE_MODULES or CODEX_PRIMARY_RUNTIME_NODE_MODULES.`)}
}
const {marked}=await import(pathToFileURL(resolveDependency('marked')));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const cutoff='2026-10-19';
const onlyLanguage=process.argv.find(a=>a.startsWith('--language='))?.split('=')[1];
if(onlyLanguage&&!['ko','en'].includes(onlyLanguage))throw Error('--language must be ko or en.');
const publicBase=process.argv.find(a=>a.startsWith('--public-base='))?.split('=').slice(1).join('=')?.replace(/\/?$/,'/')||'';
const descriptors={ko:'OMat24의 99% 중복성 주장을 원자·구조 비율과 힘·에너지·동역학 평가로 검토하고, 국소 화학 환경에 따른 학습 집합 압축의 의미와 한계를 정리한다.',en:'A critical review of OMat24 dataset compression through local chemical environments: the denominator behind 99% redundancy, accuracy tradeoffs, and limits of the evidence.'};
const titles={ko:'OMat24 데이터 중복성과 국소 화학 환경을 이용한 학습 집합 압축',en:'Compressing OMat24: Dataset Redundancy and Local Chemical Environments'};
let stylesheet=fs.readFileSync(path.join(artifacts,'review.css'),'utf8');
for(const weight of ['regular','bold']){
 const file=`review-${weight}.woff2`;
 stylesheet=stylesheet.replaceAll(`url('${file}')`,`url('data:font/woff2;base64,${fs.readFileSync(path.join(artifacts,file)).toString('base64')}')`);
}
stylesheet='/* '+fs.readFileSync(path.join(artifacts,'font-license.txt'),'utf8').replaceAll('*/','')+' */\n'+stylesheet;

function disclosure(ko){
 const rows=ko?[
  ['책임 편집자','김현중'],['AI 보조','OpenAI Codex · 정확한 작성 모델 식별자: 미보존'],
  ['에이전트와 역할','root: 원문·공개 CSV 대조, 수치 계산, 한국어 집필·편집과 게시; identify_paper: 독립 논문 식별·선행연구 조사·영문 집필; critical_audit: 수치·방법론 감사; publication_build: 결정론적 비교 그림, 폰트·한영 HTML/PDF 제작과 출력 검사.'],
  ['입력과 산출물','논문과 공식 공개 코드·결과 자료 → 한영 기술 리뷰, 개념 표지, 수치 비교 그림과 PDF.'],
  ['제작 요청 요약','대규모 재료 데이터 중복성과 국소 화학 환경 선별 논문을 검토하고 AI Tech Review에 정리·보관.'],
  ['하네스','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>'],
  ['검증 범위','arXiv v1 본문·보충자료와 고정 commit 공개 결과의 수치·단위·해석 범위 대조; 원자·구조 비율과 오차의 산술 확인; 한영 제목·자산·모바일·PDF 출력 확인. DFT·모델 학습·MD는 재실행하지 않았다.'],
  ['사람 검토 수준','주제·리뷰·아카이브 발행 요청 확인; 문장별 사람 승인 없음.'],['근거 기준일',cutoff]
 ]:[
  ['Responsible editor','Hyun-Jung Kim'],['AI assistance','OpenAI Codex; exact authoring-model identifier not retained.'],
  ['Agents and roles','root: original-paper and public-CSV checks, arithmetic, Korean writing, editing and publication; identify_paper: independent paper identification, prior-work research and English writing; critical_audit: numerical and methodological audit; publication_build: deterministic comparison figure, fonts, bilingual HTML/PDF production and output checks.'],
  ['Inputs and outputs','Paper and official public code/results → bilingual review, conceptual cover, numerical comparison figure and PDFs.'],
  ['Production request','Review the paper on materials-dataset redundancy and local-environment selection, then summarize and archive it in AI Tech Review.'],
  ['Harness','<a href="https://infant83.github.io/AI_Tech_Review/methods/">AI Tech Review Editorial Harness 2026.08</a>'],
  ['Verification scope','arXiv v1 text/supplement and fixed-commit public outputs: values, units and interpretation; arithmetic on atom/structure shares and errors; bilingual titles, assets, mobile layout and PDF output. No rerun of DFT, model training or MD.'],
  ['Human review','Topic, review and archive publication requested; no line-by-line human approval.'],['Evidence cutoff',cutoff]
 ];
 return `<!-- AI Tech Review Authoring Disclosure --><section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading"><h2 id="disclosure-heading">${ko?'작성·검증 정보':'How this review was made'}</h2><dl>${rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl><p>${ko?'논문 보고 결과, 공개 결과의 산술 확인, 리뷰 해석과 적용 제안을 구분한다. 표지는 AI로 만든 개념 그림이며 실제 원자 구조나 계산 결과가 아니다. 수치 비교 그림은 저자 공개값을 코드로 다시 그렸다.':'Reported findings, arithmetic on public outputs, review interpretation and application proposals are distinguished. The AI-generated cover is conceptual, with no measured atomic structure or computed result. The numerical chart redraws the authors’ public values in code.'}</p></section><!-- End AI Tech Review Authoring Disclosure -->`;
}

const outputFiles=[];
for(const lang of onlyLanguage?[onlyLanguage]:['ko','en']){
 const ko=lang==='ko';
 const source=fs.readFileSync(path.join(root,'reports',`review_${lang}.md`),'utf8');
 if(/(?:\/Users\/|\/tmp\/|file:\/\/|\.\.\/\.\.\/(?:notes|sources)\/)/.test(source))throw Error(`Private or host-local material in ${lang} source.`);
 const title=source.match(/^#\s+(.+)$/m)?.[1]?.trim();
 if(title!==titles[lang])throw Error(`Unexpected ${lang} review title.`);
 let body=marked.parse(source,{gfm:true});
 if(publicBase){
  const links={'en/index.html':publicBase+'en/','en/review_en.pdf':publicBase+'en/review_en.pdf','../index.html':publicBase,'../review_ko.pdf':publicBase+'review_ko.pdf'};
  body=body.replace(/href="([^"]+)"/g,(match,href)=>links[href]?`href="${links[href]}"`:match);
 }
 let count=0;const toc=[];
 body=body.replace(/<h2(?:\s[^>]*)?>(.*?)<\/h2>/g,(_,text)=>{const id=`section-${++count}`;toc.push(`<li><a href="#${id}">${text}</a></li>`);return `<h2 id="${id}">${text}</h2>`});
 body=body.replaceAll('<table>',`<div class="table-scroll" role="region" tabindex="0" aria-label="${ko?'비교 표':'Comparison table'}"><table>`).replaceAll('</table>','</table></div>');
 const editor=`<div class="editor-line">${ko?'책임 편집: 김현중 · AI 보조 작성: Codex · 근거 기준일: 2026년 10월 19일':'Responsible editor: Hyun-Jung Kim · AI assistance: Codex · Evidence cutoff: 19 October 2026'} · <a href="#authoring-disclosure">${ko?'작성·검증 범위':'Production and verification'}</a></div>`;
 const heroEnd=body.indexOf('</figure>');
 const tocHTML=`<details class="toc"><summary>${ko?'내용 살펴보기':'Contents'}</summary><ol>${toc.join('')}</ol></details>`;
 if(heroEnd>=0){
  const heroStart=body.lastIndexOf('<figure',heroEnd);
  body=body.slice(0,heroStart)+editor+body.slice(heroStart,heroEnd+9)+tocHTML+body.slice(heroEnd+9);
 }else throw Error(`Missing conceptual hero figure in ${lang}.`);
 const dir=path.join(root,'dist',ko?'':'en');fs.mkdirSync(dir,{recursive:true});
 const other=publicBase?publicBase+(ko?'en/':''):(ko?'en/index.html':'../index.html');
 const url=publicBase?publicBase+(ko?'':'en/'):'';
 const metadata=publicBase?`<link rel="canonical" href="${esc(url)}"><link rel="alternate" hreflang="ko" href="${esc(publicBase)}"><link rel="alternate" hreflang="en" href="${esc(publicBase)}en/"><link rel="alternate" hreflang="x-default" href="${esc(publicBase)}"><meta property="og:url" content="${esc(url)}"><meta property="og:image" content="${esc(publicBase)}hero.webp"><meta property="article:published_time" content="2026-10-19">`:'';
 const localBadge=publicBase?'':`<span class="local-status">${ko?'로컬 검토본':'Local review copy'}</span>`;
 const html=`<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><meta name="description" content="${esc(descriptors[lang])}"><meta name="author" content="${ko?'김현중':'Hyun-Jung Kim'}"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(descriptors[lang])}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">${metadata}<link rel="stylesheet" href="review.css"></head><body>
<header><a class="brand" href="https://infant83.github.io/AI_Tech_Review/">AI TECH REVIEW LETTERS</a><div class="topline-actions">${localBadge}<nav class="language-switcher" aria-label="${ko?'언어 선택':'Language'}"><span class="language-current" aria-current="page" lang="${lang}">${ko?'한국어':'English'}</span><a href="${other}" lang="${ko?'en':'ko'}" hreflang="${ko?'en':'ko'}">${ko?'English':'한국어'}</a></nav><a class="download" href="review_${lang}.pdf">PDF ↓</a></div></header>
<main class="paper"><div class="issue-meta"><span>RESEARCH LETTER</span><span>2026.10.19</span><span>${ko?'재료 데이터 · 원자간 포텐셜 · 과학기계학습':'MATERIALS DATA · INTERATOMIC POTENTIALS · SCIENTIFIC ML'}</span></div><article>${body}${disclosure(ko)}</article><div class="downloads"><a href="review_${lang}.pdf">${ko?'한국어 PDF 내려받기':'Download English PDF'}</a><a href="${other}">${ko?'English version':'한국어판'}</a></div><footer class="footer">AI Tech Review Letters · ${cutoff}<br>${ko?'재료 데이터 압축의 정확도와 적용 범위를 검토하는 기술 리뷰.':'A critical review of accuracy and scope in materials-dataset compression.'}</footer></main></body></html>\n`;
 fs.writeFileSync(path.join(dir,'index.html'),html);
 fs.writeFileSync(path.join(dir,'review.css'),stylesheet);
 const publicMarkdown=source.replace(/^#\s+.+$/m,heading=>heading+'\n\n'+editor)+'\n'+disclosure(ko)+'\n';
 fs.writeFileSync(path.join(dir,`review_${lang}.md`),publicMarkdown);
 const assetNames=new Set(['review-regular.woff2','review-bold.woff2','font-license.txt']);
 for(const match of html.matchAll(/\bsrc="([^"#]+)"/g)){
  if(!/^(?:https?:|data:|\/)/.test(match[1]))assetNames.add(match[1]);
 }
 const allowedAssets=new Set(['hero.webp',`force_mae_${lang}.svg`,'review-regular.woff2','review-bold.woff2','font-license.txt']);
 for(const filename of assetNames){
  if(path.basename(filename)!==filename||!allowedAssets.has(filename))throw Error(`Asset outside public allowlist: ${filename}`);
  const asset=path.join(artifacts,filename);if(!fs.existsSync(asset))throw Error(`Missing asset: ${filename}`);
  fs.copyFileSync(asset,path.join(dir,filename));
 }
 outputFiles.push({language:lang,sections:count,assets:assetNames.size,file:path.relative(root,path.join(dir,'index.html'))});
}
for(const result of outputFiles)console.log(JSON.stringify(result));
