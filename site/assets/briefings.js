(() => {
  'use strict';

  const source = document.getElementById('briefing-data');
  if (!source) return;
  let data;
  try { data = JSON.parse(source.textContent); } catch (_) { return; }
  const byId = id => document.getElementById(id);
  const ui = {
    month: byId('briefing-month'), prev: byId('briefing-prev'), next: byId('briefing-next'),
    search: byId('briefing-search'), all: byId('briefing-all-months'), reset: byId('briefing-reset'),
    title: byId('briefing-calendar-title'), calendar: byId('briefing-calendar'),
    panel: byId('briefing-day-panel'), heading: byId('briefing-day-heading'),
    content: byId('briefing-day-content'), list: byId('briefing-list'),
    count: byId('briefing-count'), label: byId('briefing-filter-label'),
    clear: byId('briefing-clear-day'), empty: byId('briefing-empty')
  };
  if (Object.values(ui).some(element => !element)) return;
  const en = document.documentElement.lang === 'en';
  const legend = document.querySelector('.briefing-calendar-legend');
  const defaultLegend = legend ? legend.textContent : '';
  const locale = en ? 'en-GB' : 'ko-KR';
  const clean = value => String(value || '').normalize('NFKC').toLocaleLowerCase(locale).replace(/\s+/g, ' ').trim();
  const validDate = value => {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const parsed = new Date(`${value}T12:00:00Z`);
    return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
  };
  const validMonth = value => typeof value === 'string' && /^\d{4}-\d{2}$/.test(value) && validDate(`${value}-01`);
  const dateObject = value => new Date(`${value}T12:00:00Z`);
  const dateLabel = value => dateObject(value).toLocaleDateString(locale, {
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'short', timeZone: 'UTC'
  });
  const monthLabel = value => dateObject(`${value}-01`).toLocaleDateString(locale, {
    year: 'numeric', month: 'long', timeZone: 'UTC'
  });
  const monthStep = (value, step) => {
    const parsed = dateObject(`${value}-01`);
    parsed.setUTCMonth(parsed.getUTCMonth() + step);
    return parsed.toISOString().slice(0, 7);
  };
  const element = (tag, className, text) => {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (text !== undefined) item.textContent = text;
    return item;
  };
  const documents = (Array.isArray(data.documents) ? data.documents : [])
    .filter(item => item && validDate(item.date) && typeof item.id === 'string' && typeof item.href === 'string')
    .sort((a, b) => b.date.localeCompare(a.date) || b.id.localeCompare(a.id));
  const months = [...new Set(documents.map(item => item.date.slice(0, 7)))].sort();
  if (!months.length) return;
  const firstMonth = months[0];
  const latestMonth = months[months.length - 1];
  const calendarMonths = [];
  for (let month = firstMonth; month <= latestMonth; month = monthStep(month, 1)) calendarMonths.push(month);
  const inRange = value => validMonth(value) && value >= firstMonth && value <= latestMonth;
  const documentsByDate = new Map();
  const searchText = new Map();
  documents.forEach(item => {
    if (!documentsByDate.has(item.date)) documentsByDate.set(item.date, []);
    documentsByDate.get(item.date).push(item);
    searchText.set(item.id, clean([item.title, item.title_en, item.summary, item.summary_en,
      item.date, item.series, ...(Array.isArray(item.tags) ? item.tags : [])].join(' ')));
  });
  const rows = [...ui.list.querySelectorAll('.briefing-row')];
  const state = { month: latestMonth, date: null, query: '', all: false };
  const readLocation = () => {
    const parameters = new URLSearchParams(location.search);
    const month = parameters.get('month');
    const date = parameters.get('date');
    state.month = inRange(month) ? month : latestMonth;
    state.date = validDate(date) && documentsByDate.has(date) ? date : null;
    if (state.date) state.month = state.date.slice(0, 7);
    state.query = (parameters.get('q') || '').slice(0, 300).trim();
    state.all = parameters.get('scope') === 'all' && !state.date;
  };
  const writeLocation = () => {
    const url = new URL(location.href);
    ['month', 'date', 'q', 'scope'].forEach(key => url.searchParams.delete(key));
    if (state.month !== latestMonth || state.date) url.searchParams.set('month', state.month);
    if (state.date) url.searchParams.set('date', state.date);
    if (state.query) url.searchParams.set('q', state.query);
    if (state.all) url.searchParams.set('scope', 'all');
    const next = `${url.pathname}${url.search}${url.hash}`;
    if (next !== `${location.pathname}${location.search}${location.hash}`) history.replaceState(null, '', next);
  };
  const topicLink = (item, className) => {
    const link = element('a', className, item.title || item.title_en || item.date);
    link.href = item.href;
    link.target = '_blank';
    link.rel = 'noopener';
    link.lang = item.language || 'ko';
    link.title = `${item.title || item.title_en || item.date} · PDF`;
    return link;
  };
  const matches = item => {
    const tokens = clean(state.query).split(' ').filter(Boolean);
    return tokens.every(token => searchText.get(item.id).includes(token));
  };
  const renderDetails = matchingDocuments => {
    const monthDocuments = matchingDocuments.filter(item => item.date.startsWith(state.month));
    const previewDate = state.date || (monthDocuments[0] && monthDocuments[0].date);
    ui.panel.dataset.selected = state.date ? 'true' : 'false';
    ui.heading.textContent = previewDate ? dateLabel(previewDate) : monthLabel(state.month);
    ui.content.replaceChildren();
    const hint = element('p', 'briefing-detail-hint', state.date
      ? (en ? 'Topics published on the selected day' : '선택한 날짜에 발행된 브리핑')
      : (en ? 'Latest topics in this month · Select a date to explore.' : '이 달의 최근 브리핑 · 날짜를 선택하면 그날의 주제를 볼 수 있습니다.'));
    ui.content.append(hint);
    const appendCalendarLink = () => {
      if (!state.date) return;
      const link = element('a', 'briefing-calendar-back', en ? 'Choose another date ↑' : '다른 날짜 선택 ↑');
      link.href = '#briefing-calendar-title';
      ui.content.append(link);
    };
    const dayDocuments = previewDate ? matchingDocuments.filter(item => item.date === previewDate) : [];
    if (!dayDocuments.length) {
      const message = state.date
        ? (en ? 'No briefings match the current search on the selected date.' : '선택한 날짜에는 검색 조건에 맞는 브리핑이 없습니다.')
        : state.query
          ? (en ? 'No briefings match the current search in this month.' : '이 달에는 검색 조건에 맞는 브리핑이 없습니다.')
          : (en ? 'No briefings are registered for this month.' : '이 달에는 등록된 브리핑이 없습니다.');
      ui.content.append(element('p', 'briefing-detail-empty', message));
      if (state.query) {
        const clearSearch = element('button', 'briefing-clear-search', en ? 'Clear search' : '검색어 지우기');
        clearSearch.type = 'button';
        clearSearch.addEventListener('click', () => {
          state.query = '';
          render();
          ui.search.focus({ preventScroll: true });
        });
        ui.content.append(clearSearch);
      }
      appendCalendarLink();
      return;
    }
    dayDocuments.forEach(item => {
      const article = element('article', 'briefing-detail-item');
      const heading = element('h4');
      heading.append(topicLink(item));
      article.append(heading);
      const summary = en ? item.summary_en || item.summary : item.summary;
      if (summary) {
        const paragraph = element('p', 'briefing-detail-summary', summary);
        paragraph.lang = en && item.summary_en ? 'en' : item.language || 'ko';
        article.append(paragraph);
      }
      if (Array.isArray(item.tags) && item.tags.length) {
        const tags = element('div', 'briefing-tags');
        item.tags.slice(0, 5).forEach(tag => tags.append(element('span', '', tag)));
        article.append(tags);
      }
      const action = topicLink(item, 'briefing-read');
      action.textContent = en ? 'Read PDF ↗' : '브리핑 읽기 ↗';
      action.removeAttribute('lang');
      article.append(action);
      ui.content.append(article);
    });
    appendCalendarLink();
  };
  const renderCalendar = matchingDocuments => {
    ui.calendar.replaceChildren();
    ui.title.textContent = monthLabel(state.month);
    if (legend) legend.textContent = state.query
      ? (en ? '● Matches your search · ○ Published on another topic' : '● 검색과 일치 · ○ 다른 주제로 발행')
      : defaultLegend;
    const firstDay = dateObject(`${state.month}-01`);
    const offset = (firstDay.getUTCDay() + 6) % 7;
    const lastDay = dateObject(`${monthStep(state.month, 1)}-01`);
    lastDay.setUTCDate(0);
    const dayCount = lastDay.getUTCDate();
    const monthMatching = matchingDocuments.filter(item => item.date.startsWith(state.month));
    const preview = state.date || (monthMatching[0] && monthMatching[0].date);
    const enabledDates = documents.filter(item => item.date.startsWith(state.month)).map(item => item.date);
    const tabDate = preview || enabledDates[0];
    for (let position = 0; position < Math.ceil((offset + dayCount) / 7) * 7; position++) {
      if (position % 7 === 0) ui.calendar.append(element('tr'));
      const day = position - offset + 1;
      const cell = element('td', day < 1 || day > dayCount ? 'calendar-pad' : 'calendar-day');
      ui.calendar.lastElementChild.append(cell);
      if (day < 1 || day > dayCount) { cell.setAttribute('aria-hidden', 'true'); continue; }
      const date = `${state.month}-${String(day).padStart(2, '0')}`;
      const originals = documentsByDate.get(date) || [];
      const items = originals.filter(matches);
      if (items.length) cell.classList.add('has-briefing');
      else if (originals.length) cell.classList.add('has-unmatched');
      if (state.date === date) cell.classList.add('is-selected');
      if (preview === date && !state.date) cell.classList.add('is-preview');
      const button = element('button', 'day-select');
      button.type = 'button';
      button.dataset.date = date;
      button.disabled = originals.length === 0;
      button.tabIndex = date === tabDate ? 0 : -1;
      button.setAttribute('aria-pressed', String(state.date === date));
      const label = items.length
        ? `${dateLabel(date)} · ${items.map(item => item.title || item.title_en || '').join('; ')}`
        : `${dateLabel(date)} · ${originals.length
          ? (en ? 'Briefing published · No match for the current search' : '발행된 브리핑 있음 · 현재 검색 일치 없음')
          : (en ? 'No published briefing' : '등록된 브리핑 없음')}`;
      button.setAttribute('aria-label', label);
      button.append(element('span', 'day-number', day));
      if (items.length) {
        const count = element('span', 'day-count', items.length > 1 ? String(items.length) : '●');
        count.setAttribute('aria-hidden', 'true');
        button.append(count);
      } else if (originals.length) {
        const count = element('span', 'day-count is-unmatched', '○');
        count.setAttribute('aria-hidden', 'true');
        button.append(count);
      }
      cell.append(button);
      if (items.length) {
        const topics = element('div', 'day-topics');
        items.slice(0, 2).forEach(item => topics.append(topicLink(item)));
        if (items.length > 2) topics.append(element('span', 'day-more', en ? `+${items.length - 2} topics` : `외 ${items.length - 2}건`));
        cell.append(topics);
      }
    }
  };
  const render = (focusDate = null, updateLocation = true) => {
    ui.month.value = state.month;
    ui.search.value = state.query;
    ui.all.checked = state.all;
    ui.prev.disabled = state.month <= firstMonth;
    ui.next.disabled = state.month >= latestMonth;
    ui.clear.hidden = !state.date;
    const matchingDocuments = documents.filter(matches);
    const visible = matchingDocuments.filter(item => (state.all || item.date.startsWith(state.month)) && (!state.date || item.date === state.date));
    const ids = new Set(visible.map(item => item.id));
    rows.forEach(row => { row.hidden = !ids.has(row.dataset.id); });
    ui.empty.hidden = visible.length !== 0;
    ui.count.textContent = en ? `${visible.length} briefing${visible.length === 1 ? '' : 's'}` : `브리핑 ${visible.length}건`;
    const scope = state.date ? dateLabel(state.date) : state.all
      ? (en ? 'All published dates' : '전체 발행 기간') : monthLabel(state.month);
    ui.label.textContent = `${scope}${state.query ? ` · ${en ? 'Search' : '검색'}: “${state.query}”` : ''}`;
    renderCalendar(matchingDocuments);
    renderDetails(matchingDocuments);
    if (updateLocation) writeLocation();
    if (focusDate) {
      const focused = ui.calendar.querySelector(`button[data-date="${focusDate}"]`);
      if (focused) focused.focus({ preventScroll: true });
    }
  };
  ui.month.replaceChildren(...calendarMonths.reverse().map(month => {
    const option = element('option', '', monthLabel(month));
    option.value = month;
    return option;
  }));
  ui.month.addEventListener('change', () => {
    state.month = ui.month.value;
    state.date = null;
    render();
  });
  [[ui.prev, -1], [ui.next, 1]].forEach(([button, step]) => button.addEventListener('click', () => {
    const month = monthStep(state.month, step);
    if (!inRange(month)) return;
    state.month = month;
    state.date = null;
    render();
  }));
  const updateSearch = () => {
    const selection = ui.search.selectionStart;
    state.query = ui.search.value.slice(0, 300);
    render();
    if (selection !== null) ui.search.setSelectionRange(selection, selection);
  };
  let composing = false;
  ui.search.addEventListener('compositionstart', () => { composing = true; });
  ui.search.addEventListener('compositionend', () => { composing = false; updateSearch(); });
  ui.search.addEventListener('input', event => {
    if (!composing && !event.isComposing) updateSearch();
  });
  ui.all.addEventListener('change', () => {
    state.all = ui.all.checked;
    state.date = null;
    render();
  });
  ui.clear.addEventListener('click', () => {
    state.date = null;
    render();
    ui.month.focus({ preventScroll: true });
  });
  ui.reset.addEventListener('click', () => {
    Object.assign(state, { month: latestMonth, date: null, query: '', all: false });
    render();
    ui.search.focus({ preventScroll: true });
  });
  ui.calendar.addEventListener('click', event => {
    const button = event.target.closest('button.day-select');
    if (!button || button.disabled) return;
    state.date = button.dataset.date;
    state.all = false;
    render(state.date);
    if (event.detail > 0 && window.matchMedia('(max-width: 720px)').matches) {
      ui.panel.scrollIntoView({
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
        block: 'nearest'
      });
    }
  });
  ui.calendar.addEventListener('keydown', event => {
    const button = event.target.closest('button.day-select');
    if (!button || !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const date = dateObject(button.dataset.date);
    let step = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 }[event.key];
    if (event.key === 'Home' || event.key === 'End') {
      const offset = (date.getUTCDay() + 6) % 7;
      date.setUTCDate(date.getUTCDate() + (event.key === 'Home' ? -offset : 6 - offset));
      step = event.key === 'Home' ? 1 : -1;
    } else date.setUTCDate(date.getUTCDate() + step);
    for (let attempts = 0; attempts < 31; attempts++, date.setUTCDate(date.getUTCDate() + step)) {
      const value = date.toISOString().slice(0, 10);
      if (!value.startsWith(state.month)) return;
      const candidate = ui.calendar.querySelector(`button[data-date="${value}"]`);
      if (candidate && !candidate.disabled) {
        ui.calendar.querySelectorAll('.day-select').forEach(item => { item.tabIndex = item === candidate ? 0 : -1; });
        candidate.focus();
        return;
      }
    }
  });
  window.addEventListener('popstate', () => { readLocation(); render(null, false); });
  readLocation();
  render();
})();
