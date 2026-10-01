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

new Game();