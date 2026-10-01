import os

os.makedirs('src/world', exist_ok=True)
os.makedirs('src/entities', exist_ok=True)

# 1. INDEX.HTML
index_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>OPERAÇÃO GHOST — DRONE WARFARE</title>
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; touch-action: none; }
    html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; color: #00ff96; }
    #canvas-container { width: 100%; height: 100%; position: absolute; top:0; left:0; z-index: 1; }

    #hud { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10; pointer-events: none; display: flex; flex-direction: column; justify-content: space-between; padding: 10px; }
    .hud-header { display: flex; justify-content: space-between; align-items: flex-start; background: rgba(0, 20, 10, 0.85); padding: 8px 12px; border: 1px solid rgba(0, 255, 150, 0.5); border-radius: 6px; width: calc(100% - 180px); }
    
    #btn-fullscreen { position: absolute; top: 10px; right: 10px; width: 44px; height: 44px; background: rgba(0, 255, 150, 0.2); border: 1px solid #00ff96; color: #00ff96; font-size: 20px; border-radius: 6px; display: flex; justify-content: center; align-items: center; pointer-events: auto; z-index: 35; cursor: pointer; }
    #btn-fullscreen:active { background: rgba(0, 255, 150, 0.6); }

    #pip-container { position: absolute; top: 62px; right: 10px; width: 150px; height: 110px; border: 2px solid #00c8ff; background: rgba(0, 10, 20, 0.85); z-index: 20; pointer-events: none; box-shadow: 0 0 10px rgba(0,200,255,0.4); }
    #pip-title { position: absolute; top: -16px; left: 0; width: 100%; font-size: 8px; font-weight: bold; color: #00c8ff; text-align: center; }

    .joystick-zone { position: absolute; bottom: 15px; width: 110px; height: 110px; border-radius: 50%; background: rgba(0, 255, 150, 0.08); border: 2px dashed rgba(0, 255, 150, 0.4); pointer-events: auto; z-index: 25; }
    #zone-left { left: 15px; }
    #zone-right { right: 15px; }

    .joystick-stick { width: 44px; height: 44px; border-radius: 50%; background: rgba(0, 255, 150, 0.4); border: 2px solid #00ff96; position: absolute; top: 33px; left: 33px; pointer-events: none; }

    #btn-drop-missile { position: absolute; bottom: 135px; right: 20px; width: 68px; height: 68px; border-radius: 50%; background: rgba(255, 180, 0, 0.35); border: 2px solid #ffb400; color: #ffb400; font-size: 22px; display: flex; justify-content: center; align-items: center; pointer-events: auto; z-index: 30; font-weight: bold; }
    #btn-drop-missile:active { background: rgba(255, 180, 0, 0.8); transform: scale(0.92); }

    .modal { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 10, 5, 0.95); z-index: 100; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
    .btn-main { pointer-events: auto; background: #00ff96; color: #000; border: none; padding: 14px 28px; font-size: 15px; font-weight: bold; border-radius: 6px; cursor: pointer; }
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

  <button id="btn-fullscreen" title="Tela Cheia">⛶</button>

  <div id="hud">
    <div class="hud-header">
      <div>
        <div style="font-size: 9px; font-weight: bold; color: #00ff96;">DRONE FPV RECON</div>
        <div id="enemy-count" style="font-size: 11px; font-weight: bold; color: #ff3c3c; margin-top: 2px;">INIMIGOS: 10/10</div>
      </div>
      <div style="text-align: right;">
        <div id="alt-info" style="font-size: 10px; color: #00c8ff;">ALTITUDE: 12m</div>
        <div id="range-info" style="font-size: 10px; color: #00ff96; margin-top: 2px;">ALCANCE OP: 0.10 / 3.00 km</div>
      </div>
    </div>
  </div>

  <div id="pip-container">
    <div id="pip-title">CAM DESTINO (MÍSSIL)</div>
  </div>

  <div id="zone-left" class="joystick-zone"><div id="stick-left" class="joystick-stick"></div></div>
  <div id="zone-right" class="joystick-zone"><div id="stick-right" class="joystick-stick"></div></div>

  <button id="btn-drop-missile">🚀</button>

  <div id="modal-start" class="modal">
    <h1>OPERAÇÃO GHOST 3D</h1>
    <p><b>CENÁRIO EXPANDIDO & OPERADOR DE DRONE</b><br><br>
    📡 <b>Operador e Tubo de Lançamento:</b> Localizados na retaguarda em uma posição fortificada.<br>
    📡 <b>Alcance Limitado:</b> Máximo de 3.00 km de distância do operador.<br>
    🕹️ <b>Controles:</b> Use os dois analógicos e lance os mísseis no monitor superior (PiP).</p>
    <button id="btn-start" class="btn-main">INICIAR COMBATE</button>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 2. CREAÇÃO DO OPERADOR E TUBO DE LANÇAMENTO (src/entities/Operator.js)
operator_code = '''import * as THREE from 'three';

export class Operator {
  constructor(scene, position = new THREE.Vector3(0, 0, 70)) {
    this.scene = scene;
    this.position = position;
    this.group = new THREE.Group();

    this.buildOperator();
    this.buildLauncherTube();
    this.buildBunker();

    this.group.position.copy(this.position);
    this.scene.add(this.group);
  }

  buildOperator() {
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0x2e3d2c });
    const gearMat = new THREE.MeshStandardMaterial({ color: 0x111111 });

    const bodyGeo = new THREE.BoxGeometry(0.8, 1.3, 0.5);
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 0.65;
    this.group.add(body);

    const headGeo = new THREE.BoxGeometry(0.45, 0.45, 0.45);
    const head = new THREE.Mesh(headGeo, bodyMat);
    head.position.set(0, 1.5, 0);

    const gogglesGeo = new THREE.BoxGeometry(0.5, 0.18, 0.22);
    const goggles = new THREE.Mesh(gogglesGeo, gearMat);
    goggles.position.set(0, 1.55, -0.2);

    this.group.add(head);
    this.group.add(goggles);

    const tabletGeo = new THREE.BoxGeometry(0.6, 0.05, 0.4);
    const tabletMat = new THREE.MeshBasicMaterial({ color: 0x00ff96 });
    const tablet = new THREE.Mesh(tabletGeo, tabletMat);
    tablet.position.set(0, 0.9, -0.4);
    tablet.rotation.x = 0.4;
    this.group.add(tablet);
  }

  buildLauncherTube() {
    const tubeGeo = new THREE.CylinderGeometry(0.22, 0.22, 2.0, 16);
    const tubeMat = new THREE.MeshStandardMaterial({ color: 0x1f261d, roughness: 0.8 });
    const tube = new THREE.Mesh(tubeGeo, tubeMat);
    tube.position.set(1.4, 0.8, -0.4);
    tube.rotation.x = -Math.PI / 4;
    this.group.add(tube);

    const legGeo = new THREE.CylinderGeometry(0.04, 0.04, 1.1);
    const legMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
    const leg1 = new THREE.Mesh(legGeo, legMat);
    leg1.position.set(1.1, 0.5, -0.2);
    leg1.rotation.z = 0.3;
    this.group.add(leg1);

    const leg2 = new THREE.Mesh(legGeo, legMat);
    leg2.position.set(1.7, 0.5, -0.2);
    leg2.rotation.z = -0.3;
    this.group.add(leg2);
  }

  buildBunker() {
    const sandbagMat = new THREE.MeshStandardMaterial({ color: 0x736551, roughness: 0.9 });
    for (let i = -1.8; i <= 1.8; i += 0.7) {
      const bag1 = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.28, 0.4), sandbagMat);
      bag1.position.set(i, 0.14, -0.9);
      this.group.add(bag1);

      const bag2 = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.28, 0.4), sandbagMat);
      bag2.position.set(i, 0.42, -0.9);
      this.group.add(bag2);
    }

    const poleGeo = new THREE.CylinderGeometry(0.04, 0.04, 3.8);
    const poleMat = new THREE.MeshStandardMaterial({ color: 0x444444 });
    const pole = new THREE.Mesh(poleGeo, poleMat);
    pole.position.set(-1.8, 1.9, 0);
    this.group.add(pole);

    const dishGeo = new THREE.ConeGeometry(0.5, 0.25, 16);
    const dish = new THREE.Mesh(dishGeo, poleMat);
    dish.position.set(-1.8, 3.6, -0.15);
    dish.rotation.x = Math.PI / 3;
    this.group.add(dish);
  }
}
'''

with open('src/entities/Operator.js', 'w', encoding='utf-8') as f:
    f.write(operator_code)

# 3. CREAÇÃO DO CENÁRIO EXPANDIDO (src/world/Scenario.js)
scenario_code = '''import * as THREE from 'three';

export class Scenario {
  constructor(scene) {
    this.scene = scene;
    this.buildTerrain();
    this.buildRuins();
    this.buildDeadTrees();
    this.buildVehicles();
  }

  buildTerrain() {
    const grid = new THREE.GridHelper(300, 150, 0x00ff96, 0x002211);
    this.scene.add(grid);

    const groundGeo = new THREE.PlaneGeometry(300, 300);
    const groundMat = new THREE.MeshBasicMaterial({ color: 0x040a06, side: THREE.DoubleSide });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = Math.PI / 2;
    ground.position.y = -0.05;
    this.scene.add(ground);
  }

  buildRuins() {
    const wallMat = new THREE.MeshStandardMaterial({ color: 0x222b25, roughness: 0.9 });
    for (let i = 0; i < 18; i++) {
      const w = 6 + Math.random() * 8;
      const h = 3 + Math.random() * 5;
      const wall = new THREE.Mesh(new THREE.BoxGeometry(w, h, 1.2), wallMat);
      
      const x = (Math.random() - 0.5) * 180;
      const z = (Math.random() - 0.5) * 180 - 10;
      wall.position.set(x, h / 2, z);
      wall.rotation.y = Math.random() * Math.PI;
      this.scene.add(wall);
    }
  }

  buildDeadTrees() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x1a120b });
    for (let i = 0; i < 25; i++) {
      const h = 4 + Math.random() * 5;
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.35, h), trunkMat);
      const x = (Math.random() - 0.5) * 220;
      const z = (Math.random() - 0.5) * 220 - 10;
      trunk.position.set(x, h / 2, z);
      this.scene.add(trunk);
    }
  }

  buildVehicles() {
    const vehicleMat = new THREE.MeshStandardMaterial({ color: 0x332a1e, roughness: 0.8 });
    for (let i = 0; i < 7; i++) {
      const tankGroup = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(3.8, 1.6, 5.5), vehicleMat);
      body.position.y = 0.8;
      tankGroup.add(body);

      const turret = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.0, 2.8), vehicleMat);
      turret.position.set(0, 2.0, -0.4);
      tankGroup.add(turret);

      const cannon = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 3.8), vehicleMat);
      cannon.position.set(0, 2.0, -2.8);
      cannon.rotation.x = Math.PI / 2;
      tankGroup.add(cannon);

      const x = (Math.random() - 0.5) * 160;
      const z = (Math.random() - 0.5) * 160;
      tankGroup.position.set(x, 0, z);
      tankGroup.rotation.y = Math.random() * Math.PI * 2;
      this.scene.add(tankGroup);
    }
  }
}
'''

with open('src/world/Scenario.js', 'w', encoding='utf-8') as f:
    f.write(scenario_code)

# 4. PLAYER COM CÁLCULO DE DISTÂNCIA / ALCANCE MÁXIMO (src/entities/Player.js)
player_code = '''import * as THREE from 'three';

export class Player {
  constructor(scene, camera, operatorPosition) {
    this.scene = scene;
    this.camera = camera;
    this.operatorPos = operatorPosition || new THREE.Vector3(0, 0, 70);
    
    this.position = new THREE.Vector3(0, 12, 60);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
    
    this.speed = 18;
    this.rotSpeed = 1.8;
    this.minAltitude = 1.2;
    this.maxAltitude = 60.0;

    // Alcance Máximo Rádio (Representando 3.00 km = 180 metros no espaço do jogo)
    this.maxRangeMeters = 180;
    this.currentDistance = 0;

    const bodyGeo = new THREE.BoxGeometry(1.2, 0.2, 1.2);
    const mat = new THREE.MeshStandardMaterial({ color: 0x00ff96, wireframe: true });
    this.mesh = new THREE.Mesh(bodyGeo, mat);
    this.scene.add(this.mesh);
  }

  getForwardDirection() {
    const fwd = new THREE.Vector3(0, -0.4, -1);
    fwd.applyEuler(this.rotation);
    return fwd.normalize();
  }

  update(delta, input) {
    if (input.leftX) {
      this.rotation.y -= input.leftX * this.rotSpeed * delta;
    }

    if (input.leftY) {
      this.position.y -= input.leftY * this.speed * delta;
    }

    const nextPos = this.position.clone();
    if (input.rightX || input.rightY) {
      const moveVec = new THREE.Vector3(input.rightX, 0, input.rightY);
      moveVec.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      nextPos.addScaledVector(moveVec, this.speed * delta);
    }

    // Calcular distância até o Operador
    const distToOperator = new THREE.Vector2(nextPos.x - this.operatorPos.x, nextPos.z - this.operatorPos.z).length();
    
    // Bloquear movimento se exceder o alcance
    if (distToOperator <= this.maxRangeMeters) {
      this.position.copy(nextPos);
      this.currentDistance = distToOperator;
    }

    if (this.position.y < this.minAltitude) this.position.y = this.minAltitude;
    if (this.position.y > this.maxAltitude) this.position.y = this.maxAltitude;

    this.mesh.position.copy(this.position);
    this.mesh.rotation.copy(this.rotation);

    this.camera.position.copy(this.position);
    this.camera.rotation.copy(this.rotation);
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

# 5. ATUALIZAÇÃO DO MAIN.JS
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
    this.scene.background = new THREE.Color(0x0a100d);
    this.scene.fog = new THREE.FogExp2(0x0a100d, 0.012);

    this.camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 300);

    this.targetCamera = new THREE.OrthographicCamera(-15, 15, 15, -15, 0.1, 100);
    this.targetCamera.rotation.x = -Math.PI / 2;

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00ff96, 1.2);
    dirLight.position.set(30, 60, 30);
    this.scene.add(dirLight);

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

    const rangeInfo = this.player.getRangeStatus();
    document.getElementById('enemy-count').innerText = `INIMIGOS: ${this.soldierManager.getAliveCount()} / 10`;
    document.getElementById('alt-info').innerText = `ALTITUDE: ${Math.round(this.player.position.y)}m`;
    
    const rangeElem = document.getElementById('range-info');
    if (rangeElem) {
      rangeElem.innerText = rangeInfo.isWarning 
        ? `⚠️ SINAL FRACO: ${rangeInfo.km} / 3.00 km` 
        : `ALCANCE OP: ${rangeInfo.km} / 3.00 km`;
      rangeElem.style.color = rangeInfo.isWarning ? '#ff3c3c' : '#00ff96';
    }

    this.renderer.setScissorTest(false);
    this.renderer.clear();

    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    const pipW = 150;
    const pipH = 110;
    const pipX = window.innerWidth - pipW - 10;
    const pipY = window.innerHeight - pipH - 62;

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

print("Cenário, operador e alcance rádio atualizados com sucesso!")
