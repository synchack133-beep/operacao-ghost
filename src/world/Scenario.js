import * as THREE from 'three';

export class Scenario {
  constructor(scene) {
    this.scene = scene;
    this.smokeParticles = [];
    this.setupAtmosphere();
    this.buildWarTerrain();
    this.buildTrenchSystem();
    this.buildWarForest();
    this.buildCratersAndSmoke();
    this.buildWreckedVehicles();
  }

  setupAtmosphere() {
    this.scene.background = new THREE.Color(0x6b776e);
    this.scene.fog = new THREE.FogExp2(0x6b776e, 0.0065);

    const sun = new THREE.DirectionalLight(0xfff3db, 1.2);
    sun.position.set(80, 120, 50);
    this.scene.add(sun);

    const ambient = new THREE.HemisphereLight(0x6b776e, 0x2b3323, 0.7);
    this.scene.add(ambient);
  }

  buildWarTerrain() {
    const groundGeo = new THREE.PlaneGeometry(400, 400, 60, 60);
    const posAttr = groundGeo.attributes.position;

    for (let i = 0; i < posAttr.count; i++) {
      const x = posAttr.getX(i);
      const y = posAttr.getY(i);
      const height = Math.sin(x * 0.04) * Math.cos(y * 0.04) * 1.2;
      posAttr.setZ(i, height);
    }
    groundGeo.computeVertexNormals();

    const groundMat = new THREE.MeshStandardMaterial({ color: 0x3b382b, roughness: 0.9 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    this.scene.add(ground);
  }

  buildTrenchSystem() {
    const sandbagMat = new THREE.MeshStandardMaterial({ color: 0x5e523f, roughness: 0.9 });
    const woodMat = new THREE.MeshStandardMaterial({ color: 0x2b1e15, roughness: 0.8 });

    const points = [
      new THREE.Vector3(-60, 0, 20),
      new THREE.Vector3(-30, 0, 10),
      new THREE.Vector3(0, 0, 30),
      new THREE.Vector3(35, 0, 15),
      new THREE.Vector3(70, 0, 35)
    ];

    for (let p = 0; p < points.length - 1; p++) {
      const start = points[p];
      const end = points[p + 1];
      const dist = start.distanceTo(end);
      const dir = new THREE.Vector3().subVectors(end, start).normalize();
      const angle = Math.atan2(dir.x, dir.z);

      for (let d = 0; d < dist; d += 1.5) {
        const pos = start.clone().addScaledVector(dir, d);
        for (let side of [-1.2, 1.2]) {
          const bag = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.4, 0.5), sandbagMat);
          const offset = new THREE.Vector3(side, 0.2, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), angle);
          bag.position.copy(pos).add(offset);
          bag.rotation.y = angle;
          this.scene.add(bag);
        }
      }
    }
  }

  buildWarForest() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x261c14, roughness: 0.9 });
    const burntMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.95 });
    const foliageMat = new THREE.MeshStandardMaterial({ color: 0x27361d, roughness: 0.8 });

    for (let i = 0; i < 70; i++) {
      const x = (Math.random() - 0.5) * 300;
      const z = (Math.random() - 0.5) * 300;
      if (Math.abs(x) < 15 && Math.abs(z) < 15) continue;

      const isDestroyed = Math.random() < 0.4;

      if (isDestroyed) {
        const height = 2 + Math.random() * 3;
        const stump = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.35, height, 6), burntMat);
        stump.position.set(x, height / 2, z);
        this.scene.add(stump);
      } else {
        const treeGroup = new THREE.Group();
        const height = 6 + Math.random() * 4;
        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.4, height, 6), trunkMat);
        trunk.position.y = height / 2;
        treeGroup.add(trunk);

        const foliage = new THREE.Mesh(new THREE.ConeGeometry(2.2, 4.0, 6), foliageMat);
        foliage.position.y = height * 0.6;
        treeGroup.add(foliage);

        treeGroup.position.set(x, 0, z);
        this.scene.add(treeGroup);
      }
    }
  }

  buildCratersAndSmoke() {
    const craterMat = new THREE.MeshBasicMaterial({ color: 0x15120e });
    const smokeMat = new THREE.MeshBasicMaterial({ color: 0x555555, transparent: true, opacity: 0.35 });

    const craterLocations = [
      new THREE.Vector3(-25, 0.05, -40),
      new THREE.Vector3(45, 0.05, -80),
      new THREE.Vector3(-70, 0.05, 50)
    ];

    craterLocations.forEach(loc => {
      const craterRim = new THREE.Mesh(new THREE.RingGeometry(1.5, 4.0, 12), craterMat);
      craterRim.rotation.x = -Math.PI / 2;
      craterRim.position.copy(loc);
      this.scene.add(craterRim);

      for (let p = 0; p < 5; p++) {
        const particle = new THREE.Mesh(new THREE.SphereGeometry(0.8, 6, 6), smokeMat);
        particle.position.set(loc.x + (Math.random() - 0.5) * 2, loc.y + Math.random() * 3, loc.z + (Math.random() - 0.5) * 2);
        this.scene.add(particle);
        this.smokeParticles.push({ mesh: particle, baseY: loc.y, speed: 0.6 + Math.random() * 0.6 });
      }
    });
  }

  buildWreckedVehicles() {
    const rustedMat = new THREE.MeshStandardMaterial({ color: 0x211c18, roughness: 0.9 });
    for (let i = 0; i < 4; i++) {
      const tank = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(4.0, 1.4, 6.0), rustedMat);
      body.position.y = 0.7;
      tank.add(body);

      const x = (Math.random() - 0.5) * 200;
      const z = (Math.random() - 0.5) * 200;
      tank.position.set(x, 0, z);
      tank.rotation.y = Math.random() * Math.PI * 2;
      this.scene.add(tank);
    }
  }

  update(delta) {
    this.smokeParticles.forEach(p => {
      p.mesh.position.y += p.speed * delta;
      if (p.mesh.position.y > p.baseY + 10) {
        p.mesh.position.y = p.baseY + 0.5;
      }
    });
  }
}