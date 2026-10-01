import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Configuração de Viewport para Tela Cheia no Celular
viewport = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">'
if '<head>' in html and 'viewport-fit=cover' not in html:
    html = html.replace('<head>', '<head>\n  ' + viewport)

# Código completo de correção CSS e JS
injected_code = '''
<style>
/* 1. TELA CHEIA REAL SEM BORDAS PRETAS */
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
  -webkit-touch-callout: none !important;
}

#game-container, #canvas-container, canvas, .game-wrapper, main, body > div:not(#mobile-hud-root) {
  width: 100vw !important;
  height: 100vh !important;
  max-width: 100vw !important;
  max-height: 100vh !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  box-sizing: border-box !important;
}

/* 2. ADAPTAÇÃO RESPONSIVA DO MENU DE INÍCIO */
#modal, .modal, #menu, .menu-overlay, div[class*="modal"], div[class*="menu"], #start-screen, .start-screen {
  position: fixed !important;
  z-index: 10000000 !important;
  max-width: 92vw !important;
  max-height: 88vh !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  padding: 16px !important;
  box-sizing: border-box !important;
  overflow-y: auto !important;
  background: rgba(5, 18, 12, 0.94) !important;
  border: 1px solid rgba(0, 255, 150, 0.4) !important;
  box-shadow: 0 0 25px rgba(0, 255, 150, 0.25) !important;
  border-radius: 8px !important;
}

#modal h1, #modal h2, .modal h1, .modal h2 { font-size: clamp(16px, 4vw, 24px) !important; }
#modal p, .modal p { font-size: clamp(11px, 2.5vw, 14px) !important; line-height: 1.3 !important; }
#modal button, .modal button, .btn { padding: 10px 18px !important; font-size: clamp(12px, 3vw, 15px) !important; margin: 5px !important; }

/* 3. INTERFACE TOUCH E BOTÕES TÁTICOS */
#mobile-hud-root {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 999999;
  pointer-events: none;
  display: none;
}

#touch-overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
}

.hud-btn-cluster {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 180px;
  height: 180px;
  pointer-events: auto;
}

.hud-btn {
  position: absolute;
  background: rgba(5, 20, 14, 0.75);
  border: 1.5px solid rgba(0, 255, 150, 0.5);
  color: #00ff96;
  font-family: monospace, sans-serif;
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
  background: rgba(0, 255, 150, 0.4);
  color: #ffffff;
  transform: scale(0.92);
}

#btn-fogo { right: 0; bottom: 0; width: 65px; height: 65px; border-color: rgba(255, 60, 60, 0.8); color: #ff5555; font-size: 11px; }
#btn-subir { right: 10px; bottom: 80px; width: 50px; height: 50px; font-size: 16px; }
#btn-descer { right: 80px; bottom: 10px; width: 50px; height: 50px; font-size: 16px; }
#btn-interagir { right: 75px; bottom: 75px; width: 44px; height: 44px; font-size: 12px; }
</style>

<div id="mobile-hud-root">
  <canvas id="touch-overlay-canvas"></canvas>
  <div class="hud-btn-cluster">
    <div id="btn-interagir" class="hud-btn">E</div>
    <div id="btn-subir" class="hud-btn">▲</div>
    <div id="btn-descer" class="hud-btn">▼</div>
    <div id="btn-fogo" class="hud-btn">FOGO</div>
  </div>
</div>

<script>
(function() {
  // Ignora chamadas de PointerLock que exibem avisos no navegador
  Element.prototype.requestPointerLock = function() { return Promise.resolve(); };
  document.exitPointerLock = function() {};

  // Força o Three.js a aceitar movimentação de câmera por toque
  function patchPointerLockControls() {
    if (window.THREE && THREE.PointerLockControls) {
      const origOnMouseMove = THREE.PointerLockControls.prototype.onMouseMove;
      THREE.PointerLockControls.prototype.onMouseMove = function(event) {
        const wasLocked = this.isLocked;
        this.isLocked = true;
        origOnMouseMove.call(this, event);
        this.isLocked = wasLocked;
      };
    }
  }
  patchPointerLockControls();
  window.addEventListener('DOMContentLoaded', patchPointerLockControls);

  // Redimensionamento do Canvas
  function resizeGame() {
    const canvas = document.querySelector('canvas:not(#touch-overlay-canvas)');
    if (canvas) {
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
    }
    const hudCanvas = document.getElementById('touch-overlay-canvas');
    if (hudCanvas) {
      hudCanvas.width = window.innerWidth;
      hudCanvas.height = window.innerHeight;
    }
    window.dispatchEvent(new Event('resize'));
  }

  window.addEventListener('resize', resizeGame);
  window.addEventListener('orientationchange', () => setTimeout(resizeGame, 200));

  // Ativa os controles ao clicar em "INICIAR MISSÃO"
  const hudRoot = document.getElementById('mobile-hud-root');
  document.addEventListener('click', function(e) {
    const txt = (e.target.innerText || e.target.textContent || '').toUpperCase();
    if (txt.includes('INICIAR') || txt.includes('START') || e.target.id === 'start-btn') {
      if (hudRoot) hudRoot.style.display = 'block';
      resizeGame();
    }
  }, true);

  // Áreas Touch (Esquerda = Joystick / Direita = Câmera)
  const leftZone = document.createElement('div');
  leftZone.style.cssText = 'position:fixed; top:0; left:0; width:50vw; height:100vh; z-index:999998; touch-action:none;';

  const rightZone = document.createElement('div');
  rightZone.style.cssText = 'position:fixed; top:0; right:0; width:50vw; height:100vh; z-index:999998; touch-action:none;';

  document.body.appendChild(leftZone);
  document.body.appendChild(rightZone);

  // Simulação de Teclado (WASD)
  const activeKeys = { w: false, a: false, s: false, d: false };
  function setKeyState(key, code, isPressed) {
    if (activeKeys[key] === isPressed) return;
    activeKeys[key] = isPressed;
    const type = isPressed ? 'keydown' : 'keyup';
    const ev = new KeyboardEvent(type, { key: key, code: code, bubbles: true, cancelable: true });
    window.dispatchEvent(ev);
    document.dispatchEvent(ev);
  }

  // Joystick Analógico Dinâmico (Lado Esquerdo)
  const hudCanvas = document.getElementById('touch-overlay-canvas');
  const ctx = hudCanvas ? hudCanvas.getContext('2d') : null;
  let joyTouchId = null;
  let joyBase = { x: 0, y: 0 };
  let joyStick = { x: 0, y: 0 };
  const maxRadius = 45;

  leftZone.addEventListener('touchstart', (e) => {
    if (joyTouchId !== null) return;
    const touch = e.changedTouches[0];
    joyTouchId = touch.identifier;
    joyBase = { x: touch.clientX, y: touch.clientY };
    joyStick = { x: touch.clientX, y: touch.clientY };
    drawJoystick();
  }, { passive: false });

  leftZone.addEventListener('touchmove', (e) => {
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

        setKeyState('w', 'KeyW', dy < -12);
        setKeyState('s', 'KeyS', dy > 12);
        setKeyState('a', 'KeyA', dx < -12);
        setKeyState('d', 'KeyD', dx > 12);

        drawJoystick();
        break;
      }
    }
  }, { passive: false });

  const releaseJoystick = (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === joyTouchId) {
        joyTouchId = null;
        setKeyState('w', 'KeyW', false);
        setKeyState('s', 'KeyS', false);
        setKeyState('a', 'KeyA', false);
        setKeyState('d', 'KeyD', false);
        if (ctx) ctx.clearRect(0, 0, hudCanvas.width, hudCanvas.height);
        break;
      }
    }
  };

  leftZone.addEventListener('touchend', releaseJoystick);
  leftZone.addEventListener('touchcancel', releaseJoystick);

  function drawJoystick() {
    if (!ctx || joyTouchId === null) return;
    ctx.clearRect(0, 0, hudCanvas.width, hudCanvas.height);

    ctx.beginPath();
    ctx.arc(joyBase.x, joyBase.y, maxRadius, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 255, 150, 0.08)';
    ctx.strokeStyle = 'rgba(0, 255, 150, 0.4)';
    ctx.lineWidth = 2;
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(joyStick.x, joyStick.y, 22, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 255, 150, 0.65)';
    ctx.fill();
  }

  // Rotação da Câmera (Lado Direito)
  let camTouchId = null;
  let lastCamX = 0, lastCamY = 0;

  rightZone.addEventListener('touchstart', (e) => {
    if (camTouchId !== null) return;
    const touch = e.changedTouches[0];
    camTouchId = touch.identifier;
    lastCamX = touch.clientX;
    lastCamY = touch.clientY;
  }, { passive: false });

  rightZone.addEventListener('touchmove', (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === camTouchId) {
        const touch = e.changedTouches[i];
        const deltaX = (touch.clientX - lastCamX) * 2.2;
        const deltaY = (touch.clientY - lastCamY) * 2.2;
        lastCamX = touch.clientX;
        lastCamY = touch.clientY;

        window.dispatchEvent(new MouseEvent('mousemove', {
          movementX: deltaX,
          movementY: deltaY,
          clientX: touch.clientX,
          clientY: touch.clientY,
          bubbles: true
        }));
        break;
      }
    }
  }, { passive: false });

  const releaseCamera = (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === camTouchId) {
        camTouchId = null;
        break;
      }
    }
  };

  rightZone.addEventListener('touchend', releaseCamera);
  rightZone.addEventListener('touchcancel', releaseCamera);

  // Mapeamento dos Botões de Ação
  function bindTouchBtn(id, key, code) {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener('touchstart', (e) => { e.preventDefault(); setKeyState(key, code, true); });
    btn.addEventListener('touchend', (e) => { e.preventDefault(); setKeyState(key, code, false); });
  }

  bindTouchBtn('btn-subir', ' ', 'Space');
  bindTouchBtn('btn-descer', 'Shift', 'ShiftLeft');
  bindTouchBtn('btn-interagir', 'e', 'KeyE');

  const fireBtn = document.getElementById('btn-fogo');
  if (fireBtn) {
    fireBtn.addEventListener('touchstart', (e) => {
      e.preventDefault();
      window.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, button: 0 }));
    });
    fireBtn.addEventListener('touchend', (e) => {
      e.preventDefault();
      window.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, button: 0 }));
    });
  }
})();
</script>
'''

if '</body>' in html:
    html = html.replace('</body>', injected_code + '\n</body>')
else:
    html += injected_code

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('REPARO CONCLUÍDO COM SUCESSO!')
