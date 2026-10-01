import os

# 1. ATUALIZAÇÃO DO INDEX.HTML (Botão de Tela Cheia + Ajuste de Layout)
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
    
    /* BOTÃO TELA CHEIA */
    #btn-fullscreen { position: absolute; top: 10px; right: 10px; width: 44px; height: 44px; background: rgba(0, 255, 150, 0.2); border: 1px solid #00ff96; color: #00ff96; font-size: 20px; border-radius: 6px; display: flex; justify-content: center; align-items: center; pointer-events: auto; z-index: 35; cursor: pointer; }
    #btn-fullscreen:active { background: rgba(0, 255, 150, 0.6); }

    /* MOLDURA CÂMERA PIP */
    #pip-container { position: absolute; top: 62px; right: 10px; width: 150px; height: 110px; border: 2px solid #00c8ff; background: rgba(0, 10, 20, 0.85); z-index: 20; pointer-events: none; box-shadow: 0 0 10px rgba(0,200,255,0.4); }
    #pip-title { position: absolute; top: -16px; left: 0; width: 100%; font-size: 8px; font-weight: bold; color: #00c8ff; text-align: center; }

    /* CONTROLES TOUCH */
    .joystick-zone { position: absolute; bottom: 15px; width: 110px; height: 110px; border-radius: 50%; background: rgba(0, 255, 150, 0.08); border: 2px dashed rgba(0, 255, 150, 0.4); pointer-events: auto; z-index: 25; }
    #zone-left { left: 15px; }
    #zone-right { right: 15px; }

    .joystick-stick { width: 44px; height: 44px; border-radius: 50%; background: rgba(0, 255, 150, 0.4); border: 2px solid #00ff96; position: absolute; top: 33px; left: 33px; pointer-events: none; }

    /* BOTÃO SOLTAR MÍSSIL */
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
        <div id="alt-info" style="font-size: 10px; color: #00c8ff;">ALTITUDE: 15m</div>
      </div>
    </div>
  </div>

  <div id="pip-container">
    <div id="pip-title">CAM DESTINO (MÍSSIL)</div>
  </div>

  <!-- JOYSTICKS -->
  <div id="zone-left" class="joystick-zone"><div id="stick-left" class="joystick-stick"></div></div>
  <div id="zone-right" class="joystick-zone"><div id="stick-right" class="joystick-stick"></div></div>

  <!-- BOTÃO SOLTAR MÍSSIL -->
  <button id="btn-drop-missile">🚀</button>

  <div id="modal-start" class="modal">
    <h1>OPERAÇÃO GHOST 3D</h1>
    <p><b>GUERRA DE DRONES & CÂMERA DE DESTINO</b><br><br>
    🕹️ <b>Analógico Esquerdo:</b> Altitude (Subir/Descer) e Girar<br>
    🕹️ <b>Analógico Direito:</b> Mover pelo campo de batalha<br>
    🚀 <b>Botão Míssil:</b> Lança munição no alvo exibido no monitor superior (PiP)</p>
    <button id="btn-start" class="btn-main">INICIAR COMBATE</button>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 2. ATUALIZAÇÃO DO PLAYER.JS (ALTITUDE MÍNIMA DO CHÃO FIXADA)
player_code = '''import * as THREE from 'three';

export class Player {
  constructor(scene, camera) {
    this.scene = scene;
    this.camera = camera;
    
    this.position = new THREE.Vector3(0, 12, 25);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
    
    this.speed = 15;
    this.rotSpeed = 1.8;
    this.minAltitude = 1.2; // Impedir que o drone desça abaixo do chão
    this.maxAltitude = 50.0;

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

    if (input.rightX || input.rightY) {
      const moveVec = new THREE.Vector3(input.rightX, 0, input.rightY);
      moveVec.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      this.position.addScaledVector(moveVec, this.speed * delta);
    }

    // BLOQUEIO DE COLISÃO COM O SOLO
    if (this.position.y < this.minAltitude) {
      this.position.y = this.minAltitude;
    }
    if (this.position.y > this.maxAltitude) {
      this.position.y = this.maxAltitude;
    }

    this.mesh.position.copy(this.position);
    this.mesh.rotation.copy(this.rotation);

    this.camera.position.copy(this.position);
    this.camera.rotation.copy(this.rotation);
  }
}
'''

with open('src/entities/Player.js', 'w', encoding='utf-8') as f:
    f.write(player_code)

# 3. ATUALIZAÇÃO DO MAIN.JS (EVENTO DE TELA CHEIA E VIEWPORT PIP)
main_code = '''import * as THREE from 'three';
import { Player } from './entities/Player.js';
import { SoldierManager } from './entities/Soldier.js';
import { MissileSystem } from './entities/Missile.js';
import { ExplosionSystem } from './effects/Explosions.js';
import { soundManager } from './audio/SoundManager.js';
import { JoystickController } from './controls/Joystick.js';

class Game {
  constructor() {
    this.container = document.getElementById('canvas-container');
    
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a100d);
    this.scene.fog = new THREE.FogExp2(0x0a100d, 0.015);

    this.camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 200);

    this.targetCamera = new THREE.OrthographicCamera(-15, 15, 15, -15, 0.1, 100);
    this.targetCamera.rotation.x = -Math.PI / 2;

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00ff96, 1.2);
    dirLight.position.set(30, 50, 30);
    this.scene.add(dirLight);

    const targetGeo = new THREE.RingGeometry(0.8, 1.0, 16);
    const targetMat = new THREE.MeshBasicMaterial({ color: 0xff3c3c, side: THREE.DoubleSide });
    this.targetMarker = new THREE.Mesh(targetGeo, targetMat);
    this.targetMarker.rotation.x = Math.PI / 2;
    this.scene.add(this.targetMarker);

    this.player = new Player(this.scene, this.camera);
    this.soldierManager = new SoldierManager(this.scene);
    this.missileSystem = new MissileSystem(this.scene);
    this.explosionSystem = new ExplosionSystem(this.scene);

    this.joysticks = new JoystickController({
      leftZoneId: 'zone-left',
      rightZoneId: 'zone-right',
      leftStickId: 'stick-left',
      rightStickId: 'stick-right'
    });

    this.buildTerrain();
    this.setupEvents();

    this.clock = new THREE.Clock();
    this.isPlaying = false;
    this.recentExplosions = [];

    window.addEventListener('resize', () => this.onResize());
  }

  buildTerrain() {
    const grid = new THREE.GridHelper(160, 80, 0x00ff96, 0x003318);
    this.scene.add(grid);

    const groundGeo = new THREE.PlaneGeometry(160, 160);
    const groundMat = new THREE.MeshBasicMaterial({ color: 0x050d08, side: THREE.DoubleSide });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = Math.PI / 2;
    ground.position.y = -0.05;
    this.scene.add(ground);

    const trenchMat = new THREE.MeshStandardMaterial({ color: 0x1f1a14 });
    for (let i = 0; i < 12; i++) {
      const wall = new THREE.Mesh(new THREE.BoxGeometry(12, 1.2, 1.5), trenchMat);
      wall.position.set((Math.random() - 0.5) * 70, 0.6, (Math.random() - 0.5) * 70);
      wall.rotation.y = Math.random() * Math.PI;
      this.scene.add(wall);
    }
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

    document.getElementById('enemy-count').innerText = `INIMIGOS: ${this.soldierManager.getAliveCount()} / 10`;
    document.getElementById('alt-info').innerText = `ALTITUDE: ${Math.round(this.player.position.y)}m`;

    this.renderer.setScissorTest(false);
    this.renderer.clear();

    // 1. Visão Geral (Tela Cheia)
    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    // 2. Visão PiP
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

print("Ajustes concluídos com sucesso!")
