import * as THREE from 'three';

export class Scenario {
  constructor(scene) {
    this.scene = scene;
    this.buildTerrain();
    this.buildOutpost();
    this.buildTrees();
    this.setupLighting();
  }

  buildTerrain() {
    const size = 600;
    const geometry = new THREE.PlaneGeometry(size, size, 80, 80);
    geometry.rotateX(-Math.PI / 2);

    const pos = geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      const elevation = Math.sin(x * 0.015) * Math.cos(z * 0.015) * 4 + Math.sin(x * 0.04) * 1.5;
      pos.setY(i, elevation);
    }
    geometry.computeVertexNormals();

    const terrainMat = new THREE.MeshStandardMaterial({
      color: 0x3a4d33,
      roughness: 0.95,
      metalness: 0.05,
      flatShading: true
    });

    this.terrain = new THREE.Mesh(geometry, terrainMat);
    this.scene.add(this.terrain);

    const roadGeo = new THREE.PlaneGeometry(16, 400);
    roadGeo.rotateX(-Math.PI / 2);
    roadGeo.rotateY(0.3);
    const roadMat = new THREE.MeshStandardMaterial({ color: 0x221d17, roughness: 0.9 });
    const road = new THREE.Mesh(roadGeo, roadMat);
    road.position.set(-20, 0.1, 0);
    this.scene.add(road);
  }

  buildOutpost() {
    const crateMat = new THREE.MeshStandardMaterial({ color: 0x6e563b, roughness: 0.8 });
    const metalCrateMat = new THREE.MeshStandardMaterial({ color: 0x4a554a, metalness: 0.5 });
    const bunkerMat = new THREE.MeshStandardMaterial({ color: 0x555555, roughness: 0.9 });

    const bunker = new THREE.Mesh(new THREE.BoxGeometry(10, 3, 8), bunkerMat);
    bunker.position.set(-40, 1.5, -60);
    this.scene.add(bunker);

    const towerLegMat = new THREE.MeshStandardMaterial({ color: 0x332211 });
    for (let i = 0; i < 4; i++) {
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 8), towerLegMat);
      const dx = (i % 2 === 0 ? 1 : -1) * 1.5;
      const dz = (i < 2 ? 1 : -1) * 1.5;
      leg.position.set(-50 + dx, 4, -40 + dz);
      this.scene.add(leg);
    }
    const towerTop = new THREE.Mesh(new THREE.BoxGeometry(4, 0.4, 4), bunkerMat);
    towerTop.position.set(-50, 8, -40);
    this.scene.add(towerTop);

    const crateCoords = [
      { x: -35, z: -55 }, { x: -33, z: -57 }, { x: -44, z: -68 },
      { x: 30, z: -20 }, { x: 32, z: -18 }, { x: -10, z: -80 }
    ];
    crateCoords.forEach(c => {
      const crate = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.5, 1.5), Math.random() > 0.5 ? crateMat : metalCrateMat);
      crate.position.set(c.x, 0.75, c.z);
      this.scene.add(crate);
    });
  }

  buildTrees() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x422a1d, roughness: 0.9 });
    const foliageMat = new THREE.MeshStandardMaterial({ color: 0x224422, roughness: 0.8, flatShading: true });

    const trunkGeo = new THREE.CylinderGeometry(0.2, 0.35, 2.5, 6);
    const foliageGeo = new THREE.ConeGeometry(2.0, 5.0, 6);

    for (let i = 0; i < 110; i++) {
      const x = (Math.random() - 0.5) * 450;
      const z = (Math.random() - 0.5) * 450;
      if (Math.hypot(x, z - 70) < 18) continue;

      const tree = new THREE.Group();
      const trunk = new THREE.Mesh(trunkGeo, trunkMat);
      trunk.position.y = 1.25;
      tree.add(trunk);

      const foliage = new THREE.Mesh(foliageGeo, foliageMat);
      foliage.position.y = 4.25;
      tree.add(foliage);

      const scale = 0.7 + Math.random() * 0.6;
      tree.scale.set(scale, scale, scale);
      tree.position.set(x, 0, z);

      this.scene.add(tree);
    }
  }

  setupLighting() {
    this.scene.fog = new THREE.FogExp2(0x18241b, 0.006);

    const ambientLight = new THREE.AmbientLight(0xd4e6d4, 0.7);
    this.scene.add(ambientLight);

    const sun = new THREE.DirectionalLight(0xfff5dd, 1.1);
    sun.position.set(100, 150, 80);
    this.scene.add(sun);
  }

  update(delta) {}
}