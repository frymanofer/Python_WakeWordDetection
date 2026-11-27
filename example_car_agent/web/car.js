// The top-down car of the React Native example (src/redesign/CarDrawing.tsx), as an SVG string.
// 260 x 460 viewBox, front at the top: the left of the drawing is the car's left side.
'use strict';

const CAR = (() => {
  const MINT = '#34D399', TITANIUM = '#4B5552', OLIVE = '#3A4D3F', WARNING = '#F59E0B';
  const POSITIONS = ['front_left', 'front_right', 'rear_left', 'rear_right'];
  const WINDOW_LEVEL = { open: 1, half: 0.5, crack: 0.2, close: 0 };
  const LEVEL_ALPHA = { low: 0.35, medium: 0.5, high: 0.65 };
  const SEAT_RECT = {
    front_left: { x: 74, y: 194, h: 52 }, front_right: { x: 142, y: 194, h: 52 },
    rear_left: { x: 74, y: 262, h: 50 }, rear_right: { x: 142, y: 262, h: 50 },
  };
  const WINDOW_BAR = {
    front_left: { x: 55, y: 170, h: 70 }, front_right: { x: 200, y: 170, h: 70 },
    rear_left: { x: 55, y: 250, h: 66 }, rear_right: { x: 200, y: 250, h: 66 },
  };
  const DOOR = {
    front_left: { x: 44, y: 168, h: 72, rot: 'rotate(38 51 168)' },
    front_right: { x: 209, y: 168, h: 72, rot: 'rotate(-38 209 168)' },
    rear_left: { x: 44, y: 248, h: 70, rot: 'rotate(38 51 248)' },
    rear_right: { x: 209, y: 248, h: 70, rot: 'rotate(-38 209 248)' },
  };
  const AMBIENT = [
    [/blue|azul/i, '#60A5FA'], [/red|vermelh/i, '#F87171'], [/purple|violet|roxo|lilás|lilas/i, '#C084FC'],
    [/green|verde/i, '#34D399'], [/orange|laranja/i, '#FB923C'], [/pink|rosa/i, '#F472B6'],
    [/yellow|amarel/i, '#FACC15'], [/warm|quente/i, '#FDE68A'], [/white|branc/i, '#E5E7EB'],
  ];
  const ambientHex = (c) => (AMBIENT.find(([re]) => re.test(c || '')) || [0, '#2DD4BF'])[1];

  function resolve(target, steering) {
    const t = target === undefined || target === null || target === '' ? 'all' : String(target);
    const driver = steering === 'right' ? 'front_right' : 'front_left';
    const passenger = steering === 'right' ? 'front_left' : 'front_right';
    switch (t) {
      case 'all': return [...POSITIONS];
      case 'driver': return [driver];
      case 'passenger': return [passenger];
      case 'front': return ['front_left', 'front_right'];
      case 'rear': return ['rear_left', 'rear_right'];
      case 'left': return ['front_left', 'rear_left'];
      case 'right': return ['front_right', 'rear_right'];
      default: return POSITIONS.includes(t) ? [t] : [];
    }
  }

  function seatPos(seat, steering) {
    if (seat === 'driver') return steering === 'right' ? 'front_right' : 'front_left';
    if (seat === 'passenger') return steering === 'right' ? 'front_left' : 'front_right';
    return seat;
  }

  // The part of the car a refused tool call was about (blinks amber).
  function blockedPart(action, steering) {
    if (!action || action.ok) return null;
    const t = action.tool, a = action.args || {};
    if (/trunk/.test(t)) return a.target === 'frunk' ? 'frunk' : 'trunk';
    if (/sunroof/.test(t)) return 'sunroof';
    if (/charge/.test(t)) return 'chargePort';
    if (/lock/.test(t)) return 'lock';
    const where = resolve(a.door ?? a.window ?? a.position ?? a.target, steering);
    if (/door/.test(t)) return { doors: where };
    if (/window/.test(t)) return { windows: where };
    return null;
  }

  const FRUNK = 'M70 40 Q130 22 190 40 L192 116 L68 116 Z';
  const TRUNK = 'M68 356 L192 356 L196 420 Q130 440 64 420 Z';

  function svg(s, latest) {
    const steering = (s.vehicle && s.vehicle.steering) || 'left';
    const blocked = blockedPart(latest, steering);
    const seatFill = (pos) => {
      const seat = ['driver', 'passenger', 'rear_left', 'rear_right'].find((x) => seatPos(x, steering) === pos);
      const heat = s.seatHeater[seat], vent = s.seatVentilation[seat];
      if (heat && heat !== 'off') return `rgba(245, 158, 11, ${LEVEL_ALPHA[heat] ?? 0.6})`;
      if (vent && vent !== 'off') return `rgba(96, 165, 250, ${LEVEL_ALPHA[vent] ?? 0.5})`;
      return '#26322E';
    };
    const wheelX = steering === 'right' ? 164 : 96;
    const ambient = s.ambient && s.ambient.on ? ambientHex(s.ambient.color) : null;
    const locked = s.locked || Object.values(s.doorLocks || {}).some(Boolean);
    const focusSeat = s.call ? seatPos('driver', steering)
      : ['driver', 'passenger', 'rear_left', 'rear_right'].includes(s.audioFocus) ? seatPos(s.audioFocus, steering) : null;
    const roof = s.sunroof;
    const p = [];
    p.push(`<svg viewBox="0 0 260 460" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Car seen from above. ${latest ? 'Last action: ' + esc(latest.summary) : 'No action yet'}.">`);
    p.push(`<defs><linearGradient id="dvBody" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#1B2321"/><stop offset=".5" stop-color="#3B4542"/><stop offset="1" stop-color="#1B2321"/></linearGradient>
      <linearGradient id="dvGlass" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#2A4A40"/><stop offset="1" stop-color="#0F1C18"/></linearGradient></defs>`);
    for (const [x, y] of [[38, 76], [210, 76], [38, 346], [210, 346]]) p.push(`<rect x="${x}" y="${y}" width="12" height="58" rx="4" fill="#050706"/>`);
    p.push('<ellipse cx="44" cy="150" rx="9" ry="5" fill="#2C3331"/><ellipse cx="216" cy="150" rx="9" ry="5" fill="#2C3331"/>');
    p.push('<path d="M88 14 Q130 2 172 14 Q206 24 208 70 L211 384 Q211 444 168 452 L92 452 Q49 444 49 384 L52 70 Q54 24 88 14 Z" fill="url(#dvBody)" stroke="#6B7470" stroke-width="1.5"/>');
    p.push(`<path d="M64 36 Q78 22 102 18" fill="none" stroke="${MINT}" stroke-width="4" stroke-linecap="round"/><path d="M196 36 Q182 22 158 18" fill="none" stroke="${MINT}" stroke-width="4" stroke-linecap="round"/>`);
    p.push('<path d="M62 438 Q84 448 104 449" fill="none" stroke="#F87171" stroke-width="3" stroke-linecap="round" opacity=".8"/><path d="M198 438 Q176 448 156 449" fill="none" stroke="#F87171" stroke-width="3" stroke-linecap="round" opacity=".8"/>');
    const frunkOpen = s.frunk === 'open';
    p.push(`<path d="${FRUNK}" fill="${frunkOpen ? 'rgba(52, 211, 153, 0.22)' : 'none'}" stroke="${frunkOpen ? MINT : TITANIUM}" stroke-width="1.6"/>`);
    p.push(`<path d="M70 120 L190 120 L180 160 L80 160 Z" fill="url(#dvGlass)" stroke="${TITANIUM}"/>`);
    if (s.defrost && s.defrost.windshield) {
      p.push('<g stroke="#FB923C" stroke-width="1.6" fill="none" stroke-linecap="round"><path d="M84 132 Q130 126 176 132"/><path d="M82 142 Q130 136 178 142"/><path d="M81 152 Q130 146 179 152"/></g>');
    }
    p.push(`<rect x="64" y="162" width="132" height="162" rx="14" fill="#0A100E" stroke="${ambient || '#2C3331'}" stroke-width="${ambient ? 3 : 1}"/>`);
    if (s.airflow === 'face' && s.fan >= 5) {
      p.push('<g stroke="#7DD3FC" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-dasharray="3 4"><path d="M96 166 L96 188"/><path d="M164 166 L164 188"/></g>');
    }
    p.push(`<circle cx="${wheelX}" cy="178" r="12" fill="none" stroke="${s.wheelHeater ? WARNING : '#59625F'}" stroke-width="4"/>`);
    for (const pos of POSITIONS) {
      const r = SEAT_RECT[pos];
      p.push(`<rect x="${r.x}" y="${r.y}" width="44" height="${r.h}" rx="10" fill="${seatFill(pos)}" stroke="${OLIVE}"/>`);
    }
    p.push(`<rect x="114" y="198" width="32" height="104" rx="8" fill="${roof === 'open' ? 'rgba(52, 211, 153, 0.12)' : 'rgba(30, 60, 50, 0.75)'}"
      stroke="${roof === 'close' ? TITANIUM : MINT}" stroke-width="1.5" ${roof === 'tilt' ? 'stroke-dasharray="4 3"' : ''}/>`);
    for (const pos of POSITIONS) {
      const w = WINDOW_BAR[pos], level = WINDOW_LEVEL[s.windows[pos]] ?? 0;
      p.push(`<rect x="${w.x}" y="${w.y}" width="5" height="${w.h}" rx="2.5" fill="#2A3632"/>`);
      if (level > 0) p.push(`<rect x="${w.x}" y="${w.y}" width="5" height="${Math.round(w.h * level)}" rx="2.5" fill="${MINT}"/>`);
    }
    for (const pos of POSITIONS) {
      if (s.doors[pos] !== 'open') continue;
      const d = DOOR[pos];
      p.push(`<rect x="${d.x}" y="${d.y}" width="7" height="${d.h}" rx="3" fill="rgba(52, 211, 153, 0.25)" stroke="${MINT}" stroke-width="1.5" transform="${d.rot}"/>`);
    }
    p.push(`<path d="M80 328 L180 328 L188 352 L72 352 Z" fill="url(#dvGlass)" stroke="${TITANIUM}"/>`);
    if (s.defrost && s.defrost.rear) p.push('<g stroke="#FB923C" stroke-width="1.4" fill="none"><path d="M84 336 L176 336"/><path d="M80 344 L180 344"/></g>');
    const trunkOpen = s.trunk === 'open';
    p.push(`<path d="${TRUNK}" fill="${trunkOpen ? 'rgba(52, 211, 153, 0.22)' : 'none'}" stroke="${trunkOpen ? MINT : TITANIUM}" stroke-width="1.8"/>`);
    p.push(`<rect x="47" y="370" width="7" height="16" rx="2" fill="${s.chargePort === 'open' ? MINT : '#2C3331'}"/>`);
    if (locked) p.push(`<g><rect x="120" y="384" width="20" height="16" rx="3" fill="${MINT}"/><path d="M124 384 v-5 a6 6 0 0 1 12 0 v5" fill="none" stroke="${MINT}" stroke-width="2.5"/></g>`);

    if (blocked) {
      const g = [];
      if (blocked === 'trunk') g.push(`<path d="${TRUNK}"/>`);
      if (blocked === 'frunk') g.push(`<path d="${FRUNK}"/>`);
      if (blocked === 'sunroof') g.push('<rect x="114" y="198" width="32" height="104" rx="8"/>');
      if (blocked === 'chargePort') g.push('<rect x="45" y="368" width="11" height="20" rx="3"/>');
      if (blocked === 'lock') g.push('<rect x="116" y="372" width="28" height="32" rx="5"/>');
      if (blocked.doors) for (const pos of blocked.doors) { const d = DOOR[pos]; g.push(`<rect x="${d.x}" y="${d.y}" width="7" height="${d.h}" rx="3" transform="${d.rot}"/>`); }
      if (blocked.windows) for (const pos of blocked.windows) { const w = WINDOW_BAR[pos]; g.push(`<rect x="${w.x - 1}" y="${w.y}" width="7" height="${w.h}" rx="3"/>`); }
      p.push(`<g class="blink" fill="rgba(245, 158, 11, 0.3)" stroke="${WARNING}" stroke-width="2">${g.join('')}</g>`);
    }
    if (focusSeat) {
      const cx = SEAT_RECT[focusSeat].x + 22, cy = SEAT_RECT[focusSeat].y + 26;
      p.push(`<circle class="wave" cx="${cx}" cy="${cy}" r="34" fill="none" stroke="${MINT}" stroke-width="1.5"/>`);
      p.push(`<circle class="wave b" cx="${cx}" cy="${cy}" r="34" fill="none" stroke="${MINT}" stroke-width="1.5"/>`);
    }
    p.push('</svg>');
    return p.join('');
  }

  return { svg };
})();
