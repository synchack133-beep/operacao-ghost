import os

# 1. INDEX.HTML
index_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <title>OPERAÇÃO GHOST — DRONE WARFARE</title>
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; touch-action: manipulation; }
    html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; color: #00ff96; }
    #canvas-container { width: 100%; height: 100%; position: absolute; top:0; left:0; z-index: 1; }
    
    /* HUD Overlays */
    #hud { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10; pointer-events: none; display: flex; flex-direction: column; justify-content: space-between; padding: max(10px, env(safe-area-inset-top)) max(10px, env(safe-area-inset-right)) max(10px, env(safe-area-inset-bottom)) max(10px, env(safe-area-inset-left)); }
    
    .hud-header { display: flex; justify-content: space-between; align-items: flex-start; background: rgba(0, 20, 10, 0.75); padding: 8px 14px; border: 1px solid rgba(0, 255, 150, 0.4); border-radius: 6px; backdrop-filter: blur(4px); }
    .bar-container { width: 120px; height: 10px; background: rgba(0, 50, 25, 0.8); border: 1px solid #00ff96; margin-top: 4px; border-radius: 3px; overflow: hidden; }
    .bar-fill { height: 100%; background: #00ff96; width: 100%; transition: width 0.1s ease; }
    .bar-fill.battery { background: #00ccff; }
    
    /* Mira Central */
    #crosshair { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 36px; height: 36px; pointer-events: none; z-index: 11; }
    #crosshair::before, #crosshair::after { content: ''; position: absolute; background: #00ff96; box-shadow: 0 0 8px #00ff96; }
    #crosshair::before { top: 17px; left: 0; width: 36px; height: 2px; }
    #crosshair::after { top: 0; left: 17px; width: 2px; height: 36px; }
    
    /* Radar Canvas */
    #radar-canvas { width: 80px; height: 80px; border-radius: 50%; border: 2px solid #00ff96; background: rgba(0,25,10,0.8); box-shadow: 0 0 10px rgba(0,255,150,0.3); }

    /* Touch Controls */
    #touch-controls { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 20; pointer-events: none; }
    .touch-btn { pointer-events: auto; background: rgba(0, 255, 150, 0.18); border: 2px solid #00ff96; color: #00ff96; font-weight: bold; border-radius: 50%; display: flex; justify-content: center; align-items: center; text-shadow: 0 0 5px #00ff96; font-size: 14px; box-shadow: 0 0 12px rgba(0,255,150,0.2); }
    .touch-btn:active { background: rgba(0, 255, 150, 0.5); transform: scale(0.95); }
    
    #btn-shoot { position: absolute; bottom: 25px; right: 25px; width: 75px; height: 75px; background: rgba(255, 0, 85, 0.3); border-color: #ff0055; color: #ff0055; font-size: 20px; text-shadow: 0 0 5px #ff0055; }
    #btn-shoot:active { background: rgba(255, 0, 85, 0.7); }
    
    #btn-up { position: absolute; bottom: 115px; right: 25px; width: 55px; height: 55px; }
    #btn-down { position: absolute; bottom: 115px; right: 90px; width: 55px; height: 55px; }

    /* Modais */
    .modal { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 10, 5, 0.94); z-index: 100; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
    .modal h1 { color: #00ff96; font-size: 24px; text-shadow: 0 0 10px #00ff96; margin-bottom: 10px; letter-spacing: 2px; }
    .modal p { color: #a0ffd0; font-size: 13px; max-width: 480px; line-height: 1.5; margin-bottom: 20px; }
    .btn-main { pointer-events: auto; background: #00ff96; color: #000; border: none; padding: 14px 28px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 0 15px #00ff96; letter-spacing: 1px; }
    .btn-main:active { transform: scale(0.96); }
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
        <div style="font-size: 10px; font-weight: bold;">INTEGRIDADE STRUCT</div>
        <div class="bar-container"><div id="health-bar" class="bar-fill"></div></div>
        <div style="font-size: 10px; font-weight: bold; margin-top: 4px;">BATERIA DRONE</div>
        <div class="bar-container"><div id="battery-bar" class="bar-fill battery"></div></div>
      </div>
      <div style="text-align: center;">
        <canvas id="radar-canvas" width="80" height="80"></canvas>
      </div>
      <div style="text-align: right;">
        <div id="intel-count" style="font-size: 12px; font-weight: bold;">DADOS: 0 / 4</div>
        <div id="alt-speed" style="font-size: 10px; color: #80ffc0; margin-top: 4px;">ALT: 5m | VEL: 0km/h</div>
      </div>
    </div>
  </div>

  <div id="crosshair"></div>

  <div id="touch-controls">
    <button id="btn-fullscreen" class="touch-btn" style="position: absolute; top: 12px; right: 12px; width: auto; height: auto; border-radius: 4px; padding: 6px 10px; font-size: 11px;" onclick="toggleFS()">📺 TELA CHEIA</button>
    <button id="btn-nightvision" class="touch-btn" style="position: absolute; top: 52px; right: 12px; width: 42px; height: 42px; border-radius: 8px;">🌙</button>
    <button id="btn-shoot" class="touch-btn">🔥</button>
    <button id="btn-up" class="touch-btn">▲</button>
    <button id="btn-down" class="touch-btn">▼</button>
  </div>

  <div id="modal-start" class="modal">
    <h1>OPERAÇÃO GHOST</h1>
    <p>COMBATE ARCADE TÁTICO<br><br>• Elimine os caças inimigos com o botão de disparo (🔥)<br>• Colete os 4 módulos de dados espalhados<br>• Arraste o dedo na tela para pilotar e direcionar a visão</p>
    <button id="btn-start" class="btn-main">INICIAR MISSÃO</button>
  </div>

  <div id="modal-end" class="modal" style="display: none;">
    <h1 id="end-title">FALHA NA MISSÃO</h1>
    <p id="end-message">Seu drone foi destruído no combate.</p>
    <button id="btn-restart" class="btn-main">REINICIAR MISSÃO</button>
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

# 2. SOUND MANAGER (Web Audio API)
os.makedirs('src/audio', exist_ok=True)
sound_code = '''export class SoundManager {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    } else if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playLaser() {
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(850, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(120, this.ctx.currentTime + 0.15);
    gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.15);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.15);
  }

  playExplosion() {
    if (!this.ctx) return;
    const bufferSize = this.ctx.sampleRate * 0.35;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = Math.random() * 2 - 1;
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(800, this.ctx.currentTime);
    filter.frequency.linearRampToValueAtTime(80, this.ctx.currentTime + 0.35);
    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.35, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.35);
    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.ctx.destination);
    noise.start();
  }

  playCollect() {
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(523, this.ctx.currentTime);
    osc.frequency.setValueAtTime(659, this.ctx.currentTime + 0.08);
    osc.frequency.setValueAtTime(783, this.ctx.currentTime + 0.16);
    gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, this.ctx.currentTime + 0.25);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.25);
  }
}
export const soundManager = new SoundManager();'''

with open('src/audio/SoundManager.js', 'w', encoding='utf-8') as f:
    f.write(sound_code)

# 3. PROJECTILES
os.makedirs('src/entities', exist_ok=True)
proj_code = '''import * as THREE from 'three';

export class ProjectileSystem {
  constructor(scene) {
    this.scene = scene;
    this.bullets = [];
    this.bulletGeo = new THREE.CylinderGeometry(0.08, 0.08, 1.2, 6);
    this.bulletGeo.rotateX(Math.PI / 2);
    this.bulletMat = new THREE.MeshBasicMaterial({ color: 0x00ffff });
  }

  spawnBullet(position, direction) {
    const mesh = new THREE.Mesh(this.bulletGeo, this.bulletMat);
    mesh.position.copy(position);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, -1), direction.clone().normalize());
    this.scene.add(mesh);

    this.bullets.push({
      mesh: mesh,
      velocity: direction.clone().normalize().multiplyScalar(1.3),
      life: 2.0
    });
  }

  update(delta, enemies, explosionSystem, soundManager) {
    for (let i = this.bullets.length - 1; i >= 0; i--) {
      const b = this.bullets[i];
      b.life -= delta;
      b.mesh.position.add(b.velocity);

      let hit = false;
      if (enemies) {
        for (let j = 0; j < enemies.length; j++) {
          const enemy = enemies[j];
          if (enemy.active && b.mesh.position.distanceTo(enemy.group.position) < 2.2) {
            enemy.active = false;
            enemy.group.visible = false;
            hit = true;
            if (explosionSystem) explosionSystem.createExplosion(enemy.group.position, 0xff0055, 45);
            if (soundManager) soundManager.playExplosion();
            break;
          }
        }
      }

      if (hit || b.life <= 0 || b.mesh.position.y < 0) {
        this.scene.remove(b.mesh);
        this.bullets.splice(i, 1);
      }
    }
  }

  reset() {
    this.bullets.forEach(b => this.scene.remove(b.mesh));
    this.bullets = [];
  }
}'''

with open('src/entities/Projectiles.js', 'w', encoding='utf-8') as f:
    f.write(proj_code)

# 4. RADAR UI
os.makedirs('src/ui', exist_ok=True)
radar_code = '''export class Radar {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (this.canvas) this.ctx = this.canvas.getContext('2d');
  }

  draw(player, enemies, dataModules) {
    if (!this.ctx) return;
    const w = this.canvas.width;
    const h = this.canvas.height;
    const cx = w / 2;
    const cy = h / 2;
    const scale = 1.3;

    this.ctx.clearRect(0, 0, w, h);

    this.ctx.strokeStyle = 'rgba(0, 255, 150, 0.3)';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, 18, 0, Math.PI * 2);
    this.ctx.arc(cx, cy, 34, 0, Math.PI * 2);
    this.ctx.stroke();

    if (!player) return;

    if (dataModules) {
      this.ctx.fillStyle = '#00ff96';
      dataModules.forEach(mod => {
        if (!mod.collected) {
          const dx = (mod.mesh.position.x - player.position.x) * scale;
          const dz = (mod.mesh.position.z - player.position.z) * scale;
          if (Math.hypot(dx, dz) < cx - 4) {
            this.ctx.fillRect(cx + dx - 2, cy + dz - 2, 4, 4);
          }
        }
      });
    }

    if (enemies) {
      this.ctx.fillStyle = '#ff0055';
      enemies.forEach(e => {
        if (e.active) {
          const dx = (e.group.position.x - player.position.x) * scale;
          const dz = (e.group.position.z - player.position.z) * scale;
          if (Math.hypot(dx, dz) < cx - 4) {
            this.ctx.beginPath();
            this.ctx.arc(cx + dx, cy + dz, 3, 0, Math.PI * 2);
            this.ctx.fill();
          }
        }
      });
    }

    this.ctx.fillStyle = '#00ffff';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    this.ctx.fill();
  }
}'''

with open('src/ui/Radar.js', 'w', encoding='utf-8') as f:
    f.write(radar_code)

# 5. MAIN SCRIPT INTEGRADO
main_code = '''import * as THREE from 'three';
import { Player } from './entities/Player.js';
import { EnemyManager } from './entities/EnemyManager.js';
import { ProjectileSystem } from './entities/Projectiles.js';
import { ExplosionSystem } from './effects/Explosions.js';
import { soundManager } from './audio/SoundManager.js';
import { Radar } from './ui/Radar.js';

class Game {
  constructor() {
    this.container = document.getElementById('canvas-container');
    
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x020805);
    this.scene.fog = new THREE.FogExp2(0x020805, 0.025);

    this.camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 200);
    
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00ff96, 1.2);
    dirLight.position.set(20, 40, 20);
    this.scene.add(dirLight);

    this.input = { forward: false, backward: false, left: false, right: false, up: false, down: false, lookX: 0, lookY: 0 };

    this.player = new Player(this.scene, this.camera);
    this.explosionSystem = new ExplosionSystem(this.scene);
    this.enemyManager = new EnemyManager(this.scene, this.player, this.explosionSystem);
    this.projectileSystem = new ProjectileSystem(this.scene);
    this.radar = new Radar('radar-canvas');

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
    const grid = new THREE.GridHelper(120, 60, 0x00ff96, 0x004422);
    grid.position.y = 0;
    this.scene.add(grid);

    const buildingGeo = new THREE.BoxGeometry(1, 1, 1);
    const buildingMat = new THREE.MeshStandardMaterial({ color: 0x0a1a10, wireframe: true });

    for (let i = 0; i < 25; i++) {
      const mesh = new THREE.Mesh(buildingGeo, buildingMat);
      const w = 3 + Math.random() * 5;
      const h = 4 + Math.random() * 12;
      const d = 3 + Math.random() * 5;
      mesh.scale.set(w, h, d);
      mesh.position.set((Math.random() - 0.5) * 80, h / 2, (Math.random() - 0.5) * 80);
      this.scene.add(mesh);
    }
  }

  setupDataModules() {
    const geo = new THREE.IcosahedronGeometry(0.8, 0);
    const mat = new THREE.MeshBasicMaterial({ color: 0x00ff96, wireframe: true });

    const pos = [{ x: 18, z: 18 }, { x: -22, z: 22 }, { x: 25, z: -25 }, { x: -18, z: -20 }];

    pos.forEach(p => {
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(p.x, 1.5, p.z);
      this.scene.add(mesh);
      this.dataModules.push({ mesh: mesh, collected: false });
    });
  }

  setupEvents() {
    let touchStartX = 0;
    let touchStartY = 0;

    window.addEventListener('touchstart', (e) => {
      soundManager.init();
      if (e.touches.length > 0) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (e.touches.length > 0) {
        const dx = e.touches[0].clientX - touchStartX;
        const dy = e.touches[0].clientY - touchStartY;
        this.input.lookX = dx * 0.15;
        this.input.lookY = dy * 0.15;
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;

        this.input.forward = dy < -18;
        this.input.backward = dy > 18;
        this.input.left = dx < -18;
        this.input.right = dx > 18;
      }
    }, { passive: true });

    window.addEventListener('touchend', () => {
      this.input.lookX = 0;
      this.input.lookY = 0;
      this.input.forward = false;
      this.input.backward = false;
      this.input.left = false;
      this.input.right = false;
    });

    const btnUp = document.getElementById('btn-up');
    const btnDown = document.getElementById('btn-down');
    const btnShoot = document.getElementById('btn-shoot');
    const btnStart = document.getElementById('btn-start');
    const btnRestart = document.getElementById('btn-restart');
    const btnNV = document.getElementById('btn-nightvision');

    if (btnUp) {
      btnUp.addEventListener('touchstart', (e) => { e.preventDefault(); this.input.up = true; });
      btnUp.addEventListener('touchend', () => { this.input.up = false; });
    }
    if (btnDown) {
      btnDown.addEventListener('touchstart', (e) => { e.preventDefault(); this.input.down = true; });
      btnDown.addEventListener('touchend', () => { this.input.down = false; });
    }
    if (btnShoot) {
      btnShoot.addEventListener('click', () => this.shoot());
      btnShoot.addEventListener('touchstart', (e) => { e.preventDefault(); this.shoot(); });
    }
    if (btnNV) {
      btnNV.addEventListener('click', () => this.toggleNightVision());
      btnNV.addEventListener('touchstart', (e) => { e.preventDefault(); this.toggleNightVision(); });
    }

    if (btnStart) {
      btnStart.addEventListener('click', () => this.startMission());
      btnStart.addEventListener('touchstart', (e) => { e.preventDefault(); this.startMission(); });
    }
    if (btnRestart) {
      btnRestart.addEventListener('click', () => this.restartMission());
      btnRestart.addEventListener('touchstart', (e) => { e.preventDefault(); this.restartMission(); });
    }
  }

  toggleNightVision() {
    this.isNightVision = !this.isNightVision;
    this.scene.background = new THREE.Color(this.isNightVision ? 0x00180a : 0x020805);
    this.scene.fog.color = new THREE.Color(this.isNightVision ? 0x00180a : 0x020805);
  }

  shoot() {
    if (!this.isPlaying) return;
    const spawnPos = this.player.position.clone().add(this.player.getForwardDirection().multiplyScalar(1.2));
    this.projectileSystem.spawnBullet(spawnPos, this.player.getForwardDirection());
    soundManager.playLaser();
  }

  startMission() {
    document.getElementById('modal-start').style.display = 'none';
    this.isPlaying = true;
    this.clock.start();
    this.animate();
  }

  restartMission() {
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
      const vel = Math.round(this.player.velocity.length() * 100);
      altSpeedText.innerText = `ALT: ${alt}m | VEL: ${vel}km/h`;
    }
  }

  animate() {
    if (!this.isPlaying) return;
    requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();

    this.player.update(delta, this.input);
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
          this.gameOver('MISSÃO CUMPRIDA!', 'Todos os módulos de dados foram recuperados com sucesso!');
        }
      }
      if (!mod.collected) {
        mod.mesh.rotation.y += 0.02;
      }
    });

    if (this.player.health <= 0) {
      this.gameOver('FALHA NA MISSÃO', 'Seu drone foi abatido por fogo inimigo.');
    } else if (this.player.battery <= 0) {
      this.gameOver('FALHA NA MISSÃO', 'A bateria do drone esgotou.');
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

print("Sistema completo compilado com sucesso!")
