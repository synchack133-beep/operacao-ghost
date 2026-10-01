import os

files = {}

files['package.json'] = '''{
  "name": "operacao-ghost",
  "version": "2.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "vite": "^5.1.0"
  },
  "dependencies": {
    "three": "^0.162.0"
  }
}'''

files['README.md'] = '''# OPERAÇÃO GHOST - Tactical Drone Recon 3D

Jogo 3D de simulação e reconhecimento tático com drone desenvolvido em WebGL / Three.js com suporte completo a PC e dispositivos móveis (Touch UI).

## 🎮 Controles
- **Teclado / Mouse**: WASD (Mover), Espaço (Subir), Shift (Descer), E (Hackear Terminal), Mouse (Rotacionar Câmera).
- **Dispositivos Móveis**: Joystick virtual (Esquerda), Arrasto na tela (Câmera), Botões táticos t-btn (Direita).

## ⚙️ Edição e Parâmetros
Todas as configurações de velocidade, bateria, altitudes, câmera e missões estão centralizadas no arquivo:
`src/config/gameConfig.js`
'''

files['.gitignore'] = '''node_modules/
dist/
*.log
.DS_Store
'''

files['index.html'] = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>OPERAÇÃO GHOST - Tactical Drone Recon 3D</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; }
    html, body { width: 100%; height: 100%; overflow: hidden; background-color: #030806; font-family: 'Courier New', Courier, monospace; color: #00ff96; }
    #game-container { width: 100vw; height: 100vh; position: relative; }
    canvas { display: block; width: 100%; height: 100%; }

    /* HUD OVERLAY */
    #hud { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; display: none; }
    .hud-panel { position: absolute; padding: 10px 14px; background: rgba(3, 15, 10, 0.85); border: 1px solid rgba(0, 255, 150, 0.4); border-radius: 6px; box-shadow: 0 0 10px rgba(0,255,150,0.15); }
    #hud-top-left { top: 15px; left: 15px; width: 220px; }
    #hud-top-right { top: 15px; right: 15px; width: 220px; text-align: right; }
    .crosshair { width: 24px; height: 24px; border: 1.5px solid rgba(0, 255, 150, 0.6); border-radius: 50%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }
    .crosshair::after { content: ''; display: block; width: 4px; height: 4px; background: #00ff96; border-radius: 50%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }

    /* BARRAS DE STATUS */
    .bar-container { width: 100%; height: 10px; background: rgba(0, 40, 20, 0.8); border: 1px solid #00ff96; border-radius: 3px; margin-top: 4px; overflow: hidden; }
    .bar-fill { height: 100%; width: 100%; transition: width 0.2s ease-out; }
    #energy-bar { background: linear-gradient(90deg, #00ff96, #00b36b); }
    #health-bar { background: linear-gradient(90deg, #ff3333, #ff6666); }

    /* TOUCH CONTROLS OVERLAY */
    #touch-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 20; display: none; }
    #touch-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
    .touch-btn-group { position: absolute; bottom: 15px; right: 15px; pointer-events: auto; display: flex; gap: 8px; align-items: flex-end; }
    .t-btn { background: rgba(3, 20, 12, 0.85); border: 1.5px solid #00ff96; color: #00ff96; font-family: monospace; font-weight: bold; border-radius: 50%; display: flex; align-items: center; justify-content: center; touch-action: none; cursor: pointer; box-shadow: 0 0 10px rgba(0,255,150,0.3); }
    .t-btn:active { background: #00ff96; color: #030806; }
    #btn-fire { width: 62px; height: 62px; border-color: #ff4444; color: #ff5555; font-size: 11px; }
    #btn-up { width: 48px; height: 48px; font-size: 16px; }
    #btn-down { width: 48px; height: 48px; font-size: 16px; }
    #btn-action { width: 44px; height: 44px; font-size: 12px; }

    /* MODAIS DA INTERFACE DE USUÁRIO */
    .modal-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 8, 5, 0.92); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 15px; }
    .modal-card { background: rgba(4, 20, 13, 0.95); border: 1.5px solid #00ff96; box-shadow: 0 0 25px rgba(0, 255, 150, 0.25); border-radius: 8px; width: 100%; max-width: 480px; max-height: 90vh; overflow-y: auto; padding: 18px; text-align: center; color: #e0ffe0; }
    .modal-card h1 { font-size: clamp(16px, 4vh, 22px); color: #00ff96; margin-bottom: 10px; text-shadow: 0 0 8px rgba(0,255,150,0.5); }
    .modal-card h2 { font-size: clamp(13px, 3vh, 16px); color: #70ffc0; margin-bottom: 8px; }
    .modal-card p { font-size: clamp(11px, 2.5vh, 13px); line-height: 1.4; color: #a0dfb0; margin-bottom: 12px; text-align: left; }
    .modal-card ul { text-align: left; margin: 0 0 15px 20px; font-size: clamp(10px, 2.2vh, 12px); color: #88d0a0; }
    .btn-main { display: inline-block; width: 100%; padding: 12px 20px; background: #00ff96; color: #030806; font-family: monospace; font-weight: bold; font-size: 14px; border: none; border-radius: 4px; cursor: pointer; box-shadow: 0 0 12px rgba(0,255,150,0.4); margin-top: 8px; transition: transform 0.1s; }
    .btn-main:active { transform: scale(0.98); }
  </style>

  <script type="importmap">
    {
      "imports": {
        "three": "https://unpkg.com/three@0.162.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.162.0/examples/jsm/"
      }
    }
  </script>
</head>
<body>
  <div id="game-container">
    <div id="hud">
      <div class="crosshair"></div>
      <div id="hud-top-left" class="hud-panel">
        <div style="font-size: 10px; color: #00ff96;">BATERIA DRONE</div>
        <div class="bar-container"><div id="energy-bar" class="bar-fill"></div></div>
        <div style="font-size: 10px; color: #ff5555; margin-top: 6px;">INTEGRIDADE STRUCT</div>
        <div class="bar-container"><div id="health-bar" class="bar-fill"></div></div>
      </div>
      <div id="hud-top-right" class="hud-panel">
        <div style="font-size: 10px; color: #70ffc0;">OBJETIVO DA MISSÃO</div>
        <div id="intel-count" style="font-size: 16px; font-weight: bold; color: #00ff96; margin-top: 2px;">DADOS: 0 / 4</div>
        <div id="mission-status" style="font-size: 10px; color: #a0dfb0; margin-top: 4px;">Infiltre-se na base</div>
      </div>
    </div>

    <div id="touch-layer">
      <canvas id="touch-canvas"></canvas>
      <div class="touch-btn-group">
        <button id="btn-action" class="t-btn">E</button>
        <button id="btn-down" class="t-btn">▼</button>
        <button id="btn-up" class="t-btn">▲</button>
        <button id="btn-fire" class="t-btn">FOGO</button>
      </div>
    </div>

    <div id="modal-start" class="modal-overlay">
      <div class="modal-card">
        <h1>OPERAÇÃO GHOST</h1>
        <h2>RECONHECIMENTO TÁTICO DE DRONE</h2>
        <p>Infiltre-se no complexo militar inimigo, hackeie os <strong>4 Terminais de Dados Intel</strong> e retorne à Zona de Extração antes que a energia do drone acabe.</p>
        <ul>
          <li><strong>PC:</strong> WASD (Mover), Espaço/Shift (Subir/Descer), E (Hackear), Mouse (Câmera)</li>
          <li><strong>Celular:</strong> Joystick Esquerdo (Mover), Arrasto Direito (Visão), Botões ▲/▼/E/FOGO</li>
        </ul>
        <button id="btn-start" class="btn-main">INICIAR MISSÃO TÁTICA</button>
      </div>
    </div>

    <div id="modal-end" class="modal-overlay" style="display: none;">
      <div class="modal-card">
        <h1 id="end-title">MISSÃO CUMPRIDA!</h1>
        <p id="end-message">Todos os dados foram interceptados com sucesso.</p>
        <button id="btn-restart" class="btn-main">REINICIAR MISSÃO</button>
      </div>
    </div>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

files['src/config/gameConfig.js'] = '''export const GAME_CONFIG = {
  PLAYER: {
    speed: 18.0,
    ascendSpeed: 10.0,
    turnSpeed: 2.2,
    tiltAngleMax: 0.25,
    maxEnergy: 100,
    energyDepletionRate: 1.5,
    maxHealth: 100,
    startPosition: { x: 0, y: 3, z: 45 },
    minAltitude: 0.8,
    maxAltitude: 25.0
  },
  CAMERA: {
    distance: 4.5,
    height: 1.8,
    fov: 70,
    sensitivityMouse: 0.0025,
    sensitivityTouch: 0.004,
    damping: 0.1
  },
  WORLD: {
    mapSize: 120,
    fogColor: 0x030d08,
    fogNear: 15,
    fogFar: 90,
    clearColor: 0x030806
  },
  MISSION: {
    totalIntelCount: 4,
    intelLocations: [
      { id: 1, x: -25, z: -20, collected: false },
      { id: 2, x: 25, z: -25, collected: false },
      { id: 3, x: -30, z: 20, collected: false },
      { id: 4, x: 30, z: 15, collected: false }
    ],
    extractionZone: { x: 0, z: 45, radius: 6 }
  },
  AUDIO: {
    masterVolume: 0.7,
    sfxVolume: 0.8
  }
};'''

files['src/core/EventBus.js'] = '''class EventBus {
  constructor() {
    this.listeners = {};
  }
  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  }
  off(event, callback) {
    if (!this.listeners[event]) return;
    this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
  }
  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }
}
export const eventBus = new EventBus();'''

files['src/core/GameState.js'] = '''import { eventBus } from './EventBus.js';

export const STATES = {
  MENU: 'MENU',
  PLAYING: 'PLAYING',
  PAUSED: 'PAUSED',
  VICTORY: 'VICTORY',
  GAMEOVER: 'GAMEOVER'
};

export class GameStateMachine {
  constructor() {
    this.currentState = STATES.MENU;
  }
  setState(newState) {
    if (this.currentState === newState) return;
    const previousState = this.currentState;
    this.currentState = newState;
    eventBus.emit('gameStateChanged', { state: newState, previousState });
  }
  isPlaying() {
    return this.currentState === STATES.PLAYING;
  }
}
export const gameStateMachine = new GameStateMachine();'''

files['src/core/Engine.js'] = '''import * as THREE from 'three';
import { GAME_CONFIG } from '../config/gameConfig.js';

export class Engine {
  constructor(container) {
    this.container = container;
    
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(GAME_CONFIG.WORLD.clearColor);
    this.scene.fog = new THREE.FogExp2(GAME_CONFIG.WORLD.fogColor, 0.018);

    this.camera = new THREE.PerspectiveCamera(
      GAME_CONFIG.CAMERA.fov,
      window.innerWidth / window.innerHeight,
      0.1,
      500
    );

    this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.container.appendChild(this.renderer.domElement);

    this.clock = new THREE.Clock();
    this.updateCallbacks = [];

    window.addEventListener('resize', () => this.onWindowResize());
  }

  addLighting() {
    const ambientLight = new THREE.AmbientLight(0x1a382b, 1.2);
    this.scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight(0xa0ffda, 1.8);
    sunLight.position.set(30, 50, 20);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 150;
    const d = 60;
    sunLight.shadow.camera.left = -d;
    sunLight.shadow.camera.right = d;
    sunLight.shadow.camera.top = d;
    sunLight.shadow.camera.bottom = -d;
    this.scene.add(sunLight);

    const hemiLight = new THREE.HemisphereLight(0x00ffaa, 0x05100a, 0.4);
    this.scene.add(hemiLight);
  }

  onRegisterUpdate(cb) {
    this.updateCallbacks.push(cb);
  }

  onWindowResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  start() {
    this.renderer.setAnimationLoop(() => {
      const deltaTime = Math.min(this.clock.getDelta(), 0.1);
      for (const cb of this.updateCallbacks) {
        cb(deltaTime);
      }
      this.renderer.render(this.scene, this.camera);
    });
  }
}'''

files['src/player/DroneModel.js'] = '''import * as THREE from 'three';

export function createDroneMesh() {
  const droneGroup = new THREE.Group();

  const bodyGeo = new THREE.ConeGeometry(0.5, 1.2, 5);
  bodyGeo.rotateX(Math.PI / 2);
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x111e18, roughness: 0.3, metalness: 0.8 });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.castShadow = true;
  droneGroup.add(body);

  const lensGeo = new THREE.SphereGeometry(0.12, 16, 16);
  const lensMat = new THREE.MeshBasicMaterial({ color: 0x00ff96 });
  const lens = new THREE.Mesh(lensGeo, lensMat);
  lens.position.set(0, 0, -0.6);
  droneGroup.add(lens);

  const spotLight = new THREE.SpotLight(0x00ffaa, 4, 25, Math.PI / 6, 0.5);
  spotLight.position.set(0, -0.1, -0.5);
  spotLight.target.position.set(0, -5, -15);
  droneGroup.add(spotLight);
  droneGroup.add(spotLight.target);

  const armMat = new THREE.MeshStandardMaterial({ color: 0x08140e, metalness: 0.9 });
  const propMat = new THREE.MeshBasicMaterial({ color: 0x00ff96, transparent: true, opacity: 0.6 });
  const rotors = [];

  const offsets = [
    { x: 0.7, z: -0.6 },
    { x: -0.7, z: -0.6 },
    { x: 0.8, z: 0.6 },
    { x: -0.8, z: 0.6 }
  ];

  offsets.forEach((off) => {
    const armGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.9);
    const arm = new THREE.Mesh(armGeo, armMat);
    arm.position.set(off.x / 2, 0, off.z / 2);
    arm.rotation.z = Math.atan2(off.x, off.z);
    arm.rotation.x = Math.PI / 2;
    droneGroup.add(arm);

    const propGeo = new THREE.BoxGeometry(0.7, 0.01, 0.08);
    const prop = new THREE.Mesh(propGeo, propMat);
    prop.position.set(off.x, 0.1, off.z);
    droneGroup.add(prop);
    rotors.push(prop);
  });

  droneGroup.userData.rotors = rotors;
  return droneGroup;
}'''

files['src/player/PlayerController.js'] = '''import * as THREE from 'three';
import { GAME_CONFIG } from '../config/gameConfig.js';
import { createDroneMesh } from './DroneModel.js';
import { eventBus } from '../core/EventBus.js';
import { gameStateMachine } from '../core/GameState.js';

export class PlayerController {
  constructor(scene) {
    this.scene = scene;
    this.mesh = createDroneMesh();
    this.mesh.position.set(
      GAME_CONFIG.PLAYER.startPosition.x,
      GAME_CONFIG.PLAYER.startPosition.y,
      GAME_CONFIG.PLAYER.startPosition.z
    );
    this.scene.add(this.mesh);

    this.velocity = new THREE.Vector3();
    this.energy = GAME_CONFIG.PLAYER.maxEnergy;
    this.health = GAME_CONFIG.PLAYER.maxHealth;
    this.yaw = Math.PI;

    eventBus.on('resetPlayer', () => this.reset());
  }

  reset() {
    this.mesh.position.set(
      GAME_CONFIG.PLAYER.startPosition.x,
      GAME_CONFIG.PLAYER.startPosition.y,
      GAME_CONFIG.PLAYER.startPosition.z
    );
    this.velocity.set(0, 0, 0);
    this.energy = GAME_CONFIG.PLAYER.maxEnergy;
    this.health = GAME_CONFIG.PLAYER.maxHealth;
    this.yaw = Math.PI;
    eventBus.emit('energyUpdated', this.energy);
    eventBus.emit('healthUpdated', this.health);
  }

  update(deltaTime, inputState, cameraRotation) {
    if (!gameStateMachine.isPlaying()) return;

    this.energy -= GAME_CONFIG.PLAYER.energyDepletionRate * deltaTime;
    if (this.energy <= 0) {
      this.energy = 0;
      eventBus.emit('playerDied', 'Bateria Esgotada!');
    }
    eventBus.emit('energyUpdated', this.energy);

    if (this.mesh.userData.rotors) {
      this.mesh.userData.rotors.forEach(r => r.rotation.y += 25 * deltaTime);
    }

    this.yaw = cameraRotation.yaw;

    const moveDir = new THREE.Vector3();
    if (inputState.forward) moveDir.z -= 1;
    if (inputState.backward) moveDir.z += 1;
    if (inputState.left) moveDir.x -= 1;
    if (inputState.right) moveDir.x += 1;
    moveDir.normalize();

    moveDir.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.yaw);

    const targetVelX = moveDir.x * GAME_CONFIG.PLAYER.speed;
    const targetVelZ = moveDir.z * GAME_CONFIG.PLAYER.speed;

    this.velocity.x += (targetVelX - this.velocity.x) * 0.1;
    this.velocity.z += (targetVelZ - this.velocity.z) * 0.1;

    if (inputState.up) this.velocity.y += GAME_CONFIG.PLAYER.ascendSpeed * deltaTime * 5;
    else if (inputState.down) this.velocity.y -= GAME_CONFIG.PLAYER.ascendSpeed * deltaTime * 5;
    else this.velocity.y *= 0.9;

    this.mesh.position.x += this.velocity.x * deltaTime;
    this.mesh.position.y += this.velocity.y * deltaTime;
    this.mesh.position.z += this.velocity.z * deltaTime;

    this.mesh.position.y = THREE.MathUtils.clamp(
      this.mesh.position.y,
      GAME_CONFIG.PLAYER.minAltitude,
      GAME_CONFIG.PLAYER.maxAltitude
    );

    const limit = GAME_CONFIG.WORLD.mapSize / 2 - 2;
    this.mesh.position.x = THREE.MathUtils.clamp(this.mesh.position.x, -limit, limit);
    this.mesh.position.z = THREE.MathUtils.clamp(this.mesh.position.z, -limit, limit);

    this.mesh.rotation.y = this.yaw;
    const tiltZ = -this.velocity.x * 0.02;
    const tiltX = this.velocity.z * 0.02;
    this.mesh.rotation.z = THREE.MathUtils.lerp(this.mesh.rotation.z, tiltZ, 0.1);
    this.mesh.rotation.x = THREE.MathUtils.lerp(this.mesh.rotation.x, tiltX, 0.1);
  }
}'''

files['src/camera/CameraController.js'] = '''import * as THREE from 'three';
import { GAME_CONFIG } from '../config/gameConfig.js';

export class CameraController {
  constructor(camera) {
    this.camera = camera;
    this.yaw = Math.PI;
    this.pitch = -0.2;

    this.targetPosition = new THREE.Vector3();
    this.currentPosition = new THREE.Vector3();
  }

  handleLookDelta(dx, dy) {
    this.yaw -= dx;
    this.pitch -= dy;
    this.pitch = THREE.MathUtils.clamp(this.pitch, -Math.PI / 3, Math.PI / 4);
  }

  update(targetMesh) {
    if (!targetMesh) return;

    const dist = GAME_CONFIG.CAMERA.distance;
    const height = GAME_CONFIG.CAMERA.height;

    const offsetX = Math.sin(this.yaw) * Math.cos(this.pitch) * dist;
    const offsetZ = Math.cos(this.yaw) * Math.cos(this.pitch) * dist;
    const offsetY = Math.sin(-this.pitch) * dist + height;

    this.targetPosition.set(
      targetMesh.position.x + offsetX,
      targetMesh.position.y + offsetY,
      targetMesh.position.z + offsetZ
    );

    this.currentPosition.lerp(this.targetPosition, GAME_CONFIG.CAMERA.damping);
    this.camera.position.copy(this.currentPosition);

    const lookTarget = targetMesh.position.clone().add(new THREE.Vector3(0, 0.3, 0));
    this.camera.lookAt(lookTarget);
  }
}'''

files['src/input/InputManager.js'] = '''import { GAME_CONFIG } from '../config/gameConfig.js';
import { eventBus } from '../core/EventBus.js';

export class InputManager {
  constructor(cameraController) {
    this.cameraController = cameraController;
    this.state = {
      forward: false,
      backward: false,
      left: false,
      right: false,
      up: false,
      down: false,
      action: false,
      fire: false
    };

    this.initKeyboard();
    this.initMouse();
  }

  initKeyboard() {
    window.addEventListener('keydown', (e) => this.onKey(e, true));
    window.addEventListener('keyup', (e) => this.onKey(e, false));
  }

  onKey(e, isDown) {
    switch (e.code) {
      case 'KeyW': case 'ArrowUp': this.state.forward = isDown; break;
      case 'KeyS': case 'ArrowDown': this.state.backward = isDown; break;
      case 'KeyA': case 'ArrowLeft': this.state.left = isDown; break;
      case 'KeyD': case 'ArrowRight': this.state.right = isDown; break;
      case 'Space': this.state.up = isDown; break;
      case 'ShiftLeft': case 'ShiftRight': this.state.down = isDown; break;
      case 'KeyE':
        this.state.action = isDown;
        if (isDown) eventBus.emit('actionTriggered');
        break;
    }
  }

  initMouse() {
    let isDragging = false;
    let prevX = 0, prevY = 0;

    window.addEventListener('mousedown', (e) => {
      if (e.target.tagName === 'CANVAS') {
        isDragging = true;
        prevX = e.clientX;
        prevY = e.clientY;
      }
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const dx = (e.clientX - prevX) * GAME_CONFIG.CAMERA.sensitivityMouse;
      const dy = (e.clientY - prevY) * GAME_CONFIG.CAMERA.sensitivityMouse;
      prevX = e.clientX;
      prevY = e.clientY;
      this.cameraController.handleLookDelta(dx, dy);
    });

    window.addEventListener('mouseup', () => isDragging = false);
  }
}'''

files['src/input/TouchOverlay.js'] = '''import { GAME_CONFIG } from '../config/gameConfig.js';

export class TouchOverlay {
  constructor(inputState, cameraController) {
    this.inputState = inputState;
    this.cameraController = cameraController;
    this.touchLayer = document.getElementById('touch-layer');
    this.canvas = document.getElementById('touch-canvas');
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;

    this.joyId = null;
    this.joyBase = { x: 0, y: 0 };
    this.joyStick = { x: 0, y: 0 };
    this.maxRadius = 45;

    this.lookId = null;
    this.lastLook = { x: 0, y: 0 };

    this.init();
  }

  init() {
    if (!this.touchLayer) return;
    this.resize();
    window.addEventListener('resize', () => this.resize());

    window.addEventListener('touchstart', (e) => this.onTouchStart(e), { passive: false });
    window.addEventListener('touchmove', (e) => this.onTouchMove(e), { passive: false });
    window.addEventListener('touchend', (e) => this.onTouchEnd(e));
    window.addEventListener('touchcancel', (e) => this.onTouchEnd(e));

    this.bindBtn('btn-up', 'up');
    this.bindBtn('btn-down', 'down');
    this.bindBtn('btn-action', 'action');
    this.bindBtn('btn-fire', 'fire');
  }

  resize() {
    if (this.canvas) {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    }
  }

  bindBtn(id, key) {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener('touchstart', (e) => { e.preventDefault(); this.inputState[key] = true; });
    btn.addEventListener('touchend', (e) => { e.preventDefault(); this.inputState[key] = false; });
  }

  onTouchStart(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const t = e.changedTouches[i];
      if (t.clientX < window.innerWidth / 2 && this.joyId === null) {
        this.joyId = t.identifier;
        this.joyBase = { x: t.clientX, y: t.clientY };
        this.joyStick = { x: t.clientX, y: t.clientY };
        this.drawJoy();
      } else if (t.clientX >= window.innerWidth / 2 && this.lookId === null) {
        this.lookId = t.identifier;
        this.lastLook = { x: t.clientX, y: t.clientY };
      }
    }
  }

  onTouchMove(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const t = e.changedTouches[i];
      if (t.identifier === this.joyId) {
        let dx = t.clientX - this.joyBase.x;
        let dy = t.clientY - this.joyBase.y;
        const dist = Math.hypot(dx, dy);
        if (dist > this.maxRadius) {
          dx = (dx / dist) * this.maxRadius;
          dy = (dy / dist) * this.maxRadius;
        }
        this.joyStick = { x: this.joyBase.x + dx, y: this.joyBase.y + dy };

        this.inputState.forward = dy < -12;
        this.inputState.backward = dy > 12;
        this.inputState.left = dx < -12;
        this.inputState.right = dx > 12;

        this.drawJoy();
      } else if (t.identifier === this.lookId) {
        const dx = (t.clientX - this.lastLook.x) * GAME_CONFIG.CAMERA.sensitivityTouch;
        const dy = (t.clientY - this.lastLook.y) * GAME_CONFIG.CAMERA.sensitivityTouch;
        this.lastLook = { x: t.clientX, y: t.clientY };
        this.cameraController.handleLookDelta(dx, dy);
      }
    }
  }

  onTouchEnd(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const t = e.changedTouches[i];
      if (t.identifier === this.joyId) {
        this.joyId = null;
        this.inputState.forward = false;
        this.inputState.backward = false;
        this.inputState.left = false;
        this.inputState.right = false;
        if (this.ctx) this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      } else if (t.identifier === this.lookId) {
        this.lookId = null;
      }
    }
  }

  drawJoy() {
    if (!this.ctx) return;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.beginPath();
    this.ctx.arc(this.joyBase.x, this.joyBase.y, this.maxRadius, 0, Math.PI * 2);
    this.ctx.fillStyle = 'rgba(0, 255, 150, 0.12)';
    this.ctx.strokeStyle = 'rgba(0, 255, 150, 0.5)';
    this.ctx.lineWidth = 2;
    this.ctx.fill(); this.ctx.stroke();

    this.ctx.beginPath();
    this.ctx.arc(this.joyStick.x, this.joyStick.y, 18, 0, Math.PI * 2);
    this.ctx.fillStyle = 'rgba(0, 255, 150, 0.7)';
    this.ctx.fill();
  }

  show(visible) {
    if (this.touchLayer) this.touchLayer.style.display = visible ? 'block' : 'none';
  }
}'''

files['src/world/Environment.js'] = '''import * as THREE from 'three';
import { GAME_CONFIG } from '../config/gameConfig.js';

export class Environment {
  constructor(scene) {
    this.scene = scene;
    this.intelMeshes = [];
    this.buildTerrain();
    this.buildMilitaryBase();
  }

  buildTerrain() {
    const size = GAME_CONFIG.WORLD.mapSize;
    const geo = new THREE.PlaneGeometry(size, size, 32, 32);
    geo.rotateX(-Math.PI / 2);

    const mat = new THREE.MeshStandardMaterial({ color: 0x07140e, roughness: 0.9, metalness: 0.1 });
    const ground = new THREE.Mesh(geo, mat);
    ground.receiveShadow = true;
    this.scene.add(ground);

    const grid = new THREE.GridHelper(size, 40, 0x00ff96, 0x00331b);
    grid.position.y = 0.02;
    this.scene.add(grid);
  }

  buildMilitaryBase() {
    const wallMat = new THREE.MeshStandardMaterial({ color: 0x12241b, roughness: 0.7 });
    const crateMat = new THREE.MeshStandardMaterial({ color: 0x1b3628 });

    const wallGeo = new THREE.BoxGeometry(110, 6, 2);
    const nWall = new THREE.Mesh(wallGeo, wallMat); nWall.position.set(0, 3, -55);
    const sWall = new THREE.Mesh(wallGeo, wallMat); sWall.position.set(0, 3, 55);
    const eWall = new THREE.Mesh(wallGeo, wallMat); eWall.position.set(55, 3, 0); eWall.rotation.y = Math.PI / 2;
    const wWall = new THREE.Mesh(wallGeo, wallMat); wWall.position.set(-55, 3, 0); wWall.rotation.y = Math.PI / 2;
    
    [nWall, sWall, eWall, wWall].forEach(w => { w.castShadow = true; w.receiveShadow = true; this.scene.add(w); });

    for (let i = 0; i < 25; i++) {
      const boxGeo = new THREE.BoxGeometry(3, 3, 3);
      const box = new THREE.Mesh(boxGeo, crateMat);
      box.position.set((Math.random() - 0.5) * 80, 1.5, (Math.random() - 0.5) * 80);
      box.castShadow = true;
      box.receiveShadow = true;
      this.scene.add(box);
    }

    this.createIntelTerminals();
  }

  createIntelTerminals() {
    GAME_CONFIG.MISSION.intelLocations.forEach((loc) => {
      const group = new THREE.Group();
      group.position.set(loc.x, 0, loc.z);

      const baseGeo = new THREE.CylinderGeometry(0.8, 1, 1.5, 8);
      const baseMat = new THREE.MeshStandardMaterial({ color: 0x0a1a12 });
      const base = new THREE.Mesh(baseGeo, baseMat);
      base.position.y = 0.75;
      group.add(base);

      const holoGeo = new THREE.OctahedronGeometry(0.5);
      const holoMat = new THREE.MeshBasicMaterial({ color: 0x00ff96, wireframe: true });
      const holo = new THREE.Mesh(holoGeo, holoMat);
      holo.position.y = 2.2;
      group.add(holo);

      const light = new THREE.PointLight(0x00ff96, 2, 8);
      light.position.y = 2;
      group.add(light);

      group.userData = { id: loc.id, holo: holo };
      this.scene.add(group);
      this.intelMeshes.push(group);
    });
  }

  update(deltaTime) {
    this.intelMeshes.forEach(m => {
      if (m.userData.holo) m.userData.holo.rotation.y += 1.5 * deltaTime;
    });
  }
}'''

files['src/audio/SoundManager.js'] = '''export class SoundManager {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
  }

  playIntelCollected() {
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(880, this.ctx.currentTime + 0.25);

    gain.gain.setValueAtTime(0.3, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.25);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.25);
  }

  playVictory() {
    if (!this.ctx) return;
    [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
      setTimeout(() => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.3);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.3);
      }, idx * 120);
    });
  }
}
export const soundManager = new SoundManager();'''

files['src/gameplay/MissionManager.js'] = '''import { GAME_CONFIG } from '../config/gameConfig.js';
import { eventBus } from '../core/EventBus.js';
import { gameStateMachine, STATES } from '../core/GameState.js';
import { soundManager } from '../audio/SoundManager.js';

export class MissionManager {
  constructor(environment) {
    this.environment = environment;
    this.collectedCount = 0;
    this.totalIntel = GAME_CONFIG.MISSION.totalIntelCount;

    eventBus.on('actionTriggered', () => this.tryCollectIntel());
  }

  reset() {
    this.collectedCount = 0;
    GAME_CONFIG.MISSION.intelLocations.forEach(loc => loc.collected = false);
    eventBus.emit('intelUpdated', { collected: 0, total: this.totalIntel });
  }

  checkPlayerProximity(playerPos) {
    if (!gameStateMachine.isPlaying()) return;

    GAME_CONFIG.MISSION.intelLocations.forEach((loc) => {
      if (loc.collected) return;
      const dist = Math.hypot(playerPos.x - loc.x, playerPos.z - loc.z);
      if (dist < 3.5 && playerPos.y < 4.0) {
        eventBus.emit('nearIntel', loc.id);
      }
    });

    if (this.collectedCount >= this.totalIntel) {
      const ext = GAME_CONFIG.MISSION.extractionZone;
      const distExt = Math.hypot(playerPos.x - ext.x, playerPos.z - ext.z);
      if (distExt < ext.radius) {
        soundManager.playVictory();
        gameStateMachine.setState(STATES.VICTORY);
        eventBus.emit('missionComplete');
      }
    }
  }

  tryCollectIntel() {
    eventBus.emit('checkProximityAndCollect');
  }

  collect(id) {
    const loc = GAME_CONFIG.MISSION.intelLocations.find(l => l.id === id);
    if (loc && !loc.collected) {
      loc.collected = true;
      this.collectedCount++;
      soundManager.playIntelCollected();
      eventBus.emit('intelUpdated', { collected: this.collectedCount, total: this.totalIntel });

      const mesh = this.environment.intelMeshes.find(m => m.userData.id === id);
      if (mesh) mesh.visible = false;
    }
  }
}'''

files['src/ui/UIManager.js'] = '''import { eventBus } from '../core/EventBus.js';
import { gameStateMachine, STATES } from '../core/GameState.js';
import { soundManager } from '../audio/SoundManager.js';

export class UIManager {
  constructor(touchOverlay) {
    this.touchOverlay = touchOverlay;
    
    this.hud = document.getElementById('hud');
    this.modalStart = document.getElementById('modal-start');
    this.modalEnd = document.getElementById('modal-end');
    
    this.energyBar = document.getElementById('energy-bar');
    this.healthBar = document.getElementById('health-bar');
    this.intelCountText = document.getElementById('intel-count');
    this.missionStatusText = document.getElementById('mission-status');

    this.btnStart = document.getElementById('btn-start');
    this.btnRestart = document.getElementById('btn-restart');

    this.initEvents();
  }

  initEvents() {
    this.btnStart.addEventListener('click', () => {
      soundManager.init();
      this.modalStart.style.display = 'none';
      this.hud.style.display = 'block';
      this.touchOverlay.show(true);
      gameStateMachine.setState(STATES.PLAYING);
    });

    this.btnRestart.addEventListener('click', () => {
      this.modalEnd.style.display = 'none';
      this.hud.style.display = 'block';
      this.touchOverlay.show(true);
      eventBus.emit('resetPlayer');
      eventBus.emit('resetMission');
      gameStateMachine.setState(STATES.PLAYING);
    });

    eventBus.on('energyUpdated', (val) => {
      if (this.energyBar) this.energyBar.style.width = `${Math.max(0, val)}%`;
    });

    eventBus.on('healthUpdated', (val) => {
      if (this.healthBar) this.healthBar.style.width = `${Math.max(0, val)}%`;
    });

    eventBus.on('intelUpdated', (data) => {
      if (this.intelCountText) this.intelCountText.innerText = `DADOS: ${data.collected} / ${data.total}`;
      if (data.collected >= data.total) {
        if (this.missionStatusText) {
          this.missionStatusText.innerText = "RETORNE À ZONA DE EXTRAÇÃO!";
          this.missionStatusText.style.color = "#00ff96";
        }
      }
    });

    eventBus.on('playerDied', (reason) => {
      this.showEndScreen('FALHA NA MISSÃO', reason);
    });

    eventBus.on('missionComplete', () => {
      this.showEndScreen('MISSÃO CUMPRIDA!', 'Todos os dados sigilosos foram coletados com sucesso e o drone retornou à base.');
    });
  }

  showEndScreen(title, message) {
    this.hud.style.display = 'none';
    this.touchOverlay.show(false);
    document.getElementById('end-title').innerText = title;
    document.getElementById('end-message').innerText = message;
    this.modalEnd.style.display = 'flex';
  }
}'''

files['src/main.js'] = '''import { Engine } from './core/Engine.js';
import { CameraController } from './camera/CameraController.js';
import { InputManager } from './input/InputManager.js';
import { TouchOverlay } from './input/TouchOverlay.js';
import { PlayerController } from './player/PlayerController.js';
import { Environment } from './world/Environment.js';
import { MissionManager } from './gameplay/MissionManager.js';
import { UIManager } from './ui/UIManager.js';
import { eventBus } from './core/EventBus.js';

window.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('game-container');

  const engine = new Engine(container);
  engine.addLighting();

  const cameraController = new CameraController(engine.camera);
  const inputManager = new InputManager(cameraController);
  const touchOverlay = new TouchOverlay(inputManager.state, cameraController);

  const environment = new Environment(engine.scene);
  const playerController = new PlayerController(engine.scene);
  const missionManager = new MissionManager(environment);
  const uiManager = new UIManager(touchOverlay);

  eventBus.on('checkProximityAndCollect', () => {
    const pos = playerController.mesh.position;
    environment.intelMeshes.forEach(mesh => {
      if (mesh.visible) {
        const dist = Math.hypot(pos.x - mesh.position.x, pos.z - mesh.position.z);
        if (dist < 3.8) {
          missionManager.collect(mesh.userData.id);
        }
      }
    });
  });

  eventBus.on('resetMission', () => {
    environment.intelMeshes.forEach(m => m.visible = true);
    missionManager.reset();
  });

  engine.onRegisterUpdate((deltaTime) => {
    playerController.update(deltaTime, inputManager.state, { yaw: cameraController.yaw });
    cameraController.update(playerController.mesh);
    environment.update(deltaTime);
    missionManager.checkPlayerProximity(playerController.mesh.position);
  });

  engine.start();
});'''

for filepath, content in files.items():
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Gerado com sucesso: {filepath}")

