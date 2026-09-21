/* TServe predict console — vanilla JS, no build step, no external deps.
   Endpoints used: GET /health, GET /models, GET /stats, POST /predict. */

(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const SERIES_VARS = ['--s1', '--s2', '--s3', '--s4', '--s5'];
  const POLL_MS = 5000;
  const MAX_HISTORY_POINTS = 240;

  const state = {
    models: [],
    stats: null,
    data: { columns: [], rows: [] },
    time: null,
    targets: [],
    fh: 12,
    useQuantiles: false,
    quantiles: [0.1, 0.5, 0.9],
    history: null,
    result: null,
    hoverIndex: null,
    chartGeom: null,
    log: [],
  };

  /* ── formatting helpers ─────────────────────────────────────────── */

  const isNum = (v) => typeof v === 'number' && Number.isFinite(v);

  function fmtNum(v, digits = 2) {
    if (!isNum(v)) return '—';
    const a = Math.abs(v);
    if (a >= 1e9) return (v / 1e9).toFixed(2) + 'B';
    if (a >= 1e6) return (v / 1e6).toFixed(2) + 'M';
    if (a >= 1e4) return v.toFixed(0);
    if (a >= 100) return v.toFixed(Math.min(digits, 1));
    if (a === 0) return '0';
    return v.toFixed(digits);
  }

  function fmtSeconds(s) {
    if (!isNum(s)) return '—';
    if (s < 1) return (s * 1000).toFixed(0) + 'ms';
    if (s < 60) return s.toFixed(1) + 's';
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = Math.floor(s % 60);
    if (h) return `${h}h ${String(m).padStart(2, '0')}m`;
    return `${m}m ${String(sec).padStart(2, '0')}s`;
  }

  function fmtLatency(s) {
    if (!isNum(s)) return '—';
    return s < 1 ? (s * 1000).toFixed(0) + 'ms' : s.toFixed(2) + 's';
  }

  function shortTime(v) {
    const s = String(v);
    const m = s.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})/);
    if (m) return m[2] === '00' && m[3] === '00' ? m[1] : `${m[1].slice(5)} ${m[2]}:${m[3]}`;
    return s.length > 16 ? s.slice(0, 16) : s;
  }

  const clock = () => new Date().toLocaleTimeString([], { hour12: false });

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  }

  /* ── http ───────────────────────────────────────────────────────── */

  async function api(path, options) {
    const started = performance.now();
    const res = await fetch(path, options);
    const ms = performance.now() - started;
    let body = null;
    const text = await res.text();
    if (text) {
      try { body = JSON.parse(text); } catch { body = text; }
    }
    if (!res.ok) {
      const err = new Error(errorMessage(res.status, body));
      err.status = res.status;
      err.body = body;
      throw err;
    }
    return { body, ms };
  }

  function errorMessage(status, body) {
    const detail = body && body.detail !== undefined ? body.detail : body;
    if (detail && typeof detail === 'object' && !Array.isArray(detail) && detail.error) {
      return detail.error;
    }
    if (Array.isArray(detail)) {
      return detail
        .map((d) => `${(d.loc || []).slice(1).join('.') || 'body'}: ${d.msg || ''}`)
        .join(' · ');
    }
    if (typeof detail === 'string' && detail) return detail;
    return `HTTP ${status}`;
  }

  /* ── activity log ───────────────────────────────────────────────── */

  function log(msg, { ms = null, error = false } = {}) {
    state.log.unshift({ t: clock(), msg, ms, error });
    state.log = state.log.slice(0, 40);
    renderLog();
  }

  function renderLog() {
    const el = $('#log');
    if (!state.log.length) {
      el.innerHTML = '<li class="log__empty">nothing yet</li>';
      return;
    }
    el.innerHTML = state.log
      .map((e) => `<li class="${e.error ? 'is-err' : ''}">
          <span class="log__time">${e.t}</span>
          <span class="log__msg">${esc(e.msg)}</span>
          ${e.ms != null ? `<span class="log__ms">${e.ms.toFixed(0)}ms</span>` : ''}
        </li>`)
      .join('');
  }

  /* ── GET /health ────────────────────────────────────────────────── */

  async function refreshHealth(quiet = true) {
    const pill = $('#health-pill');
    const card = $('#health-card');
    try {
      const { body, ms } = await api('/health');
      const ok = body && body.status === 'ok';
      pill.className = `pill ${ok ? 'is-ok' : 'is-err'}`;
      $('#health-pill-text').textContent = ok ? 'healthy' : String(body?.status ?? 'unknown');
      card.className = `panel card card--health ${ok ? 'is-ok' : 'is-err'}`;
      $('#health-beacon').className = 'statusline__beacon';
      $('#health-status').textContent = String(body?.status ?? 'unknown');
      const err = body && body.error;
      const note = err ? `${err.code}: ${err.message}` : `probe ${ms.toFixed(0)}ms · ${clock()}`;
      setNote(note, String(body?.status ?? 'unknown'));
      if (!quiet) log('GET /health', { ms });
    } catch (e) {
      pill.className = 'pill is-err';
      $('#health-pill-text').textContent = 'unreachable';
      card.className = 'panel card card--health is-err';
      $('#health-status').textContent = 'unreachable';
      setNote(`${e.message} · ${clock()}`, 'unreachable');
      if (!quiet) log(`GET /health failed — ${e.message}`, { error: true });
    }
  }

  function setNote(note, status) {
    const el = $('#health-note');
    el.textContent = note;
    el.title = note;
    $('#health-status').title = status;
    $('#health-pill-text').title = status;
  }

  /* ── GET /models ────────────────────────────────────────────────── */

  async function refreshModels(quiet = true) {
    const select = $('#model-select');
    try {
      const { body, ms } = await api('/models');
      state.models = (body && body.models) || [];
      const previous = select.value;

      if (!state.models.length) {
        select.innerHTML = '<option value="">no models loaded</option>';
        select.disabled = true;
        $('#model-hint').textContent = 'naive is a test baseline; pass extra ids after tserve for a real forecast';
      } else {
        select.disabled = false;
        select.innerHTML = state.models
          .map((m) => `<option value="${esc(m.id)}">${esc(m.id)}</option>`)
          .join('');
        if (previous && state.models.some((m) => m.id === previous)) select.value = previous;
        updateModelHint();
      }
      renderModelList();
      updateRunState();
      if (!quiet) log(`GET /models — ${state.models.length} loaded`, { ms });
    } catch (e) {
      select.innerHTML = '<option value="">unavailable</option>';
      select.disabled = true;
      $('#model-hint').textContent = e.message;
      if (!quiet) log(`GET /models failed — ${e.message}`, { error: true });
    }
  }

  function selectedModel() {
    return state.models.find((m) => m.id === $('#model-select').value) || null;
  }

  function updateModelHint() {
    const m = selectedModel();
    $('#model-hint').textContent = m ? `executor ${m.executor} · source ${m.source}` : '';
    renderModelList();
  }

  function renderModelList() {
    const el = $('#model-list');
    if (!state.models.length) {
      el.innerHTML = '<li class="modellist__empty">no models loaded</li>';
      return;
    }
    const current = $('#model-select').value;
    const perModel = (state.stats && state.stats.models) || {};
    el.innerHTML = state.models
      .map((m) => {
        const s = perModel[m.id];
        const req = s ? s.requests.total : 0;
        const mean = s && s.latency_s ? fmtLatency(s.latency_s.mean) : '—';
        return `<li class="${m.id === current ? 'is-selected' : ''}">
            <div class="modellist__top">
              <span class="modellist__id">${esc(m.id)}</span>
              <span class="chip chip--muted">${req} req</span>
            </div>
            <div class="modellist__meta">
              <span class="tag">${esc(m.executor)}</span>
              <span class="tag">${esc(m.source)}</span>
              <span class="tag">mean ${mean}</span>
            </div>
          </li>`;
      })
      .join('');
  }

  /* ── GET /stats ─────────────────────────────────────────────────── */

  async function refreshStats(quiet = true) {
    try {
      const { body, ms } = await api('/stats');
      state.stats = body;
      renderStats(body);
      renderModelList();
      if (!quiet) log('GET /stats', { ms });
    } catch (e) {
      if (!quiet) log(`GET /stats failed — ${e.message}`, { error: true });
    }
  }

  function renderStats(stats) {
    $('#stat-uptime').textContent = fmtSeconds(stats.uptime_s);
    const mem = stats.memory || {};
    $('#stat-rss').innerHTML = `${isNum(mem.cpu_rss_mb) ? fmtNum(mem.cpu_rss_mb, 0) : '—'}<small>MB</small>`;
    $('#stat-gpu').innerHTML = `${isNum(mem.gpu_mb) ? fmtNum(mem.gpu_mb, 0) : '—'}<small>MB</small>`;

    const models = stats.models || {};
    const ids = Object.keys(models);
    $('#stat-models').textContent = String(ids.length);

    let ok = 0;
    let failed = 0;
    let count = 0;
    let total = 0;
    let fastest = null;
    let slowest = null;
    for (const id of ids) {
      const m = models[id];
      ok += m.requests.ok;
      failed += m.requests.failed;
      const lat = m.latency_s || {};
      count += lat.count || 0;
      total += lat.total || 0;
      if (isNum(lat.fastest)) fastest = fastest === null ? lat.fastest : Math.min(fastest, lat.fastest);
      if (isNum(lat.slowest)) slowest = slowest === null ? lat.slowest : Math.max(slowest, lat.slowest);
    }
    const all = ok + failed;
    $('#req-total').textContent = `${all} total`;
    $('#req-ok').textContent = String(ok);
    $('#req-failed').textContent = String(failed);
    $('#req-ok-bar').style.width = all ? `${(ok / all) * 100}%` : '0%';
    $('#req-err-bar').style.width = all ? `${(failed / all) * 100}%` : '0%';
    $('#lat-mean').textContent = count ? fmtLatency(total / count) : '—';
    $('#lat-fast').textContent = fmtLatency(fastest);
    $('#lat-slow').textContent = fmtLatency(slowest);
  }

  /* ── sample data ────────────────────────────────────────────────── */

  function mulberry32(seed) {
    let a = seed >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function isoStamp(date, hourly) {
    const p = (n) => String(n).padStart(2, '0');
    const day = `${date.getUTCFullYear()}-${p(date.getUTCMonth() + 1)}-${p(date.getUTCDate())}`;
    return hourly ? `${day}T${p(date.getUTCHours())}:00:00` : day;
  }

  function buildSample(kind, seed = Date.now()) {
    const rnd = mulberry32(seed);
    const noise = (amp) => (rnd() - 0.5) * 2 * amp;
    const start = new Date(Date.UTC(2024, 0, 1));
    const rows = [];
    let columns;

    if (kind === 'energy') {
      columns = ['timestamp', 'demand_mw'];
      for (let i = 0; i < 192; i++) {
        const d = new Date(start.getTime() + i * 3600e3);
        const daily = 220 * Math.sin(((i % 24) / 24) * 2 * Math.PI - 1.5);
        const v = 1450 + daily + 60 * Math.sin(i / 37) + noise(45);
        rows.push([isoStamp(d, true), Math.round(v * 10) / 10]);
      }
    } else if (kind === 'traffic') {
      columns = ['timestamp', 'requests', 'errors'];
      for (let i = 0; i < 216; i++) {
        const d = new Date(start.getTime() + i * 3600e3);
        const hour = i % 24;
        const daily = 1 + 0.75 * Math.sin(((hour - 3) / 24) * 2 * Math.PI);
        const weekly = 1 - 0.25 * (Math.floor(i / 24) % 7 >= 5 ? 1 : 0);
        const reqs = Math.max(20, 900 * daily * weekly + i * 1.4 + noise(70));
        rows.push([
          isoStamp(d, true),
          Math.round(reqs),
          Math.max(0, Math.round(reqs * 0.012 + noise(3))),
        ]);
      }
    } else if (kind === 'airline') {
      columns = ['timestamp', 'passengers'];
      for (let i = 0; i < 144; i++) {
        const d = new Date(Date.UTC(2013, i, 1));
        const trend = 112 + i * 2.4;
        const season = 1 + 0.22 * Math.sin(((i % 12) / 12) * 2 * Math.PI - 0.9);
        rows.push([isoStamp(d, false), Math.round(trend * season + noise(9))]);
      }
    } else {
      columns = ['timestamp', 'sales'];
      for (let i = 0; i < 180; i++) {
        const d = new Date(start.getTime() + i * 86400e3);
        const weekly = 26 * Math.sin(((i % 7) / 7) * 2 * Math.PI);
        const v = 320 + i * 0.85 + weekly + 40 * Math.sin(i / 29) + noise(18);
        rows.push([isoStamp(d, false), Math.round(v * 10) / 10]);
      }
    }
    return { columns, rows };
  }

  /* ── CSV parsing ────────────────────────────────────────────────── */

  function splitLine(line, delim) {
    const out = [];
    let cur = '';
    let quoted = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (quoted) {
        if (ch === '"') {
          if (line[i + 1] === '"') { cur += '"'; i++; } else quoted = false;
        } else cur += ch;
      } else if (ch === '"') {
        quoted = true;
      } else if (ch === delim) {
        out.push(cur.trim());
        cur = '';
      } else cur += ch;
    }
    out.push(cur.trim());
    return out;
  }

  function parseCSV(text) {
    const lines = text.split(/\r?\n/).filter((l) => l.trim() !== '');
    if (!lines.length) throw new Error('no rows found');
    const head = lines[0];
    const delim = [',', ';', '\t', '|']
      .map((d) => [d, head.split(d).length])
      .sort((a, b) => b[1] - a[1])[0][0];

    const matrix = lines.map((l) => splitLine(l, delim));
    const first = matrix[0];
    const looksHeader = first.some((c) => c !== '' && !Number.isFinite(Number(c)));
    const columns = looksHeader ? first.map((c, i) => c || `col_${i}`) : first.map((_, i) => `col_${i}`);
    const body = looksHeader ? matrix.slice(1) : matrix;

    const rows = body
      .filter((r) => r.length && r.some((c) => c !== ''))
      .map((r) =>
        columns.map((_, i) => {
          const raw = r[i] ?? '';
          if (raw === '') return null;
          const n = Number(raw);
          return raw !== '' && Number.isFinite(n) ? n : raw;
        }));

    if (!rows.length) throw new Error('no data rows found');
    return { columns, rows };
  }

  /* ── data / column mapping ──────────────────────────────────────── */

  function numericColumns(data) {
    return data.columns.filter((c, i) =>
      data.rows.some((r) => isNum(r[i])) && data.rows.every((r) => r[i] === null || isNum(r[i])));
  }

  function setData(data, label) {
    state.data = data;
    const numeric = numericColumns(data);
    state.time = data.columns.find((c) => !numeric.includes(c)) || data.columns[0];
    state.targets = numeric.filter((c) => c !== state.time).slice(0, 5);
    if (!state.targets.length) {
      state.targets = data.columns.filter((c) => c !== state.time).slice(0, 1);
    }
    renderColumnControls();
    $('#data-shape').textContent = `${data.rows.length} × ${data.columns.length}`;
    updateRunState();
    if (label) log(label);
  }

  function renderColumnControls() {
    const timeSelect = $('#time-select');
    timeSelect.innerHTML = state.data.columns
      .map((c) => `<option value="${esc(c)}"${c === state.time ? ' selected' : ''}>${esc(c)}</option>`)
      .join('');

    const chips = $('#target-chips');
    const candidates = state.data.columns.filter((c) => c !== state.time);
    if (!candidates.length) {
      chips.innerHTML = '<span class="chips__empty">no target columns available</span>';
      return;
    }
    chips.innerHTML = candidates
      .map((c, i) => {
        const active = state.targets.includes(c);
        const color = `var(${SERIES_VARS[state.targets.indexOf(c) % SERIES_VARS.length]})`;
        return `<button type="button" class="chips__item ${active ? 'is-active' : ''}"
            data-col="${esc(c)}" style="--series:${active ? color : `var(${SERIES_VARS[i % SERIES_VARS.length]})`}">
            <span class="dotmark"></span>${esc(c)}
          </button>`;
      })
      .join('');
  }

  function updateRunState() {
    const ready = state.models.length > 0 && state.targets.length > 0 && state.data.rows.length > 1;
    $('#run-btn').disabled = !ready;
  }

  /* ── POST /predict ──────────────────────────────────────────────── */

  function buildRequestBody() {
    const cols = [state.time, ...state.targets];
    const idx = cols.map((c) => state.data.columns.indexOf(c));
    const body = {
      past: {
        columns: cols,
        data: state.data.rows.map((r) => idx.map((i) => r[i])),
      },
      time: state.time,
      target: state.targets,
      fh: state.fh,
      model: $('#model-select').value,
    };
    if (state.useQuantiles) body.quantiles = state.quantiles;
    return body;
  }

  async function runPredict() {
    const btn = $('#run-btn');
    const model = $('#model-select').value;
    if (!model) return;

    btn.classList.add('is-busy');
    $('.btn__label', btn).textContent = 'Predicting…';
    hideError();

    try {
      const { body, ms } = await api('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildRequestBody()),
      });
      state.result = body;
      state.history = { columns: state.data.columns, rows: state.data.rows, time: state.time, targets: [...state.targets] };
      state.hoverIndex = null;
      $('#request-id').textContent = `request_id ${String(body.request_id).slice(0, 8)}…`;
      $('#chart-sub').textContent =
        `${model} · horizon ${state.fh} · ${state.targets.length} target${state.targets.length > 1 ? 's' : ''} · ${ms.toFixed(0)}ms round trip`;
      $('#download-btn').disabled = false;
      renderChart();
      renderTable();
      log(`POST /predict ${model} fh=${state.fh}`, { ms });
      refreshStats();
    } catch (e) {
      showError(e);
      log(`POST /predict failed — ${e.message}`, { error: true });
      refreshStats();
    } finally {
      btn.classList.remove('is-busy');
      $('.btn__label', btn).textContent = 'Run prediction';
    }
  }

  function showError(e) {
    const box = $('#error-box');
    $('#error-title').textContent = e.status ? `Request failed · HTTP ${e.status}` : 'Request failed';
    $('#error-body').textContent = e.message;
    box.hidden = false;
  }

  function hideError() { $('#error-box').hidden = true; }

  /* ── result shaping ─────────────────────────────────────────────── */

  function resultSeries() {
    const res = state.result;
    const hist = state.history;
    if (!res || !res.predictions || !hist) return null;

    const preds = res.predictions;
    const timeKey = hist.time in preds ? hist.time : Object.keys(preds)[0];
    const futureTimes = (preds[timeKey] || []).map(String);
    const quant = res.quantiles || null;

    const timeIdx = hist.columns.indexOf(hist.time);
    const allRows = hist.rows;
    const rows = allRows.slice(Math.max(0, allRows.length - MAX_HISTORY_POINTS));
    const pastTimes = rows.map((r) => String(r[timeIdx]));

    const series = hist.targets
      .filter((t) => t in preds)
      .map((t, i) => {
        const colIdx = hist.columns.indexOf(t);
        const past = rows.map((r) => (isNum(r[colIdx]) ? r[colIdx] : null));
        const future = (preds[t] || []).map((v) => (isNum(v) ? v : Number(v)));
        let band = null;
        if (quant) {
          const alphas = Object.keys(quant)
            .filter((k) => k.startsWith(`${t}_`))
            .map((k) => ({ key: k, a: Number(k.slice(t.length + 1)) }))
            .filter((o) => Number.isFinite(o.a))
            .sort((x, y) => x.a - y.a);
          if (alphas.length >= 2) {
            band = {
              lower: quant[alphas[0].key].map(Number),
              upper: quant[alphas[alphas.length - 1].key].map(Number),
              label: `${Math.round((alphas[alphas.length - 1].a - alphas[0].a) * 100)}%`,
            };
          }
        }
        return { name: t, color: cssVar(SERIES_VARS[i % SERIES_VARS.length]), past, future, band };
      });

    return { pastTimes, futureTimes, times: [...pastTimes, ...futureTimes], series };
  }

  /* ── chart ──────────────────────────────────────────────────────── */

  function niceTicks(min, max, count) {
    if (!Number.isFinite(min) || !Number.isFinite(max)) return [0, 1];
    if (min === max) { min -= 1; max += 1; }
    const span = max - min;
    const step0 = span / count;
    const mag = Math.pow(10, Math.floor(Math.log10(step0)));
    const norm = step0 / mag;
    const step = (norm >= 5 ? 10 : norm >= 2 ? 5 : norm >= 1 ? 2 : 1) * mag;
    const first = Math.ceil(min / step) * step;
    const ticks = [];
    for (let v = first; v <= max + step * 0.001; v += step) ticks.push(Number(v.toFixed(10)));
    return ticks.length ? ticks : [min, max];
  }

  function renderChart() {
    const wrap = $('#chart');
    const svg = $('#chart-svg');
    const shaped = resultSeries();

    // a re-render (resize, theme swap, new result) invalidates the hover state
    state.hoverIndex = null;
    $('#chart-tooltip').hidden = true;

    if (!shaped || !shaped.series.length) {
      wrap.classList.remove('has-data');
      svg.innerHTML = '';
      $('#legend').innerHTML = '';
      state.chartGeom = null;
      return;
    }
    wrap.classList.add('has-data');

    const W = Math.max(320, wrap.clientWidth - 12);
    const H = Math.max(220, wrap.clientHeight - 6);
    const m = { top: 18, right: 14, bottom: 26, left: 54 };
    const iw = W - m.left - m.right;
    const ih = H - m.top - m.bottom;

    const nPast = shaped.pastTimes.length;
    const nAll = shaped.times.length;
    const step = nAll > 1 ? iw / (nAll - 1) : iw;
    const X = (i) => m.left + i * step;

    let lo = Infinity;
    let hi = -Infinity;
    for (const s of shaped.series) {
      for (const v of s.past) if (isNum(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
      for (const v of s.future) if (isNum(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
      if (s.band) {
        for (const v of s.band.lower) if (isNum(v)) lo = Math.min(lo, v);
        for (const v of s.band.upper) if (isNum(v)) hi = Math.max(hi, v);
      }
    }
    if (!Number.isFinite(lo)) { lo = 0; hi = 1; }
    const pad = (hi - lo || Math.abs(hi) || 1) * 0.12;
    lo -= pad; hi += pad;
    const Y = (v) => m.top + ih - ((v - lo) / (hi - lo)) * ih;

    const yTicks = niceTicks(lo + pad * 0.5, hi - pad * 0.5, 5);
    const xTickCount = Math.max(2, Math.min(7, Math.floor(iw / 110)));
    const xTicks = [];
    for (let k = 0; k < xTickCount; k++) {
      xTicks.push(Math.round((k * (nAll - 1)) / (xTickCount - 1)));
    }

    const p = [];
    p.push(`<defs>
      ${shaped.series.map((s, i) => `<linearGradient id="band-${i}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="${s.color}" stop-opacity="0.30"/>
          <stop offset="100%" stop-color="${s.color}" stop-opacity="0.06"/>
        </linearGradient>`).join('')}
      <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="3.2" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>`);

    // grid + y axis
    for (const t of yTicks) {
      const y = Y(t).toFixed(1);
      p.push(`<line class="grid-line" x1="${m.left}" y1="${y}" x2="${m.left + iw}" y2="${y}"/>`);
      p.push(`<text class="axis-text" x="${m.left - 9}" y="${y}" text-anchor="end" dominant-baseline="middle">${fmtNum(t, 1)}</text>`);
    }
    p.push(`<line class="axis-line" x1="${m.left}" y1="${m.top + ih}" x2="${m.left + iw}" y2="${m.top + ih}"/>`);

    // x axis labels
    for (const i of xTicks) {
      const x = X(i);
      const anchor = i === 0 ? 'start' : i === nAll - 1 ? 'end' : 'middle';
      p.push(`<text class="axis-text" x="${x.toFixed(1)}" y="${m.top + ih + 15}" text-anchor="${anchor}">${esc(shortTime(shaped.times[i]))}</text>`);
    }

    // prediction split marker
    if (nPast > 0 && nPast < nAll) {
      const sx = X(nPast - 1).toFixed(1);
      p.push(`<line class="split-line" x1="${sx}" y1="${m.top}" x2="${sx}" y2="${m.top + ih}"/>`);
      p.push(`<text class="split-text" x="${Number(sx) + 6}" y="${m.top + 9}">PREDICTION</text>`);
    }

    const path = (pts) => pts.map((pt, i) => `${i ? 'L' : 'M'}${pt[0].toFixed(1)} ${pt[1].toFixed(1)}`).join(' ');

    shaped.series.forEach((s, si) => {
      // interval band
      if (s.band) {
        const up = [];
        const dn = [];
        const anchorY = isNum(s.past[nPast - 1]) ? s.past[nPast - 1] : s.future[0];
        up.push([X(nPast - 1), Y(anchorY)]);
        dn.push([X(nPast - 1), Y(anchorY)]);
        s.band.upper.forEach((v, i) => { if (isNum(v)) up.push([X(nPast + i), Y(v)]); });
        s.band.lower.forEach((v, i) => { if (isNum(v)) dn.push([X(nPast + i), Y(v)]); });
        dn.reverse();
        p.push(`<path d="${path(up)} ${path(dn).replace(/^M/, 'L')} Z" fill="url(#band-${si})" stroke="none"/>`);
      }

      // history
      const hp = [];
      s.past.forEach((v, i) => { if (isNum(v)) hp.push([X(i), Y(v)]); });
      if (hp.length) {
        p.push(`<path d="${path(hp)}" fill="none" stroke="${s.color}" stroke-width="1.9" stroke-opacity="0.55" stroke-linejoin="round" stroke-linecap="round"/>`);
      }

      // prediction (anchored to the last observation)
      const fp = [];
      if (isNum(s.past[nPast - 1])) fp.push([X(nPast - 1), Y(s.past[nPast - 1])]);
      s.future.forEach((v, i) => { if (isNum(v)) fp.push([X(nPast + i), Y(v)]); });
      if (fp.length > 1) {
        p.push(`<path d="${path(fp)}" fill="none" stroke="${s.color}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)"/>`);
      }
      if (fp.length <= 20) {
        fp.slice(1).forEach((pt) => {
          p.push(`<circle cx="${pt[0].toFixed(1)}" cy="${pt[1].toFixed(1)}" r="2.6" fill="${s.color}"/>`);
        });
      }
    });

    p.push(`<g id="hover-layer"></g>`);
    p.push(`<rect id="hover-target" x="${m.left}" y="${m.top}" width="${iw}" height="${ih}" fill="transparent"/>`);

    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.setAttribute('width', W);
    svg.setAttribute('height', H);
    svg.innerHTML = p.join('');

    state.chartGeom = { X, Y, m, iw, ih, nPast, nAll, step, shaped };
    attachHover();
    renderLegend(shaped);
  }

  function renderLegend(shaped) {
    const parts = shaped.series.map(
      (s) => `<span class="legend__item"><span class="legend__swatch" style="background:${s.color}"></span>${esc(s.name)}</span>`);
    if (shaped.series.some((s) => s.band)) {
      const label = shaped.series.find((s) => s.band).band.label;
      parts.push(`<span class="legend__item"><span class="legend__swatch legend__swatch--band" style="background:${shaped.series[0].color}"></span>${label} interval</span>`);
    }
    $('#legend').innerHTML = parts.join('');
  }

  function attachHover() {
    const svg = $('#chart-svg');
    const target = $('#hover-target', svg);
    if (!target) return;
    target.addEventListener('mousemove', onHover);
    target.addEventListener('mouseleave', clearHover);
    target.addEventListener('touchmove', (e) => {
      if (e.touches.length) onHover(e.touches[0]);
    }, { passive: true });
    target.addEventListener('touchend', clearHover);
  }

  function onHover(evt) {
    const geom = state.chartGeom;
    if (!geom) return;
    const svg = $('#chart-svg');
    const rect = svg.getBoundingClientRect();
    const scale = rect.width / (svg.viewBox.baseVal.width || rect.width);
    const x = (evt.clientX - rect.left) / (scale || 1);
    let idx = Math.round((x - geom.m.left) / geom.step);
    idx = Math.max(0, Math.min(geom.nAll - 1, idx));
    state.hoverIndex = idx;
    drawHover(idx);
  }

  function clearHover() {
    state.hoverIndex = null;
    const layer = $('#hover-layer');
    if (layer) layer.innerHTML = '';
    $('#chart-tooltip').hidden = true;
  }

  function drawHover(idx) {
    const geom = state.chartGeom;
    const layer = $('#hover-layer');
    if (!geom || !layer) return;
    const { X, Y, m, ih, nPast, shaped } = geom;
    const x = X(idx);
    const parts = [`<line class="hover-line" x1="${x.toFixed(1)}" y1="${m.top}" x2="${x.toFixed(1)}" y2="${m.top + ih}"/>`];
    const rows = [];

    for (const s of shaped.series) {
      const isFuture = idx >= nPast;
      const v = isFuture ? s.future[idx - nPast] : s.past[idx];
      if (!isNum(v)) continue;
      parts.push(`<circle cx="${x.toFixed(1)}" cy="${Y(v).toFixed(1)}" r="4" fill="${s.color}" stroke="var(--bg)" stroke-width="1.6"/>`);
      let extra = '';
      if (isFuture && s.band) {
        const lo = s.band.lower[idx - nPast];
        const hi = s.band.upper[idx - nPast];
        if (isNum(lo) && isNum(hi)) extra = `<span class="tt__range">${fmtNum(lo)} – ${fmtNum(hi)}</span>`;
      }
      rows.push(`<div class="tt__row">
          <span class="tt__name"><span class="dotmark" style="background:${s.color}"></span>${esc(s.name)}${isFuture ? ' ⟶' : ''}</span>
          <b>${fmtNum(v)}</b>
        </div>${extra ? `<div class="tt__row"><span class="tt__name">interval</span><b>${extra}</b></div>` : ''}`);
    }
    layer.innerHTML = parts.join('');

    const tip = $('#chart-tooltip');
    const chartRect = $('#chart').getBoundingClientRect();
    const svgRect = $('#chart-svg').getBoundingClientRect();
    const scale = svgRect.width / (($('#chart-svg').viewBox.baseVal.width) || svgRect.width);
    tip.innerHTML = `<div class="tt__time">${esc(shaped.times[idx] ?? '')}</div>${rows.join('')}`;
    tip.hidden = false;
    const left = svgRect.left - chartRect.left + x * scale;
    tip.style.left = `${Math.max(70, Math.min(chartRect.width - 70, left))}px`;
    tip.style.top = `${Math.max(60, geom.m.top * scale + 60)}px`;
  }

  /* ── predictions table ──────────────────────────────────────────── */

  function renderTable() {
    const res = state.result;
    const table = $('#pred-table');
    if (!res || !res.predictions) return;

    const preds = res.predictions;
    const quant = res.quantiles || {};
    const timeKey = state.history && state.history.time in preds ? state.history.time : Object.keys(preds)[0];
    const predCols = Object.keys(preds).filter((c) => c !== timeKey);
    const quantCols = Object.keys(quant).filter((c) => c !== timeKey);
    const n = (preds[timeKey] || []).length;

    const header = [timeKey, ...predCols, ...quantCols];
    const bodyRows = [];
    for (let i = 0; i < n; i++) {
      const cells = [`<td>${esc(preds[timeKey][i])}</td>`];
      for (const c of predCols) cells.push(`<td>${fmtNum(Number(preds[c][i]))}</td>`);
      for (const c of quantCols) cells.push(`<td>${fmtNum(Number(quant[c][i]))}</td>`);
      bodyRows.push(`<tr>${cells.join('')}</tr>`);
    }

    table.innerHTML =
      `<thead><tr>${header.map((h) => `<th>${esc(h)}</th>`).join('')}</tr></thead>` +
      `<tbody>${bodyRows.join('') || '<tr><td class="table__empty">no rows</td></tr>'}</tbody>`;
  }

  function downloadCSV() {
    const res = state.result;
    if (!res || !res.predictions) return;
    const preds = res.predictions;
    const quant = res.quantiles || {};
    const cols = [...Object.keys(preds), ...Object.keys(quant).filter((c) => !(c in preds))];
    const n = Object.values(preds)[0].length;
    const lines = [cols.join(',')];
    for (let i = 0; i < n; i++) {
      lines.push(cols.map((c) => (preds[c] ? preds[c][i] : quant[c][i])).join(','));
    }
    const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tserve-predict-${res.model}-${String(res.request_id).slice(0, 8)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    log('downloaded predictions.csv');
  }

  /* ── wiring ─────────────────────────────────────────────────────── */

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem('tserve-theme', theme); } catch { /* ignore */ }
    renderChart();
  }

  function updateRangeFill(input) {
    const pct = ((input.value - input.min) / (input.max - input.min)) * 100;
    input.style.setProperty('--fill', `${pct}%`);
  }

  function bindEvents() {
    $('#model-select').addEventListener('change', updateModelHint);

    const fh = $('#fh-range');
    fh.addEventListener('input', () => {
      state.fh = Number(fh.value);
      $('#fh-value').textContent = fh.value;
      updateRangeFill(fh);
    });

    $('#quantiles-toggle').addEventListener('change', (e) => {
      state.useQuantiles = e.target.checked;
      $('#coverage-group').classList.toggle('is-disabled', !e.target.checked);
    });

    $$('#coverage-group .segmented__item').forEach((btn) => {
      btn.addEventListener('click', () => {
        $$('#coverage-group .segmented__item').forEach((b) => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        state.quantiles = btn.dataset.q.split(',').map(Number);
      });
    });

    $$('.tabs__btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        $$('.tabs__btn').forEach((b) => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        $$('.tabpanel').forEach((p) => p.classList.toggle('is-active', p.dataset.panel === btn.dataset.tab));
      });
    });

    $('#sample-select').addEventListener('change', loadSample);
    $('#regen-btn').addEventListener('click', loadSample);

    $('#parse-btn').addEventListener('click', () => {
      try {
        setData(parseCSV($('#csv-input').value), 'parsed pasted CSV');
        hideError();
      } catch (e) { showError(e); }
    });

    const fileInput = $('#csv-file');
    fileInput.addEventListener('change', () => {
      const file = fileInput.files[0];
      if (file) readFile(file);
    });

    const dropzone = $('.dropzone');
    ['dragenter', 'dragover'].forEach((ev) =>
      dropzone.addEventListener(ev, (e) => { e.preventDefault(); dropzone.classList.add('is-over'); }));
    ['dragleave', 'drop'].forEach((ev) =>
      dropzone.addEventListener(ev, (e) => { e.preventDefault(); dropzone.classList.remove('is-over'); }));
    dropzone.addEventListener('drop', (e) => {
      const file = e.dataTransfer.files[0];
      if (file) readFile(file);
    });

    $('#time-select').addEventListener('change', (e) => {
      state.time = e.target.value;
      state.targets = state.targets.filter((t) => t !== state.time);
      if (!state.targets.length) {
        const numeric = numericColumns(state.data).filter((c) => c !== state.time);
        state.targets = numeric.slice(0, 1);
      }
      renderColumnControls();
      updateRunState();
    });

    $('#target-chips').addEventListener('click', (e) => {
      const btn = e.target.closest('.chips__item');
      if (!btn) return;
      const col = btn.dataset.col;
      if (state.targets.includes(col)) {
        if (state.targets.length > 1) state.targets = state.targets.filter((t) => t !== col);
      } else if (state.targets.length < SERIES_VARS.length) {
        state.targets = state.data.columns.filter((c) => state.targets.includes(c) || c === col);
      }
      renderColumnControls();
      updateRunState();
    });

    $('#run-btn').addEventListener('click', runPredict);
    $('#download-btn').addEventListener('click', downloadCSV);
    $('#clear-log').addEventListener('click', () => { state.log = []; renderLog(); });

    $('#refresh-btn').addEventListener('click', async () => {
      const btn = $('#refresh-btn');
      btn.classList.add('is-busy');
      await Promise.all([refreshHealth(false), refreshModels(false), refreshStats(false)]);
      btn.classList.remove('is-busy');
    });

    $('#theme-btn').addEventListener('click', () => {
      const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      setTheme(next);
    });

    let poller = null;
    const setPolling = (on) => {
      if (poller) { clearInterval(poller); poller = null; }
      if (on) poller = setInterval(() => { refreshHealth(); refreshStats(); }, POLL_MS);
    };
    $('#auto-refresh').addEventListener('change', (e) => setPolling(e.target.checked));
    setPolling($('#auto-refresh').checked);

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && $('#auto-refresh').checked) { refreshHealth(); refreshStats(); }
    });

    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') { e.preventDefault(); runPredict(); }
    });

    let raf = null;
    new ResizeObserver(() => {
      if (raf) cancelAnimationFrame(raf);
      raf = requestAnimationFrame(renderChart);
    }).observe($('#chart'));

    setInterval(() => { $('#footer-clock').textContent = clock(); }, 1000);
    $('#footer-clock').textContent = clock();
  }

  function readFile(file) {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        setData(parseCSV(String(reader.result)), `loaded ${file.name}`);
        $('#file-hint').textContent = `${file.name} · ${(file.size / 1024).toFixed(1)} kB`;
        hideError();
      } catch (e) { showError(e); }
    };
    reader.readAsText(file);
  }

  function loadSample() {
    const kind = $('#sample-select').value;
    setData(buildSample(kind), `sample series · ${kind}`);
  }

  async function init() {
    let stored = null;
    try { stored = localStorage.getItem('tserve-theme'); } catch { /* ignore */ }
    document.documentElement.setAttribute('data-theme', stored || 'dark');

    bindEvents();
    updateRangeFill($('#fh-range'));
    renderLog();
    loadSample();

    await Promise.all([refreshHealth(), refreshModels(), refreshStats()]);
    log('console ready');
  }

  document.addEventListener('DOMContentLoaded', init);
})();
