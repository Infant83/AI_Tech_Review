export function solveTwoState(delta, v) {
  if (!Number.isFinite(delta) || !Number.isFinite(v) || delta <= 0) throw new RangeError('Finite inputs and positive gap required');
  const gapNorm = Math.hypot(delta, 2*v);
  return {energy: -2*v*v/(delta+gapNorm), weight:(1-delta/gapNorm)/2, sensitivity:2*Math.abs(v)/gapNorm};
}
if (typeof document !== 'undefined' && document.getElementById('two-state-model')) {
 const panel=document.getElementById('two-state-model'), d=document.getElementById('delta'), v=document.getElementById('coupling');
 const ko=panel.dataset.language==='ko';
 function update(){
  const gap=d.valueAsNumber, coupling=v.valueAsNumber;
  const valid=Number.isFinite(gap)&&Number.isFinite(coupling)&&gap>=.1&&gap<=2&&coupling>=0&&coupling<=.5;
  document.getElementById('toy-error').textContent=valid?'':(ko?'표시된 입력 범위 안의 숫자를 넣어 주세요. 마지막 유효 결과를 표시합니다.':'Enter numbers within the displayed ranges. The last valid result remains visible.');
  if(!valid) return;
  const r=solveTwoState(gap,coupling);
  document.getElementById('energy').textContent=r.energy.toFixed(5)+' eV';
  document.getElementById('weight').textContent=(100*r.weight).toFixed(2)+'%';
  document.getElementById('sensitivity').textContent=r.sensitivity.toFixed(5);
  document.getElementById('classical-bar').style.width=(100*(1-r.weight))+'%';
 }
 for(const input of [d,v]) input.addEventListener('input',update);
 document.getElementById('toy-reset').addEventListener('click',()=>{d.value='1';v.value='.2';update();});
 document.getElementById('toy-strong').addEventListener('click',()=>{d.value='.2';v.value='.4';update();});
 update();
}
