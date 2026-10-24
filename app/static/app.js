'use strict';
let user = null, csrf = '', events = [], signup = false, mine = false;
const $ = id => document.getElementById(id);
const esc = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path, method='GET', data) {
  const response = await fetch('/api' + path, {method, headers:{'Content-Type':'application/json','X-CSRF-Token':csrf}, ...(data ? {body:JSON.stringify(data)} : {})});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Sorğu uğursuz oldu.');
  return result;
}
function notice(message) { $('notice').textContent = message; $('notice').hidden = false; }
async function sessionLoad() {
  const state = await api('/session'); user = state.user; csrf = state.csrf;
  $('userName').textContent = user ? user.name : '';
  $('authOpen').hidden = !!user; $('logout').hidden = !user; $('mineTab').hidden = !user;
  $('newEvent').hidden = user?.role !== 'admin'; $('statsTab').hidden = user?.role !== 'admin';
}
async function loadEvents() {
  const params = new URLSearchParams(new FormData($('filters')));
  if (mine) params.set('mine','1');
  events = await api('/events?' + params);
  $('resultCount').textContent = `${events.length} tədbir tapıldı`;
  $('eventGrid').innerHTML = events.length ? events.map(e => {
    const day = e.starts_at.slice(8,10), month = ['YAN','FEV','MAR','APR','MAY','İYN','İYL','AVQ','SEN','OKT','NOY','DEK'][Number(e.starts_at.slice(5,7))-1];
    const full = e.registered >= e.capacity;
    const button = e.is_registered ? `<button data-action="cancel" data-id="${e.id}">Qeydiyyatı ləğv et</button>` : `<button class="primary" data-action="register" data-id="${e.id}" ${e.past || full ? 'disabled' : ''}>${e.past ? 'Başa çatıb' : full ? 'Yer qalmayıb' : 'Qeydiyyatdan keç ↗'}</button>`;
    return `<article class="card"><div class="cardBanner"><span class="symbol">${['◈','◎','✦','◇','◉'][e.category_id-1] || '◈'}</span><div class="dateBox"><strong>${day}</strong>${month}</div></div><div class="cardBody"><span class="badge ${e.past ? 'past' : ''}">${esc(e.category)} · ${e.past ? 'KEÇMİŞ' : 'GƏLƏCƏK'}</span><h3>${esc(e.title)}</h3><div class="eventMeta">◷ ${esc(e.starts_at.slice(0,10))} · ${esc(e.starts_at.slice(11,16))}<br>⌖ ${esc(e.location)}</div><p>${esc(e.description.slice(0,110))}${e.description.length > 110 ? '…' : ''}</p><div class="cardBottom"><div class="capacity"><span>${e.registered} / ${e.capacity} iştirakçı</span><span>${e.capacity-e.registered} boş yer</span></div><progress value="${e.registered}" max="${e.capacity}" aria-label="Qeydiyyat doluluğu"></progress><div class="actions">${button}<button data-action="details" data-id="${e.id}">Ətraflı</button>${user?.role === 'admin' ? `<button data-action="edit" data-id="${e.id}">Redaktə</button><button data-action="delete" data-id="${e.id}">Sil</button><a href="/api/events/${e.id}/participants.csv">CSV ixracı ↓</a>` : ''}</div></div></div></article>`;
  }).join('') : '<div class="empty">Uyğun tədbir tapılmadı. Axtarış şərtlərini dəyişin.</div>';
}
function showCatalog(own=false) {
  mine = own; $('catalog').hidden=false; $('dashboard').hidden=true;
  $('allTab').classList.toggle('active',!own); $('mineTab').classList.toggle('active',own); $('statsTab').classList.remove('active');
  $('listTitle').textContent = own ? 'Qeydiyyatlarım' : 'Tədbirləri kəşf et';
  loadEvents().catch(e=>notice(e.message));
}
$('filters').onsubmit = e => { e.preventDefault(); loadEvents().catch(e=>notice(e.message)); };
$('filters').onreset = () => setTimeout(()=>loadEvents().catch(e=>notice(e.message)),0);
$('allTab').onclick = ()=>showCatalog(); $('mineTab').onclick = ()=>showCatalog(true);
$('authOpen').onclick = ()=>$('authDialog').showModal();
for (const close of document.querySelectorAll('[data-close]')) close.onclick=()=>$(close.dataset.close).close();
$('authToggle').onclick = ()=>{
  signup = !signup; $('nameLabel').hidden = !signup; $('authForm').elements.name.required = signup;
  $('authTitle').textContent = signup ? 'Yeni hesab yarat' : 'Xoş gəlmisiniz';
  $('authSubmit').textContent = signup ? 'Hesab yarat' : 'Daxil ol';
  $('authToggle').textContent = signup ? 'Hesabın var? Daxil ol' : 'Hesabın yoxdur? Qeydiyyatdan keç'; $('authError').textContent='';
};
$('authForm').onsubmit = async e=>{
  e.preventDefault(); $('authSubmit').disabled=true;
  try { const result = await api(signup ? '/signup' : '/login','POST',Object.fromEntries(new FormData(e.target))); notice(result.message);
    if (signup) { $('authToggle').click(); e.target.elements.password.value=''; }
    else { e.target.reset(); $('authDialog').close(); await sessionLoad(); await loadEvents(); }
  } catch(error) { $('authError').textContent=error.message; }
  finally { $('authSubmit').disabled=false; }
};
$('logout').onclick = async()=>{try {await api('/logout','POST',{});await sessionLoad();showCatalog();notice('Hesabdan çıxıldı.');}catch(e){notice(e.message);}};
function editor(event) {
  $('eventForm').reset(); $('eventError').textContent=''; $('editorTitle').textContent=event?'Tədbiri redaktə et':'Yeni tədbir';
  $('eventForm').elements.id.value=event?.id || '';
  if (event) for (const key of ['title','description','category_id','starts_at','location','capacity']) $('eventForm').elements[key].value=event[key];
  $('eventDialog').showModal();
}
$('newEvent').onclick=()=>editor();
$('eventForm').onsubmit=async e=>{e.preventDefault();const data=Object.fromEntries(new FormData(e.target)), id=data.id;delete data.id;
  try {await api('/events'+(id?'/'+id:''),id?'PUT':'POST',data);$('eventDialog').close();await loadEvents();notice('Tədbir yadda saxlanıldı.');}catch(error){$('eventError').textContent=error.message;}
};
$('eventGrid').onclick=async e=>{
  const target=e.target.closest('button[data-action]');if(!target)return;
  const id=Number(target.dataset.id), event=events.find(x=>x.id===id), action=target.dataset.action;
  if(action==='edit'){editor(event);return;}
  if(action==='details'){$('details').innerHTML=`<span class="badge">${esc(event.category)}</span><h2>${esc(event.title)}</h2><p>${esc(event.description)}</p><p>Tarix: ${esc(event.starts_at.replace('T',' '))} (Bakı)<br>Məkan: ${esc(event.location)}<br>İştirakçılar: ${event.registered} / ${event.capacity}</p>`;$('detailDialog').showModal();return;}
  if(!user){$('authDialog').showModal();return;}
  if(action==='delete' && !confirm('Tədbir və bütün əlaqəli qeydiyyatlar silinsin?'))return;
  target.disabled=true;
  try {const result=await api(`/events/${id}`+(action==='delete'?'':'/registration'),action==='register'?'POST':'DELETE',{});notice(result.message);await loadEvents();}catch(error){notice(error.message);target.disabled=false;}
};
$('statsTab').onclick=async()=>{
  try {const stats=await api('/stats');$('catalog').hidden=true;$('dashboard').hidden=false;
    for(const id of ['allTab','mineTab'])$(id).classList.remove('active');$('statsTab').classList.add('active');
    $('totalEvents').textContent=stats.events;$('totalRegs').textContent=stats.registrations;
    const rows=(items,key)=>{const max=Math.max(1,...items.map(x=>x.count));return items.length?items.map(x=>`<div class="chartRow">${esc(x[key])}<strong>${x.count}</strong><progress value="${x.count}" max="${max}" aria-label="${esc(x[key])}"></progress></div>`).join(''):'Məlumat yoxdur.';};
    $('popular').innerHTML=rows(stats.popular,'title');$('categoryStats').innerHTML=rows(stats.categories,'name');
  }catch(error){notice(error.message);}
};
(async()=>{try{await sessionLoad();const categories=await api('/categories');for(const c of categories){$('categoryFilter').add(new Option(c.name,c.id));$('editorCategory').add(new Option(c.name,c.id));}await loadEvents();}catch(e){notice(e.message);}})();
