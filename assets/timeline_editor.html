<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LTX Director</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; height: 100%; background: #1a1a1a; color: #e0e0e0; overflow: hidden; }
body { font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; font-size: 13px; display: flex; flex-direction: column; }

/* ── Toolbar ── */
#toolbar {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
  padding: 8px 10px; background: #111; border-bottom: 1px solid #333; flex-shrink: 0;
}
.btn {
  display: inline-flex; align-items: center; gap: 5px;
  background: #2a2a2a; color: #ddd; border: 1px solid #444;
  border-radius: 5px; padding: 5px 11px; font-size: 12px; cursor: pointer;
  transition: background .12s, border-color .12s, color .12s; white-space: nowrap;
  font-family: inherit;
}
.btn:hover { background: #383838; border-color: #666; color: #fff; }
.btn.danger:hover { background: #3a1515; border-color: #c33; color: #ffaaaa; }
.btn.primary { background: #1a4a2a; border-color: #2d7a44; color: #8ef0a8; }
.btn.primary:hover { background: #205a32; border-color: #3a9a54; color: #afffbf; }
.sep { width: 1px; height: 20px; background: #444; flex-shrink: 0; }
.lbl { font-size: 11px; color: #777; white-space: nowrap; }
.num-input {
  background: #222; border: 1px solid #444; border-radius: 4px;
  color: #ddd; font-size: 12px; width: 58px; padding: 4px 6px;
  text-align: center; font-family: inherit;
}
.num-input:focus { outline: none; border-color: #666; }
#timecode { font-size: 13px; font-family: monospace; color: #bbb; margin-left: auto; white-space: nowrap; }

/* ── Canvas wrap ── */
#canvas-wrap {
  position: relative; flex-shrink: 0;
  overflow: hidden;
  background: #222; border-bottom: 1px solid #333;
}
#timeline { display: block; cursor: default; }

/* ── Zoom/nav bar ── */
#zoom-bar-wrap {
  flex-shrink: 0; background: #111;
  border-bottom: 1px solid #2a2a2a; padding: 0;
  height: 28px; position: relative;
}
#zoom-bar { display: block; width: 100%; height: 28px; cursor: default; }

/* ── Properties panel ── */
#props {
  flex: 1; min-height: 0; overflow-y: auto;
  background: #1e1e1e; border-top: 1px solid #333; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 8px;
}
#prop-title { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: .05em; }
#prop-body { display: none; flex-direction: column; gap: 8px; }
#prop-body.visible { display: flex; }
.prop-row { display: flex; align-items: center; gap: 8px; }
.prop-label { font-size: 12px; color: #999; min-width: 90px; flex-shrink: 0; }
textarea#prop-prompt {
  width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444;
  border-radius: 5px; padding: 7px 9px; font-size: 12px; resize: vertical;
  min-height: 64px; outline: none; font-family: inherit; line-height: 1.45;
}
textarea#prop-prompt:focus { border-color: #666; }
input[type=range].slider {
  -webkit-appearance: none; appearance: none;
  height: 4px; background: #444; border-radius: 2px; outline: none; cursor: pointer; width: 120px;
}
input[type=range].slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 13px; height: 13px; border-radius: 50%; background: #aaa; cursor: pointer;
}
#prop-strength-val { font-size: 12px; color: #ccc; min-width: 32px; }
#prop-audio-info { font-size: 12px; color: #69b4ff; }
#prop-hint { font-size: 11px; color: #555; }
#status { font-size: 11px; color: #777; min-height: 15px; margin-top: 2px; }
</style>
</head>
<body>

<!-- Hidden file inputs -->
<input type="file" id="file-img"   accept="image/*"  multiple style="display:none">
<input type="file" id="file-audio" accept="audio/*"  multiple style="display:none">

<!-- Toolbar -->
<div id="toolbar">
  <button class="btn" id="btn-add-text">📝 Add Text</button>
  <button class="btn" id="btn-upload-img">🖼 Add Image</button>
  <button class="btn" id="btn-upload-audio">🎵 Add Audio</button>
  <div class="sep"></div>
  <span class="lbl">FPS</span>
  <input class="num-input" type="number" id="ctrl-fps" value="24" min="1" max="120" step="1">
  <span class="lbl">Duration (s)</span>
  <input class="num-input" type="number" id="ctrl-dur" value="5" min="0.5" max="600" step="0.5">
  <div class="sep"></div>
  <button class="btn" id="btn-play">[Play]</button>
  <button class="btn danger" id="btn-clear">🗑 Clear</button>
  <span id="timecode">0.00s / 5.00s</span>
</div>

<!-- Timeline canvas -->
<div id="canvas-wrap">
  <canvas id="timeline"></canvas>
</div>

<!-- Zoom/navigation bar -->
<div id="zoom-bar-wrap">
  <canvas id="zoom-bar"></canvas>
</div>

<!-- Properties -->
<div id="props">
  <div id="prop-title">No segment selected — click a segment to edit · Double-click a gap to add text · Drag &amp; drop images or audio onto the timeline</div>
  <div id="prop-body">
    <textarea id="prop-prompt" placeholder="Describe what happens in this segment…" rows="3"></textarea>
    <div class="prop-row" id="prop-strength-row">
      <span class="prop-label">Guide strength</span>
      <input type="range" class="slider" id="prop-strength" min="0" max="1" step="0.01" value="1">
      <span id="prop-strength-val">1.00</span>
    </div>
    <div id="prop-audio-info"></div>
    <div class="prop-row">
      <button class="btn danger" id="btn-del-seg">🗑 Delete segment</button>
    </div>
  </div>
  <div id="prop-hint">Drag segments to move · Drag edge to resize · Double-click gap to add text · Drop files onto timeline · Scroll wheel to zoom · Shift+drag or middle-drag to pan</div>
  <div id="status"></div>
</div>

<script>
(function () {
'use strict';

// ── Layout constants ────────────────────────────────────────────────────────
const RULER_H  = 26;
const IMG_H    = 148;
const AUDIO_H  = 64;
const TOTAL_H  = RULER_H + IMG_H + AUDIO_H;
const HANDLE   = 10;   // px of resize handle at each edge
const MIN_LEN  = 4;    // minimum segment length in frames

// ── State ───────────────────────────────────────────────────────────────────
let fps = 24;
let durSec = 5;
function durF() { return Math.max(1, Math.round(durSec * fps)); }

let segs  = [];   // {id,type:'image'|'text',start,length,prompt,imageB64,imgObj,guideStrength}
let audio = [];   // {id,type:'audio',start,length,trimStart,audioB64,fileName}

let selTrack = 'image';   // 'image' | 'audio'
let selId    = null;

let playhead = 0;
let playing  = false;
let rafId    = null;
let playT0   = 0;
let playF0   = 0;

// ── Drag ────────────────────────────────────────────────────────────────────
let drag = null;
// {track,id,zone:'move'|'left'|'right',ox,oStart,oLen}

// ── DOM ─────────────────────────────────────────────────────────────────────
const canvas     = document.getElementById('timeline');
const ctx        = canvas.getContext('2d');
const wrap       = document.getElementById('canvas-wrap');
const propBody   = document.getElementById('prop-body');
const propTitle  = document.getElementById('prop-title');
const propPrompt = document.getElementById('prop-prompt');
const propStr    = document.getElementById('prop-strength');
const propStrVal = document.getElementById('prop-strength-val');
const propStrRow = document.getElementById('prop-strength-row');
const propAudio  = document.getElementById('prop-audio-info');
const timecode   = document.getElementById('timecode');
const statusEl   = document.getElementById('status');
const btnPlay    = document.getElementById('btn-play');

// ── ID ───────────────────────────────────────────────────────────────────────
let _id = 0;
function uid() { return 's' + (++_id) + '_' + Math.random().toString(36).slice(2,6); }

// ── Canvas sizing ────────────────────────────────────────────────────────────
function resizeCanvas() {
  const w = Math.max(wrap.clientWidth || 800, 400);
  canvas.width  = w;
  canvas.height = TOTAL_H;
  render();
}
const ro = new ResizeObserver(resizeCanvas);
ro.observe(wrap);

// ── Coordinate helpers ───────────────────────────────────────────────────────

// View window — the range of frames [viewStart, viewEnd] visible on the canvas.
// Initially the full timeline is visible.
let viewStart = 0;         // first frame visible (can be fractional)
let viewEnd   = durF();    // last frame visible  (can be fractional)

// Clamp viewEnd when durF() changes
function syncView() {
  const df = durF();
  const span = Math.max(1, viewEnd - viewStart);
  viewEnd   = Math.min(df, viewEnd);
  viewStart = Math.max(0, viewEnd - span);
  if (viewEnd - viewStart < 1) { viewStart = 0; viewEnd = df; }
}

function viewSpan() { return Math.max(1, viewEnd - viewStart); }

// Frame → canvas pixel (within the current view window)
function fToPx(f) {
  return ((f - viewStart) / viewSpan()) * canvas.width;
}

// Canvas pixel → frame (within the current view window)
function pxToF(px) {
  return Math.round(clamp(viewStart + (px / canvas.width) * viewSpan(), 0, durF()));
}

// Exact (non-rounded) pixel → frame, used for zoom pivot
function pxToFExact(px) {
  return clamp(viewStart + (px / canvas.width) * viewSpan(), 0, durF());
}

function clamp(v,lo,hi) { return Math.max(lo, Math.min(hi, v)); }

// ── Zoom helpers ──────────────────────────────────────────────────────────────
const MIN_ZOOM_FRAMES = 2;   // can't zoom in further than 2 frames visible

function zoomAt(pivotPx, factor) {
  // factor > 1 = zoom in (fewer frames visible), < 1 = zoom out
  const pivotF = pxToFExact(pivotPx);
  let span = viewSpan() / factor;
  span = Math.max(MIN_ZOOM_FRAMES, Math.min(durF(), span));

  // Keep pivot frame under cursor
  const leftRatio = pivotPx / canvas.width;
  viewStart = pivotF - leftRatio * span;
  viewEnd   = viewStart + span;

  // Clamp to [0, durF()]
  if (viewStart < 0) { viewEnd -= viewStart; viewStart = 0; }
  if (viewEnd > durF()) { viewStart -= (viewEnd - durF()); viewEnd = durF(); }
  viewStart = Math.max(0, viewStart);
  viewEnd   = Math.min(durF(), viewEnd);
}

function panBy(deltaF) {
  const span = viewSpan();
  viewStart = clamp(viewStart + deltaF, 0, durF() - span);
  viewEnd   = viewStart + span;
}

// ── Render ───────────────────────────────────────────────────────────────────
function render() {
  const W = canvas.width;
  ctx.clearRect(0, 0, W, TOTAL_H);

  // Track backgrounds
  ctx.fillStyle = '#252525'; ctx.fillRect(0, RULER_H, W, IMG_H);
  ctx.fillStyle = '#1c1c1c'; ctx.fillRect(0, RULER_H + IMG_H, W, AUDIO_H);

  // Track labels
  ctx.fillStyle = '#444'; ctx.font = '10px sans-serif';
  ctx.fillText('VIDEO  (images · text prompts)', 8, RULER_H + 14);
  ctx.fillText('AUDIO', 8, RULER_H + IMG_H + 14);

  // Track separator line
  ctx.strokeStyle = '#333'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, RULER_H + IMG_H); ctx.lineTo(W, RULER_H + IMG_H); ctx.stroke();

  // Ruler
  drawRuler(W);

  // Segments
  segs.forEach(s  => drawSeg(s,  'image'));
  audio.forEach(s => drawSeg(s, 'audio'));

  // Playhead
  const ph = fToPx(playhead);
  ctx.strokeStyle = '#ff4444'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(ph, 0); ctx.lineTo(ph, TOTAL_H); ctx.stroke();
  // Playhead triangle
  ctx.fillStyle = '#ff4444';
  ctx.beginPath(); ctx.moveTo(ph-5,0); ctx.lineTo(ph+5,0); ctx.lineTo(ph,8); ctx.fill();

  // Timecode
  const tc = (playhead/fps).toFixed(2);
  const tot = durSec.toFixed(2);
  timecode.textContent = tc + 's / ' + tot + 's';
}

function drawRuler(W) {
  ctx.fillStyle = '#2a2a2a'; ctx.fillRect(0, 0, W, RULER_H);

  // Tick step based on the VISIBLE span, not total duration.
  // This keeps tick density correct at all zoom levels.
  const targetMarks = Math.max(4, Math.floor(W / 90));
  const rawStep = viewSpan() / targetMarks;
  const niceSteps = [1,2,5,10,15,24,30,48,60,120,240,480,960];
  const step = niceSteps.reduce((p,c) => Math.abs(c-rawStep)<Math.abs(p-rawStep)?c:p);

  // Only iterate over frames that are actually visible
  const firstTick = Math.ceil(viewStart / step) * step;
  const lastTick  = viewEnd;

  ctx.fillStyle = '#888'; ctx.font = '10px monospace'; ctx.textBaseline = 'top';
  for (let f = firstTick; f <= lastTick; f += step) {
    const x = fToPx(f);
    if (x < 0 || x > W) continue;
    ctx.strokeStyle = '#555'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x, RULER_H-6); ctx.lineTo(x, RULER_H); ctx.stroke();
    const label = (f/fps).toFixed(1) + 's';
    if (x + 4 < W) ctx.fillText(label, x+2, 5);
  }
  ctx.textBaseline = 'alphabetic';
}

function drawSeg(seg, track) {
  const isAudio = track === 'audio';
  const trackY  = isAudio ? RULER_H + IMG_H : RULER_H;
  const trackH  = isAudio ? AUDIO_H : IMG_H;
  const x    = fToPx(seg.start);
  const xEnd = fToPx(seg.start + seg.length);
  const w    = Math.max(xEnd - x, 2);
  const sel = selId === seg.id && selTrack === track;

  // Background fill
  let fill;
  if (isAudio)           fill = sel ? '#1a4570' : '#142e4e';
  else if (seg.type==='text') fill = sel ? '#3a2e5a' : '#261e3e';
  else                        fill = sel ? '#1a4a2a' : '#102e18';

  ctx.fillStyle = fill;
  roundRect(x, trackY+2, w, trackH-4, 4);
  ctx.fill();

  // Image thumbnail (tiled)
  if (!isAudio && seg.type==='image' && seg.imgObj?.complete && seg.imgObj.naturalWidth > 0) {
    ctx.save();
    ctx.beginPath(); roundRect(x+2, trackY+4, w-4, trackH-8, 3); ctx.clip();
    const ih = trackH - 8;
    const iw = Math.max(1, Math.round(seg.imgObj.naturalWidth * ih / seg.imgObj.naturalHeight));
    for (let tx = x+2; tx < x+w-2; tx += iw) {
      ctx.drawImage(seg.imgObj, tx, trackY+4, Math.min(iw, x+w-2-tx), ih);
    }
    ctx.restore();
  }

  // Audio bars
  if (isAudio) {
    ctx.fillStyle = '#2a7abf';
    const bars = Math.max(1, Math.floor(w/3));
    for (let i=0; i<bars; i++) {
      const bx = x + (i * w / bars);
      const bh = (trackH*0.25) + (trackH*0.5)*Math.abs(Math.sin(i*0.8 + seg.start*0.1));
      ctx.fillRect(bx+1, trackY+(trackH-bh)/2, 2, bh);
    }
    // File name
    if (w > 30) {
      ctx.save();
      ctx.beginPath(); ctx.rect(x+4, trackY+2, w-8, AUDIO_H-4); ctx.clip();
      ctx.fillStyle = '#9ad0ff'; ctx.font = '10px sans-serif';
      ctx.fillText(seg.fileName || 'audio', x+5, trackY+AUDIO_H-6);
      ctx.restore();
    }
  }

  // Prompt overlay at bottom of video segments
  if (!isAudio && seg.prompt && w > 20) {
    const oH = Math.max(16, Math.round(trackH * 0.22));
    const oY = trackY + trackH - oH - 2;
    ctx.save();
    ctx.beginPath(); ctx.rect(x+2, oY, w-4, oH); ctx.clip();
    ctx.fillStyle = 'rgba(0,0,0,0.68)'; ctx.fillRect(x+2, oY, w-4, oH);
    ctx.fillStyle = '#dde2f0'; ctx.font = `${Math.min(11, Math.floor(oH*0.62))}px sans-serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    let lbl = seg.prompt;
    const maxW = w - 12;
    while (lbl.length > 1 && ctx.measureText(lbl+'…').width > maxW) lbl = lbl.slice(0,-1);
    if (lbl !== seg.prompt) lbl += '…';
    ctx.fillText(lbl, x + w/2, oY + oH/2);
    ctx.restore();
    ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  }

  // Type icon for text-only segments
  if (!isAudio && seg.type==='text' && w > 30) {
    ctx.fillStyle = '#9090d0'; ctx.font = 'bold 13px sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('T', x + Math.min(18, w/2), trackY + trackH/2 - (seg.prompt?12:0));
    ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  }

  // Border
  ctx.strokeStyle = sel ? '#fff' : (isAudio ? '#2a7abf' : (seg.type==='text' ? '#6060b0' : '#2a7a4a'));
  ctx.lineWidth = sel ? 2 : 1;
  roundRect(x, trackY+2, w, trackH-4, 4); ctx.stroke();

  // Resize handles if selected
  if (sel) {
    ctx.fillStyle = '#fff';
    [[x, trackY+trackH/2-14, 4, 28], [x+w-4, trackY+trackH/2-14, 4, 28]].forEach(([hx,hy,hw,hh])=>{
      ctx.beginPath(); ctx.roundRect(hx,hy,hw,hh,2); ctx.fill();
    });
  }
}

function roundRect(x,y,w,h,r) {
  if (w < 2*r) r = w/2; if (h < 2*r) r = h/2;
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y);
  ctx.quadraticCurveTo(x+w,y,x+w,y+r);
  ctx.lineTo(x+w,y+h-r); ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
  ctx.lineTo(x+r,y+h); ctx.quadraticCurveTo(x,y+h,x,y+h-r);
  ctx.lineTo(x,y+r); ctx.quadraticCurveTo(x,y,x+r,y);
  ctx.closePath();
}

// ── Hit-testing ───────────────────────────────────────────────────────────
function hitTest(mx, my) {
  const isAud = my >= RULER_H + IMG_H;
  const arr   = isAud ? audio : segs;
  const track = isAud ? 'audio' : 'image';
  for (let i = arr.length-1; i >= 0; i--) {
    const s = arr[i];
    const sx   = fToPx(s.start);
    const sxEnd = fToPx(s.start + s.length);
    const sw   = sxEnd - sx;
    if (mx >= sx - HANDLE/2 && mx <= sx + sw + HANDLE/2) {
      let zone = 'move';
      if (mx < sx + HANDLE) zone = 'left';
      else if (mx > sx + sw - HANDLE) zone = 'right';
      return { track, id: s.id, zone };
    }
  }
  return null;
}

// ── Mouse events ─────────────────────────────────────────────────────────
canvas.addEventListener('mousedown', e => {
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left, my = e.clientY - r.top;

  // Seek on ruler click
  if (my < RULER_H) {
    setPlayhead(pxToF(mx)); return;
  }

  const hit = hitTest(mx, my);
  if (hit) {
    selTrack = hit.track; selId = hit.id;
    const arr = hit.track==='audio' ? audio : segs;
    const s   = arr.find(x => x.id === hit.id);
    drag = { track: hit.track, id: hit.id, zone: hit.zone,
             oxF: pxToFExact(mx), oStart: s.start, oLen: s.length };
    updateProps(); render();
  } else {
    selId = null; updateProps(); render();
  }
});

canvas.addEventListener('mousemove', e => {
  if (!drag) return;
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left;
  const dfF = pxToFExact(mx) - drag.oxF;
  const arr = drag.track==='audio' ? audio : segs;
  const s   = arr.find(x => x.id === drag.id);
  if (!s) return;

  if (drag.zone==='move') {
    s.start = Math.round(clamp(drag.oStart + dfF, 0, durF() - s.length));
  } else if (drag.zone==='left') {
    const ns = Math.round(clamp(drag.oStart + dfF, 0, drag.oStart + drag.oLen - MIN_LEN));
    const delta = ns - s.start;
    s.start  = ns;
    s.length = Math.max(MIN_LEN, drag.oLen - (ns - drag.oStart));
    if (drag.track==='audio') s.trimStart = Math.max(0, (s.trimStart||0) + delta);
  } else {
    s.length = Math.max(MIN_LEN, Math.round(drag.oLen + dfF));
  }
  render();
});

canvas.addEventListener('mouseup',    () => { if (drag) { drag=null; commit(); } });
canvas.addEventListener('mouseleave', () => { if (drag) { drag=null; commit(); } });

// Cursor style
canvas.addEventListener('mousemove', e => {
  if (drag) return;
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left, my = e.clientY - r.top;
  if (my < RULER_H) { canvas.style.cursor = 'col-resize'; return; }
  const hit = hitTest(mx, my);
  if (!hit) { canvas.style.cursor = 'crosshair'; return; }
  if (hit.zone==='left'||hit.zone==='right') canvas.style.cursor = 'ew-resize';
  else canvas.style.cursor = 'grab';
});

// ── Mouse wheel → zoom ───────────────────────────────────────────────────────
canvas.addEventListener('wheel', e => {
  e.preventDefault();
  const r    = canvas.getBoundingClientRect();
  const mx   = e.clientX - r.left;
  // deltaY > 0 = scroll down = zoom out; < 0 = zoom in
  const factor = e.deltaY < 0 ? 1.25 : 1 / 1.25;
  zoomAt(mx, factor);
  render();
  renderZoomBar();
}, { passive: false });

// ── Middle-mouse / Shift+drag → pan ──────────────────────────────────────────
let panDrag = null;  // { startX, startViewStart }

canvas.addEventListener('mousedown', e => {
  if (e.button === 1 || (e.button === 0 && e.shiftKey)) {
    e.preventDefault();
    const r = canvas.getBoundingClientRect();
    panDrag = { startX: e.clientX - r.left, startViewStart: viewStart };
  }
}, true);  // capture so it fires before the existing mousedown

canvas.addEventListener('mousemove', e => {
  if (!panDrag) return;
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left;
  const dF = ((panDrag.startX - mx) / canvas.width) * viewSpan();
  const span = viewSpan();
  viewStart = clamp(panDrag.startViewStart + dF, 0, durF() - span);
  viewEnd   = viewStart + span;
  render();
  renderZoomBar();
}, true);

canvas.addEventListener('mouseup', e => {
  if (e.button === 1 || panDrag) panDrag = null;
}, true);

canvas.addEventListener('mouseleave', () => { panDrag = null; });

// Double-click on gap → add text segment
canvas.addEventListener('dblclick', e => {
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left, my = e.clientY - r.top;
  if (my < RULER_H || my >= RULER_H + IMG_H) return;
  const hit = hitTest(mx, my);
  if (!hit) addText(clamp(pxToF(mx) - Math.round(fps), 0, durF() - MIN_LEN*2));
});

// ── Drag-and-drop files ───────────────────────────────────────────────────
canvas.addEventListener('dragover',  e => { e.preventDefault(); wrap.style.outline = '2px dashed #666'; });
canvas.addEventListener('dragleave', ()=> { wrap.style.outline = ''; });
canvas.addEventListener('drop', e => {
  e.preventDefault(); wrap.style.outline = '';
  const r     = canvas.getBoundingClientRect();
  const mx    = e.clientX - r.left, my = e.clientY - r.top;
  const isAud = my >= RULER_H + IMG_H;
  const atF   = clamp(pxToF(mx), 0, durF());
  const files = Array.from(e.dataTransfer.files);
  const imgs  = files.filter(f => f.type.startsWith('image/'));
  const auds  = files.filter(f => f.type.startsWith('audio/'));
  if (isAud || (auds.length > 0 && imgs.length === 0)) {
    auds.forEach(f => loadAudio(f, atF));
  } else {
    imgs.forEach((f,i) => loadImage(f, clamp(atF + i*fps, 0, durF())));
    if (imgs.length === 0) auds.forEach(f => loadAudio(f, atF));
  }
});

// ── Segment creators ──────────────────────────────────────────────────────
function addText(startF) {
  const s = { id:uid(), type:'text', start:startF, length:Math.round(fps*2), prompt:'', guideStrength:1 };
  segs.push(s);
  selTrack='image'; selId=s.id;
  updateProps(); render(); commit();
  propPrompt.focus();
}

function loadImage(file, startF) {
  const reader = new FileReader();
  reader.onload = ev => {
    const b64 = ev.target.result;
    const img = new Image();
    img.onload = () => {
      const s = { id:uid(), type:'image', start:startF, length:Math.round(fps*2), prompt:'', imageB64:b64, imgObj:img, guideStrength:1 };
      segs.push(s);
      selTrack='image'; selId=s.id;
      updateProps(); setStatus('Image: ' + file.name); render(); commit();
    };
    img.src = b64;
  };
  reader.readAsDataURL(file);
}

function loadAudio(file, startF) {
  const reader = new FileReader();
  reader.onload = ev => {
    const b64 = ev.target.result;
    const a   = new Audio(b64);
    a.addEventListener('loadedmetadata', () => {
      const lenF = Math.max(MIN_LEN, Math.round(a.duration * fps));
      const s = { id:uid(), type:'audio', start:startF, length:lenF, trimStart:0, audioB64:b64, fileName:file.name };
      audio.push(s);
      selTrack='audio'; selId=s.id;
      updateProps(); setStatus('Audio: ' + file.name + ' (' + a.duration.toFixed(2) + 's)'); render(); commit();
    });
    a.addEventListener('error', () => {
      setStatus('Could not read audio duration for ' + file.name + ' — added with default length.');
      const s = { id:uid(), type:'audio', start:startF, length:Math.round(fps*3), trimStart:0, audioB64:b64, fileName:file.name };
      audio.push(s);
      selTrack='audio'; selId=s.id;
      updateProps(); render(); commit();
    });
  };
  reader.readAsDataURL(file);
}

// ── Toolbar buttons ───────────────────────────────────────────────────────
document.getElementById('btn-add-text').addEventListener('click', () => {
  addText(clamp(playhead, 0, durF() - MIN_LEN*2));
});
document.getElementById('btn-upload-img').addEventListener('click', () => {
  document.getElementById('file-img').click();
});
document.getElementById('btn-upload-audio').addEventListener('click', () => {
  document.getElementById('file-audio').click();
});
document.getElementById('file-img').addEventListener('change', e => {
  Array.from(e.target.files).forEach((f,i) => loadImage(f, clamp(playhead + i*fps, 0, durF())));
  e.target.value = '';
});
document.getElementById('file-audio').addEventListener('change', e => {
  Array.from(e.target.files).forEach(f => loadAudio(f, clamp(playhead, 0, durF())));
  e.target.value = '';
});

document.getElementById('ctrl-fps').addEventListener('change', e => {
  fps = Math.max(1, parseInt(e.target.value)||24);
  syncView(); viewEnd = Math.max(viewEnd, durF()); render(); renderZoomBar(); commit();
});
document.getElementById('ctrl-dur').addEventListener('change', e => {
  durSec = Math.max(0.5, parseFloat(e.target.value)||5);
  syncView(); viewEnd = Math.max(viewEnd, durF()); render(); renderZoomBar(); commit();
});

// Play/pause
function setPlayhead(f) { playhead = clamp(f,0,durF()); render(); }

function tick() {
  const elapsed = (performance.now() - playT0) / 1000;
  playhead = Math.round(playF0 + elapsed * fps);
  if (playhead >= durF()) { playhead = 0; playT0 = performance.now(); playF0 = 0; }
  render();
  if (playing) rafId = requestAnimationFrame(tick);
}

btnPlay.addEventListener('click', () => {
  playing = !playing;
  btnPlay.textContent = playing ? '[Pause]' : '[Play]';
  if (playing) { playT0 = performance.now(); playF0 = playhead; tick(); }
  else cancelAnimationFrame(rafId);
});

document.getElementById('btn-clear').addEventListener('click', () => {
  if (!confirm('Clear all segments?')) return;
  segs = []; audio = []; selId = null; updateProps();
  setStatus('Cleared.'); commit();
});


// Delete selected
document.getElementById('btn-del-seg').addEventListener('click', () => {
  if (!selId) return;
  if (selTrack==='audio') audio = audio.filter(s => s.id!==selId);
  else                    segs  = segs.filter(s  => s.id!==selId);
  selId = null; updateProps(); commit();
});

// ── Properties panel ─────────────────────────────────────────────────────
function updateProps() {
  if (!selId) {
    propTitle.textContent = 'No segment selected — click a segment to edit · Double-click a gap to add text';
    propBody.classList.remove('visible'); return;
  }
  const arr = selTrack==='audio' ? audio : segs;
  const s   = arr.find(x => x.id===selId);
  if (!s) { selId=null; updateProps(); return; }

  propBody.classList.add('visible');
  const isAud = selTrack==='audio';

  propTitle.textContent = isAud
    ? '🎵 Audio clip — ' + (s.fileName||'audio')
    : (s.type==='text' ? '📝 Text segment' : '🖼 Image keyframe');

  propPrompt.style.display = isAud ? 'none' : 'block';
  propPrompt.value = s.prompt || '';

  propStrRow.style.display = (isAud || s.type==='text') ? 'none' : 'flex';
  if (!isAud && s.type!=='text') {
    propStr.value    = s.guideStrength ?? 1;
    propStrVal.textContent = parseFloat(propStr.value).toFixed(2);
  }

  propAudio.style.display = isAud ? 'block' : 'none';
  if (isAud) propAudio.textContent =
    'Length: ' + (s.length/fps).toFixed(2) + 's  ·  Trim start: ' + ((s.trimStart||0)/fps).toFixed(2) + 's';
}

propPrompt.addEventListener('input', () => {
  const s = segs.find(x => x.id===selId);
  if (s) { s.prompt = propPrompt.value; render(); commit(); }
});

propStr.addEventListener('input', () => {
  const s = segs.find(x => x.id===selId);
  if (s) { s.guideStrength = parseFloat(propStr.value); propStrVal.textContent = s.guideStrength.toFixed(2); commit(); }
});

// ── Zoom bar ─────────────────────────────────────────────────────────────────
const zoomCanvas = document.getElementById('zoom-bar');
const zctx       = zoomCanvas.getContext('2d');
let zbDrag = null;  // dragging the viewport handle: { mode:'viewport'|'left'|'right', startX, startVS, startVE }

function renderZoomBar() {
  const W  = zoomCanvas.parentElement.clientWidth;
  if (W < 1) return;
  zoomCanvas.width  = W;
  zoomCanvas.height = 28;
  const df = durF();

  // Background
  zctx.fillStyle = '#111';
  zctx.fillRect(0, 0, W, 28);

  // Mini segment bars (full timeline in miniature)
  function miniX(f) { return (f / df) * W; }
  segs.forEach(s => {
    zctx.fillStyle = s.type==='text' ? '#3a2e5a' : '#1a4a2a';
    zctx.fillRect(miniX(s.start), 8, Math.max(1, miniX(s.length)), 12);
  });
  audio.forEach(s => {
    zctx.fillStyle = '#142e4e';
    zctx.fillRect(miniX(s.start), 8, Math.max(1, miniX(s.length)), 8);
  });

  // Viewport rect
  const vs = (viewStart / df) * W;
  const ve = (viewEnd   / df) * W;
  const vw = Math.max(4, ve - vs);

  zctx.fillStyle = 'rgba(255,255,255,0.08)';
  zctx.fillRect(vs, 0, vw, 28);
  zctx.strokeStyle = 'rgba(255,255,255,0.35)';
  zctx.lineWidth = 1;
  zctx.strokeRect(vs + 0.5, 0.5, vw - 1, 27);

  // Resize grips on left/right edge
  zctx.fillStyle = 'rgba(255,255,255,0.55)';
  [[vs, 6, 3, 16], [vs + vw - 3, 6, 3, 16]].forEach(([x,y,w,h]) => {
    zctx.fillRect(x, y, w, h);
  });

  // Zoom percentage label
  const pct = Math.round((df / Math.max(1, viewEnd - viewStart)) * 100);
  zctx.fillStyle = '#666';
  zctx.font = '10px monospace';
  zctx.textBaseline = 'middle';
  zctx.textAlign    = 'right';
  zctx.fillText(pct + '%', W - 4, 14);
  zctx.textAlign = 'left';
  zctx.textBaseline = 'alphabetic';

  // Reset zoom hint (when zoomed in)
  if (viewStart > 0 || viewEnd < df - 0.5) {
    zctx.fillStyle = '#555';
    zctx.font = '10px sans-serif';
    zctx.textBaseline = 'middle';
    zctx.fillText('double-click to reset zoom', 6, 14);
    zctx.textBaseline = 'alphabetic';
  }
}

// Zoom bar interactions
zoomCanvas.addEventListener('dblclick', () => {
  viewStart = 0; viewEnd = durF(); render(); renderZoomBar();
});

function zbHitZone(mx) {
  const df = durF();
  const W  = zoomCanvas.width;
  const vs = (viewStart / df) * W;
  const ve = (viewEnd   / df) * W;
  const GRIP = 6;
  if (Math.abs(mx - vs) <= GRIP) return 'left';
  if (Math.abs(mx - ve) <= GRIP) return 'right';
  if (mx >= vs && mx <= ve)      return 'viewport';
  return 'seek';
}

zoomCanvas.addEventListener('mousemove', e => {
  const zone = zbHitZone(e.offsetX);
  zoomCanvas.style.cursor =
    zone==='left'||zone==='right' ? 'ew-resize' :
    zone==='viewport'             ? 'grab'       : 'pointer';
});

zoomCanvas.addEventListener('mousedown', e => {
  e.preventDefault();
  zbDrag = { mode: zbHitZone(e.offsetX), startX: e.offsetX, startVS: viewStart, startVE: viewEnd };
  if (zbDrag.mode === 'seek') {
    // Click outside viewport → jump view to click position
    const df   = durF();
    const span = viewSpan();
    const atF  = (e.offsetX / zoomCanvas.width) * df;
    viewStart  = clamp(atF - span/2, 0, df - span);
    viewEnd    = viewStart + span;
    render(); renderZoomBar();
    zbDrag = null;
  }
});

window.addEventListener('mousemove', e => {
  if (!zbDrag || zbDrag.mode==='seek') return;
  const df  = durF();
  const W   = zoomCanvas.width;
  const dx  = e.clientX - zoomCanvas.getBoundingClientRect().left - zbDrag.startX;
  const dF  = (dx / W) * df;

  if (zbDrag.mode==='viewport') {
    const span = zbDrag.startVE - zbDrag.startVS;
    viewStart = clamp(zbDrag.startVS + dF, 0, df - span);
    viewEnd   = viewStart + span;
  } else if (zbDrag.mode==='left') {
    viewStart = clamp(zbDrag.startVS + dF, 0, viewEnd - MIN_ZOOM_FRAMES);
  } else if (zbDrag.mode==='right') {
    viewEnd   = clamp(zbDrag.startVE + dF, viewStart + MIN_ZOOM_FRAMES, df);
  }
  render(); renderZoomBar();
});

window.addEventListener('mouseup', () => { zbDrag = null; });

// ── Commit: postMessage to Wan2GP parent ──────────────────────────────────
function commit() {
  const sorted = [...segs].sort((a,b) => a.start - b.start);
  const dF = durF();

  // Build local_prompts + segment_lengths
  let cursor=0, pendGap=0;
  const prompts=[], lengths=[];
  for (const s of sorted) {
    if (s.start >= dF) break;
    if (s.start > cursor) {
      const gap = Math.min(s.start, dF) - cursor;
      if (lengths.length) lengths[lengths.length-1] += gap; else pendGap += gap;
    }
    const clen = Math.min(s.start+s.length, dF) - s.start;
    lengths.push(clen + pendGap);
    prompts.push(s.prompt || '');
    pendGap = 0;
    cursor  = s.start + s.length;
  }
  // Pad last to fill duration
  if (lengths.length && Math.min(cursor,dF) < dF) {
    lengths[lengths.length-1] += dF - Math.min(cursor,dF);
  }

  const imgStrengths = sorted.filter(s => s.type!=='text').map(s => (s.guideStrength??1).toFixed(2));

  // Strip imgObj before serialising
  const toSave = {
    fps,
    durationSec: durSec,
    segments:      sorted.map(({imgObj,...r}) => r),
    audioSegments: audio.map(s => ({...s})),
  };

  window.parent.postMessage({
    source:          'wdc_ltx_director',
    timeline_data:    JSON.stringify(toSave),
    local_prompts:    prompts.join(' | '),
    segment_lengths:  lengths.join(','),
    guide_strength:   imgStrengths.join(','),
  }, '*');

  render();
  renderZoomBar();
}

function setStatus(msg) { statusEl.textContent = msg; }

// ── Inbound commands from the parent page ─────────────────────────────────
// The bridge JS sends postMessage({ source:'wdc_parent', cmd:... }) here.
// Without this listener, load/autosave/recover/clear all silently fail.
window.addEventListener('message', function(e) {
  const d = e.data;
  if (!d || d.source !== 'wdc_parent') return;

  if (d.cmd === 'get_state') {
    // Parent wants current state immediately (called before Apply/Preview)
    commit();

  } else if (d.cmd === 'clear') {
    // Parent clear button — wipe internal state and re-render
    segs = []; audio = []; selId = null;
    playhead = 0; playing = false;
    cancelAnimationFrame(rafId);
    btnPlay.textContent = '[Play]';
    updateProps();
    setStatus('Timeline cleared.');
    commit();

  } else if (d.cmd === 'restore' && d.data) {
    // Load / autosave restore.
    // d.data is the FULL session payload:
    //   { fps, duration_sec, global_prompt, epsilon, timeline: { segments, audioSegments } }
    // (The timeline sub-object may also be at the root for backwards compat.)
    try {
      const p = d.data;

      // ── Restore fps and duration from top-level fields ──────────────────
      // Note: the save format uses "duration_sec", not "durationSec"
      const newFps = parseInt(p.fps) || 24;
      const newDur = parseFloat(p.duration_sec || p.durationSec) || 5;
      fps    = newFps;
      durSec = newDur;
      document.getElementById('ctrl-fps').value = fps;
      document.getElementById('ctrl-dur').value = durSec;

      // Reset view to show full timeline
      viewStart = 0;
      viewEnd   = durF();

      // ── Find segments — may be nested under .timeline ───────────────────
      const src = (p.timeline && (p.timeline.segments || p.timeline.audioSegments))
                  ? p.timeline
                  : p;

      const rawSegs  = src.segments      || [];
      const rawAudio = src.audioSegments || [];

      // ── Restore audio (no async needed) ────────────────────────────────
      audio = rawAudio.map(function(s) {
        return {
          id:        s.id || uid(),
          type:      'audio',
          start:     parseInt(s.start)     || 0,
          length:    parseInt(s.length)    || Math.round(fps * 3),
          trimStart: parseInt(s.trimStart) || 0,
          audioB64:  s.audioB64  || '',
          fileName:  s.fileName  || 'audio',
        };
      });

      // ── Restore video segments, waiting for images to load ──────────────
      segs = [];
      let pending = 0;

      rawSegs.forEach(function(s) {
        const seg = {
          id:            s.id || uid(),
          type:          s.type || 'image',
          start:         parseInt(s.start)  || 0,
          length:        parseInt(s.length) || Math.round(fps * 2),
          prompt:        s.prompt           || '',
          guideStrength: parseFloat(s.guideStrength) || 1.0,
        };
        segs.push(seg);

        if (s.type === 'image' && s.imageB64) {
          seg.imageB64 = s.imageB64;
          pending++;
          const img = new Image();
          img.onload = function() {
            seg.imgObj = img;
            pending--;
            if (pending === 0) finalise();
          };
          img.onerror = function() {
            pending--;
            if (pending === 0) finalise();
          };
          img.src = s.imageB64;
        }
      });

      function finalise() {
        selId = null;
        updateProps();
        render();
        renderZoomBar();
        commit();
        setStatus('Restored: ' + segs.length + ' video segment(s), ' + audio.length + ' audio clip(s).');
      }

      // If no images to wait for, finalise immediately
      if (pending === 0) finalise();

    } catch(err) {
      console.error('[LTXDirector] restore error:', err);
      setStatus('Restore error: ' + err.message);
    }
  }
});

// ── Boot ─────────────────────────────────────────────────────────────────
resizeCanvas();
renderZoomBar();
new ResizeObserver(() => { renderZoomBar(); }).observe(document.getElementById('zoom-bar-wrap'));

// Notify parent of our height so iframe can auto-size
function notifyHeight() {
  window.parent.postMessage({ source:'wdc_ltx_director', height: document.body.scrollHeight }, '*');
}
window.addEventListener('load', notifyHeight);
new ResizeObserver(notifyHeight).observe(document.body);

})();
</script>
</body>
</html>
