import * as THREE from 'three';
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
}
