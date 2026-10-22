import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const bases=(process.env.REVIEW_NODE_MODULES||'').split(path.delimiter).filter(Boolean);
const dep=name=>require.resolve(name,{paths:bases.length?bases:[ROOT]});
const {marked}=await import(pathToFileURL(dep('marked')));
const {mathjax}=require(dep('mathjax-full/js/mathjax.js'));
const {TeX}=require(dep('mathjax-full/js/input/tex.js'));
const {SVG}=require(dep('mathjax-full/js/output/svg.js'));
const {liteAdaptor}=require(dep('mathjax-full/js/adaptors/liteAdaptor.js'));
const {RegisterHTMLHandler}=require(dep('mathjax-full/js/handlers/html.js'));
const {AllPackages}=require(dep('mathjax-full/js/input/tex/AllPackages.js'));
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const math=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'none'})});
const ordered=['README.md','sessions/01-new-platform.md','sessions/02-cuda-q-finance.md','sessions/03-ai-agents.md','sessions/04-finance-foundations.md','technical-companion.md','glossary.md','workbook.md','sources.md'];
const figureManifest=JSON.parse(await fs.readFile(path.join(ROOT,'figures','manifest.json'),'utf8'));
const figureFiles=new Set(figureManifest.figures.map(f=>f.file));
for(const f of figureFiles)if(!/^figures\/(concepts|screens)\/[a-z0-9-]+\.(svg|png)$/.test(f))throw new Error('Invalid figure allowlist entry '+f);
const usedFigures=new Set();
const ids=new Map(ordered.map((f,i)=>[f,'chapter-'+i]));
const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let equations=0;
function render(source,file){
 const code=[];source=source.replace(/(^```[^\n]*\n[\s\S]*?^```[^\n]*$|`+[^`\n]*`+)/gm,v=>'CODETOKEN'+(code.push(v)-1)+'END');
 const eq=[];source=source.replace(/\$\$([\s\S]*?)\$\$|\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)/g,(v,a,b,c)=>'MATHTOKEN'+(eq.push({tex:a??b??c,display:c===undefined})-1)+'END');
 source=source.replace(/CODETOKEN(\d+)END/g,(_,i)=>code[+i]);
 let html=marked.parse(source,{gfm:true});
 eq.forEach(({tex,display},i)=>{
  const svg=adaptor.outerHTML(math.convert(tex,{display,em:16,ex:8,containerWidth:760}));
  if(/data-mjx-error|data-mml-node="merror"/.test(svg))throw new Error(file+': invalid TeX '+tex);
  const token='MATHTOKEN'+i+'END';const value='<'+(display?'div':'span')+' class="math-'+(display?'display':'inline')+'" aria-label="'+esc(tex)+'">'+svg+'</'+(display?'div':'span')+'>';
  if(display)html=html.replace('<p>'+token+'</p>',value);html=html.replaceAll(token,value);equations++;
 });
 let h=0;html=html.replace(/<h([1-6])>/g,(_,n)=>'<h'+n+' id="'+ids.get(file)+'-heading-'+(h++)+'">');
 html=html.replace(/<table>/g,'<div class="table-wrap"><table>').replace(/<\/table>/g,'</table></div>');
 html=html.replace(/<p>(<img\b[^>]*>)<\/p>\s*<p>(그림 (\d+-\d+)\.[\s\S]*?)<\/p>/g,(_,img,caption,num)=>{
  const src=img.match(/src="([^"]+)"/)?.[1];
  return '<figure class="teaching-figure'+(src.includes('/screens/')?' replay-figure':' concept-figure')+'" id="fig-'+num+'"><a class="figure-zoom" href="'+src+'" target="_blank" rel="noopener" aria-label="그림 '+num+' 원본 크게 보기">'+img+'</a><figcaption>'+caption+'</figcaption></figure>';
 });
 html=html.replace(/src="([^"]+)"/g,(_,raw)=>{
  const local=path.posix.normalize(path.posix.join(path.posix.dirname(file),decodeURIComponent(raw)));
  if(!figureFiles.has(local))throw new Error(file+': unapproved image '+raw);
  usedFigures.add(local);return 'src="'+esc(local)+'"';
 });
 html=html.replace(/href="([^"]+)"/g,(whole,raw)=>{
  if(/^(https?:|#)/.test(raw))return whole;
  const [name,fragment]=raw.split('#');
  const local=path.posix.normalize(path.posix.join(path.posix.dirname(file),decodeURIComponent(name)));
  if(figureFiles.has(local))return 'href="'+esc(local)+'"';
  if(ids.has(local))return 'href="#'+ids.get(local)+'"';
  if(local==='dist/index.html')return 'href="#cover"';
  if(local==='output/pdf/classiq-talk-series-notes-ko.pdf')return 'href="notes.pdf"';
  throw new Error(file+': unapproved link '+raw);
 });
 return html;
}
const docs=[];for(const file of ordered){const source=await fs.readFile(path.join(ROOT,file),'utf8');docs.push({file,title:source.match(/^# (.+)$/m)?.[1]||file,html:render(source,file)});}
const dist=path.join(ROOT,'dist');await fs.mkdir(path.join(dist,'assets'),{recursive:true});
// Only explicitly named final files are copied; raw audio/transcripts remain private.
for(const f of ['notes.css','font-OFL.txt'])await fs.copyFile(path.join(ROOT,'artifacts',f),path.join(dist,f));
for(const style of ['regular','bold'])await fs.copyFile(path.join(ROOT,'artifacts','fonts','qml-sans-'+style+'.woff2'),path.join(dist,'assets','qml-sans-'+style+'.woff2'));
if(usedFigures.size!==figureFiles.size)throw new Error('Manifest contains unused figures: '+[...figureFiles].filter(f=>!usedFigures.has(f)).join(', '));
for(const f of figureFiles){const target=path.join(dist,f);await fs.mkdir(path.dirname(target),{recursive:true});await fs.copyFile(path.join(ROOT,f),target);}
await fs.copyFile(path.join(ROOT,'figures','manifest.json'),path.join(dist,'figures','manifest.json'));
const nav=docs.map(d=>'<li><a href="#'+ids.get(d.file)+'">'+esc(d.title)+'</a></li>').join('');
const body=docs.map(d=>'<section class="document" id="'+ids.get(d.file)+'" data-source="'+esc(d.file)+'">'+d.html+'<footer>Classiq 최근 토크시리즈 · 한국어 상세 노트 · 2026-10-22</footer></section>').join('\n');
const html='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="author" content="김현중"><meta name="description" content="Classiq 최근 네 회의 실제 다시보기와 질의응답, 기술 보충 해설·용어·복습 풀이."><title>Classiq 최근 토크시리즈 상세 학습 노트</title><link rel="stylesheet" href="notes.css"></head><body><a class="skip" href="#cover">본문 바로가기</a><aside class="sidebar"><div class="brand">CLASSIQ REPLAY NOTES</div><h2>양자 문제의 모델링에서<br>회로 실행과 평가까지</h2><p>2026년 7–10월 네 회차<br>실제 질의응답 · 보충 해설<br>용어집 · 복습문제와 풀이</p><a class="download" href="notes.pdf">통합 PDF 내려받기</a><details id="navigation" open><summary>목차 펼치기 / 접기</summary><ol>'+nav+'</ol></details></aside><main class="workspace"><section class="cover" id="cover"><div><div class="eyebrow">CLASSIQ · QUANTUM OFFICE HOURS</div><h1>Classiq 최근 토크시리즈<br>상세 학습 노트</h1><p class="subtitle">모델링 · 합성 · 실행 · 해석<br>네 회의 다시보기와 실제 질의응답</p></div><div><p class="scope">새 플랫폼과 AI 에이전트, 금융 모델링과 NVIDIA CUDA-Q 연동을 원영상의 흐름에 따라 읽는다. 원리의 유도와 손계산, 용어집과 복습문제 풀이를 함께 수록했다.</p><p class="edition">책임 편집 김현중 · AI 보조 OpenAI Codex<br>기준일 2026-10-22 · 판본 1.1<br>발표 요약과 독립 보충 해설을 구분한 한국어 학습 자료</p></div></section>'+body+'</main><script>if(innerWidth<=720)document.getElementById("navigation").open=false;</script></body></html>';
if(/\/Users\/|file:\/\/|MATHTOKEN|CODETOKEN|video-access\?|getcontrast\.io\/ls\/click/.test(html))throw new Error('Private data or unresolved markup');
await fs.writeFile(path.join(dist,'index.html'),html);console.log(JSON.stringify({documents:docs.length,equations,figures:usedFigures.size,bytes:Buffer.byteLength(html)}));
