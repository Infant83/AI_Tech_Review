/* Deterministic synthetic two-level lab. No source-paper data or network calls. */
(() => {
  'use strict';
  const lab=document.querySelector('[data-two-level-lab]');
  if(!lab)return;
  const ko=document.documentElement.lang==='ko';
  const theta=lab.querySelector('[data-theta]');
  const shots=lab.querySelector('[data-shots]');
  const fraction=lab.querySelector('[data-fraction]');
  const nformat=(n,d=4)=>Number(n).toLocaleString(ko?'ko-KR':'en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
  const set=(key,value)=>{lab.querySelector(`[data-value="${key}"]`).textContent=value};
  function update(){
    const angle=Number(theta.value),t=angle*Math.PI/180,N=Number(shots.value),f=Number(fraction.value)/100;
    const delta=100,p=Math.sin(t)**2,q=Math.cos(t)**2,r=delta*Math.sin(t)*Math.cos(t),reference=delta*p;
    const A=r*r*(1-p)/(4*q),B=r*r*p*(1-q)/(4*q*q);
    const optimal=Math.sqrt(A)/(Math.sqrt(A)+Math.sqrt(B));
    const se=Math.sqrt(A/(N*f)+B/(N*(1-f)));
    const seOpt=(Math.sqrt(A)+Math.sqrt(B))/Math.sqrt(N);
    set('theta',`${angle}°`);set('shots',nformat(N,0));set('fraction',`${fraction.value}%`);
    set('reference',`${nformat(reference)} mHa`);set('correction',`${nformat(-r*Math.sqrt(p/q))} mHa`);
    set('energy',`${nformat(reference-r*Math.sqrt(p/q))} mHa`);
    set('r',`${nformat(r)} mHa`);set('p',nformat(p));set('q',nformat(q));
    set('residual-shots',nformat(N*f,0));set('reference-shots',nformat(N*(1-f),0));
    set('se',`${nformat(se)} mHa`);set('optimal-fraction',`${nformat(100*optimal,1)}%`);set('optimal-se',`${nformat(seOpt)} mHa`);
    const rare=Math.min(N*f*p,N*f*(1-p),N*(1-f)*q,N*(1-f)*(1-q));
    lab.querySelector('[data-rare-event]').hidden=rare>=30;
    lab.querySelector('[data-energy-bar]').setAttribute('width',String(Math.max(0,Math.min(240,reference*2.4))));
    lab.querySelector('[data-correction-bar]').setAttribute('width',String(Math.max(0,Math.min(240,reference*2.4))));
    lab.querySelector('[data-lab-status]').textContent=ko?`기준 ${nformat(reference,2)} mHa와 보정 ${nformat(-reference,2)} mHa가 상쇄된다. 선택한 배분의 근사 표준오차 ${nformat(se)} mHa.`:`The reference ${nformat(reference,2)} mHa and correction ${nformat(-reference,2)} mHa cancel. Approximate standard error for this allocation: ${nformat(se)} mHa.`;
  }
  for(const input of [theta,shots,fraction])input.addEventListener('input',update);
  lab.querySelector('[data-lab-reset]').addEventListener('click',()=>{theta.value='30';shots.value='10000';fraction.value='75';update()});
  lab.querySelector('[data-lab-optimal]').addEventListener('click',()=>{fraction.value=String(Math.max(1,Math.min(99,Math.round(100*Math.cos(Number(theta.value)*Math.PI/180)**2))));update()});
  update();
})();
