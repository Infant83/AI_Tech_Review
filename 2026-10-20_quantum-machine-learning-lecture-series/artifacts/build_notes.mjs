#!/usr/bin/env node
// Set REVIEW_NODE_MODULES to one or more node_modules directories, separated
// by the platform path delimiter. Needs marked and mathjax-full.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const bases = (process.env.REVIEW_NODE_MODULES || '').split(path.delimiter).filter(Boolean);
function dependency(name) {return require.resolve(name, {paths:bases.length ? bases : [ROOT]});}
const {marked} = await import(pathToFileURL(dependency('marked')));
const {mathjax} = require(dependency('mathjax-full/js/mathjax.js'));
const {TeX} = require(dependency('mathjax-full/js/input/tex.js'));
const {SVG} = require(dependency('mathjax-full/js/output/svg.js'));
const {liteAdaptor} = require(dependency('mathjax-full/js/adaptors/liteAdaptor.js'));
const {RegisterHTMLHandler} = require(dependency('mathjax-full/js/handlers/html.js'));
const {AllPackages} = require(dependency('mathjax-full/js/input/tex/AllPackages.js'));
const adaptor = liteAdaptor(); RegisterHTMLHandler(adaptor);
const math = mathjax.document('', {InputJax:new TeX({packages:AllPackages}), OutputJax:new SVG({fontCache:'none'})});
const DIST = path.join(ROOT,'dist');
const lectureFiles = (await fs.readdir(path.join(ROOT,'lectures'))).filter(n=>n.endsWith('.md')).sort();
const ordered = ['README.md','syllabus.md','study-guide.md','math-primer.md','glossary.md',...lectureFiles.map(n=>'lectures/'+n),'self-study-workbook.md','labs/README.md','projects/capstone.md','sources.md'];
const assetAllowlist = ['labs/qml_labs.py','labs/pennylane_compare.py','labs/requirements.txt',
  'labs/requirements-pennylane.txt','labs/sdk-lock.txt','labs/qpu_submission_template.json',
  'labs/results/reference-results.json','labs/results/pennylane-results.json'];
const figureAllowlist = ['gradient-variance.svg','shot-error.svg','signal-attenuation.svg'];
const ids = new Map(ordered.map(file=>[file, 'doc-'+file.replace(/\.md$/,'').replace(/[^a-zA-Z0-9]+/g,'-').toLowerCase()]));
const escape = s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let equationCount=0;
function renderMarkdown(source, filename) {
  const code=[];
  // Protect fenced blocks and inline code before detecting any TeX delimiter.
  source=source.replace(/(^```[^\n]*\n[\s\S]*?^```[^\n]*$|^~~~[^\n]*\n[\s\S]*?^~~~[^\n]*$)/gm,
    value=>{const i=code.push(value)-1;return `QMLCODEPROTECTED${i}END`;});
  source=source.replace(/(`+)([^`]*?)\1/g,(value)=>{const i=code.push(value)-1;return `QMLCODEPROTECTED${i}END`;});
  const equations=[];
  source=source.replace(/\$\$([\s\S]*?)\$\$|\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)/g,
    (value,a,b,c)=>{const tex=a??b??c;const display=c===undefined;const i=equations.push({tex,display})-1;return `QMLMATHTOKEN${i}END`;});
  source=source.replace(/QMLCODEPROTECTED(\d+)END/g,(_,i)=>code[Number(i)]);
  let html=marked.parse(source,{gfm:true,breaks:false});
  for(let i=0;i<equations.length;i++) {
    const {tex,display}=equations[i];
    const node=math.convert(tex,{display,em:16,ex:8,containerWidth:760});
    const svg=adaptor.outerHTML(node);
    if(svg.includes('data-mjx-error') || svg.includes('data-mml-node="merror"')) throw new Error('TeX error in '+filename+': '+tex);
    equationCount++;
    const token=`QMLMATHTOKEN${i}END`;
    const content=`<${display?'div':'span'} class="math-${display?'display':'inline'}" aria-label="${escape(tex)}">${svg}</${display?'div':'span'}>`;
    if(display) html=html.replace(`<p>${token}</p>`,content);
    html=html.replaceAll(token,content);
  }
  html=html.replace(/<table>/g,'<div class="table-wrap"><table>').replace(/<\/table>/g,'</table></div>');
  html=html.replace(/<p>(<img\b[^>]*>)<\/p>\s*<p>(그림 \d+-\d+\.[\s\S]*?)<\/p>/g,
    '<figure class="teaching-figure">$1<figcaption>$2</figcaption></figure>');
  const tailParagraph=[...html.matchAll(/<p>([\s\S]*?)<\/p>/g)].at(-1);
  if(tailParagraph && !tailParagraph[1].replace(/<a\b[^>]*>[\s\S]*?<\/a>/g,'').replace(/[·\s]/g,''))
    html=html.slice(0,tailParagraph.index)+html.slice(tailParagraph.index).replace('<p>','<p class="document-nav">');
  if(filename==='glossary.md') {
    html=html.replace(/<h3>(G\d{3})\. ([\s\S]*?)<\/h3>([\s\S]*?)(?=<h[23]>|$)/g,
      (_,key,title,body)=>`<div class="term-entry" id="term-${key.toLowerCase()}"><h3>${key}. ${title}</h3>${body}</div>`);
    html=html.replace(/(<h1>[\s\S]*?<\/h1>)/,'$1<div class="glossary-search"><label for="term-query">용어 검색 · 한국어 / English / 약어</label><input id="term-query" type="search" placeholder="예: 불편 추정량, RKHS, parameter shift" autocomplete="off"><p id="term-count" role="status" aria-live="polite">144개 항목</p></div>');
  }
  if(filename.startsWith('lectures/')) {
    const headings=[...html.matchAll(/<h2>([^<]+)<\/h2>/g)];
    const last=headings.at(-1);
    if(last&&/^(읽을 자료|더 읽기와 실습|원문|읽기와 검증 범위)/.test(last[1]))
      html=html.slice(0,last.index)+'<div class="references">'+html.slice(last.index)+'</div>';
  }
  html=html.replace(/src="([^"]*)"/g,(whole,raw)=>{
    const local=path.posix.normalize(path.posix.join(path.posix.dirname(filename),raw));
    const name=path.posix.basename(local);
    if(local==='artifacts/'+name&&figureAllowlist.includes(name))return 'src="'+name+'"';
    throw new Error('Unapproved image in '+filename+': '+raw);
  });
  html=html.replace(/href="([^"]*)"/g,(whole,raw)=> {
    const href=raw.replaceAll('&amp;','&');
    if(/^(https?:|mailto:|#)/.test(href)) return whole;
    const [file,fragment]=href.split('#');
    const local=path.posix.normalize(path.posix.join(path.posix.dirname(filename),decodeURIComponent(file)));
    if(ids.has(local)) return 'href="#'+(fragment?escape(decodeURIComponent(fragment)):ids.get(local))+'"';
    if(local==='dist/index.html'||local==='index.html') return 'href="#front-cover"';
    if(local==='output/pdf/quantum-machine-learning-lecture-notes-ko.pdf'||local==='dist/notes.pdf') return 'href="notes.pdf"';
    if(assetAllowlist.includes(local)) return 'href="'+escape(local)+'"';
    if(local==='labs/.gitignore') return '';
    if(local==='labs/README') return 'href="#'+ids.get('labs/README.md')+'"';
    throw new Error('Unapproved local link in '+filename+': '+href+' -> '+local);
  });
  return html;
}
const documents=[];
for(const filename of ordered) {
  const source=await fs.readFile(path.join(ROOT,filename),'utf8');
  const heading=(source.match(/^#\s+(.+)$/m)||[])[1]||filename;
  documents.push({filename,heading,html:renderMarkdown(source,filename)});
}
// Only the explicit source list, code/data allowlist, fonts and license are copied.
await fs.rm(DIST,{recursive:true,force:true}); await fs.mkdir(path.join(DIST,'assets'),{recursive:true});
for(const asset of assetAllowlist) {const dest=path.join(DIST,asset);await fs.mkdir(path.dirname(dest),{recursive:true});await fs.copyFile(path.join(ROOT,asset),dest);}
for(const name of figureAllowlist) await fs.copyFile(path.join(ROOT,'artifacts',name),path.join(DIST,name));
await fs.copyFile(path.join(ROOT,'artifacts','figure-manifest.json'),path.join(DIST,'assets','figure-manifest.json'));
for(const style of ['regular','bold']) await fs.copyFile(path.join(ROOT,'artifacts','fonts',`qml-sans-${style}.woff2`),path.join(DIST,'assets',`qml-sans-${style}.woff2`));
await fs.copyFile(path.join(ROOT,'artifacts','font-OFL.txt'),path.join(DIST,'assets','font-OFL.txt'));
await fs.copyFile(path.join(ROOT,'artifacts','notes.css'),path.join(DIST,'notes.css'));
const nav=documents.map(doc=>`<li><a href="#${ids.get(doc.filename)}">${escape(doc.heading)}</a></li>`).join('\n');
const sections=documents.map(doc=>`<section class="document" id="${ids.get(doc.filename)}" data-source="${escape(doc.filename)}">${doc.html}<footer>독립 한국어 렉처 노트 · 근거 기준일 2026-10-20 · <a href="#front-cover">표지와 목차로</a></footer></section>`).join('\n');
const html=`<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="수학 준비편·한영 용어 144항목·80분 강의 18개·풀이 72문제·실습 5개로 구성한 독립 양자 머신러닝 자율학습서."><meta name="author" content="김현중"><title>퀀텀 머신러닝: 데이터, 학습과 양자 우위의 조건</title><link rel="stylesheet" href="notes.css"></head><body><a class="skip" href="#front-cover">본문 바로가기</a><aside class="sidebar"><div class="brand">QUANTUM MACHINE LEARNING</div><h2>데이터, 학습과<br>양자 우위의 조건</h2><p>독립 한국어 렉처 노트<br>18강 · 72문제 · 용어 144항목<br>수학 준비편 · 실습 5개 · 프로젝트 3개</p><a class="download" href="notes.pdf">통합 PDF 내려받기</a><details id="navigation" open><summary>전체 목차 펼치기 / 접기</summary><ol><li><a href="#front-cover">표지</a></li>${nav}</ol></details></aside><main class="workspace"><section id="front-cover" class="cover"><div><div class="eyebrow">LECTURE NOTE ARCHIVE · 2026.10</div><h1>퀀텀 머신러닝:<br>데이터, 학습과<br>양자 우위의 조건</h1><p class="subtitle">수학의 기초에서 최신 연구의 주장까지<br>직접 계산하며 읽는 독립 학습 시리즈</p></div><div><p class="scope">CMU 17-620의 공개 실라버스에서 출발해 수학 준비편, 한영 용어 144항목, 80분 강의 18개와 풀이 72문제, 실습 5개, 최종 프로젝트 3개를 한 권으로 묶었다. 원강의 녹취·공식 교재·강사 승인 자료가 아니다.</p><p class="edition">책임 편집 김현중 · AI 보조 OpenAI Codex<br>근거 기준일 2026-10-20 · 판본 2.0<br>직접 실행 범위: CPU 기반 고전 시뮬레이션</p></div></section>${sections}</main><script>if(innerWidth<=720)document.getElementById('navigation').open=false;document.querySelectorAll('.sidebar a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{if(innerWidth<=720)document.getElementById('navigation').open=false}));const termQuery=document.getElementById('term-query');if(termQuery){const entries=[...document.querySelectorAll('.term-entry')];termQuery.addEventListener('input',()=>{const query=termQuery.value.trim().toLocaleLowerCase();let visible=0;for(const entry of entries){entry.hidden=!entry.textContent.toLocaleLowerCase().includes(query);if(!entry.hidden)visible++;}document.getElementById('term-count').textContent=visible+' / '+entries.length+'개 항목';});}</script></body></html>`;
if(/(?:\/Users\/|\/tmp\/|file:\/\/\/|QMLMATHTOKEN|QMLCODEPROTECTED)/.test(html))throw new Error('Private path or unresolved token in output');
await fs.writeFile(path.join(DIST,'index.html'),html);
console.log(JSON.stringify({documents:documents.length,equations:equationCount,approved_downloads:assetAllowlist.length,html_bytes:Buffer.byteLength(html)}));
