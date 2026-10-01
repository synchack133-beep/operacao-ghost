import * as THREE from 'three';

export class Scenario {
  constructor(scene) {
    this.scene = scene;
    this.buildTerrain();
    this.buildRuins();
    this.buildDeadTrees();
    this.buildVehicles();
  }

  buildTerrain() {
    const grid = new THREE.GridHelper(300, 150, 0x00ff96, 0x002211);
    this.scene.add(grid);

    const groundGeo = new THREE.PlaneGeometry(300, 300);
    const groundMat = new THREE.MeshBasicMaterial({ color: 0x040a06, side: THREE.DoubleSide });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = Math.PI / 2;
    ground.position.y = -0.05;
    this.scene.add(ground);
  }

  buildRuins() {
    const wallMat = new THREE.MeshStandardMaterial({ color: 0x222b25, roughness: 0.9 });
    for (let i = 0; i < 18; i++) {
      const w = 6 + Math.random() * 8;
      const h = 3 + Math.random() * 5;
      const wall = new THREE.Mesh(new THREE.BoxGeometry(w, h, 1.2), wallMat);
      
      const x = (Math.random() - 0.5) * 180;
      const z = (Math.random() - 0.5) * 180 - 10;
      wall.position.set(x, h / 2, z);
      wall.rotation.y = Math.random() * Math.PI;
      this.scene.add(wall);
    }
  }

  buildDeadTrees() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x1a120b });
    for (let i = 0; i < 25; i++) {
      const h = 4 + Math.random() * 5;
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.35, h), trunkMat);
      const x = (Math.random() - 0.5) * 220;
      const z = (Math.random() - 0.5) * 220 - 10;
      trunk.position.set(x, h / 2, z);
      this.scene.add(trunk);
    }
  }

  buildVehicles() {
    const vehicleMat = new THREE.MeshStandardMaterial({ color: 0x332a1e, roughness: 0.8 });
    for (let i = 0; i < 7; i++) {
      const tankGroup = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(3.8, 1.6, 5.5), vehicleMat);
      body.position.y = 0.8;
      tankGroup.add(body);

      const turret = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.0, 2.8), vehicleMat);
      turret.position.set(0, 2.0, -0.4);
      tankGroup.add(turret);

      const cannon = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 3.8), vehicleMat);
      cannon.position.set(0, 2.0, -2.8);
      cannon.rotation.x = Math.PI / 2;
      tankGroup.add(cannon);

      const x = (Math.random() - 0.5) * 160;
      const z = (Math.random() - 0.5) * 160;
      tankGroup.position.set(x, 0, z);
      tankGroup.rotation.y = Math.random() * Math.PI * 2;
      this.scene.add(tankGroup);
    }
  }
}
