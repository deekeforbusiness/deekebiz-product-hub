(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.DeekeQuoteComparison = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const currencies = ['USD', 'CAD', 'GBP', 'EUR', 'AUD'];
  function cents(value) {
    let text = String(value == null ? '' : value).trim();
    if (!text) return null;
    if (text.startsWith('.')) text = '0' + text;
    if (!/^\d+(?:\.\d{1,2})?$/.test(text)) return null;
    const parts = text.split('.');
    const result = Number(parts[0]) * 100 + Number((parts[1] || '').padEnd(2, '0'));
    return Number.isSafeInteger(result) && result <= 99999999999 ? result : null;
  }
  function money(value, currency) {
    if (value === null) return 'Not entered';
    return new Intl.NumberFormat('en', {style: 'currency', currency: currencies.includes(currency) ? currency : 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2}).format(value / 100);
  }
  function analyzeQuote(data, prefix) {
    const get = key => String(data[prefix + '_' + key] || '').trim();
    const base = cents(get('amount'));
    const extra = cents(get('extras'));
    const taxStatus = get('tax_status');
    const tax = taxStatus === 'included' ? 0 : taxStatus === 'excluded' ? cents(get('tax')) : null;
    const gaps = [], questions = [];
    if (base === null) gaps.push('Quoted price is missing or invalid.');
    if (extra === null) gaps.push('Additional cost estimate is missing. Enter 0 only when no extras are expected.');
    if (tax === null) gaps.push('Tax inclusion or the additional tax amount is not confirmed.');
    if (!get('scope')) gaps.push('Included scope is not recorded.');
    if (!get('exclusions')) gaps.push('Exclusions are not recorded. Enter “None stated” only if that is what the quote says.');
    if (get('costs_confirmed') !== 'yes') gaps.push('Some scope changes, allowance costs, or other charges remain unpriced.');
    const allowances = [];
    for (let i = 1; i <= 3; i++) {
      const name = get('allowance_' + i + '_name');
      const budget = cents(get('allowance_' + i + '_budget'));
      const planned = cents(get('allowance_' + i + '_planned'));
      if (!name && budget === null && planned === null) continue;
      const gap = budget === null || planned === null ? null : Math.max(0, planned - budget);
      allowances.push({name: name || 'Unnamed allowance', budget, planned, gap});
      if (gap === null) gaps.push('Allowance “' + (name || i) + '” has a missing or invalid amount.');
      if (gap !== null && gap > 0) questions.push('Confirm the ' + (name || 'item') + ' allowance overrun, any markup or tax, and whether it is already in the extras estimate.');
    }
    if (!get('schedule')) questions.push('Ask for the start date, duration, and conditions that could delay completion.');
    if (!get('payments')) questions.push('Ask for deposit, progress-payment, and change-order terms in writing.');
    const subtotal = base === null ? null : base + (tax === null ? 0 : tax) + (extra === null ? 0 : extra);
    const allowanceGap = allowances.some(a => a.gap === null) ? null : allowances.reduce((sum, a) => sum + a.gap, 0);
    return {name: get('name') || 'Quote ' + prefix.toUpperCase(), base, extra, tax, taxStatus, subtotal, allowances, allowanceGap, gaps, questions, scope: get('scope'), exclusions: get('exclusions'), schedule: get('schedule'), payments: get('payments'), complete: gaps.length === 0};
  }
  function compare(data) {
    const a = analyzeQuote(data, 'a'), b = analyzeQuote(data, 'b');
    const scopeMatches = data.scope_match === 'yes';
    const comparable = a.complete && b.complete && scopeMatches;
    const difference = a.subtotal === null || b.subtotal === null ? null : Math.abs(a.subtotal - b.subtotal);
    const lower = !comparable ? null : a.subtotal === b.subtotal ? 'equal' : a.subtotal < b.subtotal ? 'a' : 'b';
    return {a, b, currency: currencies.includes(data.currency) ? data.currency : 'USD', comparable, difference, lower, scopeMatches};
  }
  function escape(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#039;'}[c]));
  }
  function render(data) {
    const r = compare(data), e = escape, cash = v => money(v, r.currency);
    const row = (label, a, b) => '<tr><th scope="row">' + label + '</th><td>' + e(a) + '</td><td>' + e(b) + '</td></tr>';
    let heading = 'Resolve the gaps before comparing totals.';
    if (r.comparable) heading = r.lower === 'equal' ? 'The entered totals are equal for the scope you marked as matching.' : (r.lower === 'a' ? r.a.name : r.b.name) + ' has the lower entered total for the scope you marked as matching.';
    const notice = r.comparable ? 'This comparison uses your figures and confirmation of matching scope. It does not assess contractor quality, suitability, or the accuracy of a quote.' : 'Unentered amounts remain unknown. Known subtotals do not include missing tax, missing extras, or unpriced scope. No quote is ranked while these gaps remain.';
    let output = '<div class="cp-comparison-summary"><h3>' + e(heading) + '</h3><p>' + notice + '</p></div>';
    output += '<div class="cp-table-wrap"><table class="cp-quote-table"><caption>Entered costs in ' + r.currency + '</caption><thead><tr><th scope="col">Cost</th><th scope="col">' + e(r.a.name) + '</th><th scope="col">' + e(r.b.name) + '</th></tr></thead><tbody>';
    output += row('Quoted amount', cash(r.a.base), cash(r.b.base));
    output += row('Tax treatment', r.a.taxStatus === 'included' ? 'Included in quote' : r.a.taxStatus === 'excluded' ? 'Excluded: ' + cash(r.a.tax) : 'Not confirmed', r.b.taxStatus === 'included' ? 'Included in quote' : r.b.taxStatus === 'excluded' ? 'Excluded: ' + cash(r.b.tax) : 'Not confirmed');
    output += row('Extra costs entered', cash(r.a.extra), cash(r.b.extra));
    output += row('Known subtotal', cash(r.a.subtotal), cash(r.b.subtotal)) + '</tbody></table></div>';
    if (r.difference !== null) output += '<p><strong>Difference between known subtotals: ' + cash(r.difference) + '.</strong> ' + (r.comparable ? 'Compare the written scope and terms before deciding.' : 'This difference does not establish which full project will cost less.') + '</p>';
    if (!r.scopeMatches) output += '<p class="cp-quote-warning">Matching scope has not been confirmed. Review what each quote includes and excludes.</p>';
    [r.a,r.b].forEach(q => {
      output += '<section class="cp-quote-detail"><h3>' + e(q.name) + '</h3><dl>';
      [['Included scope',q.scope],['Exclusions',q.exclusions],['Schedule',q.schedule],['Payment terms',q.payments]].forEach(([label,value]) => {output += '<div><dt>' + label + '</dt><dd>' + e(value || 'Not recorded') + '</dd></div>';});
      output += '</dl>';
      if (q.allowances.length) {
        output += '<h4>Allowances already in this quote</h4><ul>';
        q.allowances.forEach(a => {output += '<li>' + e(a.name) + ': quoted allowance ' + cash(a.budget) + '; planned amount ' + cash(a.planned) + '; potential gap ' + cash(a.gap) + '.</li>';});
        output += '</ul><p class="cp-help">Allowance gaps are shown separately and are not added automatically. Confirm markup and tax, then include the verified extra cost in the extras estimate once.</p>';
      }
      if (q.gaps.length) output += '<h4>Missing information</h4><ul>' + q.gaps.map(g => '<li>' + e(g) + '</li>').join('') + '</ul>';
      if (q.questions.length) output += '<h4>Questions to resolve</h4><ul>' + q.questions.map(g => '<li>' + e(g) + '</li>').join('') + '</ul>';
      output += '</section>';
    });
    if (data.quote_a || data.quote_b || data.differences || data.questions) output += '<section class="cp-quote-detail"><h3>Notes from your earlier draft</h3><p>These notes were preserved when the tool was upgraded. Enter the costs above to use the calculations.</p>' + ['quote_a','quote_b','differences','questions'].filter(k=>data[k]).map(k=>'<p>'+e(data[k])+'</p>').join('') + '</section>';
    if (data.notes) output += '<section class="cp-quote-detail"><h3>Your additional notes</h3><p class="cp-note-text">' + e(data.notes) + '</p></section>';
    return {html: output, completion: r.comparable ? 'Entered costs and matching scope reviewed' : 'Review the missing information', comparison: r};
  }
  return {cents, money, analyzeQuote, compare, render, escape};
});
