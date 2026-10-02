import os

# 1. JOYSTICK.JS COM ISOLAMENTO TOTAL VIA POINTER CAPTURE
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

    this.bindJoystick(leftZone, leftStick, true);
    this.bindJoystick(rightZone, rightStick, false);
  }

  bindJoystick(zone, stick, isLeft) {
    if (!zone || !stick) return;

    let activePointerId = null;

    const handleMove = (e) => {
      if (e.pointerId !== activePointerId) return;

      const rect = zone.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const maxRadius = rect.width / 2;

      let dx = e.clientX - centerX;
      let dy = e.clientY - centerY;
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

    const handleUp = (e) => {
      if (e.pointerId !== activePointerId) return;

      activePointerId = null;
      stick.style.transform = 'translate(0px, 0px)';

      if (isLeft) {
        this.input.leftX = 0;
        this.input.leftY = 0;
      } else {
        this.input.rightX = 0;
        this.input.rightY = 0;
      }

      try { zone.releasePointerCapture(e.pointerId); } catch(err) {}
    };

    zone.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      if (activePointerId !== null) return;

      activePointerId = e.pointerId;
      try { zone.setPointerCapture(e.pointerId); } catch(err) {}

      handleMove(e);
    });

    zone.addEventListener('pointermove', (e) => {
      e.preventDefault();
      handleMove(e);
    });

    zone.addEventListener('pointerup', (e) => {
      e.preventDefault();
      handleUp(e);
    });

    zone.addEventListener('pointercancel', (e) => {
      e.preventDefault();
      handleUp(e);
    });
  }
}'''

with open('src/controls/Joystick.js', 'w', encoding='utf-8') as f:
    f.write(joystick_code)

# 2. PLAYER.JS COM SUPORTE A CÂMERA 1ªP/3ªP E COMBATE/VISUAL
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

    this.viewMode = 'FPV'; // 'FPV' ou 'THIRD'
    this.opMode = 'COMBAT'; // 'COMBAT' ou 'VISUAL'

    this.orbitYaw = 0;
    this.orbitPitch = 0.3;
    this.orbitDistance = 5.0;

    this.speed = 22;
    this.rotSpeed = 2.0;
    this.minAltitude = 1.0;
    this.maxAltitude = 70.0;

    this.maxRangeMeters = 200;
    this.currentDistance = 0;

    this.buildDroneMesh();
  }

  buildDroneMesh() {
    this.droneGroup = new THREE.Group();

    const carbonMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.4 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.8 });
    const propMat = new THREE.MeshBasicMaterial({ color: 0x00ff96, transparent: true, opacity: 0.7 });
    const batteryMat = new THREE.MeshStandardMaterial({ color: 0xffaa00 });

    // Corpo Central
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.12, 0.6), carbonMat);
    this.droneGroup.add(body);

    // Bateria
    const battery = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.22, 0.5), batteryMat);
    battery.position.set(0, 0.16, 0);
    this.droneGroup.add(battery);

    // Câmera Frontal
    const cam = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.18, 0.25), metalMat);
    cam.position.set(0, 0.02, -0.35);
    this.droneGroup.add(cam);

    // 4 Motores e Hélices
    this.props = [];
    const positions = [
      { x: 0.5, z: -0.5 },
      { x: -0.5, z: -0.5 },
      { x: 0.5, z: 0.5 },
      { x: -0.5, z: 0.5 }
    ];

    positions.forEach((p, idx) => {
      const arm = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.04, 0.7), carbonMat);
      arm.position.set(p.x / 2, 0, p.z / 2);
      arm.rotation.y = Math.atan2(p.x, p.z);
      this.droneGroup.add(arm);

      const motor = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.12, 10), metalMat);
      motor.position.set(p.x, 0.06, p.z);
      this.droneGroup.add(motor);

      const propGroup = new THREE.Group();
      for (let b = 0; b < 3; b++) {
        const blade = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.01, 0.4), propMat);
        blade.rotation.y = (b * Math.PI * 2) / 3;
        blade.position.z = 0.16;
        propGroup.add(blade);
      }
      propGroup.position.set(p.x, 0.13, p.z);
      this.droneGroup.add(propGroup);
      this.props.push(propGroup);
    });

    this.droneGroup.visible = false;
    this.scene.add(this.droneGroup);
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
    return { lx, ly, rx, ry };
  }

  toggleViewMode() {
    this.viewMode = this.viewMode === 'FPV' ? 'THIRD' : 'FPV';
    return this.viewMode;
  }

  toggleOpMode() {
    this.opMode = this.opMode === 'COMBAT' ? 'VISUAL' : 'COMBAT';
    return this.opMode;
  }

  rotateOrbit(deltaYaw, deltaPitch) {
    this.orbitYaw += deltaYaw;
    this.orbitPitch = Math.max(-0.4, Math.min(1.1, this.orbitPitch + deltaPitch));
  }

  update(delta, rawInput) {
    const input = this.getInputs(rawInput);

    if (isNaN(this.position.x) || isNaN(this.position.y) || isNaN(this.position.z)) {
      this.position.set(0, 12, 60);
    }

    // Rotação YAW
    if (input.lx !== 0) {
      this.rotation.y -= input.lx * this.rotSpeed * delta;
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, -input.lx * 0.25, delta * 5);
    } else {
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, 0, delta * 5);
    }

    // Altitude
    if (input.ly !== 0) {
      this.position.y -= input.ly * this.speed * delta;
    }

    // Movimentação
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

    // Girar Hélices
    this.props.forEach(p => { p.rotation.y += 30 * delta; });

    this.droneGroup.position.copy(this.position);
    this.droneGroup.rotation.set(
      this.rotation.x + this.cameraTiltX,
      this.rotation.y,
      this.rotation.z + this.cameraRollZ,
      'YXZ'
    );

    // Câmera 1ªP vs 3ªP Órbita 360
    if (this.viewMode === 'FPV') {
      this.droneGroup.visible = false;
      this.camera.position.copy(this.position);
      this.camera.rotation.set(
        this.rotation.x + this.cameraTiltX,
        this.rotation.y,
        this.rotation.z + this.cameraRollZ,
        'YXZ'
      );
    } else {
      this.droneGroup.visible = true;
      const totalYaw = this.rotation.y + this.orbitYaw;
      const camOffset = new THREE.Vector3(
        Math.sin(totalYaw) * Math.cos(this.orbitPitch) * this.orbitDistance,
        Math.sin(this.orbitPitch) * this.orbitDistance + 0.6,
        Math.cos(totalYaw) * Math.cos(this.orbitPitch) * this.orbitDistance
      );
      this.camera.position.copy(this.position).add(camOffset);
      this.camera.lookAt(this.position);
    }
  }

  getRangeStatus() {
    const kmSimulated = ((this.currentDistance / this.maxRangeMeters) * 3.0).toFixed(2);
    const pct = (this.currentDistance / this.maxRangeMeters) * 100;
    return { km: kmSimulated, pct: pct };
  }
}'''

with open('src/entities/Player.js', 'w', encoding='utf-8') as f:
    f.write(player_code)

# 3. INDEX.HTML COM BOTÕES Z-INDEX ELEVADOS
index_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>OPERAÇÃO GHOST — WAR ZONE FPV</title>
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; touch-action: none; }
    html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; color: #00ff96; }
    #canvas-container { width: 100%; height: 100%; position: absolute; top:0; left:0; z-index: 1; }

    #lens-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none;
      background: radial-gradient(circle, rgba(0,0,0,0) 65%, rgba(0,0,0,0.6) 100%);
    }

    #compass-container {
      position: absolute; top: 8px; left: 50%; transform: translateX(-50%);
      padding: 3px 12px; background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(0, 255, 150, 0.4);
      border-radius: 4px; z-index: 10; font-size: 10px; font-weight: bold; color: #00ff96;
    }

    .telemetry-left {
      position: absolute; top: 10px; left: 10px; z-index: 10; pointer-events: none;
      font-size: 9px; line-height: 1.4; color: #00ff96; text-shadow: 1px 1px 2px #000;
      background: rgba(0, 0, 0, 0.5); padding: 4px 8px; border-radius: 3px; border-left: 2px solid #00ff96;
    }

    .telemetry-right {
      position: absolute; top: 115px; right: 10px; z-index: 10; pointer-events: none;
      font-size: 9px; line-height: 1.4; color: #00ff96; text-shadow: 1px 1px 2px #000; text-align: right;
      background: rgba(0, 0, 0, 0.5); padding: 4px 8px; border-radius: 3px; border-right: 2px solid #00ff96;
    }

    .btn-top {
      position: absolute; top: 8px; height: 34px;
      background: rgba(0, 15, 8, 0.85); border: 1.5px solid #00ff96;
      color: #00ff96; font-size: 11px; font-weight: bold; border-radius: 4px; display: flex;
      justify-content: center; align-items: center; pointer-events: auto; z-index: 100; cursor: pointer;
      padding: 0 10px; box-shadow: 0 0 6px rgba(0,255,150,0.3);
    }
    .btn-top:active { background: #00ff96; color: #000; }
    #btn-fullscreen { right: 8px; width: 34px; padding: 0; }
    #btn-view-mode { right: 48px; }
    #btn-op-mode { right: 140px; }
    
    #pip-container {
      position: absolute; top: 10px; right: 235px; width: 110px; height: 82px;
      border: 1px solid rgba(0, 255, 150, 0.5); background: rgba(0, 10, 5, 0.8); z-index: 20; pointer-events: none;
      border-radius: 2px;
    }
    #pip-title {
      position: absolute; top: 2px; left: 4px; font-size: 7px; font-weight: bold; color: #00ff96;
      background: rgba(0,0,0,0.6); padding: 1px 3px; border-radius: 2px;
    }

    #reticle-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 8; pointer-events: none;
      display: flex; justify-content: center; align-items: center;
    }

    .joystick-zone {
      position: absolute; bottom: 12px; width: 100px; height: 100px; border-radius: 50%;
      background: rgba(255, 255, 255, 0.05); border: 1.5px solid rgba(0, 255, 150, 0.3);
      pointer-events: auto; z-index: 80; touch-action: none;
    }
    #zone-left { left: 12px; }
    #zone-right { right: 12px; }
    .joystick-stick {
      width: 38px; height: 38px; border-radius: 50%;
      background: rgba(0, 255, 150, 0.4); border: 1.5px solid #00ff96;
      position: absolute; top: 31px; left: 31px; pointer-events: none;
    }

    #btn-drop-missile {
      position: absolute; bottom: 125px; right: 18px; width: 54px; height: 54px; border-radius: 50%;
      background: rgba(255, 60, 60, 0.35); border: 2px solid #ff3c3c; color: #ff3c3c;
      font-size: 20px; display: flex; justify-content: center; align-items: center;
      pointer-events: auto; z-index: 90; transition: all 0.15s;
    }
    #btn-drop-missile:active { background: rgba(255, 60, 60, 0.9); color: #fff; transform: scale(0.92); }

    .modal {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5, 8, 5, 0.95);
      z-index: 200; display: flex; flex-direction: column; justify-content: center; align-items: center;
      text-align: center; padding: 20px;
    }
    .btn-main {
      pointer-events: auto; background: #00ff96; color: #000; border: none; padding: 12px 28px;
      font-size: 14px; font-weight: bold; border-radius: 3px; cursor: pointer; letter-spacing: 1px;
    }
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

  <div id="compass-container">
    <span id="compass-text">0° [ N ]</span>
  </div>

  <div class="telemetry-left">
    <div><b>BAT:</b> 22.2V</div>
    <div><b>RSSI:</b> -65dBm</div>
    <div><b>SAT:</b> 14 GPS</div>
  </div>

  <div class="telemetry-right">
    <div><b>SPD:</b> <span id="tele-spd">0</span> km/h</div>
    <div><b>ALT:</b> <span id="tele-alt">12</span> m</div>
    <div><b>DIST:</b> <span id="tele-range">0.00</span> km</div>
  </div>

  <div id="pip-container">
    <div id="pip-title">ALVO 📷</div>
  </div>

  <button id="btn-op-mode" class="btn-top">⚔️ COMBATE</button>
  <button id="btn-view-mode" class="btn-top">🎥 FPV</button>
  <button id="btn-fullscreen" class="btn-top" title="Tela Cheia">⛶</button>

  <div id="reticle-overlay">
    <svg width="100%" height="100%" viewBox="0 0 800 450" preserveAspectRatio="none">
      <line x1="385" y1="225" x2="395" y2="225" stroke="#00ff96" stroke-width="1" opacity="0.6"/>
      <line x1="405" y1="225" x2="415" y2="225" stroke="#00ff96" stroke-width="1" opacity="0.6"/>
      <line x1="400" y1="210" x2="400" y2="220" stroke="#00ff96" stroke-width="1" opacity="0.6"/>
      <line x1="400" y1="230" x2="400" y2="240" stroke="#00ff96" stroke-width="1" opacity="0.6"/>
      <circle cx="400" cy="225" r="2" fill="#ff3c3c"/>
    </svg>
  </div>

  <div id="zone-left" class="joystick-zone"><div id="stick-left" class="joystick-stick"></div></div>
  <div id="zone-right" class="joystick-zone"><div id="stick-right" class="joystick-stick"></div></div>

  <button id="btn-drop-missile">🚀</button>

  <div id="modal-start" class="modal">
    <h2 style="color:#00ff96; margin-bottom: 8px;">ZONA DE GUERRA — FPV</h2>
    <p style="font-size: 12px; line-height: 1.5; max-width: 420px; color: #a3b8a3; margin-bottom: 20px;">
      <b>🎥 FPV / 3ª PESSOA:</b> Mude o modo de visão no topo.<br>
      <b>⚔️ COMBATE / VISUAL:</b> Alterne o HUD para visão limpa.
    </p>
    <button id="btn-start" class="btn-main">DECOLAR</button>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 4. MAIN.JS FIXANDO EVENTOS DE PONTEIRO E BOTÕES
main_code = '''import * as THREE from 'three';
import { Player } from './entities/Player.js';
import { SoldierManager } from './entities/Soldier.js';
import { MissileSystem } from './entities/Missile.js';
import { ExplosionSystem } from './effects/Explosions.js';
import { JoystickController } from './controls/Joystick.js';
import { Operator } from './entities/Operator.js';
import { Scenario } from './world/Scenario.js';

class Game {
  constructor() {
    this.container = document.getElementById('canvas-container');
    this.scene = new THREE.Scene();

    this.camera = new THREE.PerspectiveCamera(62, window.innerWidth / window.innerHeight, 0.1, 380);
    this.targetCamera = new THREE.OrthographicCamera(-12, 12, 12, -12, 0.1, 100);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    const targetGeo = new THREE.RingGeometry(0.8, 1.3, 16);
    const targetMat = new THREE.MeshBasicMaterial({ color: 0xff3c3c, side: THREE.DoubleSide });
    this.targetMarker = new THREE.Mesh(targetGeo, targetMat);
    this.targetMarker.rotation.x = -Math.PI / 2;
    this.scene.add(this.targetMarker);

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
    this.setupOrbitTouch();
    this.clock = new THREE.Clock();
    this.isPlaying = false;

    window.addEventListener('resize', () => this.onResize());
  }

  bindButton(id, callback) {
    const btn = document.getElementById(id);
    if (!btn) return;
    const trigger = (e) => {
      e.preventDefault();
      e.stopPropagation();
      callback();
    };
    btn.addEventListener('pointerdown', trigger);
    btn.addEventListener('click', trigger);
  }

  setupEvents() {
    this.bindButton('btn-fullscreen', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });

    this.bindButton('btn-view-mode', () => {
      const mode = this.player.toggleViewMode();
      const btn = document.getElementById('btn-view-mode');
      if (btn) btn.innerText = mode === 'FPV' ? '🎥 FPV' : '🚁 3ª PESSOA';
    });

    this.bindButton('btn-op-mode', () => {
      const op = this.player.toggleOpMode();
      const btn = document.getElementById('btn-op-mode');
      if (btn) btn.innerText = op === 'COMBAT' ? '⚔️ COMBATE' : '👁️ VISUAL';

      const reticle = document.getElementById('reticle-overlay');
      const pip = document.getElementById('pip-container');
      const drop = document.getElementById('btn-drop-missile');

      if (op === 'VISUAL') {
        if (reticle) reticle.style.display = 'none';
        if (pip) pip.style.display = 'none';
        if (drop) drop.style.display = 'none';
        this.targetMarker.visible = false;
      } else {
        if (reticle) reticle.style.display = 'flex';
        if (pip) pip.style.display = 'block';
        if (drop) drop.style.display = 'flex';
        this.targetMarker.visible = true;
      }
    });

    this.bindButton('btn-drop-missile', () => {
      this.dropMissile();
    });

    this.bindButton('btn-start', () => {
      document.getElementById('modal-start').style.display = 'none';
      this.isPlaying = true;
      this.clock.start();
      this.animate();
    });
  }

  setupOrbitTouch() {
    let lastX = 0, lastY = 0;
    let isDragging = false;

    window.addEventListener('pointerdown', (e) => {
      if (e.clientX > 120 && e.clientX < window.innerWidth - 120 && e.clientY < window.innerHeight - 120) {
        isDragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
      }
    });

    window.addEventListener('pointermove', (e) => {
      if (!isDragging || this.player.viewMode !== 'THIRD') return;
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      this.player.rotateOrbit(-dx * 0.008, -dy * 0.008);
      lastX = e.clientX;
      lastY = e.clientY;
    });

    window.addEventListener('pointerup', () => { isDragging = false; });
    window.addEventListener('pointercancel', () => { isDragging = false; });
  }

  getTargetImpactPosition() {
    const fwd = this.player.getForwardDirection();
    const impact = this.player.position.clone().add(fwd.multiplyScalar(this.player.position.y * 0.85));
    impact.y = 0.05;
    return impact;
  }

  dropMissile() {
    if (!this.isPlaying) return;
    const targetPos = this.getTargetImpactPosition();
    this.missileSystem.spawnMissile(this.player.position, targetPos);
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

    const targetPos = this.getTargetImpactPosition();
    this.targetMarker.position.copy(targetPos);

    this.targetCamera.position.set(targetPos.x, targetPos.y + 25, targetPos.z);
    this.targetCamera.lookAt(targetPos.x, targetPos.y, targetPos.z);

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

    // Renderizar Câmera Principal
    this.renderer.setScissorTest(false);
    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    // Renderizar Câmera Secundária (Apenas no Modo Combate)
    if (this.player.opMode === 'COMBAT') {
      const pipW = 110;
      const pipH = 82;
      const pipX = window.innerWidth - pipW - 235;
      const pipY = window.innerHeight - pipH - 10;

      this.renderer.setScissorTest(true);
      this.renderer.setScissor(pipX, pipY, pipW, pipH);
      this.renderer.setViewport(pipX, pipY, pipW, pipH);
      this.renderer.render(this.scene, this.targetCamera);
    }
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

print("Correção de ponteiros e botões aplicada!")
