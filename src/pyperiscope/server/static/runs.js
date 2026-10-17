// Run view: attempts, agent notes, and — when the ladder reaches a human —
// the failure screenshot with tools to fix the target and retry.
async function showRun(id) {
  let run;
  try { run = await api('GET', `/api/runs/${id}`); }
  catch (e) { setView('run:' + id, `<h1>Run ${esc(id)}</h1><p class="muted">Starting… (${esc(e.message)})</p>`); poll = setInterval(() => showRun(id), 1500); return; }
  const f = run.failure, waiting = run.status === 'needs_human';
  const last = run.attempts[run.attempts.length - 1];
  setView('run:' + id, `
    <div class="head"><h1>${esc(run.workflow)} <span class="chip ${run.status}">${esc(run.status)}</span></h1><span class="muted">${esc(run.id)}</span></div>
    ${run.message ? `<p>${esc(run.message)}</p>` : ''}
    <table class="attempts"><tr><th>#</th><th>from step</th><th>result</th><th>failed in</th><th>what</th><th>then</th></tr>
    ${run.attempts.map(a => `<tr><td>${a.n}</td><td>${esc(a.from_step || 'start')}</td><td><span class="chip ${a.result}">${esc(a.result)}</span></td>
      <td>${esc(a.step || '')}</td><td>${esc(a.kind ? `[${a.kind}] ` : '')}${esc(a.message || '')}</td><td>${esc(a.fixed_by || '')}</td></tr>`).join('')}</table>
    ${Object.entries(run.notes).map(([k, v]) => `<details><summary>${esc(k)} (agent notes)</summary><pre>${esc(v)}</pre></details>`).join('')}
    ${f && f.screenshot ? `<h2>Screen at failure</h2><div id="what" class="muted"></div><div id="ed" class="editor"></div>` : ''}
    ${waiting ? `<div class="panel human">
      <div id="fix-actions"></div>
      <div class="row">Then retry from <select id="from">${run.steps.map(s => `<option ${s === (last.step || '') ? 'selected' : ''}>${esc(s)}</option>`).join('')}</select>
      <button class="primary" id="retry">Retry</button><button class="danger" id="abort">Abort run</button></div></div>` : ''}`);
  if (!waiting && ['running', 'fixing', 'starting'].includes(run.status)) poll = setInterval(() => showRun(id), 2000);
  if (waiting) poll = setInterval(async () => { const r = await api('GET', `/api/runs/${id}`).catch(() => null); if (r && r.status !== 'needs_human') showRun(id); }, 3000);
  if (f && f.screenshot) await showFailure(run, f, last, waiting);
  if (waiting) {
    const decide = async action => {
      try { await api('POST', `/api/runs/${id}/decision`, { action, from_step: $('#from').value }); toast(action === 'retry' ? 'Retrying…' : 'Aborted', 'ok'); setTimeout(() => showRun(id), 1200); }
      catch (e) { toast(e.message, 'error'); }
    };
    $('#retry').onclick = () => decide('retry'); $('#abort').onclick = () => decide('abort');
  }
}

async function showFailure(run, f, last, waiting) {
  const shot = `${last.dir}/${f.screenshot}`;
  const ambiguous = f.kind === 'ambiguous' && f.target, missing = f.kind === 'not_found' && f.target;
  $('#what').innerHTML = `<b>[${esc(f.kind)}]</b> ${esc(f.message)}` + (f.target ? ` — target <a href="#" id="tlink">${esc(f.target)}</a>` : '');
  if ($('#tlink')) $('#tlink').onclick = ev => { ev.preventDefault(); showTarget(f.target); };
  const tools = !waiting ? ['pick'] : ambiguous ? ['pick', 'detail'] : missing ? ['main', 'click'] : ['pick'];
  const ed = new Editor($('#ed'), { tools });
  await ed.load(fileUrl(shot));
  const t = STATE.targets.find(x => x.name === f.target);
  const best = f.best && t && Object.assign([...f.best.at, ...t.size.map(v => v * (f.screen?.scale || 1) / t.scale)], { score: f.best.score });
  ed.set({ candidates: f.matches || [], best: f.matches?.length ? null : best });
  if (!waiting) return;
  const box = $('#fix-actions');
  if (ambiguous) {
    box.innerHTML = `<p><b>${f.matches.length} matches where one was expected.</b> Click the right green candidate, draw a detail box
      around something unique next to it (a row label, a heading), then validate. It is saved only if it makes that candidate the single match.</p>
      <button class="primary" id="fix">Add detail &amp; validate</button>`;
    $('#fix').onclick = () => addDetail(f.target, shot, ed, () => toast('Detail saved — press Retry to continue', 'ok'));
  } else if (missing) {
    box.innerHTML = `<p><b>${esc(f.target)} was not found.</b> If the element is visible but looks different, drag a new main box around it
      (and set the click point) to re-cut the target from this screenshot. This replaces the target and drops its details.
      If the screen is simply in the wrong state, fix it by hand on the machine and just Retry.</p>
      <button class="primary" id="fix">Re-cut target &amp; validate</button>`;
    $('#fix').onclick = async () => {
      if (!ed.st.main) return toast('Draw the main box first', 'error');
      try {
        const r = await api('POST', '/api/targets', { name: f.target, note: t?.note || '', confidence: t?.confidence, force: true, shot, box: ed.st.main, click: ed.clickPoint() });
        toast(`Re-cut ${f.target}: unique match (score ${r.match.score}) — press Retry`, 'ok'); refresh();
      } catch (e) { ed.set({ candidates: e.data?.matches || [] }); toast(e.message, 'error'); }
    };
  } else {
    box.innerHTML = `<p>This failure is not about a target (${esc(f.kind)}). Check the agent notes and the machine, fix what is needed, then Retry.</p>
      ${f.traceback ? `<details><summary>traceback</summary><pre>${esc(f.traceback)}</pre></details>` : ''}`;
  }
}

$('#new-target').onclick = () => showCapture();
refresh().then(() => {
  const human = STATE?.runs.find(r => r.status === 'needs_human');
  human ? showRun(human.id) : showCapture();
});
setInterval(() => VIEW === 'capture' || refresh(), 5000);
