(function () {
  'use strict';
  const form = document.querySelector('[data-clarity-form]');
  if (!form) return;
  const key = 'claritypack10:' + document.body.dataset.tool;
  const output = document.querySelector('[data-output]');
  const empty = document.querySelector('[data-empty]');
  const status = document.querySelector('[data-status]');
  let saveTimer;
  const escape = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#039;'}[c]));
  function values() { return Object.fromEntries(new FormData(form).entries()); }
  function save() {
    try { localStorage.setItem(key, JSON.stringify(values())); status.textContent = 'Saved on this device. Generate a report to refresh the output.'; }
    catch (_) { status.textContent = 'Browser storage is unavailable. You can still generate and print a report; this draft will not survive a refresh.'; }
  }
  function render() {
    clearTimeout(saveTimer);
    const data = values();
    document.querySelector('[data-report-title]').textContent = (data.subject || form.dataset.report || 'Clarity report').trim();
    if (document.body.dataset.tool === 'contractor-quote-comparison' && window.DeekeQuoteComparison) {
      const report = window.DeekeQuoteComparison.render(data);
      document.querySelector('[data-completion]').textContent = report.completion;
      document.querySelector('[data-report-body]').innerHTML = report.html;
    } else {
      const fields = Array.from(form.elements).filter(el => el.name && el.type !== 'hidden');
      const filled = fields.filter(el => String(el.value).trim()).length;
      document.querySelector('[data-completion]').textContent = Math.round(filled / Math.max(fields.length, 1) * 100) + '% of fields filled';
      document.querySelector('[data-report-body]').innerHTML = fields.filter(el => String(el.value).trim()).map(el => '<div><dt>' + escape(el.dataset.label || el.name) + '</dt><dd>' + escape(el.value) + '</dd></div>').join('');
    }
    empty.hidden = true; output.classList.add('active'); save();
  }
  function load() {
    try {
      const data = JSON.parse(localStorage.getItem(key) || '{}');
      if (!data || Array.isArray(data) || typeof data !== 'object') throw new Error('Invalid draft');
      Object.entries(data).forEach(([name, value]) => {const field = form.elements.namedItem(name); if (field && typeof value === 'string') field.value = value;});
      if (Object.keys(data).length) status.textContent = 'Previous draft restored from this device. Generate a report to review it.';
    } catch (_) { status.textContent = 'No draft could be restored. You can still enter details and print a report.'; }
  }
  form.addEventListener('submit', event => { event.preventDefault(); if (!form.reportValidity()) return; render(); output.scrollIntoView({behavior:'smooth', block:'start'}); });
  function edited() {
    clearTimeout(saveTimer);
    if (output.classList.contains('active')) {output.classList.remove('active'); empty.hidden = false;}
    status.textContent = 'Draft changed. Generate a report to refresh the output.';
    saveTimer = setTimeout(save, 350);
  }
  form.addEventListener('input', edited);
  form.addEventListener('change', edited);
  document.querySelector('[data-sample]').addEventListener('click', () => {
    if (Array.from(form.elements).some(el => el.name && el.value.trim() && el.value !== (el.tagName === 'SELECT' ? (Array.from(el.options).find(option => option.defaultSelected) || el.options[0]).value : el.defaultValue)) && !confirm('Replace the current draft with the example?')) return;
    clearTimeout(saveTimer);
    Array.from(form.elements).filter(el => el.name).forEach(el => {el.value = el.dataset.sample || el.defaultValue || '';});
    render();
  });
  document.querySelector('[data-clear]').addEventListener('click', () => {
    if (!confirm('Clear this draft from this device?')) return;
    clearTimeout(saveTimer); form.reset();
    Array.from(form.elements).filter(el => el.type === 'hidden').forEach(el => {el.value = '';});
    let cleared = true;
    try {localStorage.removeItem(key);} catch (_) {cleared = false;}
    output.classList.remove('active'); empty.hidden = false;
    document.querySelector('[data-report-body]').textContent = '';
    status.textContent = cleared ? 'Draft cleared from this browser.' : 'Form cleared. Browser storage could not be accessed; use browser settings to remove any saved draft.';
  });
  document.querySelector('[data-print]').addEventListener('click', () => {if (output.classList.contains('active')) window.print();});
  load();
})();
