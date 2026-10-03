const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname,'../assets/claritypack.js'),'utf8');
function app(storageFails=false,tool='freelancer-scope-creep-checker') {
  function element(extra={}) {
    const classes=new Set();
    return {dataset:{},value:'',defaultValue:'',name:'',type:'',tagName:'DIV',hidden:false,textContent:'',innerHTML:'',listeners:{},classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),contains:x=>classes.has(x)},addEventListener(name,fn){this.listeners[name]=fn;},scrollIntoView(){},...extra};
  }
  const subject=element({name:'subject',type:'text',tagName:'INPUT',dataset:{sample:'Example & project',label:'Project'}});
  const request=element({name:'request',tagName:'TEXTAREA',dataset:{sample:'<New request>',label:'Request'}});
  const fields=[subject,request];fields.namedItem=name=>fields.find(f=>f.name===name);
  const form=element({elements:fields,dataset:{report:'Report'},reportValidity:()=>true,reset:()=>fields.forEach(f=>f.value=f.defaultValue)});
  const output=element(),empty=element(),status=element(),body=element(),title=element(),completion=element(),notice=element({hidden:true}),meta=element();
  const sample=element({tagName:'BUTTON'}),clear=element(),print=element();
  const selectors={'[data-clarity-form]':form,'[data-output]':output,'[data-empty]':empty,'[data-status]':status,'[data-report-body]':body,'[data-report-title]':title,'[data-completion]':completion,'[data-example-notice]':notice,'[data-report-meta]':meta,'[data-sample]':subject,'button[data-sample]':sample,'[data-clear]':clear,'[data-print]':print};
  const saved=new Map(),timers=new Map();let nextTimer=0;
  const localStorage={getItem:k=>saved.get(k)||null,setItem(k,v){if(storageFails)throw Error('Storage blocked');saved.set(k,v);},removeItem(k){saved.delete(k);}};
  class FormData {constructor(f){this.f=f;}entries(){return this.f.elements.map(f=>[f.name,f.value])[Symbol.iterator]();}}
  vm.runInNewContext(source,{document:{body:{dataset:{tool}},querySelector:s=>selectors[s]},window:{print(){}},localStorage,FormData,confirm:()=>true,setTimeout(fn){const id=++nextTimer;timers.set(id,fn);return id;},clearTimeout(id){timers.delete(id);}});
  return {form,fields,subject,request,output,empty,status,body,title,completion,notice,meta,sample,clear,saved,timers};
}
test('Load example responds to the button and renders safe sample content',()=>{
  const a=app();assert.equal(a.subject.listeners.click,undefined);a.sample.listeners.click();
  assert.equal(a.subject.value,'Example & project');assert.equal(a.title.textContent,'Example & project');assert.equal(a.output.classList.contains('active'),true);assert.match(a.body.innerHTML,/&lt;New request&gt;/);
});
test('editing invalidates stale output and clearing cancels pending autosave',()=>{
  const a=app();a.sample.listeners.click();a.subject.value='Changed';a.form.listeners.input();
  assert.equal(a.output.classList.contains('active'),false);assert.equal(a.timers.size,1);
  a.clear.listeners.click();assert.equal(a.timers.size,0);assert.equal(a.saved.size,0);assert.equal(a.subject.value,'');assert.equal(a.body.textContent,'');
});
test('blocked storage still permits a usable report with an honest status',()=>{
  const a=app(true);a.sample.listeners.click();assert.equal(a.output.classList.contains('active'),true);assert.match(a.status.textContent,/storage is unavailable/);assert.equal(a.saved.size,0);
});
test('empty and whitespace-only drafts cannot produce printable empty reports',()=>{
  const a=app();a.subject.value='   ';a.form.listeners.submit({preventDefault(){}});
  assert.equal(a.output.classList.contains('active'),false);assert.match(a.status.textContent,/Enter some details/);assert.equal(a.saved.size,0);
});
test('partial records show unanswered sections and report-ready status',()=>{
  const a=app();a.request.value='Please add another landing page';a.form.listeners.submit({preventDefault(){}});
  assert.equal(a.title.textContent,'Report');assert.match(a.body.innerHTML,/Project.*Not recorded/s);assert.match(a.body.innerHTML,/Please add another landing page/);
  assert.equal(a.completion.textContent,'1 of 2 sections recorded');assert.match(a.status.textContent,/Report ready/);assert.match(a.meta.textContent,/not independently verified/);
});
test('sample warning follows actual sample use, persists and clears after replacing sample text',()=>{
  const a=app();a.sample.listeners.click();assert.equal(a.notice.hidden,false);assert.equal([...a.saved.values()].includes('true'),true);
  a.subject.value='My project';a.request.value='My request';a.form.listeners.input();a.form.listeners.submit({preventDefault(){}});
  assert.equal(a.notice.hidden,true);assert.equal([...a.saved.values()].includes('false'),true);
  a.clear.listeners.click();assert.equal(a.saved.size,0);
});
test('missing calculation engine cannot silently produce a generic quote report',()=>{
  const a=app(false,'contractor-quote-comparison');a.sample.listeners.click();
  assert.equal(a.output.classList.contains('active'),false);assert.match(a.status.textContent,/comparison could not load/);
});
