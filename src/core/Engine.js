import * as THREE from 'three';
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
}
