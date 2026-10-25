(() => {
  const en = document.documentElement.lang === 'en';
  const params = new URLSearchParams(location.search);
  if (params.get('series') === 'lecture-notes' && !['q', 'month', 'sort'].some(key => params.has(key))) {
    location.replace(en ? '../../lectures/en/' : '../lectures/');
    return;
  }
  if (['daily-quantum', 'weekly-review'].includes(params.get('series')) && !['q', 'month', 'sort'].some(key => params.has(key))) {
    location.replace(en ? '../../briefings/en/' : '../briefings/');
    return;
  }
  const search = document.querySelector('#archive-search');
  if (!search) return;
  const month = document.querySelector('#archive-month');
  const sort = document.querySelector('#archive-sort');
  const grid = document.querySelector('#document-grid');
  const cards = Array.from(grid.querySelectorAll('.document-card'));
  const buttons = Array.from(document.querySelectorAll('[data-series].collection-button'));
  const count = document.querySelector('#archive-result-count');
  const empty = document.querySelector('#archive-empty');
  const more = document.querySelector('#archive-more');
  let series = buttons.some(button => button.dataset.series === params.get('series')) ? params.get('series') : '';
  let limit = 12;
  search.value = params.get('q') || '';
  if (Array.from(month.options).some(option => option.value === params.get('month'))) month.value = params.get('month');
  if (params.get('sort') === 'oldest') sort.value = 'oldest';
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase().replace(/\s+/g, ' ').trim();
  function apply(updateUrl = true) {
    const words = normalize(search.value).split(' ').filter(Boolean);
    const ordered = [...cards].sort((a, b) => sort.value === 'oldest' ? a.dataset.date.localeCompare(b.dataset.date) : b.dataset.date.localeCompare(a.dataset.date));
    let matches = 0;
    for (const card of ordered) {
      const haystack = normalize(card.dataset.search + ' ' + card.dataset.date);
      const match = (!series || card.dataset.series === series) && (!month.value || card.dataset.date.startsWith(month.value)) && words.every(word => haystack.includes(word));
      card.hidden = !match || matches >= limit;
      if (match) matches++;
      grid.append(card);
    }
    for (const button of buttons) {
      const active = button.dataset.series === series;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    }
    count.textContent = en ? `${matches} resources · ${Math.min(limit, matches)} shown` : `${matches}건의 자료 · ${Math.min(limit, matches)}건 표시`;
    empty.hidden = matches !== 0;
    more.hidden = matches <= limit;
    more.textContent = en ? `Show more (${matches - limit} remaining) ↓` : `문서 더 보기 (${matches - limit}건 남음) ↓`;
    if (updateUrl) {
      const next = new URLSearchParams();
      if (series) next.set('series', series);
      if (search.value.trim()) next.set('q', search.value.trim());
      if (month.value) next.set('month', month.value);
      if (sort.value !== 'newest') next.set('sort', sort.value);
      history.replaceState(null, '', location.pathname + (next.size ? '?' + next : '') + location.hash);
    }
  }
  for (const control of [search, month, sort]) control.addEventListener(control === search ? 'input' : 'change', () => { limit = 12; apply(); });
  for (const button of buttons) button.addEventListener('click', () => { series = button.dataset.series; limit = 12; apply(); });
  document.querySelector('#archive-reset').addEventListener('click', () => { series = ''; search.value = ''; month.value = ''; sort.value = 'newest'; limit = 12; apply(); search.focus(); });
  more.addEventListener('click', () => { const previous = cards.filter(card => !card.hidden); limit += 12; apply(); const firstNew = Array.from(grid.children).find(card => !card.hidden && !previous.includes(card)); firstNew?.querySelector('a')?.focus(); });
  apply(false);
})();
