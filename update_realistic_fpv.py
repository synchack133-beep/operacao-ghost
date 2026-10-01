import os

# 1. INDEX.HTML (HUD ÓPTICO MILITAR COMPLETO)
index_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>OPERAÇÃO GHOST — MILITARY FPV DRONE</title>
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; touch-action: none; }
    html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; color: #ffffff; }
    #canvas-container { width: 100%; height: 100%; position: absolute; top:0; left:0; z-index: 1; }

    /* MÁSCARA E LENTE VIGNETTE FPV */
    #lens-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 5; pointer-events: none;
      background: radial-gradient(circle, rgba(0,0,0,0) 55%, rgba(0,0,0,0.65) 85%, rgba(0,0,0,0.95) 100%);
      box-shadow: inset 0 0 80px rgba(0,0,0,0.8);
    }

    /* BÚSSOLA TÁTICA NO TOPO */
    #compass-container {
      position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
      width: 280px; height: 26px; background: rgba(0, 0, 0, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 4px;
      display: flex; justify-content: center; align-items: center;
      overflow: hidden; z-index: 10; font-size: 11px; letter-spacing: 2px;
      color: #e0e0e0; text-shadow: 0 0 4px #000;
    }
    #compass-indicator { position: absolute; top: 0; color: #ff3c3c; font-weight: bold; font-size: 12px; }

    /* RETÍCULO E CURVAS DA CÂMERA */
    #reticle-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 8; pointer-events: none;
      display: flex; justify-content: center; align-items: center;
    }

    /* TELEMETRIA LATERAL */
    .telemetry-box {
      position: absolute; top: 50px; left: 15px; z-index: 10; pointer-events: none;
      font-size: 11px; line-height: 1.6; text-shadow: 1px 1px 2px #000; color: #e2e8f0;
      background: rgba(0, 0, 0, 0.35); padding: 8px 12px; border-left: 2px solid #00c8ff; border-radius: 2px;
    }

    #btn-fullscreen { position: absolute; top: 10px; right: 10px; width: 40px; height: 40px; background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(255,255,255,0.4); color: #fff; font-size: 18px; border-radius: 4px; display: flex; justify-content: center; align-items: center; pointer-events: auto; z-index: 35; cursor: pointer; }
    
    /* MONITOR PIP MÍSSIL */
    #pip-container { position: absolute; top: 58px; right: 10px; width: 150px; height: 110px; border: 1px solid rgba(0, 200, 255, 0.7); background: rgba(0, 10, 20, 0.9); z-index: 20; pointer-events: none; }
    #pip-title { position: absolute; top: -16px; left: 0; width: 100%; font-size: 8px; font-weight: bold; color: #00c8ff; text-align: center; letter-spacing: 1px; }

    /* CONTROLES TOUCH */
    .joystick-zone { position: absolute; bottom: 15px; width: 110px; height: 110px; border-radius: 50%; background: rgba(255, 255, 255, 0.05); border: 1px dashed rgba(255, 255, 255, 0.25); pointer-events: auto; z-index: 25; }
    #zone-left { left: 15px; }
    #zone-right { right: 15px; }
    .joystick-stick { width: 40px; height: 40px; border-radius: 50%; background: rgba(255, 255, 255, 0.3); border: 1px solid #fff; position: absolute; top: 35px; left: 35px; pointer-events: none; }

    /* BOTÃO DE ATAQUE */
    #btn-drop-missile { position: absolute; bottom: 135px; right: 20px; width: 66px; height: 66px; border-radius: 50%; background: rgba(255, 60, 60, 0.4); border: 2px solid #ff3c3c; color: #fff; font-size: 22px; display: flex; justify-content: center; align-items: center; pointer-events: auto; z-index: 30; font-weight: bold; text-shadow: 0 0 5px #000; }
    #btn-drop-missile:active { background: rgba(255, 60, 60, 0.8); transform: scale(0.92); }

    .modal { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(10, 15, 12, 0.96); z-index: 100; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
    .btn-main { pointer-events: auto; background: #ff3c3c; color: #fff; border: none; padding: 14px 28px; font-size: 15px; font-weight: bold; border-radius: 4px; cursor: pointer; letter-spacing: 1px; }
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

  <!-- RETÍCULO ÓPTICO MILITAR SVG -->
  <div id="reticle-overlay">
    <svg width="100%" height="100%" viewBox="0 0 800 450" preserveAspectRatio="none">
      <!-- Brackets de Câmera FPV -->
      <path d="M 280 150 Q 250 225 280 300" stroke="rgba(255,255,255,0.4)" stroke-width="1.5" fill="none"/>
      <path d="M 520 150 Q 550 225 520 300" stroke="rgba(255,255,255,0.4)" stroke-width="1.5" fill="none"/>
      <!-- Mira Central -->
      <circle cx="400" cy="225" r="4" fill="none" stroke="#ff3c3c" stroke-width="1.5"/>
      <line x1="380" y1="225" x2="392" y2="225" stroke="rgba(255,255,255,0.6)" stroke-width="1.5"/>
      <line x1="408" y1="225" x2="420" y2="225" stroke="rgba(255,255,255,0.6)" stroke-width="1.5"/>
      <line x1="400" y1="205" x2="400" y2="217" stroke="rgba(255,255,255,0.6)" stroke-width="1.5"/>
      <line x1="400" y1="233" x2="400" y2="245" stroke="rgba(255,255,255,0.6)" stroke-width="1.5"/>
    </svg>
  </div>

  <button id="btn-fullscreen" title="Tela Cheia">⛶</button>

  <!-- BÚSSOLA -->
  <div id="compass-container">
    <span id="compass-indicator">▼</span>
    <div id="compass-text">NW . . N . . NE . . E . . SE</div>
  </div>

  <!-- TELEMETRIA -->
  <div class="telemetry-box">
    <div><b>SPD:</b> <span id="tele-spd">0</span> km/h</div>
    <div><b>ALT:</b> <span id="tele-alt">12</span> m</div>
    <div><b>RANGE:</b> <span id="tele-range">0.10</span> / 3.00 km</div>
    <div><b>TARGETS:</b> <span id="tele-targets" style="color:#ff3c3c;">10 ALVOS</span></div>
  </div>

  <div id="pip-container">
    <div id="pip-title">CAM DESTINO (MÍSSIL)</div>
  </div>

  <div id="zone-left" class="joystick-zone"><div id="stick-left" class="joystick-stick"></div></div>
  <div id="zone-right" class="joystick-zone"><div id="stick-right" class="joystick-stick"></div></div>

  <button id="btn-drop-missile">🚀</button>

  <div id="modal-start" class="modal">
    <h2>MILITARY FPV DRONE RECON</h2>
    <p><b>SISTEMA DE ATAQUE & RECONHECIMENTO</b><br><br>
    📡 <b>Cenário de Guerra:</b> Campo aberto com floresta e blindados inimigos.<br>
    🕹️ <b>Controles:</b> Use os analógicos para pilotagem e o botão vermelho para disparar mísseis.</p>
    <button id="btn-start" class="btn-main">ENGATAR MISSÃO</button>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 2. CENÁRIO REALISTA DE CAMPO DE BATALHA (src/world/Scenario.js)
scenario_code = '''import * as THREE from 'three';

export class Scenario {
  constructor(scene) {
    this.scene = scene;
    this.setupAtmosphere();
    this.buildTerrain();
    this.buildPineForest();
    this.buildMilitaryVehicles();
    this.buildRuins();
  }

  setupAtmosphere() {
    // Céu e Névoa Tática Nublada
    this.scene.background = new THREE.Color(0x8fa3a8);
    this.scene.fog = new THREE.FogExp2(0x8fa3a8, 0.007);

    // Luz Sol Quente
    const dirLight = new THREE.DirectionalLight(0xfffaed, 1.4);
    dirLight.position.set(60, 100, 40);
    this.scene.add(dirLight);

    const hemiLight = new THREE.HemisphereLight(0x8fa3a8, 0x3b4a24, 0.6);
    this.scene.add(hemiLight);
  }

  buildTerrain() {
    // Textura de Solo / Campo de Batalha (Verde Terra)
    const groundGeo = new THREE.PlaneGeometry(350, 350, 64, 64);
    
    // Pequena variação de relevo no terreno
    const posAttr = groundGeo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const x = posAttr.getX(i);
      const y = posAttr.getY(i);
      const z = Math.sin(x * 0.05) * Math.cos(y * 0.05) * 0.8;
      posAttr.setZ(i, z);
    }
    groundGeo.computeVertexNormals();

    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x3d4d26,
      roughness: 0.95,
      metalness: 0.05
    });

    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    this.scene.add(ground);
  }

  buildPineForest() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x2b1e17, roughness: 0.9 });
    const foliageMat = new THREE.MeshStandardMaterial({ color: 0x1f3318, roughness: 0.8 });

    for (let i = 0; i < 60; i++) {
      const treeGroup = new THREE.Group();

      const height = 6 + Math.random() * 5;
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.4, height, 8), trunkMat);
      trunk.position.y = height / 2;
      treeGroup.add(trunk);

      // Camadas de Folha Cone (Pinheiro)
      for (let c = 0; c < 3; c++) {
        const coneHeight = 3 + c * 0.8;
        const coneRadius = 2.2 - c * 0.5;
        const foliage = new THREE.Mesh(new THREE.ConeGeometry(coneRadius, coneHeight, 8), foliageMat);
        foliage.position.y = height * 0.5 + c * 1.8;
        treeGroup.add(foliage);
      }

      const x = (Math.random() - 0.5) * 260;
      const z = (Math.random() - 0.5) * 260;
      if (Math.abs(x) > 15 || Math.abs(z) > 15) {
        treeGroup.position.set(x, 0, z);
        this.scene.add(treeGroup);
      }
    }
  }

  buildMilitaryVehicles() {
    const camoMat = new THREE.MeshStandardMaterial({ color: 0x2e3b2b, roughness: 0.7 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x1a1f1a, roughness: 0.5 });

    for (let i = 0; i < 8; i++) {
      const tank = new THREE.Group();

      // Chassi
      const body = new THREE.Mesh(new THREE.BoxGeometry(4.0, 1.4, 6.0), camoMat);
      body.position.y = 0.8;
      tank.add(body);

      // Torreta
      const turret = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.0, 3.2), camoMat);
      turret.position.set(0, 1.9, -0.4);
      tank.add(turret);

      // Canhão
      const cannon = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 4.0), metalMat);
      cannon.position.set(0, 1.9, -3.0);
      cannon.rotation.x = Math.PI / 2;
      tank.add(cannon);

      const x = (Math.random() - 0.5) * 200;
      const z = (Math.random() - 0.5) * 200;
      tank.position.set(x, 0, z);
      tank.rotation.y = Math.random() * Math.PI * 2;
      this.scene.add(tank);
    }
  }

  buildRuins() {
    const concreteMat = new THREE.MeshStandardMaterial({ color: 0x5a605c, roughness: 0.9 });
    for (let i = 0; i < 10; i++) {
      const wall = new THREE.Mesh(new THREE.BoxGeometry(8, 4, 1.0), concreteMat);
      const x = (Math.random() - 0.5) * 220;
      const z = (Math.random() - 0.5) * 220;
      wall.position.set(x, 2, z);
      wall.rotation.y = Math.random() * Math.PI;
      this.scene.add(wall);
    }
  }
}
'''

with open('src/world/Scenario.js', 'w', encoding='utf-8') as f:
    f.write(scenario_code)

# 3. ATUALIZAÇÃO DO MAIN.JS COM BÚSSOLA E TELEMETRIA
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

    this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 350);

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
    const impact = this.player.position.clone().add(fwd.multiplyScalar(this.player.position.y * 0.8));
    impact.y = 0.05;
    return impact;
  }

  dropMissile() {
    if (!this.isPlaying) return;
    const targetPos = this.getTargetImpactPosition();
    this.missileSystem.spawnMissile(this.player.position, targetPos);
  }

  updateCompass() {
    // Converte rotação da câmera em graus de bússola
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

    // Atualização da Telemetria FPV Realista
    const rangeInfo = this.player.getRangeStatus();
    const speed = Math.round((Math.abs(this.joysticks.input.rightY) + Math.abs(this.joysticks.input.rightX)) * 42);

    document.getElementById('tele-spd').innerText = speed;
    document.getElementById('tele-alt').innerText = Math.round(this.player.position.y);
    document.getElementById('tele-range').innerText = `${rangeInfo.km}`;
    document.getElementById('tele-targets').innerText = `${this.soldierManager.getAliveCount()} ALVOS`;

    this.updateCompass();

    // RENDERIZAÇÃO
    this.renderer.setScissorTest(false);
    this.renderer.clear();

    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    const pipW = 150;
    const pipH = 110;
    const pipX = window.innerWidth - pipW - 10;
    const pipY = window.innerHeight - pipH - 58;

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

print("Visual FPV realista e HUD militar aplicados com sucesso!")
