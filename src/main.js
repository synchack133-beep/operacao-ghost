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

new Game();