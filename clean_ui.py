import os

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

    /* Efeito sutil de lente */
    #lens-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none;
      background: radial-gradient(circle, rgba(0,0,0,0) 65%, rgba(0,0,0,0.6) 100%);
    }

    /* Bússola centralizada no topo */
    #compass-container {
      position: absolute; top: 8px; left: 50%; transform: translateX(-50%);
      padding: 3px 12px; background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(0, 255, 150, 0.3);
      border-radius: 4px; z-index: 10; font-size: 10px; font-weight: bold; letter-spacing: 1px; color: #00ff96;
    }

    /* Telemetria Esquerda (Dados do Drone) */
    .telemetry-left {
      position: absolute; top: 10px; left: 10px; z-index: 10; pointer-events: none;
      font-size: 9px; line-height: 1.4; color: #00ff96; text-shadow: 1px 1px 2px #000;
      background: rgba(0, 0, 0, 0.4); padding: 4px 8px; border-radius: 3px; border-left: 2px solid #00ff96;
    }

    /* Telemetria Direita (Voo e Velocidade) */
    .telemetry-right {
      position: absolute; top: 115px; right: 10px; z-index: 10; pointer-events: none;
      font-size: 9px; line-height: 1.4; color: #00ff96; text-shadow: 1px 1px 2px #000; text-align: right;
      background: rgba(0, 0, 0, 0.4); padding: 4px 8px; border-radius: 3px; border-right: 2px solid #00ff96;
    }

    /* Botão Tela Cheia */
    #btn-fullscreen {
      position: absolute; top: 8px; right: 8px; width: 30px; height: 30px;
      background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(0, 255, 150, 0.4);
      color: #00ff96; font-size: 14px; border-radius: 4px; display: flex;
      justify-content: center; align-items: center; pointer-events: auto; z-index: 35; cursor: pointer;
    }
    
    /* Quadro CAM DESTINO (Topo Direito) */
    #pip-container {
      position: absolute; top: 10px; right: 45px; width: 120px; height: 90px;
      border: 1px solid rgba(0, 255, 150, 0.5); background: rgba(0, 10, 5, 0.7); z-index: 20; pointer-events: none;
      border-radius: 2px;
    }
    #pip-title {
      position: absolute; top: 2px; left: 4px; font-size: 7px; font-weight: bold; color: #00ff96;
      background: rgba(0,0,0,0.6); padding: 1px 3px; border-radius: 2px;
    }

    /* Mira Central Limpa */
    #reticle-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 8; pointer-events: none;
      display: flex; justify-content: center; align-items: center;
    }

    /* Analógicos Discretos e Semi-transparentes */
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

    /* Botão de Disparo Limpo */
    #btn-drop-missile {
      position: absolute; bottom: 120px; right: 15px; width: 52px; height: 52px; border-radius: 50%;
      background: rgba(255, 60, 60, 0.3); border: 1.5px solid #ff3c3c; color: #ff3c3c;
      font-size: 18px; display: flex; justify-content: center; align-items: center;
      pointer-events: auto; z-index: 30; opacity: 0.7; transition: all 0.2s;
    }
    #btn-drop-missile:active { background: rgba(255, 60, 60, 0.8); color: #fff; transform: scale(0.92); opacity: 1; }

    /* Modal de Início */
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

  <!-- Bússola -->
  <div id="compass-container">
    <span id="compass-text">0° [ N ]</span>
  </div>

  <!-- Telemetria Esquerda -->
  <div class="telemetry-left">
    <div><b>BAT:</b> 22.2V</div>
    <div><b>RSSI:</b> -65dBm</div>
    <div><b>SAT:</b> 14 GPS</div>
  </div>

  <!-- Telemetria Direita -->
  <div class="telemetry-right">
    <div><b>SPD:</b> <span id="tele-spd">0</span> km/h</div>
    <div><b>ALT:</b> <span id="tele-alt">12</span> m</div>
    <div><b>DIST:</b> <span id="tele-range">0.00</span> km</div>
  </div>

  <!-- Câmera Secundária (PiP) -->
  <div id="pip-container">
    <div id="pip-title">ALVO 📷</div>
  </div>

  <button id="btn-fullscreen" title="Tela Cheia">⛶</button>

  <!-- Mira Central Discreta -->
  <div id="reticle-overlay">
    <svg width="100%" height="100%" viewBox="0 0 800 450" preserveAspectRatio="none">
      <!-- Crosshair central simples -->
      <line x1="385" y1="225" x2="395" y2="225" stroke="#00ff96" stroke-width="1" opacity="0.6"/>
      <line x1="405" y1="225" x2="415" y2="225" stroke="#00ff96" stroke-width="1" opacity="0.6"/>
      <line x1="400" y1="210" x2="400" y2="220" stroke="#00ff96" stroke-width="1" opacity="0.6"/>
      <line x1="400" y1="230" x2="400" y2="240" stroke="#00ff96" stroke-width="1" opacity="0.6"/>
      <circle cx="400" cy="225" r="2" fill="#ff3c3c"/>
    </svg>
  </div>

  <!-- Controles Touch Discretos -->
  <div id="zone-left" class="joystick-zone"><div id="stick-left" class="joystick-stick"></div></div>
  <div id="zone-right" class="joystick-zone"><div id="stick-right" class="joystick-stick"></div></div>

  <button id="btn-drop-missile">🚀</button>

  <!-- Modal Inicial -->
  <div id="modal-start" class="modal">
    <h2 style="color:#00ff96; margin-bottom: 8px;">ZONA DE GUERRA — FPV</h2>
    <p style="font-size: 12px; line-height: 1.5; max-width: 400px; color: #a3b8a3; margin-bottom: 20px;">
      Interface limpa e otimizada para celular.<br>
      Pilotagem FPV nos analógicos e câmera de alvo no canto superior.
    </p>
    <button id="btn-start" class="btn-main">DECOLAR</button>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# Atualizar as coordenadas de renderização da CAM DESTINO no main.js
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
    this.clock = new THREE.Clock();
    this.isPlaying = false;

    window.addEventListener('resize', () => this.onResize());
  }

  setupEvents() {
    const btnStart = document.getElementById('btn-start');
    const btnFullscreen = document.getElementById('btn-fullscreen');
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

    // 1. CÂMERA PRINCIPAL (TELA CHEIA)
    this.renderer.setScissorTest(false);
    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    // 2. CÂMERA SECUNDÁRIA (QUADRO PIP REPOSICIONADO)
    const pipW = 120;
    const pipH = 90;
    const pipX = window.innerWidth - pipW - 45;
    const pipY = window.innerHeight - pipH - 10;

    this.renderer.setScissorTest(true);
    this.renderer.setScissor(pipX, pipY, pipW, pipH);
    this.renderer.setViewport(pipX, pipY, pipW, pipH);
    this.renderer.render(this.scene, this.targetCamera);
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

print("Interface limpa aplicada com sucesso!")
