import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Meta para travar zoom e preencher a tela inteira do celular
meta_viewport = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">'

# CSS de redimensionamento e botões táticos discretos
css_code = '''
<style>
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

  canvas {
    width: 100vw !important;
    height: 100vh !important;
    display: block !important;
    object-fit: contain !important;
  }

  /* Overlay de controles táticos minimalistas */
  #touch-canvas-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 999999;
    pointer-events: none;
  }

  .hud-btn {
    position: fixed;
    z-index: 1000000;
    background: rgba(8, 24, 18, 0.7);
    border: 1px solid rgba(0, 255, 150, 0.4);
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
    box-shadow: 0 0 8px rgba(0, 255, 150, 0.15);
  }

  .hud-btn:active {
    background: rgba(0, 255, 150, 0.4);
    color: #fff;
    transform: scale(0.92);
  }

  #btn-fogo { right: 25px; bottom: 30px; width: 62px; height: 62px; border-color: rgba(255, 60, 60, 0.6); color: #ff5555; }
  #btn-subir { right: 25px; bottom: 105px; width: 48px; height: 48px; }
  #btn-descer { right: 85px; bottom: 30px; width: 48px; height: 48px; }
  #btn-interagir { right: 85px; bottom: 90px; width: 42px; height: 42px; font-size: 10px; }
</style>

<div id="btn-fogo" class="hud-btn">FOGO</div>
<div id="btn-subir" class="hud-btn">▲</div>
<div id="btn-descer" class="hud-btn">▼</div>
<div id="btn-interagir" class="hud-btn">E</div>

<script>
(function() {
  const keys = { w: false, a: false, s: false, d: false };

  function setKey(key, code, state) {
    if (keys[key] === state) return;
    keys[key] = state;
    const type = state ? 'keydown' : 'keyup';
    const ev = new KeyboardEvent(type, { key: key, code: code, bubbles: true });
    window.dispatchEvent(ev);
    document.dispatchEvent(ev);
  }

  // Zonas touch
  const areaLeft = document.createElement('div');
  areaLeft.style.cssText = 'position:fixed; top:0; left:0; width:50vw; height:100vh; z-index:999998; touch-action:none;';
  
  const areaRight = document.createElement('div');
  areaRight.style.cssText = 'position:fixed; top:0; right:0; width:50vw; height:100vh; z-index:999998; touch-action:none;';

  document.body.appendChild(areaLeft);
  document.body.appendChild(areaRight);

  // Canvas Overlay
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

  // Joystick Análogo Dinâmico
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
    ctx.fillStyle = 'rgba(0, 255, 150, 0.05)';
    ctx.strokeStyle = 'rgba(0, 255, 150, 0.3)';
    ctx.lineWidth = 1.5;
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(joyStick.x, joyStick.y, 20, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 255, 150, 0.5)';
    ctx.fill();
  }

  // Rotação de Câmera
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

  // Mapeamento dos Botões HUD
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
    html = html.replace('<head>', '<head>\n' + meta_viewport)

if '</body>' in html:
    html = html.replace('</body>', css_code + '\n</body>')
else:
    html += css_code

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Interface tática e encaixe de tela aplicados com sucesso!')
