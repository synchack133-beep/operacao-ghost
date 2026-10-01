import * as THREE from 'three';
import { Player } from './entities/Player.js';
import { EnemyManager } from './entities/EnemyManager.js';
import { ProjectileSystem } from './entities/Projectiles.js';
import { ExplosionSystem } from './effects/Explosions.js';
import { soundManager } from './audio/SoundManager.js';
import { Radar } from './ui/Radar.js';
import { JoystickController } from './controls/Joystick.js';

class Game {
  constructor() {
    this.container = document.getElementById('canvas-container');
    
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x020805);
    this.scene.fog = new THREE.FogExp2(0x020805, 0.022);

    this.camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 200);
    
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00ff96, 1.2);
    dirLight.position.set(20, 40, 20);
    this.scene.add(dirLight);

    this.player = new Player(this.scene, this.camera);
    this.explosionSystem = new ExplosionSystem(this.scene);
    this.enemyManager = new EnemyManager(this.scene, this.player, this.explosionSystem);
    this.projectileSystem = new ProjectileSystem(this.scene);
    this.radar = new Radar('radar-canvas');

    this.joysticks = new JoystickController({
      leftZoneId: 'zone-left',
      rightZoneId: 'zone-right',
      leftStickId: 'stick-left',
      rightStickId: 'stick-right'
    });

    this.dataModules = [];
    this.intelCollected = 0;
    this.totalIntel = 4;
    this.isNightVision = false;

    this.buildEnvironment();
    this.setupDataModules();
    this.setupEvents();

    this.clock = new THREE.Clock();
    this.isPlaying = false;

    window.addEventListener('resize', () => this.onResize());
  }

  buildEnvironment() {
    const grid = new THREE.GridHelper(140, 70, 0x00ff96, 0x003318);
    grid.position.y = 0;
    this.scene.add(grid);

    const buildingGeo = new THREE.BoxGeometry(1, 1, 1);
    const buildingMat = new THREE.MeshStandardMaterial({ color: 0x08180e, wireframe: true });

    for (let i = 0; i < 30; i++) {
      const mesh = new THREE.Mesh(buildingGeo, buildingMat);
      const w = 4 + Math.random() * 6;
      const h = 5 + Math.random() * 15;
      const d = 4 + Math.random() * 6;
      mesh.scale.set(w, h, d);
      mesh.position.set((Math.random() - 0.5) * 90, h / 2, (Math.random() - 0.5) * 90);
      this.scene.add(mesh);
    }
  }

  setupDataModules() {
    const geo = new THREE.IcosahedronGeometry(0.8, 0);
    const mat = new THREE.MeshBasicMaterial({ color: 0x00ff96, wireframe: true });

    const pos = [{ x: 20, z: 20 }, { x: -22, z: 22 }, { x: 25, z: -25 }, { x: -20, z: -20 }];

    pos.forEach(p => {
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(p.x, 1.5, p.z);
      this.scene.add(mesh);
      this.dataModules.push({ mesh: mesh, collected: false });
    });
  }

  setupEvents() {
    const btnShoot = document.getElementById('btn-shoot');
    const btnStart = document.getElementById('btn-start');
    const btnRestart = document.getElementById('btn-restart');
    const btnNV = document.getElementById('btn-nightvision');

    if (btnShoot) {
      btnShoot.addEventListener('touchstart', (e) => { e.preventDefault(); this.shoot(); });
      btnShoot.addEventListener('click', () => this.shoot());
    }

    if (btnNV) {
      btnNV.addEventListener('touchstart', (e) => { e.preventDefault(); this.toggleNightVision(); });
      btnNV.addEventListener('click', () => this.toggleNightVision());
    }

    if (btnStart) {
      btnStart.addEventListener('touchstart', (e) => { e.preventDefault(); this.startMission(); });
      btnStart.addEventListener('click', () => this.startMission());
    }

    if (btnRestart) {
      btnRestart.addEventListener('touchstart', (e) => { e.preventDefault(); this.restartMission(); });
      btnRestart.addEventListener('click', () => this.restartMission());
    }
  }

  toggleNightVision() {
    this.isNightVision = !this.isNightVision;
    this.scene.background = new THREE.Color(this.isNightVision ? 0x001a0a : 0x020805);
    this.scene.fog.color = new THREE.Color(this.isNightVision ? 0x001a0a : 0x020805);
  }

  shoot() {
    if (!this.isPlaying) return;
    soundManager.init();
    const spawnPos = this.player.position.clone().add(this.player.getForwardDirection().multiplyScalar(1.2));
    this.projectileSystem.spawnBullet(spawnPos, this.player.getForwardDirection());
    soundManager.playLaser();
  }

  startMission() {
    soundManager.init();
    document.getElementById('modal-start').style.display = 'none';
    this.isPlaying = true;
    this.clock.start();
    this.animate();
  }

  restartMission() {
    soundManager.init();
    document.getElementById('modal-end').style.display = 'none';
    this.player.reset();
    this.enemyManager.reset();
    this.projectileSystem.reset();
    this.intelCollected = 0;
    this.dataModules.forEach(mod => {
      mod.collected = false;
      mod.mesh.visible = true;
    });
    this.isPlaying = true;
    this.updateHUD();
  }

  gameOver(title, msg) {
    this.isPlaying = false;
    document.getElementById('end-title').innerText = title;
    document.getElementById('end-message').innerText = msg;
    document.getElementById('modal-end').style.display = 'flex';
  }

  updateHUD() {
    const healthBar = document.getElementById('health-bar');
    const batteryBar = document.getElementById('battery-bar');
    const intelText = document.getElementById('intel-count');
    const altSpeedText = document.getElementById('alt-speed');

    if (healthBar) healthBar.style.width = `${Math.max(0, this.player.health)}%`;
    if (batteryBar) batteryBar.style.width = `${Math.max(0, this.player.battery)}%`;
    if (intelText) intelText.innerText = `DADOS: ${this.intelCollected} / ${this.totalIntel}`;
    
    if (altSpeedText) {
      const alt = Math.round(this.player.position.y);
      const vel = Math.round(this.player.getForwardDirection().length() * 20);
      altSpeedText.innerText = `ALT: ${alt}m | VEL: ${vel}km/h`;
    }
  }

  animate() {
    if (!this.isPlaying) return;
    requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();

    // Atualiza jogador via inputs do Joystick
    this.player.update(delta, this.joysticks.input);
    this.enemyManager.update(delta);
    this.projectileSystem.update(delta, this.enemyManager.enemies, this.explosionSystem, soundManager);
    this.explosionSystem.update(delta);

    this.dataModules.forEach(mod => {
      if (!mod.collected && this.player.position.distanceTo(mod.mesh.position) < 2.0) {
        mod.collected = true;
        mod.mesh.visible = false;
        this.intelCollected++;
        soundManager.playCollect();

        if (this.intelCollected >= this.totalIntel) {
          this.gameOver('MISSÃO CUMPRIDA!', 'Todos os dados do setor foram recuperados!');
        }
      }
      if (!mod.collected) {
        mod.mesh.rotation.y += 0.02;
      }
    });

    if (this.player.health <= 0) {
      this.gameOver('FALHA NA MISSÃO', 'Seu drone foi abatido em combate.');
    } else if (this.player.battery <= 0) {
      this.gameOver('FALHA NA MISSÃO', 'Bateria do drone esgotada.');
    }

    this.radar.draw(this.player, this.enemyManager.enemies, this.dataModules);
    this.updateHUD();

    this.renderer.render(this.scene, this.camera);
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }
}

new Game();