(() => {
  const root = document.querySelector('.lab');
  if (!root) return;
  const gSlider = root.querySelector('#field-g');
  const tSlider = root.querySelector('#trial-t');
  const fmt = v => (Math.abs(v) < 5e-8 ? 0 : v).toFixed(6);
  const energy = (g, t) => -Math.cos(2*t)-2*g*Math.sin(2*t);
  const exact = g => -Math.sqrt(1+4*g*g);
  const product = g => g <= 1 ? -1-g*g : -2*g;
  const plot = root.querySelector('.lab-plot');
  const x = t => 62 + t/(Math.PI/4)*638;
  const y = e => 44 + (1-e)/6*235;
  function update() {
    const g = Number(gSlider.value), t = Number(tSlider.value);
    const values = {exact:exact(g), product:product(g), trial:energy(g,t), subspace:-1};
    root.querySelector('#g-value').textContent = g.toFixed(3);
    root.querySelector('#t-value').textContent = t.toFixed(4);
    for (const [key, value] of Object.entries(values)) {
      root.querySelector(`[data-energy="${key}"]`).textContent = fmt(value);
      root.querySelector(`[data-error="${key}"]`).textContent = fmt(Math.max(0, value-values.exact));
    }
    const curve = Array.from({length:121},(_,i)=> {
      const angle=i/120*Math.PI/4;
      return `${i?'L':'M'}${x(angle).toFixed(2)},${y(energy(g,angle)).toFixed(2)}`;
    }).join(' ');
    plot.querySelector('[data-curve]').setAttribute('d',curve);
    plot.querySelector('[data-point]').setAttribute('cx',x(t));
    plot.querySelector('[data-point]').setAttribute('cy',y(values.trial));
    plot.querySelector('[data-bound]').setAttribute('y1',y(values.exact));
    plot.querySelector('[data-bound]').setAttribute('y2',y(values.exact));
    plot.setAttribute('aria-label',`g=${g.toFixed(3)}, t=${t.toFixed(4)}; E=${fmt(values.trial)}; E0=${fmt(values.exact)}`);
  }
  gSlider.addEventListener('input',update);
  tSlider.addEventListener('input',update);
  root.querySelector('[data-optimize]').addEventListener('click',()=> {
    tSlider.value = .5*Math.atan(2*Number(gSlider.value));
    update();
  });
  root.querySelector('[data-reset]').addEventListener('click',()=> {
    gSlider.value = .5; tSlider.value = .25; update();
  });
  update();
})();
