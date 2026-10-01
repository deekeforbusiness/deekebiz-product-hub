const assert = require('node:assert/strict');
const test = require('node:test');
const api = require('../assets/quote-comparison.js');
const complete = {
  currency: 'USD', scope_match: 'yes',
  a_name: 'Alpha', a_amount: '100.25', a_tax_status: 'included', a_extras: '0', a_scope: 'Matching scope', a_exclusions: 'None stated', a_costs_confirmed: 'yes',
  b_name: 'Bravo', b_amount: '95.50', b_tax_status: 'excluded', b_tax: '7.64', b_extras: '2.11', b_scope: 'Matching scope', b_exclusions: 'None stated', b_costs_confirmed: 'yes'
};
test('money preserves cents and rejects ambiguous, negative, and oversized amounts', () => {
  assert.equal(api.cents('24.99'),2499); assert.equal(api.cents('.99'),99); assert.equal(api.cents('0'),0);
  for(const amount of ['', '-1', '1,200.00', '10.001', 'NaN', 'Infinity', '1e3', '1000000000']) assert.equal(api.cents(amount),null);
  assert.equal(api.money(2499, 'USD'), '$24.99');
});
test('adds excluded tax and entered extras using integer cents', () => {
  const r = api.compare(complete); assert.equal(r.a.subtotal,10025); assert.equal(r.b.subtotal,10525); assert.equal(r.difference,500); assert.equal(r.lower,'a');
});
test('included tax is not added twice', () => {
  assert.equal(api.compare({...complete,a_tax:'50.00'}).a.subtotal,10025);
});
test('unknown tax and extras remain gaps and cannot generate a winning quote', () => {
  const r=api.compare({...complete,b_tax_status:'unknown',b_extras:''});
  assert.equal(r.b.tax,null);assert.equal(r.b.extra,null);assert.equal(r.b.subtotal,9550);assert.equal(r.comparable,false);assert.equal(r.lower,null);
  assert.match(api.render({...complete,b_tax_status:'unknown',b_extras:''}).html,/No quote is ranked/);
});
test('missing scope and unresolved costs prevent cost ranking', () => {
  for(const overrides of [{scope_match:'different'},{scope_match:'unknown'},{a_scope:''},{a_exclusions:''},{b_costs_confirmed:'unknown'},{a_amount:''}]){
    const r=api.compare({...complete,...overrides});assert.equal(r.comparable,false);assert.equal(r.lower,null);
  }
});
test('allowance gaps are reported separately and never double counted', () => {
  const r=api.compare({...complete,a_allowance_1_name:'Tile',a_allowance_1_budget:'20',a_allowance_1_planned:'30.01'});
  assert.equal(r.a.allowanceGap,1001);assert.equal(r.a.subtotal,10025);assert.equal(r.a.questions.some(q=>q.includes('markup or tax')),true);
  const missing=api.compare({...complete,a_allowance_1_name:'Tile',a_allowance_1_budget:'20'});
  assert.equal(missing.a.allowanceGap,null);assert.equal(missing.comparable,false);
});
test('equal totals are explicit and supported currencies are bounded', () => {
  assert.equal(api.compare({...complete,b_amount:'100.25',b_tax_status:'included',b_extras:'0'}).lower,'equal');
  assert.equal(api.compare({...complete,currency:'INVALID'}).currency,'USD');
});
test('user content and earlier draft notes cannot become executable HTML', () => {
  const r=api.render({...complete,a_name:'<img src=x onerror=alert(1)>',notes:'<script>bad()</script>',quote_a:'Old & preserved'});
  assert(!r.html.includes('<img src=x'));assert(!r.html.includes('<script>bad'));assert(r.html.includes('&lt;script&gt;'));assert(r.html.includes('Old &amp; preserved'));
});
