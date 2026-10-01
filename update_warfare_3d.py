import os

# 1. IA DOS SOLDADOS INIMIGOS NAS TRINCHEIRAS (src/entities/Soldier.js)
soldier_code = '''import * as THREE from 'three';

export class SoldierManager {
  constructor(scene) {
    this.scene = scene;
    this.soldiers = [];
    this.initSoldiers(10);
  }

  initSoldiers(count) {
    const bodyGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.9, 8);
    const headGeo = new THREE.SphereGeometry(0.2, 8, 8);
    
    const matSoldier = new THREE.MeshStandardMaterial({ color: 0xeb3c3c, roughness: 0.5 });
    const matCover = new THREE.MeshStandardMaterial({ color: 0xff8c00 });

    for (let i = 0; i < count; i++) {
      const group = new THREE.Group();
      
      const body = new THREE.Mesh(bodyGeo, matSoldier);
      body.position.y = 0.45;
      group.add(body);

      const head = new THREE.Mesh(headGeo, matSoldier);
      head.position.y = 1.0;
      group.add(head);

      // Posicionamento aleatório pelo mapa
      const x = (Math.random() - 0.5) * 80;
      const z = (Math.random() - 0.5) * 80;
      group.position.set(x, 0, z);

      this.scene.add(group);

      this.soldiers.push({
        mesh: group,
        materials: [matSoldier, matCover],
        health: 100,
        alive: true,
        state: 'PATROL', // PATROL, COVER
        patrolTarget: new THREE.Vector3((Math.random() - 0.5) * 70, 0, (Math.random() - 0.5) * 70),
        timer: 0
      });
    }
  }

  update(delta, dronePos, explosions) {
    this.soldiers.forEach(s => {
      if (!s.alive) return;

      const distDrone = s.mesh.position.distanceTo(dronePos);

      // Reação a explosões próximas
      explosions.forEach(exp => {
        if (s.mesh.position.distanceTo(exp.position) < 12.0) {
          s.state = 'COVER';
          s.timer = 4.0; // Fuga por 4 segundos
        }
      });

      if (s.state === 'COVER') {
        s.timer -= delta;
        // Corre na direção oposta ao drone
        const escapeDir = new THREE.Vector3().subVectors(s.mesh.position, dronePos).normalize();
        escapeDir.y = 0;
        s.mesh.position.addScaledVector(escapeDir, delta * 4.5);

        if (s.timer <= 0) s.state = 'PATROL';
      } else {
        // Patrulha
        const dir = new THREE.Vector3().subVectors(s.patrolTarget, s.mesh.position);
        dir.y = 0;
        if (dir.length() < 1.0) {
          s.patrolTarget.set((Math.random() - 0.5) * 70, 0, (Math.random() - 0.5) * 70);
        } else {
          dir.normalize();
          s.mesh.position.addScaledVector(dir, delta * 1.8);
          s.mesh.lookAt(s.patrolTarget.x, s.mesh.position.y, s.patrolTarget.z);
        }
      }
    });
  }

  takeDamageAt(impactPos, radius, damage) {
    this.soldiers.forEach(s => {
      if (s.alive && s.mesh.position.distanceTo(impactPos) <= radius) {
        s.health -= damage;
        if (s.health <= 0) {
          s.alive = false;
          s.mesh.rotation.x = Math.PI / 2; // Soldado cai ao solo
          s.mesh.position.y = 0.1;
        }
      }
    });
  }

  getAliveCount() {
    return this.soldiers.filter(s => s.alive).length;
  }
}
'''

with open('src/entities/Soldier.js', 'w', encoding='utf-8') as f:
    f.write(soldier_code)

# 2. SISTEMA DE MÍSSEIS TÁTICOS (src/entities/Missile.js)
missile_code = '''import * as THREE from 'three';

export class MissileSystem {
  constructor(scene) {
    this.scene = scene;
    this.missiles = [];
    this.geo = new THREE.CylinderGeometry(0.08, 0.08, 0.6, 6);
    this.mat = new THREE.MeshBasicMaterial({ color: 0xffcc00 });
  }

  spawnMissile(startPos, targetPos) {
    const mesh = new THREE.Mesh(this.geo, this.mat);
    mesh.position.copy(startPos);
    this.scene.add(mesh);

    const dir = new THREE.Vector3().subVectors(targetPos, startPos).normalize();

    this.missiles.push({
      mesh: mesh,
      target: targetPos.clone(),
      dir: dir,
      speed: 25.0,
      active: true
    });
  }

  update(delta, soldierManager, explosionSystem, soundManager) {
    const impactEvents = [];

    this.missiles.forEach((m, index) => {
      if (!m.active) return;

      m.mesh.position.addScaledVector(m.dir, m.speed * delta);

      // Checa se atingiu o alvo ou o solo
      if (m.mesh.position.distanceTo(m.target) < 1.2 || m.mesh.position.y <= 0.2) {
        m.active = false;
        this.scene.remove(m.mesh);

        const impactPos = m.mesh.position.clone();
        impactPos.y = 0;

        // Dano em área nos soldados
        soldierManager.takeDamageAt(impactPos, 8.0, 100);
        explosionSystem.createExplosion(impactPos);
        if (soundManager) soundManager.playLaser();

        impactEvents.push({ position: impactPos });
        this.missiles.splice(index, 1);
      }
    });

    return impactEvents;
  }
}
'''

with open('src/entities/Missile.js', 'w', encoding='utf-8') as f:
    f.write(missile_code)

# 3. INTERFACE COM BOTÃO DE MÍSSIL E CÂMERA PIP (index.html)
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
    .hud-header { display: flex; justify-content: space-between; align-items: flex-start; background: rgba(0, 20, 10, 0.85); padding: 8px 12px; border: 1px solid rgba(0, 255, 150, 0.5); border-radius: 6px; }
    
    /* MOLDURA CÂMERA DE DESTINO PIP (Canto Superior Direito) */
    #pip-container { position: absolute; top: 65px; right: 12px; width: 160px; height: 120px; border: 2px solid #00c8ff; background: rgba(0, 10, 20, 0.8); z-index: 20; pointer-events: none; box-shadow: 0 0 10px rgba(0,200,255,0.4); }
    #pip-title { position: absolute; top: -16px; left: 0; width: 100%; font-size: 8px; font-weight: bold; color: #00c8ff; text-align: center; }

    /* CONTROLES TOUCH */
    .joystick-zone { position: absolute; bottom: 15px; width: 110px; height: 110px; border-radius: 50%; background: rgba(0, 255, 150, 0.08); border: 2px dashed rgba(0, 255, 150, 0.4); pointer-events: auto; z-index: 25; }
    #zone-left { left: 15px; }
    #zone-right { right: 15px; }

    .joystick-stick { width: 44px; height: 44px; border-radius: 50%; background: rgba(0, 255, 150, 0.4); border: 2px solid #00ff96; position: absolute; top: 33px; left: 33px; pointer-events: none; }

    /* BOTÕES DE AÇÃO */
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

  <!-- BOTÃO SOLTAR MÍSSIL / BOMBA -->
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

# 4. INTEGRAÇÃO DA CÂMERA PIP E LOOP PRINCIPAL (src/main.js)
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
    
    // Cena e Câmeras
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a100d);
    this.scene.fog = new THREE.FogExp2(0x0a100d, 0.015);

    // 1. Câmera Principal (FPV Drone)
    this.camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 200);

    // 2. Câmera Secundária de Destino do Míssil (PiP - Visão Superior/Zenital)
    this.targetCamera = new THREE.OrthographicCamera(-15, 15, 15, -15, 0.1, 100);
    this.targetCamera.rotation.x = -Math.PI / 2; // Apontada diretamente para o solo

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00ff96, 1.2);
    dirLight.position.set(30, 50, 30);
    this.scene.add(dirLight);

    // Retículo visual no solo (Ponto de impacto do Míssil)
    const targetGeo = new THREE.RingGeometry(0.8, 1.0, 16);
    const targetMat = new THREE.MeshBasicMaterial({ color: 0xff3c3c, side: THREE.DoubleSide });
    this.targetMarker = new THREE.Mesh(targetGeo, targetMat);
    this.targetMarker.rotation.x = Math.PI / 2;
    this.scene.add(this.targetMarker);

    // Entidades
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

    // Trincheiras e Bunkers
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

  getTargetImpactPosition() {
    // Projeta o ponto de impacto no solo a partir da rotação e altitude do drone
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

    // Ponto de Impacto no Solo
    const targetPos = this.getTargetImpactPosition();
    this.targetMarker.position.copy(targetPos);

    // Atualiza Câmera Zenital PiP em cima do Alvo
    this.targetCamera.position.set(targetPos.x, targetPos.y + 25, targetPos.z);

    // Atualiza IA e Mísseis
    const newImpacts = this.missileSystem.update(delta, this.soldierManager, this.explosionSystem, soundManager);
    if (newImpacts.length > 0) {
      this.recentExplosions.push(...newImpacts);
    }

    this.soldierManager.update(delta, this.player.position, this.recentExplosions);
    this.explosionSystem.update(delta);

    // Limpa lista de explosões antigas
    if (this.recentExplosions.length > 5) this.recentExplosions.shift();

    // HUD Update
    document.getElementById('enemy-count').innerText = `INIMIGOS: ${this.soldierManager.getAliveCount()} / 10`;
    document.getElementById('alt-info').innerText = `ALTITUDE: ${Math.round(this.player.position.y)}m`;

    // ---------------------------------------------------------
    // RENDERIZAÇÃO DUPLA (VISÃO PRINCIPAL + CÂMERA PIP DE DESTINO)
    // ---------------------------------------------------------
    this.renderer.setScissorTest(false);
    this.renderer.clear();

    // 1. Visão Geral (Tela Cheia)
    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    // 2. Visão PiP (Monitor do Míssil no canto superior direito)
    const pipW = 160;
    const pipH = 120;
    const pipX = window.innerWidth - pipW - 12;
    const pipY = window.innerHeight - pipH - 65;

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

print("Sistema Web3D de Guerra de Drones + Câmera PiP aplicado com sucesso!")
