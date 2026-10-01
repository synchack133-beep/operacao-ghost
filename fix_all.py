import os

# 1. INDEX.HTML
index_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>OPERAÇÃO GHOST — WAR ZONE FPV</title>
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; touch-action: none; }
    html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: #050805; font-family: 'Courier New', monospace; color: #ffffff; }
    #canvas-container { width: 100%; height: 100%; position: absolute; top:0; left:0; z-index: 1; }

    #lens-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 5; pointer-events: none;
      background: radial-gradient(circle, rgba(0,0,0,0) 50%, rgba(10,15,10,0.5) 80%, rgba(0,0,0,0.92) 100%);
    }

    #scanlines {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 6; pointer-events: none;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
      background-size: 100% 4px; opacity: 0.7;
    }

    #compass-container {
      position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
      width: 280px; height: 26px; background: rgba(0, 0, 0, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 3px;
      display: flex; justify-content: center; align-items: center;
      overflow: hidden; z-index: 10; font-size: 11px; letter-spacing: 2px; color: #d0ded0;
    }
    #compass-indicator { position: absolute; top: -1px; color: #ff3c3c; font-weight: bold; font-size: 11px; }

    #reticle-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 8; pointer-events: none;
      display: flex; justify-content: center; align-items: center;
    }

    .telemetry-left {
      position: absolute; top: 50px; left: 15px; z-index: 10; pointer-events: none;
      font-size: 10px; line-height: 1.6; text-shadow: 1px 1px 2px #000; color: #e2e8f0;
      background: rgba(0, 0, 0, 0.4); padding: 6px 10px; border-left: 2px solid #00ff96;
    }

    .telemetry-right {
      position: absolute; top: 50px; right: 170px; z-index: 10; pointer-events: none;
      font-size: 10px; line-height: 1.6; text-shadow: 1px 1px 2px #000; color: #e2e8f0; text-align: right;
      background: rgba(0, 0, 0, 0.4); padding: 6px 10px; border-right: 2px solid #ff3c3c;
    }

    #btn-fullscreen { position: absolute; top: 10px; right: 10px; width: 38px; height: 38px; background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(255,255,255,0.3); color: #fff; font-size: 16px; border-radius: 4px; display: flex; justify-content: center; align-items: center; pointer-events: auto; z-index: 35; cursor: pointer; }
    
    #pip-container { position: absolute; top: 54px; right: 10px; width: 145px; height: 105px; border: 1px solid rgba(0, 255, 150, 0.6); background: rgba(0, 10, 5, 0.9); z-index: 20; pointer-events: none; }
    #pip-title { position: absolute; top: -15px; left: 0; width: 100%; font-size: 8px; font-weight: bold; color: #00ff96; text-align: center; }

    .joystick-zone { position: absolute; bottom: 15px; width: 110px; height: 110px; border-radius: 50%; background: rgba(255, 255, 255, 0.08); border: 1px dashed rgba(255, 255, 255, 0.3); pointer-events: auto; z-index: 25; }
    #zone-left { left: 15px; }
    #zone-right { right: 15px; }
    .joystick-stick { width: 40px; height: 40px; border-radius: 50%; background: rgba(255, 255, 255, 0.4); border: 1px solid #fff; position: absolute; top: 35px; left: 35px; pointer-events: none; }

    #btn-drop-missile { position: absolute; bottom: 135px; right: 20px; width: 66px; height: 66px; border-radius: 50%; background: rgba(255, 60, 60, 0.55); border: 2px solid #ff3c3c; color: #fff; font-size: 22px; display: flex; justify-content: center; align-items: center; pointer-events: auto; z-index: 30; font-weight: bold; }
    #btn-drop-missile:active { background: rgba(255, 60, 60, 0.85); transform: scale(0.92); }

    .modal { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(8, 12, 10, 0.96); z-index: 100; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
    .btn-main { pointer-events: auto; background: #ff3c3c; color: #fff; border: none; padding: 14px 28px; font-size: 15px; font-weight: bold; border-radius: 3px; cursor: pointer; letter-spacing: 1px; }
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
  <div id="lens-overlay"></div>
  <div id="scanlines"></div>

  <div id="reticle-overlay">
    <svg width="100%" height="100%" viewBox="0 0 800 450" preserveAspectRatio="none">
      <path d="M 270 140 Q 240 225 270 310" stroke="rgba(255,255,255,0.35)" stroke-width="1.5" fill="none"/>
      <path d="M 530 140 Q 560 225 530 310" stroke="rgba(255,255,255,0.35)" stroke-width="1.5" fill="none"/>
      <line x1="360" y1="185" x2="385" y2="185" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
      <line x1="415" y1="185" x2="440" y2="185" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
      <line x1="360" y1="265" x2="385" y2="265" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
      <line x1="415" y1="265" x2="440" y2="265" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
      <circle cx="400" cy="225" r="3" fill="#ff3c3c"/>
      <circle cx="400" cy="225" r="12" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
    </svg>
  </div>

  <button id="btn-fullscreen" title="Tela Cheia">⛶</button>

  <div id="compass-container">
    <span id="compass-indicator">▼</span>
    <div id="compass-text">0° [ N ]</div>
  </div>

  <div class="telemetry-left">
    <div><b>BAT:</b> 22.2V (4S)</div>
    <div><b>RSSI:</b> -65 dBm</div>
    <div><b>SAT:</b> 14 GPS</div>
    <div><b>MODE:</b> ANGLE</div>
  </div>

  <div class="telemetry-right">
    <div><b>SPD:</b> <span id="tele-spd">0</span> km/h</div>
    <div><b>ALT:</b> <span id="tele-alt">12</span> m</div>
    <div><b>DIST:</b> <span id="tele-range">0.00</span> / 3.00 km</div>
    <div><b>COORD:</b> 48.432°N 37.811°E</div>
  </div>

  <div id="pip-container">
    <div id="pip-title">CAM DESTINO</div>
  </div>

  <div id="zone-left" class="joystick-zone"><div id="stick-left" class="joystick-stick"></div></div>
  <div id="zone-right" class="joystick-zone"><div id="stick-right" class="joystick-stick"></div></div>

  <button id="btn-drop-missile">🚀</button>

  <div id="modal-start" class="modal">
    <h2 style="color:#ff3c3c; margin-bottom: 8px;">ZONA DE GUERRA — FPV KAMIKAZE</h2>
    <p style="font-size: 13px; line-height: 1.5; max-width: 480px; color: #a3b8a3;">
    🌲 <b>Cenário de Batalha:</b> Trincheiras em ziguezague, crateras de bomba e floresta de combate.<br><br>
    🕹️ <b>Controles Touch:</b> Utilize os dois analógicos nas pontas da tela para pilotar e o botão 🚀 para lançar ataques.
    </p>
    <button id="btn-start" class="btn-main">INICIAR MISSÃO</button>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 2. JOYSTICK CONTROLLER (SRC/CONTROLS/JOYSTICK.JS)
os.makedirs('src/controls', exist_ok=True)
joystick_code = '''export class JoystickController {
  constructor(options = {}) {
    this.input = { leftX: 0, leftY: 0, rightX: 0, rightY: 0 };
    this.setup(options);
  }

  setup(options) {
    const leftZone = document.getElementById(options.leftZoneId || 'zone-left');
    const rightZone = document.getElementById(options.rightZoneId || 'zone-right');
    const leftStick = document.getElementById(options.leftStickId || 'stick-left');
    const rightStick = document.getElementById(options.rightStickId || 'stick-right');

    const handleTouch = (zone, stick, isLeft, e) => {
      if (!zone || !stick || !e.touches || e.touches.length === 0) return;
      const rect = zone.getBoundingClientRect();
      const touch = e.touches[0];
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const maxRadius = rect.width / 2;

      let dx = touch.clientX - centerX;
      let dy = touch.clientY - centerY;
      const dist = Math.hypot(dx, dy);

      if (dist > maxRadius) {
        dx = (dx / dist) * maxRadius;
        dy = (dy / dist) * maxRadius;
      }

      stick.style.transform = `translate(${dx}px, ${dy}px)`;

      const normX = dx / maxRadius;
      const normY = dy / maxRadius;

      if (isLeft) {
        this.input.leftX = normX;
        this.input.leftY = normY;
      } else {
        this.input.rightX = normX;
        this.input.rightY = normY;
      }
    };

    const resetStick = (stick, isLeft) => {
      if (stick) stick.style.transform = 'translate(0px, 0px)';
      if (isLeft) {
        this.input.leftX = 0;
        this.input.leftY = 0;
      } else {
        this.input.rightX = 0;
        this.input.rightY = 0;
      }
    };

    if (leftZone) {
      leftZone.addEventListener('touchstart', (e) => handleTouch(leftZone, leftStick, true, e), { passive: true });
      leftZone.addEventListener('touchmove', (e) => handleTouch(leftZone, leftStick, true, e), { passive: true });
      leftZone.addEventListener('touchend', () => resetStick(leftStick, true));
      leftZone.addEventListener('touchcancel', () => resetStick(leftStick, true));
    }

    if (rightZone) {
      rightZone.addEventListener('touchstart', (e) => handleTouch(rightZone, rightStick, false, e), { passive: true });
      rightZone.addEventListener('touchmove', (e) => handleTouch(rightZone, rightStick, false, e), { passive: true });
      rightZone.addEventListener('touchend', () => resetStick(rightStick, false));
      rightZone.addEventListener('touchcancel', () => resetStick(rightStick, false));
    }
  }
}'''

with open('src/controls/Joystick.js', 'w', encoding='utf-8') as f:
    f.write(joystick_code)

# 3. PLAYER ENTITY (SRC/ENTITIES/PLAYER.JS)
os.makedirs('src/entities', exist_ok=True)
player_code = '''import * as THREE from 'three';

export class Player {
  constructor(scene, camera, operatorPosition) {
    this.scene = scene;
    this.camera = camera;
    this.operatorPos = operatorPosition || new THREE.Vector3(0, 0, 70);
    
    this.position = new THREE.Vector3(0, 12, 60);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
    
    this.cameraTiltX = 0;
    this.cameraRollZ = 0;

    this.speed = 22;
    this.rotSpeed = 2.0;
    this.minAltitude = 1.0;
    this.maxAltitude = 70.0;

    this.maxRangeMeters = 200;
    this.currentDistance = 0;

    const bodyGeo = new THREE.BoxGeometry(1.0, 0.15, 1.0);
    const mat = new THREE.MeshBasicMaterial({ color: 0x00ff96, wireframe: true });
    this.mesh = new THREE.Mesh(bodyGeo, mat);
    this.scene.add(this.mesh);
  }

  getForwardDirection() {
    const fwd = new THREE.Vector3(0, -0.3, -1);
    fwd.applyEuler(this.rotation);
    return fwd.normalize();
  }

  getInputs(input) {
    let lx = 0, ly = 0, rx = 0, ry = 0;
    if (input) {
      if (typeof input.leftX === 'number') lx = input.leftX;
      if (typeof input.leftY === 'number') ly = input.leftY;
      if (typeof input.rightX === 'number') rx = input.rightX;
      if (typeof input.rightY === 'number') ry = input.rightY;
    }
    return {
      lx: isNaN(lx) ? 0 : lx,
      ly: isNaN(ly) ? 0 : ly,
      rx: isNaN(rx) ? 0 : rx,
      ry: isNaN(ry) ? 0 : ry
    };
  }

  update(delta, rawInput) {
    const input = this.getInputs(rawInput);

    if (isNaN(this.position.x) || isNaN(this.position.y) || isNaN(this.position.z)) {
      this.position.set(0, 12, 60);
    }

    if (input.lx !== 0) {
      this.rotation.y -= input.lx * this.rotSpeed * delta;
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, -input.lx * 0.25, delta * 5);
    } else {
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, 0, delta * 5);
    }

    if (input.ly !== 0) {
      this.position.y -= input.ly * this.speed * delta;
    }

    const nextPos = this.position.clone();
    if (input.rx !== 0 || input.ry !== 0) {
      const moveVec = new THREE.Vector3(input.rx, 0, input.ry);
      moveVec.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      nextPos.addScaledVector(moveVec, this.speed * delta);

      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, -input.ry * 0.2, delta * 5);
    } else {
      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, 0, delta * 5);
    }

    const distToOperator = new THREE.Vector2(nextPos.x - this.operatorPos.x, nextPos.z - this.operatorPos.z).length();
    if (!isNaN(distToOperator) && distToOperator <= this.maxRangeMeters) {
      this.position.copy(nextPos);
      this.currentDistance = distToOperator;
    }

    if (this.position.y < this.minAltitude) this.position.y = this.minAltitude;
    if (this.position.y > this.maxAltitude) this.position.y = this.maxAltitude;

    this.mesh.position.copy(this.position);
    this.mesh.rotation.copy(this.rotation);

    this.camera.position.copy(this.position);
    this.camera.rotation.set(
      this.rotation.x + this.cameraTiltX,
      this.rotation.y,
      this.rotation.z + this.cameraRollZ,
      'YXZ'
    );
  }

  getRangeStatus() {
    const kmSimulated = ((this.currentDistance / this.maxRangeMeters) * 3.0).toFixed(2);
    const pct = (this.currentDistance / this.maxRangeMeters) * 100;
    return { km: kmSimulated, pct: pct, isWarning: pct > 80 };
  }
}'''

with open('src/entities/Player.js', 'w', encoding='utf-8') as f:
    f.write(player_code)

# 4. SCENARIO (SRC/WORLD/SCENARIO.JS)
os.makedirs('src/world', exist_ok=True)
scenario_code = '''import * as THREE from 'three';

export class Scenario {
  constructor(scene) {
    this.scene = scene;
    this.smokeParticles = [];
    this.setupAtmosphere();
    this.buildWarTerrain();
    this.buildTrenchSystem();
    this.buildWarForest();
    this.buildCratersAndSmoke();
    this.buildWreckedVehicles();
  }

  setupAtmosphere() {
    this.scene.background = new THREE.Color(0x6b776e);
    this.scene.fog = new THREE.FogExp2(0x6b776e, 0.0065);

    const sun = new THREE.DirectionalLight(0xfff3db, 1.2);
    sun.position.set(80, 120, 50);
    this.scene.add(sun);

    const ambient = new THREE.HemisphereLight(0x6b776e, 0x2b3323, 0.7);
    this.scene.add(ambient);
  }

  buildWarTerrain() {
    const groundGeo = new THREE.PlaneGeometry(400, 400, 60, 60);
    const posAttr = groundGeo.attributes.position;

    for (let i = 0; i < posAttr.count; i++) {
      const x = posAttr.getX(i);
      const y = posAttr.getY(i);
      const height = Math.sin(x * 0.04) * Math.cos(y * 0.04) * 1.2;
      posAttr.setZ(i, height);
    }
    groundGeo.computeVertexNormals();

    const groundMat = new THREE.MeshStandardMaterial({ color: 0x3b382b, roughness: 0.9 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    this.scene.add(ground);
  }

  buildTrenchSystem() {
    const sandbagMat = new THREE.MeshStandardMaterial({ color: 0x5e523f, roughness: 0.9 });
    const woodMat = new THREE.MeshStandardMaterial({ color: 0x2b1e15, roughness: 0.8 });

    const points = [
      new THREE.Vector3(-60, 0, 20),
      new THREE.Vector3(-30, 0, 10),
      new THREE.Vector3(0, 0, 30),
      new THREE.Vector3(35, 0, 15),
      new THREE.Vector3(70, 0, 35)
    ];

    for (let p = 0; p < points.length - 1; p++) {
      const start = points[p];
      const end = points[p + 1];
      const dist = start.distanceTo(end);
      const dir = new THREE.Vector3().subVectors(end, start).normalize();
      const angle = Math.atan2(dir.x, dir.z);

      for (let d = 0; d < dist; d += 1.5) {
        const pos = start.clone().addScaledVector(dir, d);
        for (let side of [-1.2, 1.2]) {
          const bag = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.4, 0.5), sandbagMat);
          const offset = new THREE.Vector3(side, 0.2, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), angle);
          bag.position.copy(pos).add(offset);
          bag.rotation.y = angle;
          this.scene.add(bag);
        }
      }
    }
  }

  buildWarForest() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x261c14, roughness: 0.9 });
    const burntMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.95 });
    const foliageMat = new THREE.MeshStandardMaterial({ color: 0x27361d, roughness: 0.8 });

    for (let i = 0; i < 70; i++) {
      const x = (Math.random() - 0.5) * 300;
      const z = (Math.random() - 0.5) * 300;
      if (Math.abs(x) < 15 && Math.abs(z) < 15) continue;

      const isDestroyed = Math.random() < 0.4;

      if (isDestroyed) {
        const height = 2 + Math.random() * 3;
        const stump = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.35, height, 6), burntMat);
        stump.position.set(x, height / 2, z);
        this.scene.add(stump);
      } else {
        const treeGroup = new THREE.Group();
        const height = 6 + Math.random() * 4;
        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.4, height, 6), trunkMat);
        trunk.position.y = height / 2;
        treeGroup.add(trunk);

        const foliage = new THREE.Mesh(new THREE.ConeGeometry(2.2, 4.0, 6), foliageMat);
        foliage.position.y = height * 0.6;
        treeGroup.add(foliage);

        treeGroup.position.set(x, 0, z);
        this.scene.add(treeGroup);
      }
    }
  }

  buildCratersAndSmoke() {
    const craterMat = new THREE.MeshBasicMaterial({ color: 0x15120e });
    const smokeMat = new THREE.MeshBasicMaterial({ color: 0x555555, transparent: true, opacity: 0.35 });

    const craterLocations = [
      new THREE.Vector3(-25, 0.05, -40),
      new THREE.Vector3(45, 0.05, -80),
      new THREE.Vector3(-70, 0.05, 50)
    ];

    craterLocations.forEach(loc => {
      const craterRim = new THREE.Mesh(new THREE.RingGeometry(1.5, 4.0, 12), craterMat);
      craterRim.rotation.x = -Math.PI / 2;
      craterRim.position.copy(loc);
      this.scene.add(craterRim);

      for (let p = 0; p < 5; p++) {
        const particle = new THREE.Mesh(new THREE.SphereGeometry(0.8, 6, 6), smokeMat);
        particle.position.set(loc.x + (Math.random() - 0.5) * 2, loc.y + Math.random() * 3, loc.z + (Math.random() - 0.5) * 2);
        this.scene.add(particle);
        this.smokeParticles.push({ mesh: particle, baseY: loc.y, speed: 0.6 + Math.random() * 0.6 });
      }
    });
  }

  buildWreckedVehicles() {
    const rustedMat = new THREE.MeshStandardMaterial({ color: 0x211c18, roughness: 0.9 });
    for (let i = 0; i < 4; i++) {
      const tank = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(4.0, 1.4, 6.0), rustedMat);
      body.position.y = 0.7;
      tank.add(body);

      const x = (Math.random() - 0.5) * 200;
      const z = (Math.random() - 0.5) * 200;
      tank.position.set(x, 0, z);
      tank.rotation.y = Math.random() * Math.PI * 2;
      this.scene.add(tank);
    }
  }

  update(delta) {
    this.smokeParticles.forEach(p => {
      p.mesh.position.y += p.speed * delta;
      if (p.mesh.position.y > p.baseY + 10) {
        p.mesh.position.y = p.baseY + 0.5;
      }
    });
  }
}'''

with open('src/world/Scenario.js', 'w', encoding='utf-8') as f:
    f.write(scenario_code)

# 5. OUTROS MÓDULOS ESSENCIAIS
soldier_code = '''import * as THREE from 'three';
export class SoldierManager {
  constructor(scene) { this.scene = scene; }
  update() {}
}'''
with open('src/entities/Soldier.js', 'w', encoding='utf-8') as f: f.write(soldier_code)

missile_code = '''import * as THREE from 'three';
export class MissileSystem {
  constructor(scene) { this.scene = scene; this.missiles = []; }
  spawnMissile() {}
  update() { return []; }
}'''
with open('src/entities/Missile.js', 'w', encoding='utf-8') as f: f.write(missile_code)

operator_code = '''import * as THREE from 'three';
export class Operator {
  constructor(scene, pos) { this.position = pos || new THREE.Vector3(0,0,70); }
}'''
with open('src/entities/Operator.js', 'w', encoding='utf-8') as f: f.write(operator_code)

explosions_code = '''export class ExplosionSystem {
  constructor(scene) {}
  createExplosion() {}
  update() {}
}'''
os.makedirs('src/effects', exist_ok=True)
with open('src/effects/Explosions.js', 'w', encoding='utf-8') as f: f.write(explosions_code)

sound_code = '''export const soundManager = { playExplosion: () => {} };'''
os.makedirs('src/audio', exist_ok=True)
with open('src/audio/SoundManager.js', 'w', encoding='utf-8') as f: f.write(sound_code)

# 6. MAIN.JS
main_code = '''import * as THREE from 'three';
import { Player } from './entities/Player.js';
import { SoldierManager } from './entities/Soldier.js';
import { MissileSystem } from './entities/Missile.js';
import { ExplosionSystem } from './effects/Explosions.js';
import { soundManager } from './audio/SoundManager.js';
import { JoystickController } from './controls/Joystick.js';
import { Operator } from './entities/Operator.js';
import { Scenario } from './world/Scenario.js';

class Game {
  constructor() {
    this.container = document.getElementById('canvas-container');
    this.scene = new THREE.Scene();

    this.camera = new THREE.PerspectiveCamera(62, window.innerWidth / window.innerHeight, 0.1, 380);

    this.targetCamera = new THREE.OrthographicCamera(-15, 15, 15, -15, 0.1, 100);
    this.targetCamera.rotation.x = -Math.PI / 2;

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    this.scenario = new Scenario(this.scene);
    this.operator = new Operator(this.scene, new THREE.Vector3(0, 0, 70));

    this.player = new Player(this.scene, this.camera, this.operator.position);
    this.soldierManager = new SoldierManager(this.scene);
    this.missileSystem = new MissileSystem(this.scene);
    this.explosionSystem = new ExplosionSystem(this.scene);

    this.joysticks = new JoystickController({
      leftZoneId: 'zone-left',
      rightZoneId: 'zone-right',
      leftStickId: 'stick-left',
      rightStickId: 'stick-right'
    });

    this.setupEvents();
    this.clock = new THREE.Clock();
    this.isPlaying = false;

    window.addEventListener('resize', () => this.onResize());
  }

  setupEvents() {
    const btnStart = document.getElementById('btn-start');
    const btnFullscreen = document.getElementById('btn-fullscreen');

    if (btnFullscreen) {
      btnFullscreen.addEventListener('click', () => {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(() => {});
        } else {
          document.exitFullscreen().catch(() => {});
        }
      });
    }

    if (btnStart) {
      btnStart.addEventListener('click', () => {
        document.getElementById('modal-start').style.display = 'none';
        this.isPlaying = true;
        this.clock.start();
        this.animate();
      });
    }
  }

  updateCompass() {
    const deg = Math.round(((-this.camera.rotation.y * 180 / Math.PI) % 360 + 360) % 360);
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const idx = Math.round(deg / 45) % 8;
    
    const compassText = document.getElementById('compass-text');
    if (compassText) {
      compassText.innerText = `${deg}° [ ${directions[idx]} ]`;
    }
  }

  animate() {
    if (!this.isPlaying) return;
    requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();

    this.player.update(delta, this.joysticks.input);
    this.scenario.update(delta);

    const inputs = this.player.getInputs(this.joysticks.input);
    const speed = Math.round((Math.abs(inputs.ry) + Math.abs(inputs.rx)) * 48);
    const rangeInfo = this.player.getRangeStatus();

    const teleSpd = document.getElementById('tele-spd');
    const teleAlt = document.getElementById('tele-alt');
    const teleRange = document.getElementById('tele-range');

    if (teleSpd) teleSpd.innerText = speed;
    if (teleAlt) teleAlt.innerText = Math.round(this.player.position.y);
    if (teleRange) teleRange.innerText = rangeInfo.km;

    this.updateCompass();

    this.renderer.setScissorTest(false);
    this.renderer.clear();

    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  new Game();
});'''

with open('src/main.js', 'w', encoding='utf-8') as f:
    f.write(main_code)

print("Projeto atualizado e reconstruído com sucesso!")
