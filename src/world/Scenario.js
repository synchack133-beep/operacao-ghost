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
    // Atmosfera Nublada Típica do Front de Guerra
    this.scene.background = new THREE.Color(0x6b776e);
    this.scene.fog = new THREE.FogExp2(0x6b776e, 0.0065);

    const sun = new THREE.DirectionalLight(0xfff3db, 1.2);
    sun.position.set(80, 120, 50);
    this.scene.add(sun);

    const ambient = new THREE.HemisphereLight(0x6b776e, 0x2b3323, 0.7);
    this.scene.add(ambient);
  }

  buildWarTerrain() {
    // Terreno com variações de relevo e cor de lama/terra
    const groundGeo = new THREE.PlaneGeometry(400, 400, 80, 80);
    const posAttr = groundGeo.attributes.position;

    for (let i = 0; i < posAttr.count; i++) {
      const x = posAttr.getX(i);
      const y = posAttr.getY(i);
      // Relevo irregular
      const height = Math.sin(x * 0.04) * Math.cos(y * 0.04) * 1.2 + Math.sin(x * 0.1) * 0.4;
      posAttr.setZ(i, height);
    }
    groundGeo.computeVertexNormals();

    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x3b382b, // Solo de terra escura/lama
      roughness: 0.9,
      metalness: 0.1
    });

    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    this.scene.add(ground);
  }

  buildTrenchSystem() {
    const sandbagMat = new THREE.MeshStandardMaterial({ color: 0x5e523f, roughness: 0.9 });
    const woodMat = new THREE.MeshStandardMaterial({ color: 0x2b1e15, roughness: 0.8 });

    // Padrão de Trincheira em Ziguezague
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

      // Paredes de Sacos de Areia nas Trincheiras
      for (let d = 0; d < dist; d += 1.2) {
        const pos = start.clone().addScaledVector(dir, d);

        // Lado esquerdo e direito da vala
        for (let side of [-1.2, 1.2]) {
          const bag = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.4, 0.5), sandbagMat);
          const offset = new THREE.Vector3(side, 0.2, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), angle);
          bag.position.copy(pos).add(offset);
          bag.rotation.y = angle;
          this.scene.add(bag);

          const bagLayer2 = bag.clone();
          bagLayer2.position.y = 0.55;
          this.scene.add(bagLayer2);
        }

        // Estacas de suporte em madeira
        if (Math.random() > 0.6) {
          const post = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.6), woodMat);
          post.position.copy(pos).add(new THREE.Vector3(1.1, 0.8, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), angle));
          this.scene.add(post);
        }
      }
    }
  }

  buildWarForest() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x261c14, roughness: 0.9 });
    const burntMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.95 });
    const foliageMat = new THREE.MeshStandardMaterial({ color: 0x27361d, roughness: 0.8 });

    for (let i = 0; i < 90; i++) {
      const x = (Math.random() - 0.5) * 320;
      const z = (Math.random() - 0.5) * 320;

      // Evitar árvores no centro exato da pista
      if (Math.abs(x) < 12 && Math.abs(z) < 12) continue;

      const isDestroyed = Math.random() < 0.45; // 45% das árvores estão destruídas pela guerra

      if (isDestroyed) {
        // Árvores Partidas/Carbonizadas por Artilharia
        const height = 2 + Math.random() * 3.5;
        const stump = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.35, height, 6), burntMat);
        stump.position.set(x, height / 2, z);
        stump.rotation.z = (Math.random() - 0.5) * 0.2;
        this.scene.add(stump);
      } else {
        // Pinheiros Intactos
        const treeGroup = new THREE.Group();
        const height = 7 + Math.random() * 5;
        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.4, height, 8), trunkMat);
        trunk.position.y = height / 2;
        treeGroup.add(trunk);

        for (let c = 0; c < 3; c++) {
          const coneHeight = 3.5 - c * 0.5;
          const coneRadius = 2.4 - c * 0.6;
          const foliage = new THREE.Mesh(new THREE.ConeGeometry(coneRadius, coneHeight, 8), foliageMat);
          foliage.position.y = height * 0.4 + c * 2.0;
          treeGroup.add(foliage);
        }
        treeGroup.position.set(x, 0, z);
        this.scene.add(treeGroup);
      }
    }
  }

  buildCratersAndSmoke() {
    const craterMat = new THREE.MeshBasicMaterial({ color: 0x15120e });
    const smokeMat = new THREE.MeshBasicMaterial({ color: 0x555555, transparent: true, opacity: 0.35 });

    // Locais de Impacto de Artilharia
    const craterLocations = [
      new THREE.Vector3(-25, 0.05, -40),
      new THREE.Vector3(45, 0.05, -80),
      new THREE.Vector3(-70, 0.05, 50),
      new THREE.Vector3(15, 0.05, -120)
    ];

    craterLocations.forEach(loc => {
      // Anel da Cratera
      const craterRim = new THREE.Mesh(new THREE.RingGeometry(1.5, 4.5, 16), craterMat);
      craterRim.rotation.x = -Math.PI / 2;
      craterRim.position.copy(loc);
      this.scene.add(craterRim);

      // Emissor de Fumaça Tática
      for (let p = 0; p < 8; p++) {
        const particle = new THREE.Mesh(new THREE.SphereGeometry(0.8 + Math.random() * 0.8, 8, 8), smokeMat);
        particle.position.set(
          loc.x + (Math.random() - 0.5) * 2,
          loc.y + Math.random() * 4,
          loc.z + (Math.random() - 0.5) * 2
        );
        this.scene.add(particle);
        this.smokeParticles.push({
          mesh: particle,
          baseY: loc.y,
          speed: 0.6 + Math.random() * 0.8
        });
      }
    });
  }

  buildWreckedVehicles() {
    const rustedMat = new THREE.MeshStandardMaterial({ color: 0x211c18, roughness: 0.9 });
    for (let i = 0; i < 6; i++) {
      const tank = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(4.2, 1.5, 6.2), rustedMat);
      body.position.y = 0.75;
      tank.add(body);

      const turret = new THREE.Mesh(new THREE.BoxGeometry(2.5, 1.0, 3.0), rustedMat);
      turret.position.set(0, 1.8, -0.3);
      turret.rotation.y = Math.PI / 6; // Turreta danificada/girada
      tank.add(turret);

      const x = (Math.random() - 0.5) * 220;
      const z = (Math.random() - 0.5) * 220;
      tank.position.set(x, 0, z);
      tank.rotation.y = Math.random() * Math.PI * 2;
      this.scene.add(tank);
    }
  }

  update(delta) {
    // Animação Contínua das Colunas de Fumaça no Solo
    this.smokeParticles.forEach(p => {
      p.mesh.position.y += p.speed * delta;
      p.mesh.scale.addScalar(delta * 0.2);
      if (p.mesh.position.y > p.baseY + 12) {
        p.mesh.position.y = p.baseY + 0.5;
        p.mesh.scale.set(1, 1, 1);
      }
    });
  }
}
