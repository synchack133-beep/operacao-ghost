import os

# 1. PLAYER.JS - NOVO MODELO 3D DE DRONE E MODOS DE CÂMERA 360°
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

    // Modos de Voo e Câmera
    this.viewMode = 'FPV'; // 'FPV' ou 'THIRD'
    this.opMode = 'COMBAT'; // 'COMBAT' ou 'VISUAL'

    // Ângulos da Câmera em 3ª Pessoa (Órbita 360)
    this.orbitYaw = 0;
    this.orbitPitch = 0.3;
    this.orbitDistance = 4.5;

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

    const carbonMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.5 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x777777, metalness: 0.8, roughness: 0.2 });
    const propMat = new THREE.MeshBasicMaterial({ color: 0x00ff96, transparent: true, opacity: 0.6 });
    const batteryMat = new THREE.MeshStandardMaterial({ color: 0xffaa00, roughness: 0.6 });
    const lensMat = new THREE.MeshBasicMaterial({ color: 0x000000 });

    // Chassi Central X-Frame
    const centerPlate = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.5), carbonMat);
    this.droneGroup.add(centerPlate);

    // Bateria LiPo no Topo
    const battery = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.2, 0.55), batteryMat);
    battery.position.set(0, 0.14, 0);
    this.droneGroup.add(battery);

    // Câmera FPV na Frente
    const camMount = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.18, 0.2), carbonMat);
    camMount.position.set(0, 0.05, -0.3);
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.1, 12), lensMat);
    lens.rotation.x = Math.PI / 2;
    lens.position.set(0, 0.05, -0.38);
    this.droneGroup.add(camMount);
    this.droneGroup.add(lens);

    // 4 Braços e Motores com Hélices
    this.props = [];
    const armPositions = [
      { x: 0.45, z: -0.45, cw: true },
      { x: -0.45, z: -0.45, cw: false },
      { x: 0.45, z: 0.45, cw: false },
      { x: -0.45, z: 0.45, cw: true }
    ];

    armPositions.forEach(p => {
      // Braço de Carbono
      const armGeo = new THREE.BoxGeometry(0.08, 0.04, 0.65);
      const arm = new THREE.Mesh(armGeo, carbonMat);
      arm.position.set(p.x / 2, 0, p.z / 2);
      arm.rotation.y = Math.atan2(p.x, p.z);
      this.droneGroup.add(arm);

      // Motor Metálico
      const motor = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.12, 12), metalMat);
      motor.position.set(p.x, 0.06, p.z);
      this.droneGroup.add(motor);

      // Hélice de 3 Pás
      const propGroup = new THREE.Group();
      for (let b = 0; b < 3; b++) {
        const blade = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.01, 0.38), propMat);
        blade.rotation.y = (b * Math.PI * 2) / 3;
        blade.position.z = 0.15;
        propGroup.add(blade);
      }
      propGroup.position.set(p.x, 0.13, p.z);
      this.droneGroup.add(propGroup);
      this.props.push({ mesh: propGroup, cw: p.cw });
    });

    // Antena VTX na Traseira
    const antennaStem = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.3, 8), carbonMat);
    antennaStem.position.set(0, 0.18, 0.35);
    antennaStem.rotation.x = -0.3;
    const antennaTop = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), metalMat);
    antennaTop.position.set(0, 0.3, 0.42);
    this.droneGroup.add(antennaStem);
    this.droneGroup.add(antennaTop);

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
    return {
      lx: isNaN(lx) ? 0 : lx,
      ly: isNaN(ly) ? 0 : ly,
      rx: isNaN(rx) ? 0 : rx,
      ry: isNaN(ry) ? 0 : ry
    };
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
    this.orbitPitch = Math.max(-0.5, Math.min(1.2, this.orbitPitch + deltaPitch));
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

    // Altitude / Pitch Vertical
    if (input.ly !== 0) {
      this.position.y -= input.ly * this.speed * delta;
    }

    // Movimentação Horizontal
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

    // Animação de rotação contínua das hélices
    this.props.forEach(p => {
      p.mesh.rotation.y += (p.cw ? 35 : -35) * delta;
    });

    this.droneGroup.position.copy(this.position);
    this.droneGroup.rotation.set(
      this.rotation.x + this.cameraTiltX,
      this.rotation.y,
      this.rotation.z + this.cameraRollZ,
      'YXZ'
    );

    // Ajuste da Câmera (1ªP vs 3ªP Órbita 360)
    if (this.viewMode === 'FPV') {
      this.droneGroup.visible = false; // Esconde o modelo próprio em FPV
      this.camera.position.copy(this.position);
      this.camera.rotation.set(
        this.rotation.x + this.cameraTiltX,
        this.rotation.y,
        this.rotation.z + this.cameraRollZ,
        'YXZ'
      );
    } else {
      this.droneGroup.visible = true; // Mostra o drone em 3ª pessoa
      const totalYaw = this.rotation.y + this.orbitYaw;
      const camOffset = new THREE.Vector3(
        Math.sin(totalYaw) * Math.cos(this.orbitPitch) * this.orbitDistance,
        Math.sin(this.orbitPitch) * this.orbitDistance + 0.5,
        Math.cos(totalYaw) * Math.cos(this.orbitPitch) * this.orbitDistance
      );
      this.camera.position.copy(this.position).add(camOffset);
      this.camera.lookAt(this.position);
    }
  }

  getRangeStatus() {
    const kmSimulated = ((this.currentDistance / this.maxRangeMeters) * 3.0).toFixed(2);
    const pct = (this.currentDistance / this.maxRangeMeters) * 100;
    return { km: kmSimulated, pct: pct, isWarning: pct > 80 };
  }
}
'''

with open('src/entities/Player.js', 'w', encoding='utf-8') as f:
    f.write(player_code)

# 2. INDEX.HTML - ADICIONA BOTÕES DE VISÃO 360° E MODO COMBATE/VISUAL
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
      padding: 3px 12px; background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(0, 255, 150, 0.3);
      border-radius: 4px; z-index: 10; font-size: 10px; font-weight: bold; letter-spacing: 1px; color: #00ff96;
    }

    .telemetry-left {
      position: absolute; top: 10px; left: 10px; z-index: 10; pointer-events: none;
      font-size: 9px; line-height: 1.4; color: #00ff96; text-shadow: 1px 1px 2px #000;
      background: rgba(0, 0, 0, 0.4); padding: 4px 8px; border-radius: 3px; border-left: 2px solid #00ff96;
    }

    .telemetry-right {
      position: absolute; top: 115px; right: 10px; z-index: 10; pointer-events: none;
      font-size: 9px; line-height: 1.4; color: #00ff96; text-shadow: 1px 1px 2px #000; text-align: right;
      background: rgba(0, 0, 0, 0.4); padding: 4px 8px; border-radius: 3px; border-right: 2px solid #00ff96;
    }

    .btn-top {
      position: absolute; top: 8px; width: 32px; height: 32px;
      background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(0, 255, 150, 0.4);
      color: #00ff96; font-size: 12px; font-weight: bold; border-radius: 4px; display: flex;
      justify-content: center; align-items: center; pointer-events: auto; z-index: 35; cursor: pointer;
    }
    #btn-fullscreen { right: 8px; }
    #btn-view-mode { right: 45px; width: auto; padding: 0 8px; }
    #btn-op-mode { right: 115px; width: auto; padding: 0 8px; }
    
    #pip-container {
      position: absolute; top: 10px; right: 180px; width: 120px; height: 90px;
      border: 1px solid rgba(0, 255, 150, 0.5); background: rgba(0, 10, 5, 0.7); z-index: 20; pointer-events: none;
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
      position: absolute; bottom: 12px; width: 95px; height: 95px; border-radius: 50%;
      background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.15);
      pointer-events: auto; z-index: 25; opacity: 0.5; transition: opacity 0.2s;
    }
    .joystick-zone:active { opacity: 0.85; }
    #zone-left { left: 12px; }
    #zone-right { right: 12px; }
    .joystick-stick {
      width: 35px; height: 35px; border-radius: 50%;
      background: rgba(0, 255, 150, 0.3); border: 1px solid #00ff96;
      position: absolute; top: 30px; left: 30px; pointer-events: none;
    }

    #btn-drop-missile {
      position: absolute; bottom: 120px; right: 15px; width: 52px; height: 52px; border-radius: 50%;
      background: rgba(255, 60, 60, 0.3); border: 1.5px solid #ff3c3c; color: #ff3c3c;
      font-size: 18px; display: flex; justify-content: center; align-items: center;
      pointer-events: auto; z-index: 30; opacity: 0.7; transition: all 0.2s;
    }
    #btn-drop-missile:active { background: rgba(255, 60, 60, 0.8); color: #fff; transform: scale(0.92); opacity: 1; }

    .modal {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5, 8, 5, 0.95);
      z-index: 100; display: flex; flex-direction: column; justify-content: center; align-items: center;
      text-align: center; padding: 20px;
    }
    .btn-main {
      pointer-events: auto; background: #00ff96; color: #000; border: none; padding: 12px 26px;
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
      🚁 <b>Modos de Câmera:</b> Alterne entre 1ª Pessoa (FPV) e 3ª Pessoa (Órbita 360°).<br>
      ⚔️ <b>Modos de Jogo:</b> Alterne entre Combate e Visual (Tela Limpa).
    </p>
    <button id="btn-start" class="btn-main">DECOLAR</button>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 3. MAIN.JS - SUPORTE A TOUCH DE ÓRBITA 360° E TROCA DE MODOS
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

  setupEvents() {
    const btnStart = document.getElementById('btn-start');
    const btnFullscreen = document.getElementById('btn-fullscreen');
    const btnViewMode = document.getElementById('btn-view-mode');
    const btnOpMode = document.getElementById('btn-op-mode');
    const btnDrop = document.getElementById('btn-drop-missile');

    if (btnFullscreen) {
      btnFullscreen.addEventListener('click', () => {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(() => {});
        } else {
          document.exitFullscreen().catch(() => {});
        }
      });
    }

    if (btnViewMode) {
      btnViewMode.addEventListener('click', () => {
        const mode = this.player.toggleViewMode();
        btnViewMode.innerText = mode === 'FPV' ? '🎥 FPV' : '🚁 3ª PESSOA';
      });
    }

    if (btnOpMode) {
      btnOpMode.addEventListener('click', () => {
        const op = this.player.toggleOpMode();
        btnOpMode.innerText = op === 'COMBAT' ? '⚔️ COMBATE' : '👁️ VISUAL';

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
    }

    if (btnDrop) {
      btnDrop.addEventListener('touchstart', (e) => { e.preventDefault(); this.dropMissile(); });
      btnDrop.addEventListener('click', () => this.dropMissile());
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

  // Permite arrastar o dedo na área central da tela para girar 360° em 3ª pessoa
  setupOrbitTouch() {
    let lastX = 0, lastY = 0;
    let isDragging = false;

    window.addEventListener('touchstart', (e) => {
      for (let i = 0; i < e.changedTouches.length; i++) {
        const t = e.changedTouches[i];
        if (t.clientX > 120 && t.clientX < window.innerWidth - 120) {
          isDragging = true;
          lastX = t.clientX;
          lastY = t.clientY;
          break;
        }
      }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (!isDragging || this.player.viewMode !== 'THIRD') return;
      for (let i = 0; i < e.touches.length; i++) {
        const t = e.touches[i];
        if (t.clientX > 100 && t.clientX < window.innerWidth - 100) {
          const dx = t.clientX - lastX;
          const dy = t.clientY - lastY;
          this.player.rotateOrbit(-dx * 0.008, -dy * 0.008);
          lastX = t.clientX;
          lastY = t.clientY;
          break;
        }
      }
    }, { passive: true });

    window.addEventListener('touchend', () => { isDragging = false; });
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

    // 1. CÂMERA PRINCIPAL
    this.renderer.setScissorTest(false);
    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    // 2. CÂMERA SECUNDÁRIA (PIP) - Apenas se estiver em modo Combate
    if (this.player.opMode === 'COMBAT') {
      const pipW = 120;
      const pipH = 90;
      const pipX = window.innerWidth - pipW - 180;
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

print("Drone e modos de câmera 360°/Combate/Visual atualizados com sucesso!")
