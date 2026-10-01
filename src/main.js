import * as THREE from 'three';
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

new Game();