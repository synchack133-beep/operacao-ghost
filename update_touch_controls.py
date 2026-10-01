import os

# 1. NOVO CONTROLLER DE JOYSTICKS MULTI-TOUCH (src/controls/Joystick.js)
os.makedirs('src/controls', exist_ok=True)
joystick_code = '''export class JoystickController {
  constructor(options) {
    this.leftZone = document.getElementById(options.leftZoneId);
    this.rightZone = document.getElementById(options.rightZoneId);
    this.leftStick = document.getElementById(options.leftStickId);
    this.rightStick = document.getElementById(options.rightStickId);

    this.leftTouchId = null;
    this.rightTouchId = null;

    this.leftOrigin = { x: 0, y: 0 };
    this.rightOrigin = { x: 0, y: 0 };

    this.input = {
      throttle: 0, // Y esquerdo (-1 a 1)
      yaw: 0,      // X esquerdo (-1 a 1)
      pitch: 0,    // Y direito (-1 a 1)
      roll: 0      // X direito (-1 a 1)
    };

    this.maxRadius = 42; // Limite do analógico
    this.init();
  }

  init() {
    window.addEventListener('touchstart', (e) => this.onTouchStart(e), { passive: false });
    window.addEventListener('touchmove', (e) => this.onTouchMove(e), { passive: false });
    window.addEventListener('touchend', (e) => this.onTouchEnd(e), { passive: false });
    window.addEventListener('touchcancel', (e) => this.onTouchEnd(e), { passive: false });
  }

  onTouchStart(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      const target = document.elementFromPoint(touch.clientX, touch.clientY);
      
      if (target && target.closest('#btn-shoot, #btn-fullscreen, #btn-nightvision, .btn-main')) {
        continue; // Permite o disparo sem travar o analógico
      }

      const rectLeft = this.leftZone.getBoundingClientRect();
      const rectRight = this.rightZone.getBoundingClientRect();

      // Analógico Esquerdo (Subir/Descer + Girar)
      if (this.leftTouchId === null && 
          touch.clientX >= rectLeft.left && touch.clientX <= rectLeft.right &&
          touch.clientY >= rectLeft.top && touch.clientY <= rectLeft.bottom) {
        this.leftTouchId = touch.identifier;
        this.leftOrigin = { x: rectLeft.left + rectLeft.width / 2, y: rectLeft.top + rectLeft.height / 2 };
        this.updateLeft(touch.clientX, touch.clientY);
        e.preventDefault();
      }
      // Analógico Direito (Avançar/Recuar + Esquerda/Direita)
      else if (this.rightTouchId === null && 
               touch.clientX >= rectRight.left && touch.clientX <= rectRight.right &&
               touch.clientY >= rectRight.top && touch.clientY <= rectRight.bottom) {
        this.rightTouchId = touch.identifier;
        this.rightOrigin = { x: rectRight.left + rectRight.width / 2, y: rectRight.top + rectRight.height / 2 };
        this.updateRight(touch.clientX, touch.clientY);
        e.preventDefault();
      }
    }
  }

  onTouchMove(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      if (touch.identifier === this.leftTouchId) {
        this.updateLeft(touch.clientX, touch.clientY);
        e.preventDefault();
      } else if (touch.identifier === this.rightTouchId) {
        this.updateRight(touch.clientX, touch.clientY);
        e.preventDefault();
      }
    }
  }

  onTouchEnd(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      if (touch.identifier === this.leftTouchId) {
        this.leftTouchId = null;
        this.input.throttle = 0;
        this.input.yaw = 0;
        this.leftStick.style.transform = `translate(0px, 0px)`;
      } else if (touch.identifier === this.rightTouchId) {
        this.rightTouchId = null;
        this.input.pitch = 0;
        this.input.roll = 0;
        this.rightStick.style.transform = `translate(0px, 0px)`;
      }
    }
  }

  updateLeft(x, y) {
    let dx = x - this.leftOrigin.x;
    let dy = y - this.leftOrigin.y;
    let dist = Math.hypot(dx, dy);

    if (dist > this.maxRadius) {
      dx = (dx / dist) * this.maxRadius;
      dy = (dy / dist) * this.maxRadius;
    }

    this.leftStick.style.transform = `translate(${dx}px, ${dy}px)`;
    this.input.yaw = dx / this.maxRadius;
    this.input.throttle = -dy / this.maxRadius; // Empurrar para cima = subir
  }

  updateRight(x, y) {
    let dx = x - this.rightOrigin.x;
    let dy = y - this.rightOrigin.y;
    let dist = Math.hypot(dx, dy);

    if (dist > this.maxRadius) {
      dx = (dx / dist) * this.maxRadius;
      dy = (dy / dist) * this.maxRadius;
    }

    this.rightStick.style.transform = `translate(${dx}px, ${dy}px)`;
    this.input.roll = dx / this.maxRadius;
    this.input.pitch = -dy / this.maxRadius; // Empurrar para cima = frente
  }
}
'''

with open('src/controls/Joystick.js', 'w', encoding='utf-8') as f:
    f.write(joystick_code)

# 2. FÍSICA DE VOO DO DRONE (src/entities/Player.js)
player_code = '''import * as THREE from 'three';

export class Player {
  constructor(scene, camera) {
    this.scene = scene;
    this.camera = camera;
    
    this.mesh = new THREE.Group();
    
    // Corpo do Drone 3D estilo Tático
    const bodyGeo = new THREE.BoxGeometry(0.9, 0.2, 0.9);
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0x00ff96, wireframe: true });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    this.mesh.add(body);

    // Hélices nas pontas
    const propGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.05, 8);
    const propMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, wireframe: true });
    const offsets = [
      { x: 0.6, z: 0.6 }, { x: -0.6, z: 0.6 },
      { x: 0.6, z: -0.6 }, { x: -0.6, z: -0.6 }
    ];

    this.props = [];
    offsets.forEach(off => {
      const p = new THREE.Mesh(propGeo, propMat);
      p.position.set(off.x, 0.15, off.z);
      this.mesh.add(p);
      this.props.push(p);
    });

    this.mesh.position.set(0, 3, 0);
    this.scene.add(this.mesh);

    this.health = 100;
    this.battery = 100;
    this.velocity = new THREE.Vector3();

    this.moveSpeed = 18.0;
    this.turnSpeed = 2.4;
    this.verticalSpeed = 12.0;
  }

  get position() { return this.mesh.position; }

  getForwardDirection() {
    const dir = new THREE.Vector3(0, 0, -1);
    dir.applyQuaternion(this.mesh.quaternion);
    return dir;
  }

  update(delta, input) {
    if (this.battery > 0) {
      this.battery -= delta * 0.25;
    }

    // 1. Giro (Yaw)
    if (Math.abs(input.yaw) > 0.05) {
      this.mesh.rotation.y -= input.yaw * this.turnSpeed * delta;
    }

    // 2. Altitude (Throttle)
    if (Math.abs(input.throttle) > 0.05) {
      this.mesh.position.y += input.throttle * this.verticalSpeed * delta;
      this.mesh.position.y = Math.max(1.0, Math.min(35.0, this.mesh.position.y));
    }

    // 3. Movimento Relativo de Voo (Pitch & Roll)
    const moveDir = new THREE.Vector3(input.roll, 0, -input.pitch);
    if (moveDir.lengthSq() > 0.002) {
      moveDir.clampLength(0, 1);
      moveDir.applyQuaternion(this.mesh.quaternion);
      this.mesh.position.addScaledVector(moveDir, this.moveSpeed * delta);
    }

    // Animação das Hélices
    this.props.forEach(p => p.rotation.y += 0.4);

    // Inclinação visual dinâmica ao voar (Tilt Effect)
    this.mesh.rotation.z = THREE.MathUtils.lerp(this.mesh.rotation.z, -input.roll * 0.35, delta * 10);
    this.mesh.rotation.x = THREE.MathUtils.lerp(this.mesh.rotation.x, input.pitch * 0.3, delta * 10);

    // Posicionamento suave da câmera atrás do drone
    const camOffset = new THREE.Vector3(0, 1.4, 3.8).applyQuaternion(this.mesh.quaternion);
    this.camera.position.lerp(this.mesh.position.clone().add(camOffset), delta * 14);
    const lookTarget = this.mesh.position.clone().add(this.getForwardDirection().multiplyScalar(10));
    this.camera.lookAt(lookTarget);
  }

  reset() {
    this.mesh.position.set(0, 3, 0);
    this.mesh.rotation.set(0, 0, 0);
    this.health = 100;
    this.battery = 100;
  }
}
'''

with open('src/entities/Player.js', 'w', encoding='utf-8') as f:
    f.write(player_code)

# 3. INTERFACE REFORMULADA COM JOYSTICKS NEON (index.html)
index_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <title>OPERAÇÃO GHOST — DRONE WARFARE</title>
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; touch-action: none; }
    html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; color: #00ff96; }
    #canvas-container { width: 100%; height: 100%; position: absolute; top:0; left:0; z-index: 1; }

    #hud { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10; pointer-events: none; display: flex; flex-direction: column; justify-content: space-between; padding: max(10px, env(safe-area-inset-top)) max(10px, env(safe-area-inset-right)) max(10px, env(safe-area-inset-bottom)) max(10px, env(safe-area-inset-left)); }
    .hud-header { display: flex; justify-content: space-between; align-items: flex-start; background: rgba(0, 20, 10, 0.85); padding: 8px 12px; border: 1px solid rgba(0, 255, 150, 0.5); border-radius: 6px; backdrop-filter: blur(4px); }
    .bar-container { width: 110px; height: 8px; background: rgba(0, 50, 25, 0.8); border: 1px solid #00ff96; margin-top: 3px; border-radius: 3px; overflow: hidden; }
    .bar-fill { height: 100%; background: #00ff96; width: 100%; transition: width 0.1s ease; }
    .bar-fill.battery { background: #00ccff; }

    #crosshair { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 30px; height: 30px; pointer-events: none; z-index: 11; }
    #crosshair::before, #crosshair::after { content: ''; position: absolute; background: rgba(0,255,150,0.8); }
    #crosshair::before { top: 14px; left: 0; width: 30px; height: 2px; }
    #crosshair::after { top: 0; left: 14px; width: 2px; height: 30px; }

    #radar-canvas { width: 75px; height: 75px; border-radius: 50%; border: 2px solid #00ff96; background: rgba(0,20,10,0.85); }

    /* JOYSTICKS VIRTUAIS MOBILE */
    .joystick-zone { position: absolute; bottom: 15px; width: 110px; height: 110px; border-radius: 50%; background: rgba(0, 255, 150, 0.08); border: 2px dashed rgba(0, 255, 150, 0.4); display: flex; justify-content: center; align-items: center; pointer-events: auto; z-index: 25; }
    #zone-left { left: 15px; }
    #zone-right { right: 15px; }

    .joystick-stick { width: 44px; height: 44px; border-radius: 50%; background: rgba(0, 255, 150, 0.4); border: 2px solid #00ff96; box-shadow: 0 0 10px #00ff96; pointer-events: none; transition: transform 0.04s ease-out; }
    .joystick-label { position: absolute; top: -20px; font-size: 9px; font-weight: bold; color: #00ff96; letter-spacing: 1px; text-shadow: 0 0 4px #000; }

    /* BOTÃO DE DISPARO 🔥 */
    #btn-shoot { position: absolute; bottom: 135px; right: 20px; width: 68px; height: 68px; border-radius: 50%; background: rgba(255, 0, 85, 0.35); border: 2px solid #ff0055; color: #ff0055; font-size: 24px; display: flex; justify-content: center; align-items: center; box-shadow: 0 0 15px rgba(255,0,85,0.4); pointer-events: auto; z-index: 30; }
    #btn-shoot:active { background: rgba(255, 0, 85, 0.8); transform: scale(0.92); }

    .top-btn { pointer-events: auto; background: rgba(0,20,10,0.8); border: 1px solid #00ff96; color: #00ff96; padding: 6px 10px; font-size: 11px; border-radius: 4px; font-family: monospace; font-weight: bold; }

    .modal { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 10, 5, 0.95); z-index: 100; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
    .modal h1 { color: #00ff96; font-size: 22px; text-shadow: 0 0 10px #00ff96; margin-bottom: 10px; }
    .modal p { color: #a0ffd0; font-size: 12px; max-width: 420px; line-height: 1.6; margin-bottom: 20px; }
    .btn-main { pointer-events: auto; background: #00ff96; color: #000; border: none; padding: 14px 28px; font-size: 15px; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 0 15px #00ff96; }
  </style>
  <script type="importmap">
    {
      "imports": {
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js"
      }
    }
  </script>
</head>
<body>
  <div id="canvas-container"></div>

  <div id="hud">
    <div class="hud-header">
      <div>
        <div style="font-size: 9px; font-weight: bold;">ESTRUTURA</div>
        <div class="bar-container"><div id="health-bar" class="bar-fill"></div></div>
        <div style="font-size: 9px; font-weight: bold; margin-top: 3px;">BATERIA</div>
        <div class="bar-container"><div id="battery-bar" class="bar-fill battery"></div></div>
      </div>
      <div style="text-align: center;">
        <canvas id="radar-canvas" width="75" height="75"></canvas>
      </div>
      <div style="text-align: right;">
        <div id="intel-count" style="font-size: 11px; font-weight: bold;">DADOS: 0 / 4</div>
        <div id="alt-speed" style="font-size: 9px; color: #80ffc0; margin-top: 3px;">ALT: 3m | VEL: 0km/h</div>
      </div>
    </div>
  </div>

  <div id="crosshair"></div>

  <!-- BOTOES DE TOPO -->
  <div style="position: absolute; top: 60px; right: 12px; z-index: 40; display: flex; gap: 8px;">
    <button id="btn-nightvision" class="top-btn">🌙 NOTURNO</button>
    <button id="btn-fullscreen" class="top-btn" onclick="toggleFS()">📺 CHEIA</button>
  </div>

  <!-- JOYSTICKS VIRTUAIS -->
  <div id="zone-left" class="joystick-zone">
    <div class="joystick-label">VOO / GIRO</div>
    <div id="stick-left" class="joystick-stick"></div>
  </div>

  <div id="zone-right" class="joystick-zone">
    <div class="joystick-label">MOVIMENTO</div>
    <div id="stick-right" class="joystick-stick"></div>
  </div>

  <button id="btn-shoot">🔥</button>

  <!-- MODAIS -->
  <div id="modal-start" class="modal">
    <h1>OPERAÇÃO GHOST 3D</h1>
    <p><b>CONTROLES DE PILOTAGEM MULTI-TOUCH:</b><br><br>
    🕹️ <b>Esquerda:</b> Empurre para Cima/Baixo (Subir/Descer) e Lados (Girar)<br>
    🕹️ <b>Direita:</b> Empurre para Cima/Baixo (Avançar/Recuar) e Lados (Inclinado)<br>
    🔥 <b>Botão Redondo:</b> Atirar Lasers</p>
    <button id="btn-start" class="btn-main">INICIAR PILOTAGEM</button>
  </div>

  <div id="modal-end" class="modal" style="display: none;">
    <h1 id="end-title">FALHA NA MISSÃO</h1>
    <p id="end-message">Seu drone foi destruído.</p>
    <button id="btn-restart" class="btn-main">REINICIAR</button>
  </div>

  <script>
    function toggleFS() {
      const doc = document.documentElement;
      if (!document.fullscreenElement && !document.webkitFullscreenElement) {
        if (doc.requestFullscreen) doc.requestFullscreen();
        else if (doc.webkitRequestFullscreen) doc.webkitRequestFullscreen();
      } else {
        if (document.exitFullscreen) document.exitFullscreen();
        else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
      }
    }
  </script>
  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 4. INTEGRAÇÃO NO MAIN.JS
main_code = '''import * as THREE from 'three';
import { Player } from './entities/Player.js';
import { EnemyManager } from './entities/EnemyManager.js';
import { ProjectileSystem } from './entities/Projectiles.js';
import { ExplosionSystem } from './effects/Explosions.js';
import { soundManager } from './audio/SoundManager.js';
import { Radar } from './ui/Radar.js';
import { JoystickController } from './controls/Joystick.js';

class Game {
  constructor() {
    this.container = document.getElementById('canvas-container');
    
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x020805);
    this.scene.fog = new THREE.FogExp2(0x020805, 0.022);

    this.camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 200);
    
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00ff96, 1.2);
    dirLight.position.set(20, 40, 20);
    this.scene.add(dirLight);

    this.player = new Player(this.scene, this.camera);
    this.explosionSystem = new ExplosionSystem(this.scene);
    this.enemyManager = new EnemyManager(this.scene, this.player, this.explosionSystem);
    this.projectileSystem = new ProjectileSystem(this.scene);
    this.radar = new Radar('radar-canvas');

    this.joysticks = new JoystickController({
      leftZoneId: 'zone-left',
      rightZoneId: 'zone-right',
      leftStickId: 'stick-left',
      rightStickId: 'stick-right'
    });

    this.dataModules = [];
    this.intelCollected = 0;
    this.totalIntel = 4;
    this.isNightVision = false;

    this.buildEnvironment();
    this.setupDataModules();
    this.setupEvents();

    this.clock = new THREE.Clock();
    this.isPlaying = false;

    window.addEventListener('resize', () => this.onResize());
  }

  buildEnvironment() {
    const grid = new THREE.GridHelper(140, 70, 0x00ff96, 0x003318);
    grid.position.y = 0;
    this.scene.add(grid);

    const buildingGeo = new THREE.BoxGeometry(1, 1, 1);
    const buildingMat = new THREE.MeshStandardMaterial({ color: 0x08180e, wireframe: true });

    for (let i = 0; i < 30; i++) {
      const mesh = new THREE.Mesh(buildingGeo, buildingMat);
      const w = 4 + Math.random() * 6;
      const h = 5 + Math.random() * 15;
      const d = 4 + Math.random() * 6;
      mesh.scale.set(w, h, d);
      mesh.position.set((Math.random() - 0.5) * 90, h / 2, (Math.random() - 0.5) * 90);
      this.scene.add(mesh);
    }
  }

  setupDataModules() {
    const geo = new THREE.IcosahedronGeometry(0.8, 0);
    const mat = new THREE.MeshBasicMaterial({ color: 0x00ff96, wireframe: true });

    const pos = [{ x: 20, z: 20 }, { x: -22, z: 22 }, { x: 25, z: -25 }, { x: -20, z: -20 }];

    pos.forEach(p => {
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(p.x, 1.5, p.z);
      this.scene.add(mesh);
      this.dataModules.push({ mesh: mesh, collected: false });
    });
  }

  setupEvents() {
    const btnShoot = document.getElementById('btn-shoot');
    const btnStart = document.getElementById('btn-start');
    const btnRestart = document.getElementById('btn-restart');
    const btnNV = document.getElementById('btn-nightvision');

    if (btnShoot) {
      btnShoot.addEventListener('touchstart', (e) => { e.preventDefault(); this.shoot(); });
      btnShoot.addEventListener('click', () => this.shoot());
    }

    if (btnNV) {
      btnNV.addEventListener('touchstart', (e) => { e.preventDefault(); this.toggleNightVision(); });
      btnNV.addEventListener('click', () => this.toggleNightVision());
    }

    if (btnStart) {
      btnStart.addEventListener('touchstart', (e) => { e.preventDefault(); this.startMission(); });
      btnStart.addEventListener('click', () => this.startMission());
    }

    if (btnRestart) {
      btnRestart.addEventListener('touchstart', (e) => { e.preventDefault(); this.restartMission(); });
      btnRestart.addEventListener('click', () => this.restartMission());
    }
  }

  toggleNightVision() {
    this.isNightVision = !this.isNightVision;
    this.scene.background = new THREE.Color(this.isNightVision ? 0x001a0a : 0x020805);
    this.scene.fog.color = new THREE.Color(this.isNightVision ? 0x001a0a : 0x020805);
  }

  shoot() {
    if (!this.isPlaying) return;
    soundManager.init();
    const spawnPos = this.player.position.clone().add(this.player.getForwardDirection().multiplyScalar(1.2));
    this.projectileSystem.spawnBullet(spawnPos, this.player.getForwardDirection());
    soundManager.playLaser();
  }

  startMission() {
    soundManager.init();
    document.getElementById('modal-start').style.display = 'none';
    this.isPlaying = true;
    this.clock.start();
    this.animate();
  }

  restartMission() {
    soundManager.init();
    document.getElementById('modal-end').style.display = 'none';
    this.player.reset();
    this.enemyManager.reset();
    this.projectileSystem.reset();
    this.intelCollected = 0;
    this.dataModules.forEach(mod => {
      mod.collected = false;
      mod.mesh.visible = true;
    });
    this.isPlaying = true;
    this.updateHUD();
  }

  gameOver(title, msg) {
    this.isPlaying = false;
    document.getElementById('end-title').innerText = title;
    document.getElementById('end-message').innerText = msg;
    document.getElementById('modal-end').style.display = 'flex';
  }

  updateHUD() {
    const healthBar = document.getElementById('health-bar');
    const batteryBar = document.getElementById('battery-bar');
    const intelText = document.getElementById('intel-count');
    const altSpeedText = document.getElementById('alt-speed');

    if (healthBar) healthBar.style.width = `${Math.max(0, this.player.health)}%`;
    if (batteryBar) batteryBar.style.width = `${Math.max(0, this.player.battery)}%`;
    if (intelText) intelText.innerText = `DADOS: ${this.intelCollected} / ${this.totalIntel}`;
    
    if (altSpeedText) {
      const alt = Math.round(this.player.position.y);
      const vel = Math.round(this.player.getForwardDirection().length() * 20);
      altSpeedText.innerText = `ALT: ${alt}m | VEL: ${vel}km/h`;
    }
  }

  animate() {
    if (!this.isPlaying) return;
    requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();

    // Atualiza jogador via inputs do Joystick
    this.player.update(delta, this.joysticks.input);
    this.enemyManager.update(delta);
    this.projectileSystem.update(delta, this.enemyManager.enemies, this.explosionSystem, soundManager);
    this.explosionSystem.update(delta);

    this.dataModules.forEach(mod => {
      if (!mod.collected && this.player.position.distanceTo(mod.mesh.position) < 2.0) {
        mod.collected = true;
        mod.mesh.visible = false;
        this.intelCollected++;
        soundManager.playCollect();

        if (this.intelCollected >= this.totalIntel) {
          this.gameOver('MISSÃO CUMPRIDA!', 'Todos os dados do setor foram recuperados!');
        }
      }
      if (!mod.collected) {
        mod.mesh.rotation.y += 0.02;
      }
    });

    if (this.player.health <= 0) {
      this.gameOver('FALHA NA MISSÃO', 'Seu drone foi abatido em combate.');
    } else if (this.player.battery <= 0) {
      this.gameOver('FALHA NA MISSÃO', 'Bateria do drone esgotada.');
    }

    this.radar.draw(this.player, this.enemyManager.enemies, this.dataModules);
    this.updateHUD();

    this.renderer.render(this.scene, this.camera);
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }
}

new Game();'''

with open('src/main.js', 'w', encoding='utf-8') as f:
    f.write(main_code)

print("Controles de Drone de Alta Precisão aplicados com sucesso!")
