// DaVoice Car Agent: the screens of the React Native example (src/redesign/*), driven by car_agent.py.
// The Python process owns the microphone, the speakers and every model; this page shows its state
// (server-sent events from /events) and sends the taps to /api/<action>.
'use strict';

const $screen = document.getElementById('screen');
const $overlay = document.getElementById('overlay');
let S = {};                 // the app state from car_agent.py
const local = { picked: null, cloneName: '', carText: '', settingsOpen: false, lastMatchAt: 0 };

// ---- helpers ------------------------------------------------------------------------------------------
function esc(v) {
  return String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
const act = (name, arg) => `data-act="${name}"${arg !== undefined ? ` data-arg="${esc(JSON.stringify(arg))}"` : ''}`;
const cap = (t) => (t ? t.charAt(0).toUpperCase() + t.slice(1) : '');
const d = (v) => `calc(var(--u) * ${v})`;
function post(action, body = {}) {
  return fetch(`/api/${action}`, { method: 'POST', body: JSON.stringify(body) }).catch(() => {});
}

const ICON = {
  chevron: (dir = 'left', color = '#F9FAFB', size = 20) =>
    `<svg width="${size}" height="${size}" viewBox="0 0 24 24"><path d="${dir === 'left' ? 'm15 6-6 6 6 6' : 'm9 6 6 6-6 6'}" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`,
  check: (size = 16, color = '#34D399', w = 2.4) =>
    `<svg width="${size}" height="${size}" viewBox="0 0 24 24"><path d="m5 12 4.5 4.5L19 7" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`,
  download: (size = 16, color = '#6EE7B7', w = 2) =>
    `<svg width="${size}" height="${size}" viewBox="0 0 24 24"><path d="M12 4v11M7 10l5 5 5-5M5 20h14" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`,
  play: (size = 11, color = '#34D399') => `<svg width="${size}" height="${size}" viewBox="0 0 24 24"><path d="M7 4v16l13-8z" fill="${color}"/></svg>`,
  plus: () => '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" stroke="#04140D" stroke-width="2.6" stroke-linecap="round" fill="none"/></svg>',
  arrow: (color = '#04140D', size = 18) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6" stroke="${color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`,
  shield: (checked, color = '#04140D') => `<svg width="24" height="24" viewBox="0 0 24 24"><path d="M12 3 5 6v5c0 4.5 3 8.2 7 10 4-1.8 7-5.5 7-10V6z" stroke="${color}" stroke-width="2" stroke-linejoin="round" fill="none"/><path d="${checked ? 'm9 12 2 2 4-4' : 'M9 11v2M12 9v6M15 10.5v3'}" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`,
  mic: () => '<svg width="18" height="18" viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3" stroke="#34D399" stroke-width="2.2" fill="none"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3" stroke="#34D399" stroke-width="2.2" stroke-linecap="round" fill="none"/></svg>',
  reset: () => '<svg width="18" height="18" viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 3-6.7M3 4v4h4" stroke="#F9FAFB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>',
  sliders: () => '<svg width="18" height="18" viewBox="0 0 24 24"><path d="M4 7h10M18 7h2M4 17h4M12 17h8" stroke="#F9FAFB" stroke-width="2" stroke-linecap="round" fill="none"/><circle cx="16" cy="7" r="2" stroke="#F9FAFB" stroke-width="2" fill="none"/><circle cx="10" cy="17" r="2" stroke="#F9FAFB" stroke-width="2" fill="none"/></svg>',
  wave: (w = 62, h = 26) => `<svg width="${w}" height="${h}" viewBox="0 0 96 40"><g stroke="#34D399" stroke-width="5" stroke-linecap="round"><path d="M6 17v6M16 12v16M26 6v28M36 14v12M46 3v34M56 10v20M66 5v30M76 13v14M86 17v6"/></g></svg>`,
};

// ---- chrome.tsx -----------------------------------------------------------------------------------------
function emblemHeader(large) {
  const height = large ? 262 : 150, barTop = large ? 190 : 92, barH = large ? 44 : 38;
  const size = large ? 216 : 130, top = large ? 28 : 10, rivet = barTop + (barH - 10) / 2 - 2;
  return `<div class="eheader carbon" style="height:${height}px">
    <div class="bar" style="top:${barTop}px;height:${barH}px"></div>
    <div class="rivet" style="left:14px;top:${rivet}px"></div><div class="rivet" style="right:14px;top:${rivet}px"></div>
    <div class="scrim"></div>
    <div class="emblem" style="top:${top}px"><img src="assets/DaVoice_emblem.png" width="${size}" height="${size}" alt=""></div>
  </div>`;
}
function traces(opts) {
  if (opts === false) return '';
  const o = opts || {};
  let html = `<svg class="traces" style="right:8px" width="90" height="70" viewBox="0 0 90 70"><g fill="none" stroke="#3A4D3F" stroke-width="1.2"><path d="M2 6H58L72 20V66"/>${o.double ? '<path d="M24 14H52L62 24V50"/>' : ''}</g>
    <g fill="#0D1411" stroke="#3A4D3F" stroke-width="1.2"><circle cx="2" cy="6" r="2.5"/><circle cx="72" cy="66" r="2.5"/>${o.double ? '<circle cx="24" cy="14" r="2.5"/><circle cx="62" cy="50" r="2.5"/>' : ''}</g></svg>`;
  if (o.left) {
    html += `<svg class="traces" style="left:8px" width="70" height="70" viewBox="0 0 70 70"><path d="M68 6H22L8 20V60" fill="none" stroke="#3A4D3F" stroke-width="1.2"/>
      <g fill="#0D1411" stroke="#3A4D3F" stroke-width="1.2"><circle cx="68" cy="6" r="2.5"/><circle cx="8" cy="60" r="2.5"/></g></svg>`;
  }
  return html;
}
const panelScreen = (inner, { large, tr } = {}) =>
  `<div class="screen">${emblemHeader(large)}<div class="panel">${traces(tr)}${inner}</div></div>`;
const heading = (eyebrow, title, subtitle, style = '') =>
  `<div class="heading" style="${style}">${eyebrow ? `<div class="eyebrow">${esc(eyebrow)}</div>` : ''}<div class="title">${esc(title)}</div>${subtitle ? `<div class="subtitle">${esc(subtitle)}</div>` : ''}</div>`;
const primary = (label, a, { disabled, icon = '', cls = '', style = '' } = {}) =>
  `<button class="primary ${cls}" style="${style}" ${disabled ? 'disabled' : a}>${icon}<span>${esc(label)}</span></button>`;
const secondary = (label, a, { disabled, cls = '', style = '' } = {}) =>
  `<button class="secondary ${cls}" style="${style}" ${disabled ? 'disabled' : a}>${esc(label)}</button>`;
const backSquare = (a) => `<button class="back-square" aria-label="Back" ${a}>${ICON.chevron()}</button>`;

// ---- 1 · language "under the hood" (LanguageHoodScreen.tsx) ----------------------------------------------
function languageScreen() {
  const langs = S.languages || [];
  const defaultId = S.defaultLanguage;
  const picked = langs.some((l) => l.id === local.picked) ? local.picked : defaultId;
  const cur = langs.find((l) => l.id === picked) || langs[0];
  if (!cur) return '<div class="screen"></div>';
  const rack = [...langs.filter((l) => l.id === defaultId), ...langs.filter((l) => l.id !== defaultId)];
  const tiles = rack.map((l) => {
    const on = l.id === picked;
    return `<button class="lang-tile ${on ? 'on' : ''}" role="radio" aria-checked="${on}" ${act('pickLanguage', { id: l.id })}>
      <div class="n">${esc(l.code)}<span style="color:#34D399"> • </span>${esc(l.shortName)}</div>
      <div class="z">${l.installed ? 'Installed' : `${l.sizeMB} MB`}</div>${on ? ICON.check(16) : ICON.download(16)}</button>`;
  }).join('');
  return `<div class="screen" style="background:var(--bg)">
    <img class="hood-img" src="assets/hood_background_B.jpg" alt="">
    <div style="position:absolute;left:0;right:0;top:${d(560)};height:${d(120)};background:linear-gradient(180deg,rgba(11,15,14,0),var(--bg))"></div>
    <div style="position:absolute;left:0;right:0;top:${d(680)};bottom:0;background:var(--bg)"></div>
    <div style="position:absolute;left:0;right:0;top:${d(380)};bottom:0;background:linear-gradient(180deg,rgba(3,5,4,0) 0%,rgba(3,5,4,.8) 26%,rgba(3,5,4,.92) 100%)"></div>
    <div style="position:absolute;left:${d(24)};right:${d(24)};top:${d(190)};height:${d(68)};border-radius:${d(34)};
      background:radial-gradient(ellipse at center,rgba(8,12,11,1) 0%,rgba(8,12,11,.97) 62%,rgba(8,12,11,0) 100%)"></div>
    <div class="hood-title" style="top:${d(202)}">
      <div class="t" style="font-size:${d(18)};letter-spacing:${d(1.08)}">CHOOSE YOUR LANGUAGE</div>
      <div class="s" style="font-size:${d(12)};margin-top:${d(3)}">Select a voice pack to install on the engine</div>
    </div>
    <div class="engine" style="left:${d(132)};top:${d(263)};width:${d(132)};height:${d(132)}">
      <div class="spin" style="left:${d(-10)};top:${d(-10)};width:${d(152)};height:${d(152)}"></div>
      <div class="glow"></div>
      <div class="face">
        <div style="font-weight:700;color:var(--mint-light);font-size:${d(9)};letter-spacing:${d(1.8)}">SELECTED</div>
        <div class="code" style="font-size:${d(24)}">${esc(cur.code)}</div>
        <div style="font-weight:600;color:var(--mint-pale);font-size:${d(12)}">${esc(cur.shortName)}</div>
        <div style="color:var(--text2);font-size:${d(11)}">${cur.installed ? 'Installed' : `${cur.sizeMB} MB`}</div>
      </div>
    </div>
    <div style="position:absolute;left:${d(16)};top:${d(430)};width:${d(148)};pointer-events:none">
      <div style="font-weight:700;color:var(--mint-light);font-size:${d(10)};letter-spacing:${d(1.8)}">${langs.length} LANGUAGES</div>
      <div style="color:var(--tag);font-size:${d(12)};line-height:1.4;margin-top:${d(6)};text-shadow:0 1px 3px #000">Scroll the module rack to pick one. It installs once and runs offline.</div>
    </div>
    <div class="rack" style="left:${d(180)};right:${d(12)};top:${d(410)};bottom:98px;border-radius:${d(16)}">
      <div class="list" role="radiogroup" aria-label="Language">${tiles}</div>
    </div>
    <div style="position:absolute;left:16px;right:16px;bottom:24px">
      ${primary(cur.installed ? `Continue with ${cur.name}` : `Install ${cur.name} · ${cur.sizeMB} MB`, act('install', { id: cur.id }),
        { icon: cur.installed ? '' : ICON.download(20, '#04140D', 2.4), style: 'width:100%' })}
    </div>
  </div>`;
}

// ---- 2 · install speedometer (InstallSpeedometerScreen.tsx) ---------------------------------------------
const DIAL = { W: 340, H: 320, CX: 170, CY: 170, R: 128 };
const dialAngle = (v) => 135 + 2.7 * v;
const dialPoint = (deg, r) => [DIAL.CX + r * Math.cos((deg * Math.PI) / 180), DIAL.CY + r * Math.sin((deg * Math.PI) / 180)];
function dialArc(from, to) {
  if (to - from < 0.5) to = from + 0.5;
  const [x1, y1] = dialPoint(dialAngle(from), DIAL.R), [x2, y2] = dialPoint(dialAngle(to), DIAL.R);
  return `M${x1} ${y1} A${DIAL.R} ${DIAL.R} 0 ${(to - from) * 2.7 > 180 ? 1 : 0} 1 ${x2} ${y2}`;
}
function dialBody(value) {
  const p = [`<circle cx="170" cy="170" r="152" fill="rgba(6,12,10,.85)" stroke="#4B5552" stroke-width="3"/>
    <circle cx="170" cy="170" r="146" fill="none" stroke="#2C3331"/>
    <path d="${dialArc(0, 100)}" fill="none" stroke="#17211E" stroke-width="12" stroke-linecap="round"/>
    <path d="${dialArc(0, Math.max(value, 0.5))}" fill="none" stroke="#34D399" stroke-opacity=".22" stroke-width="22" stroke-linecap="round"/>
    <path d="${dialArc(0, Math.max(value, 0.5))}" fill="none" stroke="#34D399" stroke-width="12" stroke-linecap="round"/>`];
  for (let i = 0; i <= 100; i += 5) {
    const major = i % 10 === 0;
    const [x1, y1] = dialPoint(dialAngle(i), major ? 104 : 110), [x2, y2] = dialPoint(dialAngle(i), 116);
    p.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${i <= value ? '#6EE7B7' : '#4B5552'}" stroke-width="${major ? 3 : 1.5}" stroke-linecap="round"/>`);
  }
  for (let i = 0; i <= 100; i += 10) {
    const [x, y] = dialPoint(dialAngle(i), 88);
    p.push(`<text x="${x}" y="${y + 4.5}" fill="${i <= value ? '#F9FAFB' : '#6B7470'}" font-family="Inter" font-weight="700" font-size="13" text-anchor="middle">${i}</text>`);
  }
  return p.join('');
}
const installScreen = {
  mount() {
    return `<div class="screen" style="background:#050807">
      <div style="position:absolute;top:0;left:0;right:0;height:calc(var(--u) * 390 * .52);overflow:hidden;pointer-events:none">
        <img src="assets/hood_background_B.jpg" style="width:100%" alt="">
        <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,8,7,.55) 0%,rgba(5,8,7,.82) 55%,#050807 100%)"></div>
      </div>
      <div style="position:relative;text-align:center;padding:34px 24px 0;display:flex;flex-direction:column;gap:6px" id="inHead"></div>
      <div style="position:relative;margin:26px auto 0;width:min(340px, calc(100% - 50px))">
        <svg viewBox="0 0 340 320" style="width:100%;display:block">
          <g id="dialBody"></g>
          <g id="needle" style="transform:rotate(135deg)"><path d="M170 163 L286 168.5 L286 171.5 L170 177 Z" fill="#34D399" fill-opacity=".35"/>
            <path d="M170 166 L284 169 L284 171 L170 174 Z" fill="#F9FAFB"/><path d="M170 167 L146 169 L146 171 L170 173 Z" fill="#59625F"/></g>
          <circle cx="170" cy="170" r="16" fill="#1A2421" stroke="#59625F" stroke-width="2"/><circle cx="170" cy="170" r="9" fill="#34D399" fill-opacity=".25"/><circle cx="170" cy="170" r="5" fill="#34D399"/>
          <text id="readout" x="170" y="256" text-anchor="middle" font-family="Inter" font-weight="800" font-size="46" fill="#F9FAFB" style="filter:drop-shadow(0 0 8px rgba(52,211,153,.7))">0</text>
          <text x="170" y="276" text-anchor="middle" font-family="Inter" font-weight="700" font-size="12" letter-spacing="2.4" fill="#6EE7B7">KM/H</text>
        </svg>
      </div>
      <div id="inStages"></div>
      <div style="position:absolute;left:16px;right:16px;bottom:24px;display:flex;gap:12px" id="inButtons"></div>
    </div>`;
  },
  update() {
    const x = S.install || {};
    const value = Math.max(0, Math.min(100, Math.round(x.pct || 0)));
    setHtml('inHead', `<div class="eyebrow" style="color:var(--mint-light);letter-spacing:2.4px">${x.installed ? 'INSTALLED' : 'INSTALLING LANGUAGE PACK'}</div>
      <div class="title" style="font-size:26px">${esc(x.name)}</div><div class="subtitle" style="font-size:14px">${esc(x.code)} voice pack · ${x.sizeMB} MB</div>`);
    setHtml('dialBody', dialBody(value));
    document.getElementById('needle').style.transform = `rotate(${dialAngle(value)}deg)`;
    document.getElementById('readout').textContent = value;
    const verifying = x.stage === 'verify';
    const rows = [
      ['Downloading', x.installed && !x.mbDone ? 'already on this computer' : x.stage ? `${x.mbDone} / ${x.mbTotal} MB` : x.error ? '' : 'starting…', x.installed || verifying ? 'done' : x.error ? 'failed' : 'active'],
      ['Checking the download', verifying && !x.installed ? 'verifying…' : '', x.installed ? 'done' : verifying ? (x.error ? 'failed' : 'active') : 'todo'],
      ['Installed on the engine', x.installed ? 'ready' : '', x.installed ? 'done' : 'todo'],
    ];
    setHtml('inStages', `<div class="stages">${rows.map(([label, detail, st]) => `<div class="stage-row"><div class="dot ${st}">${st === 'done' ? ICON.check(12, '#04140D', 2.4) : ''}</div>
      <div class="stage-label" style="color:${st === 'todo' ? 'var(--text2)' : 'var(--text)'}">${label}</div><div class="stage-detail">${esc(detail)}</div></div>`).join('')}</div>
      ${x.error ? `<div class="error">${esc(x.error)}</div>` : ''}`);
    setHtml('inButtons', x.installed
      ? primary('Ready to drive — choose a voice', act('installContinue'), { icon: '', cls: 'flex1' }).replace('</button>', `${ICON.arrow('#04140D', 20)}</button>`)
      : x.error ? secondary('Cancel', act('cancelInstall'), { cls: 'flex1' }) + primary('Retry', act('retryInstall'), { cls: 'flex1' })
        : secondary('Cancel installation', act('cancelInstall'), { cls: 'flex1' }));
  },
};

// ---- 3 · voice (VoiceScreen.tsx) --------------------------------------------------------------------------
const avatar = (name, on, size) =>
  `<div class="avatar ${on ? 'on' : ''}" style="width:${size}px;height:${size}px;font-size:${size > 34 ? 15 : 13}px">${esc((name || '?').charAt(0).toUpperCase())}</div>`;
function voiceScreen() {
  const v = S.voice || {};
  const builtIn = v.originalVoice ? [v.originalVoice, ...v.builtIn] : v.builtIn || [];
  const maxStyles = Math.max(0, ...(v.expressive || []).map((x) => x.styles));
  const clonedSelected = (v.cloned || []).includes(v.selected);
  const expressive = (v.expressive || []).length ? `<div style="display:flex;flex-direction:column;gap:10px">
      <div class="section-label">Expressive · ${maxStyles} styles</div>
      <div class="row">${v.expressive.map((x) => `<button class="tile expressive ${x.name === v.selected ? 'on' : ''}" ${act('selectVoice', { voice: x.name })}>
        ${avatar(x.name, x.name === v.selected, 36)}<div style="min-width:0"><div class="vname">${esc(x.name)}</div><div class="vkind">${x.styles} styles</div></div></button>`).join('')}</div>
      ${(v.examples || []).length ? `<div class="row">${v.examples.map((e) => `<button class="style-chip ${v.playing === e.text ? 'playing' : ''}" aria-label="Play example: ${esc(e.label)}" ${act('playExample', { text: e.text })}>${ICON.play()}<span>${esc(e.label)}</span></button>`).join('')}</div>` : ''}
    </div>` : '';
  const inner = `${heading('Step 2 of 5', 'Choose Your Voice')}
    <div class="scroll">
      <button class="clone-row" ${act('openClone')}><div class="clone-icon">${ICON.plus()}</div>
        <div style="flex:1"><div style="font-weight:700;font-size:16px">Clone a new voice</div><div style="font-size:13px;color:var(--text2);margin-top:2px">Record ~10 s or upload a file</div></div>${ICON.chevron('right', '#34D399')}</button>
      ${expressive}
      <div style="display:flex;flex-direction:column;gap:10px"><div class="section-label">Built-in</div>
        <div class="grid">${builtIn.map((name) => `<button class="tile builtin ${name === v.selected ? 'on' : ''}" ${act('selectVoice', { voice: name })}>${avatar(name, name === v.selected, 32)}
          <div class="bn">${esc(name)}</div>${name === v.originalVoice ? '<div class="fastest">fastest</div>' : ''}</button>`).join('')}</div></div>
      <div style="display:flex;flex-direction:column;gap:10px"><div class="section-head"><div class="section-label">Your cloned voices</div>
        ${clonedSelected ? `<button class="link-warn" ${act('deleteCloned', { voice: v.selected })}>Delete "${esc(v.selected)}"</button>` : ''}</div>
        ${(v.cloned || []).length ? `<div class="cloned-row">${v.cloned.map((n) => `<button class="tile cloned-chip ${n === v.selected ? 'on' : ''}" ${act('selectVoice', { voice: n })}>${esc(n)}</button>`).join('')}</div>`
          : '<div class="empty-cloned">None yet — clone one above</div>'}</div>
    </div>
    <div class="footer" style="padding-top:12px">${primary(`Continue with ${v.selected}`, act('voiceContinue'), { cls: 'flex1' })}</div>`;
  return panelScreen(inner);
}

// ---- 2b · clone a voice (VoiceCloneScreen.tsx) ---------------------------------------------------------
function cloneScreen() {
  const c = S.clone || {};
  const clock = `0:${String(Math.floor(c.recordSeconds || 0)).padStart(2, '0')}`;
  const clipping = (c.peak || 0) > 0.97;
  const recordHint = c.recording
    ? clipping ? 'Too loud: move a little further from the microphone.'
      : (c.recordSeconds || 0) < c.recommendedSeconds ? `Keep reading: about ${c.recommendedSeconds} seconds is best.` : 'Good. Stop when you finish the sentence.'
    : `Recording stops by itself after ${c.maxSeconds} seconds.`;
  const volumeHint = c.volume === 100 ? 'The same loudness as the recording.' : `${Math.abs(c.volume - 100)}% ${c.volume > 100 ? 'louder' : 'quieter'} than the recording.`;
  const source = c.source === 'file'
    ? `<div class="hint">A recording of one person speaking, without music: wav, mp3, m4a, aac, flac or ogg.</div>
       ${secondary(c.sample ? 'Choose another file' : 'Choose an audio file', act('pickFile'))}`
    : `<div class="hint">Read this aloud in your normal voice:</div><div class="reading">${esc(c.readingText)}</div>
       <div class="rec-row"><div class="clock ${c.recording ? 'on' : ''}">${clock}</div><div class="level"><div class="${clipping ? 'clip' : ''}" style="width:${Math.round(Math.min(1, c.peak || 0) * 100)}%"></div></div></div>
       <div class="hint ${clipping && c.recording ? 'warn' : ''}">${recordHint}</div>
       ${c.recording ? primary('Stop recording', act('toggleRecording')) : secondary(c.sample ? 'Record again' : 'Start recording', act('toggleRecording'))}`;
  const inner = `${heading('Step 2 of 5', 'Clone a New Voice', `One person speaking for about ${c.recommendedSeconds} seconds.`, 'padding-bottom:8px')}
    <div class="scroll">
      <div class="field"><div class="section-label">Name</div>
        <input id="cloneName" class="text-input" maxlength="40" placeholder="For example: Dana" value="${esc(local.cloneName)}">
        <div class="hint">Shown under this name in the voice list. Letters, digits, spaces and dashes.</div></div>
      <div class="segments">${[['mic', 'Microphone'], ['file', 'Upload a file']].map(([k, label]) => `<button class="${c.source === k ? 'on' : ''}" ${act('cloneSource', { source: k })}>${label}</button>`).join('')}</div>
      ${source}
      ${c.sample ? `<div class="sample"><div style="flex:1;min-width:0"><div class="section-label" style="padding:0">Sample</div><div style="font-size:14px;margin-top:2px">${esc(c.sample)}</div></div>
        <button class="chip-btn" ${act('playSample')}>${ICON.play(12)}Play</button></div>` : ''}
      <div class="section-label">Voice volume</div>
      <div class="stepper"><button ${c.volume <= 50 ? 'disabled' : act('cloneVolume', { step: -10 })}>−</button><div style="font-weight:800;font-size:20px;min-width:70px;text-align:center">${c.volume}%</div>
        <button ${c.volume >= 200 ? 'disabled' : act('cloneVolume', { step: 10 })}>+</button></div>
      <div class="hint" style="text-align:center">${volumeHint}</div>
      ${c.result ? `<div class="result"><div style="font-weight:800;font-size:16px">Voice "${esc(c.result.voice)}" is ready</div>
        ${c.result.weak ? '<div class="hint warn">The recording was short or noisy: the voice may sound less like you.</div>' : ''}
        <button class="chip-btn" style="align-self:flex-start" ${act('listenClone')}>${ICON.play(12)}Listen to it</button></div>` : ''}
      ${c.error ? `<div class="error" style="margin:0">${esc(c.error)}</div>` : ''}
      <div class="hint" style="font-size:11px">Cloned voices folder: ${esc(c.folder)}</div>
    </div>
    <div class="footer" style="padding-top:12px">${backSquare(act('cloneBack'))}
      ${c.result ? primary('Use this voice', act('useClone'), { cls: 'flex1' })
        : primary(c.busy ? 'Creating voice…' : 'Create voice', act('createCloneNow'), { cls: 'flex1', disabled: c.busy || c.recording })}</div>`;
  return panelScreen(inner, { tr: false });
}

// ---- 3 · speaker verification (SpeakerScreen.tsx, SignatureScreen.tsx, VoiceTestScreen.tsx) ----------------
function speakerScreen() {
  const point = (t) => `<div class="point">${ICON.check(18, '#34D399', 2.4)}<span>${esc(t)}</span></div>`;
  const saved = S.speaker && S.speaker.hasSaved;
  const inner = `${heading('Step 3 of 5', 'Isolate your voice?', 'The agent learns your voice and then answers only you.', 'padding-top:26px')}
    <div class="points">${point('Passengers, the radio and other voices are ignored')}${point('Takes about 30 seconds: you read 5 short sentences')}${point('Your voice signature never leaves this computer')}</div>
    <div class="body">${saved
      ? primary('Use my saved signature', act('useSaved'), { icon: ICON.shield(true) }) + secondary('Record it again', act('createSignature'))
      : primary('Create my voice signature', act('createSignature'), { icon: ICON.shield(false) }) + '<div class="recommended">Recommended</div>'}</div>
    <div class="footer">${secondary('Skip · answer any voice', act('skipSpeaker'), { cls: 'flex1' })}</div>`;
  return panelScreen(inner, { tr: { left: true, double: true } });
}

function signatureScreen() {
  const g = S.signature || {};
  const total = Math.max(1, g.target || 5), done = Math.max(0, Math.min(total, g.collected || 0));
  const finished = done >= total;
  const sentence = (g.sentences || [])[Math.min(done, (g.sentences || []).length - 1)] || '';
  const R = 56, CIRC = 2 * Math.PI * R;
  const inner = `${heading('Step 3 of 5 · Voice signature', 'Read this aloud', 'Use your natural voice. The next sentence appears by itself.', 'padding-top:24px')}
    <div class="card"><div class="card-label">${finished ? `ALL ${total} SENTENCES CAPTURED` : `SENTENCE ${done + 1} OF ${total} · SAY`}</div>
      <div class="sentence" key="${done}">${finished ? '<span style="color:var(--mint-light)">Creating your voice signature…</span>' : `“${esc(sentence)}”`}</div></div>
    <div class="dots">${Array.from({ length: total }, (_, i) => `<span class="${i < done ? 'done' : i === done ? 'cur' : ''}"></span>`).join('')}</div>
    <div class="ring"><svg width="132" height="132" viewBox="0 0 132 132" style="position:absolute;inset:0;transform:rotate(-90deg)">
      <circle cx="66" cy="66" r="${R}" fill="none" stroke="#1A2421" stroke-width="8"/>
      <circle cx="66" cy="66" r="${R}" fill="none" stroke="#34D399" stroke-width="8" stroke-linecap="round" stroke-dasharray="${CIRC}" stroke-dashoffset="${CIRC * (1 - done / total)}" style="transition:stroke-dashoffset .4s"/></svg>
      <div class="inner">${ICON.wave()}<div class="listening">${finished ? 'Saving' : 'Listening'}</div></div></div>`;
  return panelScreen(inner, { tr: false });
}

function voiceTestScreen() {
  const t = S.voicetest || {};
  const r = t.result;
  if (r && r.isMatch) local.lastMatchAt = Date.now();
  const match = !!r && (r.isMatch || Date.now() - local.lastMatchAt < 2000);
  const since = t.at ? `${Math.max(0, Date.now() / 1000 - t.at).toFixed(1)}s` : '—';
  const metric = (l, v, tone) => `<div class="metric"><div class="l">${l}</div><div class="v" style="${tone === 'good' ? 'color:var(--mint-light)' : tone === 'bad' ? 'color:var(--warning2)' : ''}">${v}</div></div>`;
  const inner = `${heading('Step 3 of 5 · Voice signature', 'Test your voice', `Say “${S.wakePhrase}” or any sentence. Then let someone else try.`, 'padding-top:24px')}
    <div class="badge ${match ? 'match' : ''}">${match ? ICON.check(54, '#04140D', 2.6) : '<svg width="54" height="54" viewBox="0 0 24 24"><path d="M4 11v2M8 8v8M12 4v16M16 8v8M20 11v2" stroke="#34D399" stroke-width="2.4" stroke-linecap="round" fill="none"/></svg>'}</div>
    <div class="headline" style="${match ? 'color:var(--mint-light)' : ''}">${match ? "It's you" : 'Listening…'}</div>
    <div class="detail">${match ? 'The agent recognises this voice.' : r ? 'No match right now. It stays like this for silence, noise and other voices.' : 'Say something to test your voice signature.'}</div>
    <div class="metrics">${metric('Last score', r ? r.score.toFixed(3) : '—')}${metric('Match', r ? (r.isMatch ? 'Yes' : 'No') : '—', r ? (r.isMatch ? 'good' : 'bad') : '')}${metric('Since last', since)}</div>
    <div class="footer">${primary(r ? 'Continue' : 'Waiting for the first result…', act('voiceTestContinue'), { cls: 'flex1', disabled: !r })}</div>`;
  return panelScreen(inner, { tr: { left: true, double: true } });
}

// ---- 4 · wake word (WakeWordScreen.tsx) ---------------------------------------------------------------------
const BARS = [4, 12, 6, 20, 8, 28, 14, 34, 20, 38, 26, 38, 20, 34, 14, 28, 8, 20, 6, 12, 4];
function wakeScreen() {
  const w = S.wakeword || {};
  return `<div class="screen carbon-faint">
    <div class="wake-top"><div class="eyebrow">Step 4 of 5</div></div>
    <div class="emblem-box ${w.listening ? '' : 'off'}"><div class="r"></div><div class="r"></div><div class="r"></div><div class="static"></div>
      <img class="${w.heard ? 'heard' : ''}" src="assets/DaVoice_emblem.png" alt=""></div>
    <div class="bars ${w.listening ? '' : 'off'}"><svg width="260" height="44" viewBox="0 0 260 44"><g stroke="#34D399" stroke-width="3" stroke-linecap="round" opacity=".9">
      <path d="${BARS.map((h, i) => `M${10 + i * 12} ${22 - h / 2}v${h}`).join('')}"/></g></svg></div>
    <div class="wake-texts">${w.listening
      ? `<div class="lead">${w.heard ? 'Wake word detected' : 'Listening for the wake word'}</div><div class="phrase">“${esc(S.wakePhrase)}”</div><div class="after">then say what you want the car to do</div>`
      : `<div class="lead">Wake word · “${esc(S.wakePhrase)}”</div><div class="status">${esc(w.message)}</div>`}</div>
    <div class="chips"><span>Voice · ${esc(w.voice)}</span><span>${esc(w.language)}</span><span class="${w.driverOnly ? 'on' : ''}">${w.driverOnly ? 'Driver only' : 'Anyone'}</span></div>
    <div class="footer">${backSquare(act('wakeBack'))}${secondary('Simulate wake word', act('simulateWake'), { cls: 'flex1', style: 'color:var(--tag);font-size:15px' })}</div>
  </div>`;
}

// ---- 5 · agent loading (AgentLoadingScreen.tsx) -------------------------------------------------------------
function loadingScreen() {
  const l = S.loading || {};
  const rows = (l.stages || []).map((st, i) => {
    const done = l.activeIndex > i, active = l.activeIndex === i;
    const detail = done ? 'done' : active ? [st.detail, `${l.seconds} s`].filter(Boolean).join(' · ') : st.detail;
    const progress = active && i === 0 && l.progress != null ? `<div class="track"><div style="width:${l.progress}%"></div></div>` : '';
    return `<div class="load-row"><div class="dot ${done ? 'done' : active ? 'active' : ''}">${done ? ICON.check(16, '#04140D', 2.6) : i + 1}</div>
      <div class="info"><div class="lbl ${!done && !active ? 'muted' : ''}">${esc(st.label)}</div>${detail ? `<div class="dtl" style="${active ? 'color:var(--tag)' : ''}">${esc(detail)}</div>` : ''}${progress}</div></div>`;
  }).join('');
  const inner = `${heading('Step 5 of 5 · First start only', 'Starting the car agent', `${l.modelName || 'DaVoice Automotive Agent'} · on-device`, 'padding-top:28px;padding-bottom:22px;gap:8px')}
    <div class="load-card">${rows}</div>${l.error ? `<div class="error">${esc(l.error)}</div>` : ''}
    <div class="footer">${secondary('Back', act('loadingBack'), { cls: 'flex1' })}${l.error ? primary('Retry', act('loadingRetry'), { cls: 'flex2' }) : primary('Opens when ready', '', { cls: 'flex2', disabled: true })}</div>`;
  return panelScreen(inner, { large: true, tr: false });
}

// ---- 5 · car agent (CarAgentScreen.tsx) -------------------------------------------------------------------
const SUGGESTIONS = {
  'pt-BR': ['Abre o vidro do motorista', 'Tô com frio', 'Abre o teto', 'Me leva pra casa', 'Liga pra Ana', 'Abre o porta-malas',
    'Coloca o ar em 19', 'Luz ambiente azul', 'Abre a porta traseira esquerda', 'Tranca o carro', 'Toca Anitta',
    'Quanto tem de combustível?', 'Desembaça o vidro', 'Volume 20'],
  en: ['Open the driver window', "I'm cold", 'Open the sunroof', 'Take me home', 'Call Ana', 'Open the trunk', 'Set the AC to 19',
    'Ambient light blue', 'Open the rear left door', 'Lock the car', 'Play Anitta', 'How much fuel do I have?',
    'Defrost the windshield', 'Volume 20'],
};
const callText = (a) => `${a.tool}(${Object.entries(a.args || {}).map(([k, v]) => `${k}: ${typeof v === 'string' ? v : JSON.stringify(v)}`).join(', ')})`;
function banner(s) {
  if (s.call) return { text: `Calling ${s.call}`, meta: 'Phone' };
  if (s.destination) return { text: `→ ${s.destination}`, meta: s.avoid && s.avoid.length ? `avoid ${s.avoid.join(', ')}` : 'Navigation' };
  if (s.radio) return { text: `♪ ${s.radio}`, meta: 'Radio' };
  if (s.media) return { text: `♪ ${s.media}`, meta: s.source };
  if (s.scenario) return { text: `${s.scenario.replace('_', ' ')} mode`, meta: '' };
  return null;
}
const stat = (label, value, { unit = '', sub = '', big, color } = {}) =>
  `<div><div class="stat-label">${label.toUpperCase()}</div><div class="${big ? 'stat-big' : 'stat-value'}" style="${color ? `color:${color}` : ''}">${esc(value)}${unit ? `<span class="stat-unit">${unit}</span>` : ''}</div>${sub ? `<div class="stat-sub">${esc(sub)}</div>` : ''}</div>`;

const carScreen = {
  mount() {
    return `<div class="screen">
      <div class="car-header carbon" id="carHeader"></div>
      <div class="banner-row" id="bannerRow"></div>
      <div class="stage" id="stage"></div>
      <div class="last-card" id="lastCard" aria-live="polite"></div>
      <div class="dev-area"><div class="chip-row" id="chips"></div>
        <div class="input-row"><span id="micState">${ICON.mic()}</span>
          <input id="carText" placeholder="What the driver says…" autocomplete="off" aria-label="What the driver says">
          <button class="send" aria-label="Send" data-act="sendTyped">${ICON.arrow()}</button></div></div>
      <div id="sheet"></div>
    </div>`;
  },
  update() {
    const c = S.car || {}, s = S.carState;
    if (!s) return;
    const latest = S.carLatest;
    setHtml('carHeader', `<button class="icon-plain" aria-label="Back" ${act('carBack')}>${ICON.chevron()}</button>
      <img class="head-emblem" src="assets/DaVoice_emblem.png" alt="">
      <div style="flex:1;min-width:0"><div class="head-title">Car Agent</div><div class="head-sub">On-device</div></div>
      <div class="segment" role="radiogroup" aria-label="Vehicle state">${[false, true].map((drv) => `<button class="${s.driving === drv ? 'on' : ''}" role="radio" aria-checked="${s.driving === drv}" ${act('setDriving', { driving: drv })}>${drv ? 'Driving' : 'Parked'}</button>`).join('')}</div>`);
    const pop = banner(s);
    setHtml('bannerRow', `<div class="banner ${pop ? 'on' : ''}"><div class="bd"></div><div class="bt">${esc(pop ? pop.text : `${s.driving ? 'Driving' : 'Parked'} · all on-device`)}</div>${pop && pop.meta ? `<div class="bm">${esc(pop.meta)}</div>` : ''}</div>
      <button class="icon-button" aria-label="Reset car and chat" ${act('resetCar')}>${ICON.reset()}</button>
      <button class="icon-button" aria-label="Settings" data-act="openSettings">${ICON.sliders()}</button>`);
    const openDoors = Object.values(s.doors).filter((x) => x === 'open').length;
    const anyLock = Object.values(s.doorLocks || {}).some(Boolean);
    const doors = openDoors ? `${openDoors} open` : s.locked ? 'Locked' : anyLock ? 'Part locked' : 'Unlocked';
    setHtml('stage', `<div class="side l">${stat('Driver', `${s.temperature.driver}°`, { big: true })}${stat('Fan', String(s.fan), { unit: ' / 7' })}${stat('Fuel', `${s.fuelPercent}%`)}</div>
      <div class="side r">${stat('Passenger', `${s.temperature.passenger}°`, { big: true })}${stat('Volume', s.muted ? 'Muted' : String(s.volume), { sub: s.radio ? 'Radio' : s.source })}${stat('Doors', doors, { color: openDoors || s.locked ? '#34D399' : '' })}</div>
      ${CAR.svg(s, latest)}`);
    const blocked = !!latest && !latest.ok;
    const title = c.working ? 'Working…' : c.ignored ? 'Not for me — ignored'
      : latest ? `${blocked ? 'Blocked: ' : ''}${cap(latest.summary)}` : 'Ready for a command';
    const heard = c.partial ? `<i>“${esc(c.partial)}…”</i>` : c.heard ? `<b>“${esc(c.heard)}”</b>` : '<b>—</b>';
    const card = document.getElementById('lastCard');
    card.className = `last-card ${blocked && !c.working ? 'blocked' : latest || c.heard ? 'active' : ''}`;
    const turn = c.lastTurn && !c.working ? `<div class="turn-info">${c.lastTurn.scope ? `<b style="color:${c.lastTurn.scope === 'local' ? '#34D399' : '#FBBF24'}">${esc(cap(c.lastTurn.scope))}</b> · ` : ''}${c.lastTurn.seconds} s on this computer</div>` : '';
    setHtml('lastCard', `<div class="heard">You: ${heard}</div><div class="last-title ${blocked && !c.working ? 'warn' : ''}">${esc(title)}</div>
      <div class="call">${latest ? esc(callText(latest)) : 'Speak a command, or type it below'}</div>
      ${c.reply && !c.ignored ? `<div class="reply">${esc(c.voice)}: ${esc(c.reply)}</div>` : ''}${turn}`);
    const pool = SUGGESTIONS[c.language] || SUGGESTIONS.en;
    const k = ((S.carActionCount || 0) * 3) % pool.length;
    setHtml('chips', [0, 1, 2].map((i) => pool[(k + i) % pool.length]).map((t) => `<button class="chip" ${c.working ? 'disabled' : act('sendText', { text: t })}>${esc(t)}</button>`).join(''));
    setHtml('micState', c.working ? ICON.mic() : '<span class="mic-live" title="Listening"></span>');
    const sheet = local.settingsOpen ? `<div class="sheet-backdrop" data-act="closeSettings"></div><div class="sheet" style="z-index:11">
      <div class="sheet-title">SETTINGS</div>
      <div><div class="setting-label">Model</div><div class="setting-value">${esc(c.modelName)}</div></div>
      <div><div class="setting-label">Local confidence</div><div class="setting-value">${c.confidence ? `On · ${c.confidence.toFixed(2)}` : 'Off · every command is checked by the safety rules only'}</div></div>
      <div class="segments">${(c.choices || []).map((v) => `<button class="${v === c.confidence ? 'on' : ''}" ${c.working ? 'disabled' : act('setConfidence', { value: v })}>${v ? v.toFixed(2) : 'Off'}</button>`).join('')}</div>
      <div class="note">Below the threshold the action does not run, and the app says it needs a remote agent. The score is the model's own estimate, not a guaranteed probability. Unsafe or unsupported commands are blocked whatever this setting is.</div>
      ${secondary('Close', 'data-act="closeSettings"')}</div>` : '';
    setHtml('sheet', sheet);
  },
};

// ---- rendering ---------------------------------------------------------------------------------------------
const cache = {};
function setHtml(id, html) {
  if (cache[id] === html) return;
  const el = document.getElementById(id);
  if (!el) return;
  cache[id] = html;
  el.innerHTML = html;
}
const SCREENS = {
  language: languageScreen, install: installScreen, voice: voiceScreen, clone: cloneScreen, speaker: speakerScreen,
  signature: signatureScreen, voicetest: voiceTestScreen, wakeword: wakeScreen, loading: loadingScreen, car: carScreen,
};
let current = null, lastHtml = '';
function render() {
  const name = S.screen;
  const screen = SCREENS[name];
  if (!screen) return;
  if (screen.mount) {
    if (current !== name) {
      for (const k of Object.keys(cache)) delete cache[k];
      $screen.innerHTML = screen.mount();
      current = name;
      lastHtml = '';
    }
    screen.update();
    return;
  }
  const html = screen();
  if (current === name && html === lastHtml) return;
  const focused = document.activeElement && document.activeElement.id;
  const caret = focused ? [document.activeElement.selectionStart, document.activeElement.selectionEnd] : null;
  const scroller = $screen.querySelector('.scroll, .rack .list');
  const scrollTop = current === name && scroller ? scroller.scrollTop : 0;
  $screen.innerHTML = html;
  current = name;
  lastHtml = html;
  const again = $screen.querySelector('.scroll, .rack .list');
  if (again) again.scrollTop = scrollTop;
  if (focused) {
    const el = document.getElementById(focused);
    if (el) { el.focus(); try { el.setSelectionRange(caret[0], caret[1]); } catch (e) { /* not a text field */ } }
  }
}
let connected = true;
function renderOverlay() {
  const toast = S.toast && Date.now() / 1000 - S.toastAt < 6 ? `<div class="toast">${esc(S.toast)}</div>` : '';
  $overlay.innerHTML = (connected ? '' : '<div class="conn">Not connected to car_agent.py — is it running?</div>') + toast;
}

// ---- input --------------------------------------------------------------------------------------------------
const LOCAL_ACTIONS = {
  pickLanguage: ({ id }) => { local.picked = id; render(); },
  openSettings: () => { local.settingsOpen = true; render(); },
  closeSettings: () => { local.settingsOpen = false; render(); },
  createCloneNow: () => post('createClone', { name: local.cloneName }),
  sendTyped: () => sendTyped(),
  pickFile: () => document.getElementById('filePicker').click(),
  deleteCloned: (arg) => { if (confirm(`Delete the voice "${arg.voice}"?`)) post('deleteCloned', arg); },
};
document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-act]');
  if (!el || el.disabled) return;
  const name = el.dataset.act, arg = el.dataset.arg ? JSON.parse(el.dataset.arg) : {};
  if (LOCAL_ACTIONS[name]) LOCAL_ACTIONS[name](arg, el);
  else post(name, arg);
});
document.addEventListener('input', (e) => {
  if (e.target.id === 'cloneName') local.cloneName = e.target.value;
  if (e.target.id === 'carText') local.carText = e.target.value;
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.target.id === 'carText') sendTyped();
});
function sendTyped() {
  const input = document.getElementById('carText');
  const text = (input && input.value || '').trim();
  if (!text || (S.car && S.car.working)) return;
  input.value = '';
  local.carText = '';
  post('sendText', { text });
}
document.getElementById('filePicker').addEventListener('change', async (e) => {
  const file = e.target.files && e.target.files[0];
  e.target.value = '';
  if (file) await fetch(`/api/upload?name=${encodeURIComponent(file.name)}`, { method: 'POST', body: file }).catch(() => {});
});

function resize() {
  const phone = document.querySelector('.phone');
  phone.style.setProperty('--u', `${phone.clientWidth / 390}px`);
}
window.addEventListener('resize', resize);
resize();

// ---- state from car_agent.py ----------------------------------------------------------------------------------
function connect() {
  const events = new EventSource('/events');
  events.onmessage = (e) => {
    S = JSON.parse(e.data);
    if (S.screen !== 'car') local.settingsOpen = false;
    connected = true;
    render();
    renderOverlay();
  };
  events.onerror = () => { connected = false; renderOverlay(); };
}
setInterval(() => { if (S.screen === 'voicetest') render(); renderOverlay(); }, 500);
async function poll() {      // ?poll: plain requests instead of the event stream (proxies, headless browsers)
  try { S = await (await fetch('/state')).json(); connected = true; render(); } catch (e) { connected = false; }
  renderOverlay();
  setTimeout(poll, 700);
}
if (new URLSearchParams(location.search).has('poll')) poll(); else connect();
