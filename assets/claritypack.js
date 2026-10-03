(function () {
  'use strict';
  const form = document.querySelector('[data-clarity-form]');
  if (!form) return;
  const key = 'claritypack10:' + document.body.dataset.tool;
  const output = document.querySelector('[data-output]');
  const empty = document.querySelector('[data-empty]');
  const status = document.querySelector('[data-status]');
  const exampleNotice = document.querySelector('[data-example-notice]');
  const reportMeta = document.querySelector('[data-report-meta]');
  let saveTimer;
  let exampleLoaded = false;
  const escape = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#039;'}[c]));
  function values() { return Object.fromEntries(new FormData(form).entries()); }
  function fields() { return Array.from(form.elements).filter(el => el.name && el.type !== 'hidden'); }
  function hasExample() { return exampleLoaded && fields().some(el => el.type !== 'number' && el.tagName !== 'SELECT' && el.dataset.sample && el.value === el.dataset.sample); }
  function label(el) { return el.dataset.label || el.name; }
  function save(ready = false) {
    try { localStorage.setItem(key, JSON.stringify(values())); localStorage.setItem(key + ':example', JSON.stringify(hasExample())); status.textContent = ready ? 'Report ready. Draft saved on this device.' : 'Saved on this device. Generate a report to refresh the output.'; }
    catch (_) { status.textContent = 'Browser storage is unavailable. You can still generate and print a report; this draft will not survive a refresh.'; }
  }
  function render() {
    clearTimeout(saveTimer);
    const data = values();
    if (document.body.dataset.tool === 'contractor-quote-comparison' && !window.DeekeQuoteComparison) {
      status.textContent = 'The quote comparison could not load. Refresh this page before generating a comparison.';
      output.classList.remove('active'); empty.hidden = false;
      return;
    }
    if (!fields().some(el => el.name !== 'currency' && String(el.value).trim() && el.value !== 'unknown')) {
      status.textContent = 'Enter some details or load the example before generating a report.';
      output.classList.remove('active'); empty.hidden = false;
      return;
    }
    document.querySelector('[data-report-title]').textContent = String(data.subject || '').trim() || form.dataset.report || 'Clarity report';
    if (exampleNotice) exampleNotice.hidden = !hasExample();
    if (reportMeta) reportMeta.textContent = 'Generated ' + new Date().toLocaleString() + ' · Based on your entries; not independently verified.';
    if (document.body.dataset.tool === 'contractor-quote-comparison' && window.DeekeQuoteComparison) {
      const report = window.DeekeQuoteComparison.render(data);
      document.querySelector('[data-completion]').textContent = report.completion;
      document.querySelector('[data-report-body]').innerHTML = report.html;
    } else {
      const visibleFields = fields();
      const filled = visibleFields.filter(el => String(el.value).trim()).length;
      document.querySelector('[data-completion]').textContent = filled + ' of ' + visibleFields.length + ' sections recorded';
      document.querySelector('[data-report-body]').innerHTML = visibleFields.map(el => '<div><dt>' + escape(label(el)) + '</dt><dd>' + (String(el.value).trim() ? escape(el.tagName === 'SELECT' ? el.selectedOptions[0].textContent : el.value) : '<span class="cp-missing">Not recorded — add this information if it applies.</span>') + '</dd></div>').join('');
    }
    empty.hidden = true; output.classList.add('active'); save(true);
  }
  function load() {
    try {
      const data = JSON.parse(localStorage.getItem(key) || '{}');
      if (!data || Array.isArray(data) || typeof data !== 'object') throw new Error('Invalid draft');
      exampleLoaded = localStorage.getItem(key + ':example') === 'true';
      Object.entries(data).forEach(([name, value]) => {const field = form.elements.namedItem(name); if (field && typeof value === 'string') field.value = value;});
      if (Object.keys(data).length) status.textContent = 'Previous draft restored from this device. Generate a report to review it.';
    } catch (_) { status.textContent = 'No draft could be restored. You can still enter details and print a report.'; }
  }
  form.addEventListener('submit', event => { event.preventDefault(); if (!form.reportValidity()) return; render(); if (output.classList.contains('active')) output.scrollIntoView({behavior: window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'start'}); });
  function edited() {
    clearTimeout(saveTimer);
    if (output.classList.contains('active')) {output.classList.remove('active'); empty.hidden = false;}
    status.textContent = 'Draft changed. Generate a report to refresh the output.';
    saveTimer = setTimeout(save, 350);
  }
  form.addEventListener('input', edited);
  form.addEventListener('change', edited);
  document.querySelector('button[data-sample]').addEventListener('click', () => {
    if (Array.from(form.elements).some(el => el.name && el.value.trim() && el.value !== (el.tagName === 'SELECT' ? (Array.from(el.options).find(option => option.defaultSelected) || el.options[0]).value : el.defaultValue)) && !confirm('Replace the current draft with the example?')) return;
    clearTimeout(saveTimer);
    exampleLoaded = true;
    Array.from(form.elements).filter(el => el.name).forEach(el => {el.value = el.dataset.sample || el.defaultValue || '';});
    render();
  });
  document.querySelector('[data-clear]').addEventListener('click', () => {
    if (!confirm('Clear this draft from this device?')) return;
    clearTimeout(saveTimer); form.reset(); exampleLoaded = false;
    Array.from(form.elements).filter(el => el.type === 'hidden').forEach(el => {el.value = '';});
    let cleared = true;
    try {localStorage.removeItem(key); localStorage.removeItem(key + ':example');} catch (_) {cleared = false;}
    output.classList.remove('active'); empty.hidden = false;
    document.querySelector('[data-report-body]').textContent = '';
    status.textContent = cleared ? 'Draft cleared from this browser.' : 'Form cleared. Browser storage could not be accessed; use browser settings to remove any saved draft.';
  });
  document.querySelector('[data-print]').addEventListener('click', () => {if (output.classList.contains('active')) window.print();});
  load();
})();
