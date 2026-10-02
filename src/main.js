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
    this.setupOrbitTouch();
    this.clock = new THREE.Clock();
    this.isPlaying = false;

    window.addEventListener('resize', () => this.onResize());
  }

  setupEvents() {
    const btnStart = document.getElementById('btn-start');
    const btnFullscreen = document.getElementById('btn-fullscreen');
    const btnViewMode = document.getElementById('btn-view-mode');
    const btnOpMode = document.getElementById('btn-op-mode');
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

    if (btnViewMode) {
      btnViewMode.addEventListener('click', () => {
        const mode = this.player.toggleViewMode();
        btnViewMode.innerText = mode === 'FPV' ? '🎥 FPV' : '🚁 3ª PESSOA';
      });
    }

    if (btnOpMode) {
      btnOpMode.addEventListener('click', () => {
        const op = this.player.toggleOpMode();
        btnOpMode.innerText = op === 'COMBAT' ? '⚔️ COMBATE' : '👁️ VISUAL';

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

  // Permite arrastar o dedo na área central da tela para girar 360° em 3ª pessoa
  setupOrbitTouch() {
    let lastX = 0, lastY = 0;
    let isDragging = false;

    window.addEventListener('touchstart', (e) => {
      for (let i = 0; i < e.changedTouches.length; i++) {
        const t = e.changedTouches[i];
        if (t.clientX > 120 && t.clientX < window.innerWidth - 120) {
          isDragging = true;
          lastX = t.clientX;
          lastY = t.clientY;
          break;
        }
      }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (!isDragging || this.player.viewMode !== 'THIRD') return;
      for (let i = 0; i < e.touches.length; i++) {
        const t = e.touches[i];
        if (t.clientX > 100 && t.clientX < window.innerWidth - 100) {
          const dx = t.clientX - lastX;
          const dy = t.clientY - lastY;
          this.player.rotateOrbit(-dx * 0.008, -dy * 0.008);
          lastX = t.clientX;
          lastY = t.clientY;
          break;
        }
      }
    }, { passive: true });

    window.addEventListener('touchend', () => { isDragging = false; });
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

    // 1. CÂMERA PRINCIPAL
    this.renderer.setScissorTest(false);
    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    // 2. CÂMERA SECUNDÁRIA (PIP) - Apenas se estiver em modo Combate
    if (this.player.opMode === 'COMBAT') {
      const pipW = 120;
      const pipH = 90;
      const pipX = window.innerWidth - pipW - 180;
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