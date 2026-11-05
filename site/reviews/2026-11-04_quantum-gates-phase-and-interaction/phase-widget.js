/* Original ideal-statevector teaching widget. No network, storage or telemetry.
 * Basis |ab> (or |abc>): left bit is the left tensor factor.
 * Maximize C; U = exp(-i beta sum X) exp(-i gamma C).
 * R_x(2 beta) = cos(beta) I - i sin(beta) X.
 */
(function (scope) {
  'use strict';
  const pi = Math.PI;
  function compute(graph, gamma, beta) {
    if (!['edge', 'triangle'].includes(graph) || !Number.isFinite(gamma) || !Number.isFinite(beta)) throw Error('Invalid graph or finite angles.');
    const n = graph === 'edge' ? 2 : 3;
    const edges = n === 2 ? [[0, 1]] : [[0, 1], [1, 2], [0, 2]];
    const scores = Array.from({length: 1 << n}, (_, s) => edges.reduce((c, [a, b]) => c + Number(((s >> (n - 1 - a)) & 1) !== ((s >> (n - 1 - b)) & 1)), 0));
    const initial = scores.map(() => [1 / Math.sqrt(1 << n), 0]);
    const phased = initial.map(([a], i) => [a * Math.cos(-gamma * scores[i]), a * Math.sin(-gamma * scores[i])]);
    const final = phased.map(a => [...a]);
    const c = Math.cos(beta), s = Math.sin(beta);
    for (let q = 0; q < n; q++) {
      const bit = 1 << (n - 1 - q);
      for (let j = 0; j < final.length; j++) if (!(j & bit)) {
        const [ar, ai] = final[j], [br, bi] = final[j | bit];
        final[j] = [c * ar + s * bi, c * ai - s * br];
        final[j | bit] = [c * br + s * ai, c * bi - s * ar];
      }
    }
    const stages = [initial, phased, final].map(amplitudes => {
      const probabilities = amplitudes.map(([re, im]) => re * re + im * im);
      return {amplitudes, probabilities, expectedScore: probabilities.reduce((v, p, i) => v + p * scores[i], 0), optimalProbability: probabilities.reduce((v, p, i) => v + (scores[i] === edges.length - (n === 3 ? 1 : 0) ? p : 0), 0)};
    });
    return {graph, n, edges, gamma, beta, scores, maxScore: Math.max(...scores), stages};
  }
  const api = {compute, version: '1.0.0', basisOrder: 'left bit first', angleUnit: 'rad'};
  scope.QuantumPhaseModel = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof document === 'undefined') return;

  const words = {
    ko: {
      title: '위상을 바꾸고 측정 확률을 비교하기',
      intro: '각도와 계산 단계를 바꾸면 같은 상태벡터를 다시 계산합니다. 표의 복소 진폭과 확률을 함께 읽어 보세요.',
      graph: '문제 그래프', edge: '2노드 · 1간선', triangle: '3노드 · 삼각형',
      gamma: '문제 위상각 γ', beta: '혼합각 β', stage: '읽을 계산 단계',
      stages: ['초기 균등 상태', '문제 위상층 뒤', 'X 혼합층 뒤'],
      reset: '기본값으로', example: '선택 그래프의 예제 각도',
      basis: '비트', amplitude: '복소 진폭', probability: '확률', score: '점수',
      expected: '기댓점수', optimum: '최적 점수의 확률', max: '가능한 최대 점수',
      phase: '초기에는 모든 비트 배열의 진폭이 같습니다.',
      stageNotes: ['모든 배열의 확률이 같습니다. 두노드의 다른 비트는 합계 50%입니다.', '점수 c인 성분에 exp(−iγc)를 곱했습니다. 진폭의 방향은 달라져도 각 성분의 크기와 확률은 유지됩니다.', '각 큐비트에 Rx(2β)를 적용했습니다. 성분들이 섞이며 이전의 상대위상이 확률에 영향을 줍니다.'],
      triangleStart: '모든 8개 배열이 같은 확률입니다. 최대 점수 2인 6개 배열의 확률 합은 75%입니다.',
      legend: '화살표: 복소 진폭(실수 오른쪽·허수 위쪽). 길이 1이 원의 반지름입니다. 막대: 진폭 크기의 제곱.',
      scope: '리뷰의 이상적 상태벡터 교육 계산 · 각도 단위 rad · 기본 γ = π/2, β = π/8. 그래프를 바꾸면 현재 각도를 유지합니다. 예제 각도 버튼은 선택한 작은 그래프의 해석해를 적용합니다.',
      updated: '현재 계산', graphLabel: '다른 비트로 나뉜 간선마다 1점을 얻는 MaxCut 그래프',
    },
    en: {
      title: 'Change phases and compare measurement probabilities',
      intro: 'Changing an angle or calculation stage recomputes the same ideal statevector. Read the complex amplitudes and probabilities together.',
      graph: 'Problem graph', edge: '2 nodes · 1 edge', triangle: '3 nodes · triangle',
      gamma: 'Cost phase angle γ', beta: 'Mixer angle β', stage: 'Calculation stage',
      stages: ['Initial uniform state', 'After cost phases', 'After X mixers'],
      reset: 'Reset defaults', example: 'Example angles for this graph',
      basis: 'Bits', amplitude: 'Complex amplitude', probability: 'Probability', score: 'Score',
      expected: 'Expected score', optimum: 'Probability of an optimal score', max: 'Maximum possible score',
      stageNotes: ['Every bit string has equal probability. The different-bit strings sum to 50% in the two-node problem.', 'A component with score c is multiplied by exp(−iγc). Directions can change while magnitudes and probabilities remain fixed.', 'Rx(2β) acts on each qubit. Components mix, and the earlier relative phases affect their resulting probabilities.'],
      triangleStart: 'All 8 strings have equal probability. The 6 strings with maximum score 2 have combined probability 75%.',
      legend: 'Arrows: complex amplitudes (real right; imaginary up). Magnitude 1 reaches the circle. Bars: squared amplitude magnitudes.',
      scope: 'Review ideal-statevector educational calculation · angles in rad · default γ = π/2, β = π/8. Switching graphs keeps the current angles. The example button uses an analytic solution for the selected small graph.',
      updated: 'Current calculation', graphLabel: 'MaxCut graph: one point per edge whose endpoints have different bits',
    }
  };
  const clean = x => Math.abs(x) < 0.0000000001 ? 0 : x;
  const fmt = x => clean(x).toFixed(3);
  const esc = x => String(x).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
  const pct = x => `${(Math.max(0, Math.min(1, x)) * 100).toFixed(1)}%`;
  function amplitudeSVG(re, im) {
    const x = 23 + 19 * re, y = 23 - 19 * im, nonzero = Math.hypot(re, im) > 1e-12;
    const a = Math.atan2(y - 23, x - 23), back = 4, spread = 2;
    const arrow = nonzero ? `<path d="M23 23L${x} ${y}M${x - back * Math.cos(a) + spread * Math.sin(a)} ${y - back * Math.sin(a) - spread * Math.cos(a)}L${x} ${y}L${x - back * Math.cos(a) - spread * Math.sin(a)} ${y - back * Math.sin(a) + spread * Math.cos(a)}"/>` : '<circle cx="23" cy="23" r="1.5"/>';
    return `<svg class="phase-amplitude" viewBox="0 0 46 46" aria-hidden="true"><circle class="phase-unit-circle" cx="23" cy="23" r="19"/><path class="phase-complex-axes" d="M2 23H44M23 44V2"/><g class="phase-complex-arrow">${arrow}</g></svg>`;
  }
  function graphSVG(graph, label) {
    const pts = graph === 'edge' ? [[35,40], [145,40]] : [[90,15], [35,90], [145,90]];
    const edges = graph === 'edge' ? [[0,1]] : [[0,1],[1,2],[0,2]];
    return `<svg class="phase-graph" viewBox="0 0 180 ${graph === 'edge' ? 80 : 115}" role="img" aria-label="${esc(label)}">${edges.map(([a,b]) => `<path d="M${pts[a][0]} ${pts[a][1]}L${pts[b][0]} ${pts[b][1]}"/>`).join('')}${pts.map(([x,y], i) => `<circle cx="${x}" cy="${y}" r="12"/><text x="${x}" y="${y + 4}" text-anchor="middle">${'abc'[i]}</text>`).join('')}</svg>`;
  }
  for (const [index, host] of [...document.querySelectorAll('[data-phase-widget]')].entries()) {
    const lang = host.dataset.lang === 'en' ? 'en' : 'ko', t = words[lang], prefix = `phase-${lang}-${index}`;
    host.classList.add('phase-explorer');
    host.setAttribute('aria-labelledby', prefix + '-title');
    host.innerHTML = `<h3 id="${prefix}-title">${t.title}</h3><p class="phase-intro">${t.intro}</p>
      <div class="phase-controls"><label>${t.graph}<select data-graph><option value="edge">${t.edge}</option><option value="triangle">${t.triangle}</option></select></label>
      <label>${t.stage}<select data-stage>${t.stages.map((v,i) => `<option value="${i}"${i === 2 ? ' selected' : ''}>${v}</option>`).join('')}</select></label>
      <label>${t.gamma} <output data-gamma-out></output><input data-gamma type="range" min="0" max="${2*pi}" step="any" value="${pi/2}" aria-label="${t.gamma} (rad)"></label>
      <label>${t.beta} <output data-beta-out></output><input data-beta type="range" min="0" max="${pi/2}" step="any" value="${pi/8}" aria-label="${t.beta} (rad)"></label></div>
      <div class="phase-actions"><button type="button" data-reset>${t.reset}</button><button type="button" data-example>${t.example}</button></div>
      <div class="phase-context"><div data-graph-view></div><p data-stage-note></p></div>
      <div class="phase-results" aria-live="polite" aria-atomic="true" data-summary></div>
      <table class="phase-table"><thead><tr><th scope="col">${t.basis}</th><th scope="col">${t.amplitude}</th><th scope="col">${t.probability}</th><th scope="col">${t.score}</th></tr></thead><tbody data-rows></tbody></table>
      <p class="phase-legend">${t.legend}</p><p class="phase-scope">${t.scope}</p>`;
    const q = selector => host.querySelector(selector);
    function update() {
      const graph = q('[data-graph]').value, gamma = +q('[data-gamma]').value, beta = +q('[data-beta]').value, stage = +q('[data-stage]').value;
      const model = compute(graph, gamma, beta), state = model.stages[stage];
      for (const [name,value] of [['gamma',gamma],['beta',beta]]) {
        q(`[data-${name}-out]`).textContent = `${fmt(value)} rad (${fmt(value/pi)}π)`;
        q(`[data-${name}]`).setAttribute('aria-valuetext', `${fmt(value)} rad`);
      }
      q('[data-graph-view]').innerHTML = graphSVG(graph, t.graphLabel);
      q('[data-stage-note]').textContent = stage === 0 && graph === 'triangle' ? t.triangleStart : t.stageNotes[stage];
      q('[data-summary]').innerHTML = `<strong>${t.expected}: ${fmt(state.expectedScore)}</strong><span>${t.optimum}: ${pct(state.optimalProbability)}</span><small>${t.max}: ${model.maxScore}</small>`;
      q('[data-rows]').innerHTML = state.amplitudes.map(([re,im],i) => `<tr class="${model.scores[i] === model.maxScore ? 'phase-optimal' : ''}"><th scope="row">${i.toString(2).padStart(model.n,'0')}</th><td>${amplitudeSVG(re,im)}<span class="phase-amplitude-value">${fmt(re)} ${clean(im)<0?'−':'+'} ${fmt(Math.abs(im))}i</span></td><td><div class="phase-probability-track" aria-hidden="true"><span style="width:${100*state.probabilities[i]}%"></span></div><span>${pct(state.probabilities[i])}</span></td><td>${model.scores[i]}</td></tr>`).join('');
      host.dataset.graph = graph; host.dataset.stage = String(stage);
    }
    for (const input of host.querySelectorAll('input,select')) input.addEventListener(input.tagName === 'SELECT' ? 'change' : 'input',update);
    q('[data-reset]').addEventListener('click', () => {q('[data-graph]').value='edge';q('[data-stage]').value='2';q('[data-gamma]').value=pi/2;q('[data-beta]').value=pi/8;update();});
    q('[data-example]').addEventListener('click', () => {const triangle=q('[data-graph]').value==='triangle';q('[data-gamma]').value=triangle?Math.atan(1/Math.sqrt(2)):pi/2;q('[data-beta]').value=triangle?Math.atan(1/Math.sqrt(2))/2:pi/8;q('[data-stage]').value='2';update();});
    update();
  }
})(typeof globalThis !== 'undefined' ? globalThis : window);
