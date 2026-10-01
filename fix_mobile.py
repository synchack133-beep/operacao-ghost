import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

viewport_tag = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">'

mobile_css = '''
<style>
  /* Força Tela Cheia Real no Celular */
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
    min-width: 100vw !important;
    min-height: 100vh !important;
    overflow: hidden !important;
    background: #050b08 !important;
    touch-action: none !important;
    user-select: none !important;
    -webkit-user-select: none !important;
  }

  /* Remove limites de largura fixos do container e do Canvas */
  #game-container, #canvas-container, canvas, .game-wrapper, main, body > div:not(#touch-hud-panel) {
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

  /* Ajusta o Modal do Menu para caber no celular */
  #modal, .modal, #menu, .menu-overlay, div[class*="modal"], div[class*="menu"] {
    max-width: 90vw !important;
    max-height: 90vh !important;
    overflow-y: auto !important;
    z-index: 2000000 !important;
  }

  /* Overlay de Controles Touch */
  #touch-canvas-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 999999;
    pointer-events: none;
  }

  .hud-touch-controls {
    position: fixed;
    bottom: 15px;
    right: 15px;
    z-index: 1000000;
    display: flex;
    gap: 10px;
    align-items: flex-end;
  }

  .hud-btn {
    background: rgba(8, 24, 18, 0.8);
    border: 1px solid rgba(0, 255, 150, 0.5);
    color: #00ff96;
    font-family: monospace;
    font-size: 11px;
    font-weight: bold;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    touch-action: none;
    backdrop-filter: blur(4px);
    box-shadow: 0 0 10px rgba(0, 255, 150, 0.2);
    user-select: none;
    -webkit-user-select: none;
  }

  .hud-btn:active {
    background: rgba(0, 255, 150, 0.5);
    color: #fff;
    transform: scale(0.92);
  }

  #btn-fogo { width: 60px; height: 60px; border-color: rgba(255, 65, 65, 0.7); color: #ff5555; font-size: 11px; }
  #btn-subir { width: 48px; height: 48px; }
  #btn-descer { width: 48px; height: 48px; }
  #btn-interagir { width: 42px; height: 42px; font-size: 10px; }
</style>

<div class="hud-touch-controls" id="touch-hud-panel">
  <div id="btn-interagir" class="hud-btn">E</div>
  <div id="btn-descer" class="hud-btn">▼</div>
  <div id="btn-subir" class="hud-btn">▲</div>
  <div id="btn-fogo" class="hud-btn">FOGO</div>
</div>

<script>
(function() {
  // Redimensiona o canvas quando girar a tela
  function fixCanvasSize() {
    const canvas = document.querySelector('canvas');
    if (canvas) {
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
      window.dispatchEvent(new Event('resize'));
    }
  }
  window.addEventListener('resize', fixCanvasSize);
  window.addEventListener('orientationchange', () => setTimeout(fixCanvasSize, 200));
  fixCanvasSize();

  const keys = { w: false, a: false, s: false, d: false };

  function setKey(key, code, state) {
    if (keys[key] === state) return;
    keys[key] = state;
    const type = state ? 'keydown' : 'keyup';
    const ev = new KeyboardEvent(type, { key: key, code: code, bubbles: true });
    window.dispatchEvent(ev);
    document.dispatchEvent(ev);
  }

  // Zonas de toque
  const areaLeft = document.createElement('div');
  areaLeft.style.cssText = 'position:fixed; top:0; left:0; width:50vw; height:100vh; z-index:999998; touch-action:none;';
  
  const areaRight = document.createElement('div');
  areaRight.style.cssText = 'position:fixed; top:0; right:0; width:50vw; height:100vh; z-index:999998; touch-action:none;';

  document.body.appendChild(areaLeft);
  document.body.appendChild(areaRight);

  // Overlay Canvas do Joystick
  const canvas = document.createElement('canvas');
  canvas.id = 'touch-canvas-overlay';
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });

  // Joystick Analógico
  let joyTouchId = null;
  let joyBase = { x: 0, y: 0 };
  let joyStick = { x: 0, y: 0 };
  const maxRadius = 45;

  areaLeft.addEventListener('touchstart', (e) => {
    if (joyTouchId !== null) return;
    const touch = e.changedTouches[0];
    joyTouchId = touch.identifier;
    joyBase = { x: touch.clientX, y: touch.clientY };
    joyStick = { x: touch.clientX, y: touch.clientY };
    drawJoystick();
  }, { passive: false });

  areaLeft.addEventListener('touchmove', (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === joyTouchId) {
        const touch = e.changedTouches[i];
        let dx = touch.clientX - joyBase.x;
        let dy = touch.clientY - joyBase.y;
        const dist = Math.hypot(dx, dy);

        if (dist > maxRadius) {
          dx = (dx / dist) * maxRadius;
          dy = (dy / dist) * maxRadius;
        }

        joyStick = { x: joyBase.x + dx, y: joyBase.y + dy };

        setKey('w', 'KeyW', dy < -12);
        setKey('s', 'KeyS', dy > 12);
        setKey('a', 'KeyA', dx < -12);
        setKey('d', 'KeyD', dx > 12);

        drawJoystick();
        break;
      }
    }
  }, { passive: false });

  const resetJoy = (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === joyTouchId) {
        joyTouchId = null;
        setKey('w', 'KeyW', false);
        setKey('s', 'KeyS', false);
        setKey('a', 'KeyA', false);
        setKey('d', 'KeyD', false);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        break;
      }
    }
  };

  areaLeft.addEventListener('touchend', resetJoy);
  areaLeft.addEventListener('touchcancel', resetJoy);

  function drawJoystick() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (joyTouchId === null) return;

    ctx.beginPath();
    ctx.arc(joyBase.x, joyBase.y, maxRadius, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 255, 150, 0.08)';
    ctx.strokeStyle = 'rgba(0, 255, 150, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(joyStick.x, joyStick.y, 20, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 255, 150, 0.6)';
    ctx.fill();
  }

  // Controle de Câmera (Lado Direito)
  let camTouchId = null;
  let lastCamX = 0, lastCamY = 0;

  areaRight.addEventListener('touchstart', (e) => {
    if (camTouchId !== null) return;
    const touch = e.changedTouches[0];
    camTouchId = touch.identifier;
    lastCamX = touch.clientX;
    lastCamY = touch.clientY;
  }, { passive: false });

  areaRight.addEventListener('touchmove', (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === camTouchId) {
        const touch = e.changedTouches[i];
        const movementX = (touch.clientX - lastCamX) * 1.8;
        const movementY = (touch.clientY - lastCamY) * 1.8;
        lastCamX = touch.clientX;
        lastCamY = touch.clientY;

        window.dispatchEvent(new MouseEvent('mousemove', {
          movementX: movementX,
          movementY: movementY,
          clientX: touch.clientX,
          clientY: touch.clientY,
          bubbles: true
        }));
        break;
      }
    }
  }, { passive: false });

  const resetCam = (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === camTouchId) {
        camTouchId = null;
        break;
      }
    }
  };

  areaRight.addEventListener('touchend', resetCam);
  areaRight.addEventListener('touchcancel', resetCam);

  // Mapeamento dos Botões
  function bindBtn(id, key, code) {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener('touchstart', (e) => { e.preventDefault(); setKey(key, code, true); });
    btn.addEventListener('touchend', (e) => { e.preventDefault(); setKey(key, code, false); });
  }

  bindBtn('btn-subir', ' ', 'Space');
  bindBtn('btn-descer', 'Shift', 'ShiftLeft');
  bindBtn('btn-interagir', 'e', 'KeyE');

  const btnFogo = document.getElementById('btn-fogo');
  if (btnFogo) {
    btnFogo.addEventListener('touchstart', (e) => {
      e.preventDefault();
      window.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, button: 0 }));
    });
    btnFogo.addEventListener('touchend', (e) => {
      e.preventDefault();
      window.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, button: 0 }));
    });
  }
})();
</script>
'''

if '<head>' in html:
    html = html.replace('<head>', '<head>\n' + viewport_tag)

if '</body>' in html:
    html = html.replace('</body>', mobile_css + '\n</body>')
else:
    html += mobile_css

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Ajuste de Tela Cheia e HUD Mobile aplicados com sucesso!')
