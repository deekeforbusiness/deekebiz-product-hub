/* Progressive enhancement only. All products and links work without JS. */
(() => {
  'use strict';
  const cards = [...document.querySelectorAll('#product-grid [data-product]')];
  const count = document.querySelector('[data-product-count]');
  const links = [...document.querySelectorAll('[data-category-link]')];
  const search = document.querySelector('[data-product-search]');
  const empty = document.querySelector('[data-product-empty]');
  let activeCategory = 'all';
  const allowed = new Set(['all', 'featured', ...cards.map(card => card.dataset.category)]);
  const hashFor = key => key === 'featured' ? '#featured' : key === 'all' ? '#catalog' : '#catalog-' + key;
  const keyFromHash = () => {
    if (location.hash === '#featured') return 'featured';
    if (location.hash === '#catalog') return 'all';
    if (location.hash.startsWith('#catalog-')) {
      const key = location.hash.slice(9);
      return allowed.has(key) ? key : null;
    }
    return null;
  };
  const filter = key => {
    if (!allowed.has(key) || !cards.length) return;
    activeCategory = key;
    const query = (search?.value || '').trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const categoryMatches = key === 'all' || (key === 'featured' ? card.dataset.featured === 'true' : card.dataset.category === key);
      const matches = categoryMatches && (!query || card.textContent.toLocaleLowerCase().includes(query));
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    links.forEach(link => link.setAttribute('aria-current', String(link.dataset.categoryLink === key)));
    if (count) count.textContent = key === 'featured' ? visible + ' starting points · prices in USD' : visible + (visible === 1 ? ' product' : ' products') + ' · prices in USD';
    if (empty) empty.hidden = visible !== 0;
  };
  filter(keyFromHash() || 'all');
  search?.addEventListener('input', () => filter(activeCategory));
  const searchWrap = document.querySelector('[data-product-search-wrap]');
  if (searchWrap && cards.length) searchWrap.hidden = false;
  links.forEach(link => link.addEventListener('click', event => {
    const key = link.dataset.categoryLink;
    if (!allowed.has(key)) return;
    event.preventDefault();
    if (search) search.value = '';
    filter(key);
    const hash = hashFor(key);
    if (location.hash !== hash) history.pushState(null, '', hash);
    if (!link.classList.contains('store-filter')) document.getElementById('catalog')?.scrollIntoView({block: 'start'});
  }));
  const sync = () => { const key = keyFromHash(); if (key) filter(key); };
  window.addEventListener('hashchange', sync);
  window.addEventListener('popstate', () => filter(keyFromHash() || 'all'));

  const tabs = [...document.querySelectorAll('[data-preview-tab]')];
  const panels = [...document.querySelectorAll('.store-preview-panel')];
  const activate = (tab, focus = false) => {
    tabs.forEach(item => {
      const active = item === tab;
      item.setAttribute('aria-selected', String(active));
      item.tabIndex = active ? 0 : -1;
    });
    panels.forEach(panel => { panel.hidden = panel.id !== tab.getAttribute('aria-controls'); });
    if (focus) tab.focus();
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activate(tab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); activate(tabs[next], true); }
    });
  });
  const tablist = document.querySelector('[data-preview-tabs]');
  if (tablist && tabs.length) tablist.hidden = false;
})();
