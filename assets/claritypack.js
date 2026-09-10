(function(){
  const form=document.querySelector('[data-clarity-form]');
  if(!form)return;
  const key='claritypack10:'+document.body.dataset.tool;
  const output=document.querySelector('[data-output]');
  const empty=document.querySelector('[data-empty]');
  const status=document.querySelector('[data-status]');
  const escape=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  function values(){return Object.fromEntries(new FormData(form).entries())}
  function save(){localStorage.setItem(key,JSON.stringify(values()));status.textContent='Saved privately on this device'}
  function render(){const data=values();const filled=Object.values(data).filter(v=>String(v).trim()).length;const total=Object.keys(data).length;document.querySelector('[data-report-title]').textContent=(data.subject||form.dataset.report||'Clarity report').trim();document.querySelector('[data-completion]').textContent=Math.round(filled/total*100)+'% complete';document.querySelector('[data-report-body]').innerHTML=Array.from(form.elements).filter(el=>el.name&&el.value.trim()).map(el=>`<div><dt>${escape(el.dataset.label||el.previousElementSibling?.textContent||el.name)}</dt><dd>${escape(el.value)}</dd></div>`).join('');empty.hidden=true;output.classList.add('active');save()}
  function load(){try{const data=JSON.parse(localStorage.getItem(key)||'{}');Object.entries(data).forEach(([k,v])=>{if(form.elements[k])form.elements[k].value=v});if(Object.keys(data).length)status.textContent='Previous draft restored from this device'}catch(e){localStorage.removeItem(key)}}
  form.addEventListener('submit',e=>{e.preventDefault();render();output.scrollIntoView({behavior:'smooth',block:'start'})});
  form.addEventListener('input',()=>{clearTimeout(window.cpTimer);window.cpTimer=setTimeout(save,350)});
  document.querySelector('button[data-sample]').addEventListener('click',()=>{Array.from(form.elements).filter(el=>el.name).forEach(el=>{el.value=el.dataset.sample||''});render()});
  document.querySelector('[data-clear]').addEventListener('click',()=>{if(!confirm('Clear this draft from this device?'))return;form.reset();localStorage.removeItem(key);output.classList.remove('active');empty.hidden=false;status.textContent='Draft cleared'});
  document.querySelector('[data-print]').addEventListener('click',()=>window.print());
  load();
})();
