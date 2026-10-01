import os

# 1. INDEX.HTML COM EFEITO DE VÍDEO FPV REAL E OSD COMPLETO
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

    /* FILTRO DE RUÍDO E LENS VIGNETTE ANALÓGICO */
    #lens-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 5; pointer-events: none;
      background: radial-gradient(circle, rgba(0,0,0,0) 50%, rgba(10,15,10,0.5) 80%, rgba(0,0,0,0.92) 100%);
    }

    #scanlines {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 6; pointer-events: none;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
      background-size: 100% 4px;
      opacity: 0.7;
    }

    /* BÚSSOLA TÁTICA */
    #compass-container {
      position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
      width: 280px; height: 26px; background: rgba(0, 0, 0, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 3px;
      display: flex; justify-content: center; align-items: center;
      overflow: hidden; z-index: 10; font-size: 11px; letter-spacing: 2px; color: #d0ded0;
    }
    #compass-indicator { position: absolute; top: -1px; color: #ff3c3c; font-weight: bold; font-size: 11px; }

    /* MIRA FPV MILITAR COM PITCH LADDER */
    #reticle-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 8; pointer-events: none;
      display: flex; justify-content: center; align-items: center;
    }

    /* TELEMETRIA OSD COMPLETA DA TRANSMISSÃO */
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

    /* CONTROLES TOUCH */
    .joystick-zone { position: absolute; bottom: 15px; width: 110px; height: 110px; border-radius: 50%; background: rgba(255, 255, 255, 0.04); border: 1px dashed rgba(255, 255, 255, 0.2); pointer-events: auto; z-index: 25; }
    #zone-left { left: 15px; }
    #zone-right { right: 15px; }
    .joystick-stick { width: 40px; height: 40px; border-radius: 50%; background: rgba(255, 255, 255, 0.3); border: 1px solid #fff; position: absolute; top: 35px; left: 35px; pointer-events: none; }

    #btn-drop-missile { position: absolute; bottom: 135px; right: 20px; width: 66px; height: 66px; border-radius: 50%; background: rgba(255, 60, 60, 0.45); border: 2px solid #ff3c3c; color: #fff; font-size: 22px; display: flex; justify-content: center; align-items: center; pointer-events: auto; z-index: 30; font-weight: bold; text-shadow: 0 0 5px #000; }
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

  <!-- RETÍCULO FPV MILITAR AUTÊNTICO -->
  <div id="reticle-overlay">
    <svg width="100%" height="100%" viewBox="0 0 800 450" preserveAspectRatio="none">
      <!-- Brackets de Curvatura da Câmera -->
      <path d="M 270 140 Q 240 225 270 310" stroke="rgba(255,255,255,0.35)" stroke-width="1.5" fill="none"/>
      <path d="M 530 140 Q 560 225 530 310" stroke="rgba(255,255,255,0.35)" stroke-width="1.5" fill="none"/>
      
      <!-- Escala de Inclinamento (Pitch Ladder) -->
      <line x1="360" y1="185" x2="385" y2="185" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
      <line x1="415" y1="185" x2="440" y2="185" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
      <line x1="360" y1="265" x2="385" y2="265" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
      <line x1="415" y1="265" x2="440" y2="265" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>

      <!-- Centro de Mira -->
      <circle cx="400" cy="225" r="3" fill="#ff3c3c"/>
      <circle cx="400" cy="225" r="12" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
    </svg>
  </div>

  <button id="btn-fullscreen" title="Tela Cheia">⛶</button>

  <div id="compass-container">
    <span id="compass-indicator">▼</span>
    <div id="compass-text">NW . . N . . NE . . E</div>
  </div>

  <!-- OSD ESQUERDA -->
  <div class="telemetry-left">
    <div><b>BAT:</b> 22.2V (4S)</div>
    <div><b>RSSI:</b> -65 dBm</div>
    <div><b>SAT:</b> 14 GPS</div>
    <div><b>MODE:</b> ANGLE</div>
  </div>

  <!-- OSD DIREITA -->
  <div class="telemetry-right">
    <div><b>SPD:</b> <span id="tele-spd">0</span> km/h</div>
    <div><b>ALT:</b> <span id="tele-alt">12</span> m</div>
    <div><b>DIST:</b> <span id="tele-range">0.10</span> / 3.00 km</div>
    <div><b>COORD:</b> 48.432°N 37.811°E</div>
  </div>

  <div id="pip-container">
    <div id="pip-title">CAM DESTINO</div>
  </div>

  <div id="zone-left" class="joystick-zone"><div id="stick-left" class="joystick-stick"></div></div>
  <div id="zone-right" class="joystick-zone"><div id="stick-right" class="joystick-stick"></div></div>

  <button id="btn-drop-missile">🚀</button>

  <div id="modal-start" class="modal">
    <h2 style="color:#ff3c3c; margin-bottom: 5px;">ZONA DE GUERRA — FPV KAMIKAZE</h2>
    <p style="font-size: 13px; line-height: 1.5; max-width: 480px; color: #a3b8a3;">
    🌲 <b>Cenário de Batalha:</b> Linhas de trincheiras em ziguezague, floresta destruída por artilharia e fumaça de combate.<br><br>
    📡 <b>Operador e Tubo:</b> Protegidos no abrigo de retaguarda.<br><br>
    🕹️ <b>Pilote com os dois analógicos e destrua os alvos inimigos!</b>
    </p>
    <button id="btn-start" class="btn-main">ENTRAR NA ZONA DE COMBATE</button>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 2. CENÁRIO REALISTA DE GUERRA (TRINCHEIRAS, CRATERAS, FUMAÇA, FLORESTA DESTRUIDA)
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
    // Atmosfera Nublada Típica do Front de Guerra
    this.scene.background = new THREE.Color(0x6b776e);
    this.scene.fog = new THREE.FogExp2(0x6b776e, 0.0065);

    const sun = new THREE.DirectionalLight(0xfff3db, 1.2);
    sun.position.set(80, 120, 50);
    this.scene.add(sun);

    const ambient = new THREE.HemisphereLight(0x6b776e, 0x2b3323, 0.7);
    this.scene.add(ambient);
  }

  buildWarTerrain() {
    // Terreno com variações de relevo e cor de lama/terra
    const groundGeo = new THREE.PlaneGeometry(400, 400, 80, 80);
    const posAttr = groundGeo.attributes.position;

    for (let i = 0; i < posAttr.count; i++) {
      const x = posAttr.getX(i);
      const y = posAttr.getY(i);
      // Relevo irregular
      const height = Math.sin(x * 0.04) * Math.cos(y * 0.04) * 1.2 + Math.sin(x * 0.1) * 0.4;
      posAttr.setZ(i, height);
    }
    groundGeo.computeVertexNormals();

    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x3b382b, // Solo de terra escura/lama
      roughness: 0.9,
      metalness: 0.1
    });

    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    this.scene.add(ground);
  }

  buildTrenchSystem() {
    const sandbagMat = new THREE.MeshStandardMaterial({ color: 0x5e523f, roughness: 0.9 });
    const woodMat = new THREE.MeshStandardMaterial({ color: 0x2b1e15, roughness: 0.8 });

    // Padrão de Trincheira em Ziguezague
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

      // Paredes de Sacos de Areia nas Trincheiras
      for (let d = 0; d < dist; d += 1.2) {
        const pos = start.clone().addScaledVector(dir, d);

        // Lado esquerdo e direito da vala
        for (let side of [-1.2, 1.2]) {
          const bag = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.4, 0.5), sandbagMat);
          const offset = new THREE.Vector3(side, 0.2, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), angle);
          bag.position.copy(pos).add(offset);
          bag.rotation.y = angle;
          this.scene.add(bag);

          const bagLayer2 = bag.clone();
          bagLayer2.position.y = 0.55;
          this.scene.add(bagLayer2);
        }

        // Estacas de suporte em madeira
        if (Math.random() > 0.6) {
          const post = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.6), woodMat);
          post.position.copy(pos).add(new THREE.Vector3(1.1, 0.8, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), angle));
          this.scene.add(post);
        }
      }
    }
  }

  buildWarForest() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x261c14, roughness: 0.9 });
    const burntMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.95 });
    const foliageMat = new THREE.MeshStandardMaterial({ color: 0x27361d, roughness: 0.8 });

    for (let i = 0; i < 90; i++) {
      const x = (Math.random() - 0.5) * 320;
      const z = (Math.random() - 0.5) * 320;

      // Evitar árvores no centro exato da pista
      if (Math.abs(x) < 12 && Math.abs(z) < 12) continue;

      const isDestroyed = Math.random() < 0.45; // 45% das árvores estão destruídas pela guerra

      if (isDestroyed) {
        // Árvores Partidas/Carbonizadas por Artilharia
        const height = 2 + Math.random() * 3.5;
        const stump = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.35, height, 6), burntMat);
        stump.position.set(x, height / 2, z);
        stump.rotation.z = (Math.random() - 0.5) * 0.2;
        this.scene.add(stump);
      } else {
        // Pinheiros Intactos
        const treeGroup = new THREE.Group();
        const height = 7 + Math.random() * 5;
        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.4, height, 8), trunkMat);
        trunk.position.y = height / 2;
        treeGroup.add(trunk);

        for (let c = 0; c < 3; c++) {
          const coneHeight = 3.5 - c * 0.5;
          const coneRadius = 2.4 - c * 0.6;
          const foliage = new THREE.Mesh(new THREE.ConeGeometry(coneRadius, coneHeight, 8), foliageMat);
          foliage.position.y = height * 0.4 + c * 2.0;
          treeGroup.add(foliage);
        }
        treeGroup.position.set(x, 0, z);
        this.scene.add(treeGroup);
      }
    }
  }

  buildCratersAndSmoke() {
    const craterMat = new THREE.MeshBasicMaterial({ color: 0x15120e });
    const smokeMat = new THREE.MeshBasicMaterial({ color: 0x555555, transparent: true, opacity: 0.35 });

    // Locais de Impacto de Artilharia
    const craterLocations = [
      new THREE.Vector3(-25, 0.05, -40),
      new THREE.Vector3(45, 0.05, -80),
      new THREE.Vector3(-70, 0.05, 50),
      new THREE.Vector3(15, 0.05, -120)
    ];

    craterLocations.forEach(loc => {
      // Anel da Cratera
      const craterRim = new THREE.Mesh(new THREE.RingGeometry(1.5, 4.5, 16), craterMat);
      craterRim.rotation.x = -Math.PI / 2;
      craterRim.position.copy(loc);
      this.scene.add(craterRim);

      // Emissor de Fumaça Tática
      for (let p = 0; p < 8; p++) {
        const particle = new THREE.Mesh(new THREE.SphereGeometry(0.8 + Math.random() * 0.8, 8, 8), smokeMat);
        particle.position.set(
          loc.x + (Math.random() - 0.5) * 2,
          loc.y + Math.random() * 4,
          loc.z + (Math.random() - 0.5) * 2
        );
        this.scene.add(particle);
        this.smokeParticles.push({
          mesh: particle,
          baseY: loc.y,
          speed: 0.6 + Math.random() * 0.8
        });
      }
    });
  }

  buildWreckedVehicles() {
    const rustedMat = new THREE.MeshStandardMaterial({ color: 0x211c18, roughness: 0.9 });
    for (let i = 0; i < 6; i++) {
      const tank = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(4.2, 1.5, 6.2), rustedMat);
      body.position.y = 0.75;
      tank.add(body);

      const turret = new THREE.Mesh(new THREE.BoxGeometry(2.5, 1.0, 3.0), rustedMat);
      turret.position.set(0, 1.8, -0.3);
      turret.rotation.y = Math.PI / 6; // Turreta danificada/girada
      tank.add(turret);

      const x = (Math.random() - 0.5) * 220;
      const z = (Math.random() - 0.5) * 220;
      tank.position.set(x, 0, z);
      tank.rotation.y = Math.random() * Math.PI * 2;
      this.scene.add(tank);
    }
  }

  update(delta) {
    // Animação Contínua das Colunas de Fumaça no Solo
    this.smokeParticles.forEach(p => {
      p.mesh.position.y += p.speed * delta;
      p.mesh.scale.addScalar(delta * 0.2);
      if (p.mesh.position.y > p.baseY + 12) {
        p.mesh.position.y = p.baseY + 0.5;
        p.mesh.scale.set(1, 1, 1);
      }
    });
  }
}
'''

with open('src/world/Scenario.js', 'w', encoding='utf-8') as f:
    f.write(scenario_code)

# 3. ATUALIZAÇÃO DO PLAYER COM FÍSICA E INCLINAMENTO FPV (src/entities/Player.js)
player_code = '''import * as THREE from 'three';

export class Player {
  constructor(scene, camera, operatorPosition) {
    this.scene = scene;
    this.camera = camera;
    this.operatorPos = operatorPosition || new THREE.Vector3(0, 0, 70);
    
    this.position = new THREE.Vector3(0, 12, 60);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
    
    // Tilt dinâmico da câmera para simular FPV real
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

  update(delta, input) {
    // Rotação YAW
    if (input.leftX) {
      this.rotation.y -= input.leftX * this.rotSpeed * delta;
      // Inclinamento Lateral (Banking/Roll) ao virar
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, -input.leftX * 0.25, delta * 5);
    } else {
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, 0, delta * 5);
    }

    // Altitude
    if (input.leftY) {
      this.position.y -= input.leftY * this.speed * delta;
    }

    // Movimento para frente/trás/lados
    const nextPos = this.position.clone();
    if (input.rightX || input.rightY) {
      const moveVec = new THREE.Vector3(input.rightX, 0, input.rightY);
      moveVec.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      nextPos.addScaledVector(moveVec, this.speed * delta);

      // Inclinamento Pitch para frente/trás ao acelerar
      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, -input.rightY * 0.2, delta * 5);
    } else {
      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, 0, delta * 5);
    }

    // Limites de Alcance Rádio do Operador
    const distToOperator = new THREE.Vector2(nextPos.x - this.operatorPos.x, nextPos.z - this.operatorPos.z).length();
    if (distToOperator <= this.maxRangeMeters) {
      this.position.copy(nextPos);
      this.currentDistance = distToOperator;
    }

    if (this.position.y < this.minAltitude) this.position.y = this.minAltitude;
    if (this.position.y > this.maxAltitude) this.position.y = this.maxAltitude;

    this.mesh.position.copy(this.position);
    this.mesh.rotation.copy(this.rotation);

    // Câmera FPV com Tilt Tático
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
}
'''

with open('src/entities/Player.js', 'w', encoding='utf-8') as f:
    f.write(player_code)

# 4. ATUALIZAÇÃO DO MAIN.JS
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

    const targetGeo = new THREE.RingGeometry(0.8, 1.0, 16);
    const targetMat = new THREE.MeshBasicMaterial({ color: 0xff3c3c, side: THREE.DoubleSide });
    this.targetMarker = new THREE.Mesh(targetGeo, targetMat);
    this.targetMarker.rotation.x = Math.PI / 2;
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

    this.clock = new THREE.Clock();
    this.isPlaying = false;
    this.recentExplosions = [];

    window.addEventListener('resize', () => this.onResize());
  }

  setupEvents() {
    const btnDrop = document.getElementById('btn-drop-missile');
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

    if (btnDrop) {
      btnDrop.addEventListener('touchstart', (e) => { e.preventDefault(); this.dropMissile(); });
      btnDrop.addEventListener('click', () => this.dropMissile());
    }

    if (btnStart) {
      btnStart.addEventListener('click', () => {
        document.getElementById('modal-start').style.display = 'none';
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(() => {});
        }
        this.isPlaying = true;
        this.clock.start();
        this.animate();
      });
    }
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

    const newImpacts = this.missileSystem.update(delta, this.soldierManager, this.explosionSystem, soundManager);
    if (newImpacts.length > 0) {
      this.recentExplosions.push(...newImpacts);
    }

    this.soldierManager.update(delta, this.player.position, this.recentExplosions);
    this.explosionSystem.update(delta);

    if (this.recentExplosions.length > 5) this.recentExplosions.shift();

    const rangeInfo = this.player.getRangeStatus();
    const speed = Math.round((Math.abs(this.joysticks.input.rightY) + Math.abs(this.joysticks.input.rightX)) * 48);

    document.getElementById('tele-spd').innerText = speed;
    document.getElementById('tele-alt').innerText = Math.round(this.player.position.y);
    document.getElementById('tele-range').innerText = `${rangeInfo.km}`;

    this.updateCompass();

    // RENDERIZAÇÃO
    this.renderer.setScissorTest(false);
    this.renderer.clear();

    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    const pipW = 145;
    const pipH = 105;
    const pipX = window.innerWidth - pipW - 10;
    const pipY = window.innerHeight - pipH - 54;

    this.renderer.setScissorTest(true);
    this.renderer.setViewport(pipX, pipY, pipW, pipH);
    this.renderer.setScissor(pipX, pipY, pipW, pipH);
    this.renderer.render(this.scene, this.targetCamera);
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

print("Ambiente de guerra imersivo, trincheiras e física FPV atualizados!")
