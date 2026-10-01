import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Limpa scripts touch anteriores para evitar duplicidade
html = re.sub(r'<style>/\* Joystick Analógico.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<style>/\* Interface Touch.*?</script>', '', html, flags=re.DOTALL)

joystick_code = '''
<style>
  /* Joystick Analógico e Controles Touch Profissionais */
  #touch-canvas-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 99999;
    pointer-events: none;
    user-select: none;
    -webkit-user-select: none;
  }

  .action-btn {
    position: fixed;
    z-index: 100000;
    background: rgba(0, 0, 0, 0.6);
    border: 2px solid rgba(0, 255, 150, 0.6);
    color: #00ff96;
    font-weight: bold;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    user-select: none;
    -webkit-user-select: none;
    font-size: 12px;
    touch-action: manipulation;
  }
  .action-btn:active {
    background: rgba(0, 255, 150, 0.4);
    color: white;
  }

  #btn-subir { right: 20px; bottom: 120px; width: 60px; height: 60px; }
  #btn-descer { right: 20px; bottom: 45px; width: 60px; height: 60px; }
  #btn-disparo { right: 90px; bottom: 70px; width: 70px; height: 70px; border-color: #ff4444; color: #ff4444; }
  #btn-interagir { right: 90px; bottom: 150px; width: 55px; height: 55px; }
</style>

<div id="btn-subir" class="action-btn">SUBIR</div>
<div id="btn-descer" class="action-btn">DESCER</div>
<div id="btn-disparo" class="action-btn">FOGO</div>
<div id="btn-interagir" class="action-btn">E</div>

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

  const areaLeft = document.createElement('div');
  areaLeft.style.cssText = 'position:fixed; top:0; left:0; width:50vw; height:100vh; z-index:99998; touch-action:none;';
  
  const areaRight = document.createElement('div');
  areaRight.style.cssText = 'position:fixed; top:0; right:0; width:50vw; height:100vh; z-index:99998; touch-action:none;';

  document.body.appendChild(areaLeft);
  document.body.appendChild(areaRight);

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

  let joyTouchId = null;
  let joyBase = { x: 0, y: 0 };
  let joyStick = { x: 0, y: 0 };
  const maxRadius = 50;

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

        setKey('w', 'KeyW', dy < -15);
        setKey('s', 'KeyS', dy > 15);
        setKey('a', 'KeyA', dx < -15);
        setKey('d', 'KeyD', dx > 15);

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
    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.strokeStyle = 'rgba(0, 255, 150, 0.5)';
    ctx.lineWidth = 2;
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(joyStick.x, joyStick.y, 25, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 255, 150, 0.7)';
    ctx.fill();
  }

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
        const movementX = (touch.clientX - lastCamX) * 2.2;
        const movementY = (touch.clientY - lastCamY) * 2.2;
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

  function bindBtn(id, key, code) {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener('touchstart', (e) => { e.preventDefault(); setKey(key, code, true); });
    btn.addEventListener('touchend', (e) => { e.preventDefault(); setKey(key, code, false); });
  }

  bindBtn('btn-subir', ' ', 'Space');
  bindBtn('btn-descer', 'Shift', 'ShiftLeft');
  bindBtn('btn-interagir', 'e', 'KeyE');

  const btnFogo = document.getElementById('btn-disparo');
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

if '</body>' in html:
    html = html.replace('</body>', joystick_code + '\n</body>')
else:
    html += joystick_code

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Joystick e Câmera aplicados com sucesso sem erros!')
