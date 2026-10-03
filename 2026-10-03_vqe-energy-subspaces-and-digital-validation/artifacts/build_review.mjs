import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
const {marked} = await import(pathToFileURL(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'marked/lib/marked.esm.js')));
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const escape = s => s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const titles = {
 ko:'VQE의 현재와 다음 단계: 에너지 최소화, 부분공간 계산, 디지털 검증',
 en:'VQE Today and Beyond: Energy Minimization, Subspace Methods, and Digital Validation'
};
function lab(lang) {
 const ko=lang==='ko';
 const rows = [[ko?'정확한 바닥상태':'Exact ground state','exact'],[ko?'최적 곱상태':'Best product state','product'],[ko?'현재 얽힌 시험 상태':'Current entangled trial state','trial'],[ko?'부분공간 |00⟩, |11⟩':'Subspace |00⟩, |11⟩','subspace']];
 return `<section class="lab" aria-labelledby="lab-title"><h3 id="lab-title">${ko?'직접 바꿔 보는 두 스핀의 에너지':'Explore the two-spin energy'}</h3><p>${ko?'설명용 모델 H=−ZZ−g(XI+IX), J=1. θ 대신 얽힌 시험 상태의 각도 t를 조절합니다. 샷·장치 잡음 없이 분석식으로 계산하며, 초기 g=0.5와 t=0.25는 리뷰의 예시값입니다.':'Teaching model H=−ZZ−g(XI+IX), J=1. Adjust the field g and angle t of the entangled trial state. Results use analytical formulas without shots or device noise. Defaults g=0.5 and t=0.25 are review examples.'}</p><div class="controls"><div class="control"><label for="field-g">${ko?'횡방향 장':'Transverse field'} g = <output id="g-value">0.500</output></label><input type="range" id="field-g" min="0" max="2" step="0.005" value="0.5"></div><div class="control"><label for="trial-t">${ko?'얽힌 시험 상태의 각도':'Entangled trial-state angle'} t = <output id="t-value">0.2500</output> rad</label><input type="range" id="trial-t" min="0" max="0.7853981633974483" step="any" value="0.25"></div></div><div class="lab-buttons"><button type="button" data-optimize>${ko?'이 g에서 t 최적화':'Optimize t for this g'}</button><button type="button" data-reset>${ko?'초기값으로':'Reset'}</button></div><table class="lab-readout"><thead><tr><th>${ko?'상태·공간':'State / space'}</th><th>E / J</th><th>${ko?'E₀ 대비 오차':'Error vs E₀'}</th></tr></thead><tbody>${rows.map(([label,id])=>`<tr><td>${label}</td><td data-energy="${id}">—</td><td class="gap" data-error="${id}">—</td></tr>`).join('')}</tbody></table><svg class="lab-plot" viewBox="0 0 750 350" role="img" aria-label="${ko?'시험 상태 각도와 에너지':'Trial-state angle and energy'}"><path d="M62 44 V279 H700" fill="none" stroke="#97a6a8"/><text x="10" y="50">1</text><text x="10" y="283">−5</text><text x="60" y="310">0</text><text x="671" y="310">π/4</text><text x="285" y="340">t (rad)</text><text x="64" y="24">E / J</text><line data-bound x1="62" x2="700" y1="120" y2="120" stroke="#116f79" stroke-width="2" stroke-dasharray="7 5"/><path data-curve d="M62 122 H700" fill="none" stroke="#b44e3a" stroke-width="3"/><circle data-point cx="260" cy="130" r="7" fill="#b44e3a" stroke="white" stroke-width="2"/></svg><p>${ko?'점은 현재 시험 상태, 곡선은 E(t), 점선은 정확한 E₀입니다. 최적화 버튼은 t*=½ arctan(2g)를 대입합니다. 작은 시스템의 해석적 예제이며 QPU 실행이나 회사 성능 측정이 아닙니다.':'The dot marks the current trial state, the curve shows E(t), and the dashed line shows exact E₀. Optimize inserts t*=½ arctan(2g). This is an analytical teaching example, not a QPU execution or vendor benchmark.'}</p><noscript><p>${ko?'인터랙티브 계산에는 JavaScript가 필요합니다. 위 정적 그림과 본문의 분석식으로 같은 결과를 확인할 수 있습니다.':'JavaScript is required for the interactive calculation. The static figure and analytical formulas above provide the same reference.'}</p></noscript></section>`;
}
for (const lang of ['ko','en']) {
 const src=fs.readFileSync(path.join(root,'reports',`review_${lang}.md`),'utf8');
 const math=[];
 const protectedSource=src.replace(/\$\$([\s\S]*?)\$\$/g,(_,s)=>{math.push(s.trim());return `\n\nMATHBLOCK${math.length-1}END\n\n`;});
 let body=marked.parse(protectedSource);
 body=body.replace(/<p>MATHBLOCK(\d+)END<\/p>/g,(_,i)=>`<div class="math-block">\\[${escape(math[Number(i)])}\\]</div>`);
 let section=0; const toc=[];
 body=body.replace(/<h2>(.*?)<\/h2>/g,(_,label)=>{const id=`section-${++section}`;toc.push(`<li><a href="#${id}">${label}</a></li>`);return `<h2 id="${id}">${label}</h2>`;});
 body=body.replace('<div id="interactive-slot"></div>',lab(lang));
 body=body.replace(/<table>/g,'<div class="table-scroll"><table>').replace(/<\/table>/g,'</table></div>');
 // Keep the compact lab table within its card instead of the wide article-table wrapper.
 body=body.replace('<div class="table-scroll"><table class="lab-readout">','<table class="lab-readout">').replace('</tbody></table></div><svg class="lab-plot"','</tbody></table><svg class="lab-plot"');
 const tableOfContents=`<details class="toc"><summary>${lang==='ko'?'내용 살펴보기':'Contents'}</summary><ol>${toc.join('')}</ol></details>`;
 const firstFigureEnd=body.indexOf('</figure>')+'</figure>'.length;
 body=body.slice(0,firstFigureEnd)+tableOfContents+body.slice(firstFigureEnd);
 const dir=path.join(root,'dist',lang==='en'?'en':'');fs.mkdirSync(dir,{recursive:true});
 const html=`<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(titles[lang])}</title><meta name="description" content="${lang==='ko'?'VQE의 원리·측정 비용·최적화와 HI-VQE·SQD를 검토하고 DecaQ 400스핀 디지털 사례의 검증 범위를 분석합니다.':'A technical review of VQE, measurement costs, optimization, HI-VQE and SQD, and the evidence boundaries of DecaQ’s 400-spin digital case.'}"><meta property="og:title" content="${escape(titles[lang])}"><link rel="stylesheet" href="review.css"><script>window.MathJax={tex:{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']]},options:{enableMenu:false}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script><script defer src="interactive.js"></script></head><body><header><a class="brand" href="https://infant83.github.io/AI_Tech_Review/">AI TECH REVIEW LETTERS</a><div class="topline-actions"></div></header><main>${body}<div class="footer">AI Tech Review · 2026-10-03</div></main></body></html>`;
 const base='https://infant83.github.io/AI_Tech_Review/reviews/2026-10-03_vqe-energy-subspaces-and-digital-validation/';
 const urls={ko:base,en:base+'en/'};
 const other=lang==='ko'?'en':'ko';
 const metadata=`<link rel="alternate" hreflang="ko" href="${urls.ko}"><link rel="alternate" hreflang="en" href="${urls.en}"><link rel="alternate" hreflang="x-default" href="${urls.ko}"><meta property="og:url" content="${urls[lang]}"><meta property="og:type" content="article"><meta property="og:image" content="${base}hero.webp"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="${base}hero.webp">`;
 const nav=`<nav class="language-switcher" aria-label="${lang==='ko'?'언어':'Language'}"><span class="language-current" lang="${lang}" aria-current="page">${lang==='ko'?'한국어':'English'}</span><a lang="${other}" hreflang="${other}" href="${urls[other]}">${other==='ko'?'한국어':'English'}</a></nav>`;
 fs.writeFileSync(path.join(dir,'index.html'),html.replace('</head>',metadata+'</head>').replace('<div class="topline-actions"></div>',`<div class="topline-actions">${nav}</div>`));
 for(const name of ['hero.webp','entanglement.svg',`division_${lang}.svg`,'review.css','interactive.js']) fs.copyFileSync(path.join(root,'artifacts',name),path.join(dir,name));
 console.log(`${lang}: ${toc.length} sections, ${math.length} protected display equations`);
}
