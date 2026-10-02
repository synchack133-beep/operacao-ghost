import * as THREE from 'three';
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

    this.camera = new THREE.PerspectiveCamera(62, window.innerWidth / window.innerHeight, 0.1, 400);
    this.targetCamera = new THREE.OrthographicCamera(-14, 14, 14, -14, 0.1, 120);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    this.container.appendChild(this.renderer.domElement);

    const targetGeo = new THREE.RingGeometry(0.8, 1.4, 16);
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

    this.bindButton('btn-audio-toggle', () => {
      const muted = soundManager.toggleMute();
      const btn = document.getElementById('btn-audio-toggle');
      if (btn) btn.innerText = muted ? '🔇' : '🔊';
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
      soundManager.init();
      soundManager.resume();

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

  updateCompassAndHUD() {
    const deg = Math.round(((-this.camera.rotation.y * 180 / Math.PI) % 360 + 360) % 360);
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const idx = Math.round(deg / 45) % 8;
    
    const compassText = document.getElementById('compass-text');
    if (compassText) {
      compassText.innerText = `${deg}° [ ${directions[idx]} ]`;
    }

    const pitchLadder = document.getElementById('pitch-ladder');
    if (pitchLadder) {
      const pitchDeg = (this.player.cameraTiltX * 180 / Math.PI) * 1.5;
      const rollDeg = (this.player.cameraRollZ * 180 / Math.PI);
      pitchLadder.setAttribute('transform', `translate(400, ${225 + pitchDeg}) rotate(${rollDeg})`);
    }
  }

  animate() {
    if (!this.isPlaying) return;
    requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();

    this.player.update(delta, this.joysticks.input);
    this.scenario.update(delta);
    this.soldierManager.update(delta);
    this.missileSystem.update(delta, this.explosionSystem, this.soldierManager);
    this.explosionSystem.update(delta);

    const targetPos = this.getTargetImpactPosition();
    this.targetMarker.position.copy(targetPos);

    this.targetCamera.position.set(targetPos.x, targetPos.y + 25, targetPos.z);
    this.targetCamera.lookAt(targetPos.x, targetPos.y, targetPos.z);

    const inputs = this.player.getInputs(this.joysticks.input);
    const speed = Math.round((Math.abs(inputs.ry) + Math.abs(inputs.rx)) * 52);
    const rangeInfo = this.player.getRangeStatus();

    const teleSpd = document.getElementById('tele-spd');
    const teleAlt = document.getElementById('tele-alt');
    const teleRange = document.getElementById('tele-range');
    const teleBat = document.getElementById('tele-bat');
    const teleRssi = document.getElementById('tele-rssi');
    const teleKills = document.getElementById('tele-kills');

    if (teleSpd) teleSpd.innerText = speed;
    if (teleAlt) teleAlt.innerText = Math.round(this.player.position.y);
    if (teleRange) teleRange.innerText = rangeInfo.km;
    if (teleBat) teleBat.innerText = `${this.player.batteryVoltage.toFixed(1)}V`;
    if (teleRssi) teleRssi.innerText = `${rangeInfo.rssi}dBm`;
    if (teleKills) teleKills.innerText = this.soldierManager.kills;

    this.updateCompassAndHUD();

    this.renderer.setScissorTest(false);
    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    if (this.player.opMode === 'COMBAT') {
      const pipW = 110;
      const pipH = 82;
      const pipX = window.innerWidth - pipW - 275;
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
});