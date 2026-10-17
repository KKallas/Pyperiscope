// Pyperiscope operator UI: sidebar (workflows, runs, targets) + one main view.
const TOKEN = new URLSearchParams(location.search).get('token') || sessionStorage.getItem('pp-token') || '';
if (TOKEN) sessionStorage.setItem('pp-token', TOKEN);
const $ = (sel, el = document) => el.querySelector(sel);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fileUrl = (rel, bust = '') => `/files/${rel}?token=${encodeURIComponent(TOKEN)}&v=${bust}`;
const ago = t => { const s = Math.round(Date.now() / 1000 - t); return s < 60 ? `${s}s ago` : s < 3600 ? `${Math.round(s / 60)}m ago` : `${Math.round(s / 3600)}h ago`; };
let STATE = null, VIEW = null, poll = null;

async function api(method, path, body) {
  const res = await fetch(path, { method, headers: { 'Content-Type': 'application/json', 'X-Token': TOKEN }, body: body ? JSON.stringify(body) : undefined });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) { const e = new Error(data.error || res.statusText); e.data = data; throw e; }
  return data;
}

function toast(msg, kind = 'info') {
  const t = $('#toast'); t.textContent = msg; t.className = kind; t.hidden = false;
  clearTimeout(t._h); t._h = setTimeout(() => (t.hidden = true), kind === 'error' ? 7000 : 3500);
}

// ---------------------------------------------------------------- sidebar
async function refresh() {
  try { STATE = await api('GET', '/api/state'); } catch (e) { $('#root-path').textContent = e.message; return; }
  $('#root-path').textContent = STATE.root;
  const human = STATE.runs.filter(r => r.status === 'needs_human');
  const alert = $('#human-alert'); alert.hidden = !human.length;
  alert.innerHTML = human.length ? `<button class="alert">⚠ ${human.length} run${human.length > 1 ? 's' : ''} need${human.length > 1 ? '' : 's'} a human</button>` : '';
  if (human.length) alert.firstChild.onclick = () => showRun(human[0].id);
  $('#workflows').innerHTML = STATE.workflows.map(w => `
    <li><div class="grow"><b>${esc(w.name)}</b><div class="muted small">${w.steps.length} steps</div></div>
    <button class="small" data-run="${esc(w.name)}">▶ Run</button></li>`).join('') || '<li class="muted">No workflows yet — ask your agent to write one.</li>';
  $('#workflows').querySelectorAll('[data-run]').forEach(b => b.onclick = () => startRun(b.dataset.run));
  $('#runs').innerHTML = STATE.runs.map(r => `
    <li class="link ${VIEW === 'run:' + r.id ? 'sel' : ''}" data-id="${esc(r.id)}"><span class="chip ${r.status}">${esc(r.status)}</span>
    <div class="grow"><b>${esc(r.workflow)}</b><div class="muted small">${r.step ? esc(r.step) + ' · ' : ''}${ago(r.updated || r.created)}</div></div></li>`).join('') || '<li class="muted">No runs yet.</li>';
  $('#runs').querySelectorAll('[data-id]').forEach(li => li.onclick = () => showRun(li.dataset.id));
  $('#targets').innerHTML = STATE.targets.map(t => `
    <li class="link ${VIEW === 'target:' + t.name ? 'sel' : ''}" data-name="${esc(t.name)}"><img class="thumb" src="${fileUrl(`targets/${t.name}/main.png`, t.confidence)}" alt="">
    <div class="grow"><b>${esc(t.name)}</b><div class="muted small">${t.details.length} detail${t.details.length === 1 ? '' : 's'} · ${t.confidence}</div></div></li>`).join('') || '<li class="muted">No targets yet.</li>';
  $('#targets').querySelectorAll('[data-name]').forEach(li => li.onclick = () => showTarget(li.dataset.name));
}

async function startRun(name) {
  try { const r = await api('POST', `/api/workflows/${name}/run`, {}); toast(`Started ${name}`); setTimeout(() => showRun(r.run_id), 800); }
  catch (e) { toast(e.message, 'error'); }
}

function setView(key, html) {
  VIEW = key; clearInterval(poll); $('#view').innerHTML = html; refresh();
}

// ---------------------------------------------------------------- new target
function showCapture() {
  setView('capture', `
    <div class="head"><h1>New target</h1>
      <div class="seg"><button id="cap0">Capture now</button><button id="cap3">in 3 s</button><button id="cap5">in 5 s</button></div></div>
    <p class="muted">Capture the screen, drag a <b>main box</b> around the element, optionally set the <b>click point</b>,
      and add up to 4 <b>details</b> — nearby patches that make it unique. Saving tests it on this screenshot and only
      accepts a target that matches exactly once.</p>
    <div class="cols"><div id="ed" class="editor"></div>
    <form id="form" class="panel">
      <label>Name <input name="name" required pattern="[A-Za-z0-9][A-Za-z0-9_.\\-]*" placeholder="invoice.save_button"></label>
      <label>Note <input name="note" placeholder="what it is, for humans & agents"></label>
      <label>Confidence <input name="confidence" type="number" min="0.5" max="1" step="0.01" value="${STATE?.config.confidence ?? 0.9}"></label>
      <label class="row"><input type="checkbox" name="force"> replace if it exists</label>
      <div id="summary" class="muted small"></div>
      <button class="primary" type="submit">Save &amp; validate</button>
    </form></div>`);
  let shot = null;
  const ed = new Editor($('#ed'), { onChange: st => {
    $('#summary').innerHTML = st.main ? `main ${st.main.join(', ')}<br>click ${ed.clickPoint().join(', ')}<br>${st.details.length} detail(s)` : 'No main box yet.';
  } });
  const capture = async delay => {
    try {
      if (delay) toast(`Capturing in ${delay} s — switch to the app now`);
      ed.img = null; shot = null; ed.layout();          // no drawing on a stale image while capturing
      const r = await api('POST', '/api/screenshot', { delay }); shot = r.shot;
      await ed.load(fileUrl(shot)); ed.set({ main: null, click: null, details: [], candidates: [], picked: null });
    } catch (e) { toast(e.message, 'error'); }
  };
  $('#cap0').onclick = () => capture(0); $('#cap3').onclick = () => capture(3); $('#cap5').onclick = () => capture(5);
  $('#form').onsubmit = async ev => {
    ev.preventDefault();
    if (!shot || !ed.st.main) return toast('Capture a screenshot and draw the main box first', 'error');
    const f = new FormData(ev.target);
    try {
      const r = await api('POST', '/api/targets', { name: f.get('name'), note: f.get('note'), confidence: Number(f.get('confidence')),
        force: !!f.get('force'), shot, box: ed.st.main, click: ed.clickPoint(), details: ed.st.details.map(box => ({ box })) });
      toast(`Saved ${r.target.name}: unique match (score ${r.match.score})`, 'ok'); showTarget(r.target.name);
    } catch (e) { ed.set({ candidates: e.data?.matches || [] }); toast(e.message, 'error'); }
  };
}

// ---------------------------------------------------------------- one target
async function showTarget(name) {
  const t = STATE.targets.find(x => x.name === name); if (!t) return;
  const bust = Date.now();
  setView('target:' + name, `
    <div class="head"><h1>${esc(name)}</h1><div class="seg"><button id="test-live">Test on live screen</button><button id="del" class="danger">Delete</button></div></div>
    <div class="patches">
      <figure><img src="${fileUrl(`targets/${name}/main.png`, bust)}"><figcaption>main · click ${t.click.join(', ')}</figcaption></figure>
      ${t.details.map((d, i) => `<figure><img src="${fileUrl(`targets/${name}/${d.file}`, bust)}">
        <figcaption>D${i + 1} · offset ${d.offset.join(', ')} ±${d.tolerance} <button class="small" data-drop="${i + 1}">remove</button></figcaption></figure>`).join('')}
    </div>
    <form id="meta" class="inline"><label>Note <input name="note" value="${esc(t.note)}"></label>
      <label>Confidence <input name="confidence" type="number" min="0.5" max="1" step="0.01" value="${t.confidence}"></label><button>Save</button></form>
    <div id="result" class="muted"></div><div id="ed" class="editor" hidden></div>
    <div id="fix" class="panel" hidden><button class="primary" id="add-detail">Add detail &amp; validate</button></div>`);
  $('#meta').onsubmit = async ev => {
    ev.preventDefault(); const f = new FormData(ev.target);
    try { await api('PATCH', `/api/targets/${name}`, { note: f.get('note'), confidence: Number(f.get('confidence')) }); toast('Saved', 'ok'); await refresh(); showTarget(name); }
    catch (e) { toast(e.message, 'error'); }
  };
  document.querySelectorAll('[data-drop]').forEach(b => b.onclick = async () => {
    try { await api('PATCH', `/api/targets/${name}`, { drop_detail: Number(b.dataset.drop) }); await refresh(); showTarget(name); } catch (e) { toast(e.message, 'error'); }
  });
  $('#del').onclick = async () => { if (!confirm(`Delete target ${name}?`)) return; await api('DELETE', `/api/targets/${name}`); showCapture(); };
  $('#test-live').onclick = async () => {
    try { const r = await api('POST', `/api/targets/${name}/test`, {}); await showMatches(name, r); } catch (e) { toast(e.message, 'error'); }
  };
}

async function showMatches(name, r) {
  const n = r.matches.length;
  $('#result').innerHTML = n === 1 ? '<span class="ok">✓ exactly one match</span>' : n === 0
    ? `<span class="bad">✗ not found</span> (best score ${r.best?.score ?? '—'})` : `<span class="warn">⚠ ${n} matches</span> — pick the right one, then draw a detail next to it.`;
  $('#ed').hidden = false;
  const ed = new Editor($('#ed'), { tools: n > 1 ? ['pick', 'detail'] : ['pick'] });
  await ed.load(fileUrl(r.shot));
  const best = r.best && Object.assign([...r.best.at, ...r.size], { score: r.best.score });
  ed.set({ candidates: r.matches, best: n ? null : best });
  $('#fix').hidden = n < 2;
  $('#add-detail').onclick = () => addDetail(name, r.shot, ed);
}

async function addDetail(name, shot, ed, after) {
  if (ed.st.picked == null) return toast('Pick the right candidate first', 'error');
  if (!ed.st.details.length) return toast('Draw a detail box next to the picked candidate', 'error');
  try {
    const r = await api('POST', `/api/targets/${name}/detail`, { shot, candidate: ed.st.picked, box: ed.st.details[ed.st.details.length - 1] });
    toast(`Validated: ${name} is now unique (score ${r.match.score})`, 'ok');
    await refresh(); after ? after() : showTarget(name);
  } catch (e) { ed.set({ details: [] }); toast(e.message, 'error'); }
}
