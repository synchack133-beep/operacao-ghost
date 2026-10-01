import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Garante a tag viewport para celular
if 'viewport-fit=cover' not in html:
    viewport = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">'
    if '<head>' in html:
        html = html.replace('<head>', '<head>\n  ' + viewport)

css_and_js = '''
<style>
/* --- TELA CHEIA E SUPORTE A CELULAR --- */
html, body {
  margin: 0 !important;
  padding: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  overflow: hidden !important;
  background: #050b08 !important;
  touch-action: none !important;
  user-select: none !important;
  -webkit-user-select: none !important;
}

canvas:not(#touch-canvas) {
  width: 100vw !important;
  height: 100vh !important;
  display: block !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
}

#game-container, #canvas-container, .game-wrapper, main {
  width: 100vw !important;
  height: 100vh !important;
  max-width: none !important;
  max-height: none !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* --- PAINEL DE MENU COMPACTO EM MODO HORIZONTAL --- */
#modal, .modal, #start-screen, #briefing, div[class*="modal"], div[id*="modal"] {
  position: fixed !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  width: 90vw !important;
  max-width: 460px !important;
  max-height: 85vh !important;
  overflow-y: auto !important;
  padding: 10px 14px !important;
  box-sizing: border-box !important;
  background: rgba(4, 16, 11, 0.96) !important;
  border: 1px solid #00ff96 !important;
  box-shadow: 0 0 20px rgba(0, 255, 150, 0.3) !important;
  border-radius: 8px !important;
  z-index: 9999999 !important;
}

/* Redução dos textos para caber na horizontal */
#modal h1, .modal h1, h1 { font-size: clamp(14px, 4vh, 18px) !important; margin: 2px 0 4px 0 !important; }
#modal h2, .modal h2, h2 { font-size: clamp(12px, 3vh, 15px) !important; margin: 2px 0 4px 0 !important; }
#modal p, .modal p, p { font-size: clamp(10px, 2.5vh, 12px) !important; line-height: 1.2 !important; margin: 3px 0 !important; }

/* Botões INICIAR MISSÃO e COMO JOGAR bem visíveis */
#modal button, .modal button, button, .btn {
  display: inline-block !important;
  padding: 7px 16px !important;
  font-size: clamp(11px, 2.8vh, 13px) !important;
  font-weight: bold !important;
  margin: 6px 4px 2px 4px !important;
  background: #00ff96 !important;
  color: #020c07 !important;
  border: none !important;
  border-radius: 4px !important;
  cursor: pointer !important;
  box-shadow: 0 0 10px rgba(0, 255, 150, 0.5) !important;
}

/* --- OVERLAY DOS BOTÕES TOUCH --- */
#hud-touch-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 99999;
  pointer-events: none;
  display: none;
}

#touch-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
}

.touch-controls-group {
  position: absolute;
  bottom: 15px;
  right: 15px;
  pointer-events: auto;
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.t-btn {
  background: rgba(5, 20, 14, 0.85);
  border: 1.5px solid rgba(0, 255, 150, 0.6);
  color: #00ff96;
  font-family: monospace;
  font-weight: bold;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}
.t-btn:active { background: rgba(0, 255, 150, 0.5); color: #fff; }
#tb-fire { width: 60px; height: 60px; border-color: #ff4444; color: #ff5555; font-size: 11px; }
#tb-up { width: 46px; height: 46px; font-size: 15px; }
#tb-down { width: 46px; height: 46px; font-size: 15px; }
#tb-use { width: 40px; height: 40px; font-size: 11px; }
</style>

<div id="hud-touch-layer">
  <canvas id="touch-canvas"></canvas>
  <div class="touch-controls-group">
    <div id="tb-use" class="t-btn">E</div>
    <div id="tb-down" class="t-btn">▼</div>
    <div id="tb-up" class="t-btn">▲</div>
    <div id="tb-fire" class="t-btn">FOGO</div>
  </div>
</div>

<script>
(function() {
  Element.prototype.requestPointerLock = function() { return Promise.resolve(); };

  function fitCanvas() {
    const c = document.querySelector('canvas:not(#touch-canvas)');
    if (c) {
      c.style.width = window.innerWidth + 'px';
      c.style.height = window.innerHeight + 'px';
    }
    const tc = document.getElementById('touch-canvas');
    if (tc) {
      tc.width = window.innerWidth;
      tc.height = window.innerHeight;
    }
    window.dispatchEvent(new Event('resize'));
  }
  window.addEventListener('resize', fitCanvas);
  window.addEventListener('orientationchange', () => setTimeout(fitCanvas, 200));

  const hudLayer = document.getElementById('hud-touch-layer');
  document.addEventListener('click', function(e) {
    const text = (e.target.innerText || e.target.textContent || '').toUpperCase();
    if (text.includes('INICIAR') || text.includes('START') || text.includes('JOGAR')) {
      if (hudLayer) hudLayer.style.display = 'block';
      setTimeout(fitCanvas, 100);
    }
  }, true);

  const leftZone = document.createElement('div');
  leftZone.style.cssText = 'position:fixed; top:0; left:0; width:50vw; height:100vh; z-index:99998; touch-action:none;';
  const rightZone = document.createElement('div');
  rightZone.style.cssText = 'position:fixed; top:0; right:0; width:50vw; height:100vh; z-index:99998; touch-action:none;';
  document.body.appendChild(leftZone);
  document.body.appendChild(rightZone);

  const keys = { w: false, a: false, s: false, d: false };
  function sendKey(key, code, down) {
    if (keys[key] === down) return;
    keys[key] = down;
    const ev = new KeyboardEvent(down ? 'keydown' : 'keyup', { key: key, code: code, bubbles: true });
    window.dispatchEvent(ev);
    document.dispatchEvent(ev);
  }

  const tc = document.getElementById('touch-canvas');
  const ctx = tc ? tc.getContext('2d') : null;
  let jId = null, jBase = {x:0, y:0}, jStick = {x:0, y:0};
  const maxR = 40;

  leftZone.addEventListener('touchstart', (e) => {
    if (jId !== null) return;
    const t = e.changedTouches[0];
    jId = t.identifier;
    jBase = { x: t.clientX, y: t.clientY };
    jStick = { x: t.clientX, y: t.clientY };
    renderJoy();
  }, { passive: false });

  leftZone.addEventListener('touchmove', (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === jId) {
        const t = e.changedTouches[i];
        let dx = t.clientX - jBase.x;
        let dy = t.clientY - jBase.y;
        const dist = Math.hypot(dx, dy);
        if (dist > maxR) { dx = (dx / dist) * maxR; dy = (dy / dist) * maxR; }
        jStick = { x: jBase.x + dx, y: jBase.y + dy };

        sendKey('w', 'KeyW', dy < -10);
        sendKey('s', 'KeyS', dy > 10);
        sendKey('a', 'KeyA', dx < -10);
        sendKey('d', 'KeyD', dx > 10);

        renderJoy();
        break;
      }
    }
  }, { passive: false });

  const endJoy = (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === jId) {
        jId = null;
        sendKey('w', 'KeyW', false); sendKey('s', 'KeyS', false);
        sendKey('a', 'KeyA', false); sendKey('d', 'KeyD', false);
        if (ctx) ctx.clearRect(0, 0, tc.width, tc.height);
        break;
      }
    }
  };
  leftZone.addEventListener('touchend', endJoy);
  leftZone.addEventListener('touchcancel', endJoy);

  function renderJoy() {
    if (!ctx || jId === null) return;
    ctx.clearRect(0, 0, tc.width, tc.height);
    ctx.beginPath();
    ctx.arc(jBase.x, jBase.y, maxR, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0,255,150,0.1)';
    ctx.strokeStyle = 'rgba(0,255,150,0.5)';
    ctx.lineWidth = 2;
    ctx.fill(); ctx.stroke();
    ctx.beginPath();
    ctx.arc(jStick.x, jStick.y, 18, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0,255,150,0.7)';
    ctx.fill();
  }

  let cId = null, lastX = 0, lastY = 0;
  rightZone.addEventListener('touchstart', (e) => {
    if (cId !== null) return;
    const t = e.changedTouches[0];
    cId = t.identifier; lastX = t.clientX; lastY = t.clientY;
  }, { passive: false });

  rightZone.addEventListener('touchmove', (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === cId) {
        const t = e.changedTouches[i];
        const dx = (t.clientX - lastX) * 2;
        const dy = (t.clientY - lastY) * 2;
        lastX = t.clientX; lastY = t.clientY;
        window.dispatchEvent(new MouseEvent('mousemove', { movementX: dx, movementY: dy, bubbles: true }));
        break;
      }
    }
  }, { passive: false });

  const endCam = (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === cId) { cId = null; break; }
    }
  };
  rightZone.addEventListener('touchend', endCam);
  rightZone.addEventListener('touchcancel', endCam);

  function bindAction(id, key, code) {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener('touchstart', (e) => { e.preventDefault(); sendKey(key, code, true); });
    btn.addEventListener('touchend', (e) => { e.preventDefault(); sendKey(key, code, false); });
  }
  bindAction('tb-up', ' ', 'Space');
  bindAction('tb-down', 'Shift', 'ShiftLeft');
  bindAction('tb-use', 'e', 'KeyE');

  const fBtn = document.getElementById('tb-fire');
  if (fBtn) {
    fBtn.addEventListener('touchstart', (e) => {
      e.preventDefault();
      window.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, button: 0 }));
    });
    fBtn.addEventListener('touchend', (e) => {
      e.preventDefault();
      window.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, button: 0 }));
    });
  }
})();
</script>
'''

if '</body>' in html:
    html = html.replace('</body>', css_and_js + '\n</body>')
else:
    html += css_and_js

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Ajuste limpo e correto aplicado!")
