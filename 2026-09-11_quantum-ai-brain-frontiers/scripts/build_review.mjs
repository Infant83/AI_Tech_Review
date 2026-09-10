#!/usr/bin/env node
// Rebuild the bilingual article with Node.js and marked. No network is used by the page.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const moduleRoot=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
const {marked}=await import(moduleRoot ? path.join(moduleRoot,'marked/lib/marked.esm.js') : 'marked');
const {references,topic_discovery}=JSON.parse(fs.readFileSync(path.join(root,'references.json'),'utf8'));
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const css=`
:root{color-scheme:light;--ink:#183843;--teal:#177b80;--paper:#fbf9f3;--muted:#54676c;--line:#d2dbd8;--gold:#a66c32}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:92px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Noto Sans KR",Arial,sans-serif;font-size:18px;line-height:1.94;word-break:keep-all;overflow-wrap:anywhere}
.topbar{position:sticky;top:0;z-index:5;background:rgba(251,249,243,.96);border-bottom:1px solid var(--line);padding:10px max(20px,calc((100vw - 1060px)/2));display:flex;align-items:center;justify-content:space-between;gap:14px;font-size:13px;line-height:1.5}
.topbar a{color:var(--ink);text-decoration:none}.topbar strong{letter-spacing:.11em;font-size:12px}
main{max-width:1000px;margin:0 auto;padding:54px 44px 88px}
h1{font-size:clamp(36px,5vw,61px);font-weight:760;line-height:1.27;letter-spacing:-.04em;margin:18px 0 24px;text-wrap:balance}
.eyebrow,.chapter-no{font-size:12px;line-height:1.4;font-weight:750;letter-spacing:.15em;color:var(--teal)}
.dek{font-size:23px;line-height:1.65;color:var(--muted);max-width:850px;margin:0 0 30px}
h2{font-size:34px;line-height:1.42;letter-spacing:-.025em;margin:105px 0 32px;padding-top:32px;border-top:2px solid var(--ink);text-wrap:balance}
.chapter-no{display:block;margin-bottom:13px}
h3{font-size:24px;line-height:1.5;letter-spacing:-.018em;margin:49px 0 18px}
p{margin:18px 0 24px}a{color:var(--teal);text-underline-offset:4px}strong{font-weight:750}
figure{margin:35px 0 42px}figure img{width:100%;height:auto;display:block;border-radius:12px}
figure.hero{margin:37px -24px 42px}figcaption{font-size:14px;line-height:1.75;color:var(--muted);margin:14px 3px 0}
.scope{border-left:4px solid var(--gold);background:#f2eee3;padding:22px 27px;margin:32px 0;font-size:16px;line-height:1.85}.scope p{margin:8px 0 0}
.contents{display:grid;grid-template-columns:1fr 1fr;gap:0 30px;margin:34px 0 54px;padding:10px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.contents a{display:flex;gap:15px;padding:15px 0;font-size:15px;text-decoration:none;line-height:1.6}.contents b{color:var(--gold);min-width:22px}
.equation{font-family:"Cambria Math","STIX Two Math",Georgia,serif;font-size:26px;text-align:center;line-height:1.7;background:#eef2ef;border-radius:10px;padding:25px 22px;margin:28px 0;overflow:auto;white-space:nowrap;overflow-wrap:normal}
.equation.wide{font-size:23px}
.table-wrap{overflow-x:auto;margin:30px 0 38px;border-top:2px solid var(--ink);border-bottom:1px solid var(--line)}
table{border-collapse:collapse;width:100%;min-width:630px;font-size:15px;line-height:1.7}
th,td{text-align:left;vertical-align:top;padding:16px 16px;border-bottom:1px solid var(--line)}th{background:#eaf0ed;font-weight:750}tr:last-child td{border-bottom:0}
ul{padding-left:24px}li{margin:12px 0}.citation{font-size:13px;white-space:nowrap;font-weight:700}
.refs{font-size:14px;line-height:1.75;padding-left:30px}.refs li{padding:9px 0}.refs small{display:block;color:var(--muted);margin-top:3px;font-size:12px}
.topic-links{font-size:14px;line-height:1.8}
.interactive{padding:27px 30px;background:#163944;color:#fff;border-radius:14px;margin:30px 0}
.interactive h4{margin:0 0 8px;font-size:21px}.interactive p{font-size:14px;line-height:1.7;color:#c9dadd;margin:8px 0 20px}
.interactive label{display:block;font-size:16px;margin:12px 0}.interactive input{width:100%;accent-color:#dfaa69;height:30px;cursor:pointer}
.interactive .readout{display:flex;justify-content:space-between;gap:15px;margin:16px 0;font-variant-numeric:tabular-nums;font-size:18px}
.signal-track{height:18px;background:#385762;border-radius:12px;overflow:hidden}.signal-fill{height:100%;background:#efb774;width:1%;transition:width .12s}
button{font:inherit;font-size:14px;border:1px solid #9aafb4;background:transparent;color:white;border-radius:6px;padding:6px 14px;cursor:pointer;margin-top:18px}
button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #bf833d;outline-offset:5px}
.language-nav{font-size:14px;text-align:right;margin-bottom:25px}.source-code{font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:24px;margin-top:50px}
@media(max-width:680px){body{font-size:17px;line-height:1.9}main{padding:28px 21px 55px}h1{font-size:37px}.dek{font-size:20px}h2{font-size:28px;margin-top:75px}h3{font-size:22px}figure.hero{margin-left:0;margin-right:0}figcaption{font-size:13px}.contents{grid-template-columns:1fr;gap:0}.contents a{padding:10px 0}.scope{padding:18px 19px}.equation,.equation.wide{font-size:21px;text-align:left}.interactive{padding:22px 20px}.interactive .readout{flex-direction:column;gap:2px}.diagram-wrap{overflow-x:auto;border-radius:12px}.diagram-wrap img{min-width:680px}.topbar strong{font-size:11px}.topbar{font-size:12px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.signal-fill{transition:none}}
@media print{.topbar,.interactive{display:none}body{font-size:11pt;background:white}main{max-width:none;padding:0}h2{break-before:page;margin-top:0}figure,table{break-inside:avoid}a{color:inherit}}
`;
const js=`
(()=>{const slider=document.getElementById('phase');if(!slider)return;
const phase=document.getElementById('phase-value'),prob=document.getElementById('probability'),bar=document.getElementById('signal-fill');
const update=()=>{const v=Number(slider.value),p=Math.sin(v/2)**2;phase.textContent=v.toFixed(2)+' rad';prob.textContent=(100*p).toFixed(3)+'%';bar.style.width=(100*p)+'%';slider.setAttribute('aria-valuetext',v.toFixed(2)+' radians');};
slider.addEventListener('input',update);document.getElementById('phase-reset').addEventListener('click',()=>{slider.value='0.20';update()});update();})();
`;
for(const lang of ['ko','en']){
 let md=fs.readFileSync(path.join(root,'reports',`review.${lang}.md`),'utf8');
 const title=md.match(/^# (.+)$/m)[1];
 const desc=lang==='ko'?'양자진공 복굴절과 LHC의 스핀 상관관계, AI가 공개한 Navier–Stokes 증명의 정확한 범위, 말초 신경 자극과 기억의 근거를 원 논문으로 읽습니다. 개념 일러스트 5장과 도표 6개, 편광 조작 예제로 원리를 설명하고 엘니뇨와 아마존 전망을 짧게 덧붙였습니다.':'A long-form review of vacuum optics, collider quantum information, AI-assisted Navier–Stokes proofs and memory stimulation, with figures and a climate note.';
 const interactive=lang==='ko'?['편광의 위상차를 바꾸어 보기','설명용 위상차 범위입니다. 실제 진공 효과의 크기를 나타내지 않습니다.','상대 위상차 Δφ','교차 방향 검출 비율','초기값으로']:['Change the polarization phase','An enlarged educational range, not the size of a physical vacuum effect.','Relative phase Δφ','Crossed-channel fraction','Reset'];
 md=md.replace('{{POLARIZATION}}',`<section class="interactive" aria-label="${interactive[0]}"><h4>${interactive[0]}</h4><p>${interactive[1]}</p><label for="phase">${interactive[2]}</label><input id="phase" type="range" min="0" max="1.57" value="0.20" step="0.01"><div class="readout"><span>Δφ = <output id="phase-value" for="phase">0.20 rad</output></span><span>${interactive[3]}: <output id="probability" for="phase">0.997%</output></span></div><div class="signal-track" aria-hidden="true"><div class="signal-fill" id="signal-fill"></div></div><button type="button" id="phase-reset">${interactive[4]}</button><noscript><p>Δφ = 0.20 rad → P = sin²(0.10) ≈ 0.997%.</p></noscript></section>`);
 // Link numbered citations before inserting the bibliography.
 md=md.replace(/\[(\d+(?:,\d+)*)\]/g,(_,ids)=>'<span class="citation">'+ids.split(',').map(id=>`<a href="#ref-${id}" aria-label="Reference ${id}">[${id}]</a>`).join(' ')+'</span>');
 md=md.replace('{{REFERENCES}}','<ol class="refs">'+references.map(r=>`<li id="ref-${r.id}"><a href="${r.url}">${escape(r.title)}</a><small>${escape(r.scope)}</small></li>`).join('\n')+'</ol>');
 md=md.replace('{{NEWSLETTER_LINKS}}','<ul class="topic-links">'+topic_discovery.map(r=>`<li><a href="${r.url}">New Scientist · ${escape(r.title)}</a></li>`).join('\n')+'</ul>');
 let body=marked.parse(md,{gfm:true});
 body=body.replace(/<table>/g,'<div class="table-wrap" role="region" tabindex="0" aria-label="'+(lang==='ko'?'비교 표':'Comparison table')+'"><table>').replace(/<\/table>/g,'</table></div>');
 body=body.replace(/(<img[^>]+src="assets\/[^"]+\.svg"[^>]*>)/g,'<div class="diagram-wrap">$1</div>');
 const base='https://infant83.github.io/AI_Tech_Review/reviews/2026-09-11_quantum-ai-brain-frontiers/';
 const canonical=base+(lang==='en'?'en/':'');
 const alternates='<link rel="alternate" hreflang="ko" href="'+base+'"><link rel="alternate" hreflang="en" href="'+base+'en/"><link rel="alternate" hreflang="x-default" href="'+base+'">';
 const languageNav='<nav class="language-nav" aria-label="Language">'+(lang==='ko'?'<span lang="ko" aria-current="page">한국어</span> · <a lang="en" hreflang="en" href="'+base+'en/">English</a>':'<a lang="ko" hreflang="ko" href="'+base+'">한국어</a> · <span lang="en" aria-current="page">English</span>')+'</nav>';
 body=languageNav+body;
 if(lang==='en')fs.cpSync(path.join(root,'dist/assets'),path.join(root,'dist/en/assets'),{recursive:true});
 const html=`<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="${escape(desc)}"><meta name="author" content="AI Tech Review"><meta property="og:type" content="article"><meta property="og:description" content="${escape(desc)}"><meta property="og:url" content="${canonical}"><meta property="og:image" content="${base}vacuum.webp"><meta name="twitter:card" content="summary_large_image">${alternates}<title>${escape(title)}</title><style>${css}</style></head><body><header class="topbar"><a href="https://infant83.github.io/AI_Tech_Review/"><strong>AI TECH REVIEW</strong></a><a href="#vacuum">Quantum</a><a href="#ai">AI</a><a href="#brain">Brain</a><span>2026.09.11</span></header><main><article>${body}</article></main><script>${js}</script></body></html>\n`;
 const dest=path.join(root,'dist',...(lang==='en'?['en']:[]));fs.mkdirSync(dest,{recursive:true});fs.writeFileSync(path.join(dest,'index.html'),html);
 console.log(lang+': '+html.length+' characters, description '+desc.length);
}

