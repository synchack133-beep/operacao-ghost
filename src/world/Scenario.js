import * as THREE from 'three';

export class Scenario {
  constructor(scene) {
    this.scene = scene;
    this.setupAtmosphere();
    this.buildTerrain();
    this.buildPineForest();
    this.buildMilitaryVehicles();
    this.buildRuins();
  }

  setupAtmosphere() {
    // Céu e Névoa Tática Nublada
    this.scene.background = new THREE.Color(0x8fa3a8);
    this.scene.fog = new THREE.FogExp2(0x8fa3a8, 0.007);

    // Luz Sol Quente
    const dirLight = new THREE.DirectionalLight(0xfffaed, 1.4);
    dirLight.position.set(60, 100, 40);
    this.scene.add(dirLight);

    const hemiLight = new THREE.HemisphereLight(0x8fa3a8, 0x3b4a24, 0.6);
    this.scene.add(hemiLight);
  }

  buildTerrain() {
    // Textura de Solo / Campo de Batalha (Verde Terra)
    const groundGeo = new THREE.PlaneGeometry(350, 350, 64, 64);
    
    // Pequena variação de relevo no terreno
    const posAttr = groundGeo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const x = posAttr.getX(i);
      const y = posAttr.getY(i);
      const z = Math.sin(x * 0.05) * Math.cos(y * 0.05) * 0.8;
      posAttr.setZ(i, z);
    }
    groundGeo.computeVertexNormals();

    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x3d4d26,
      roughness: 0.95,
      metalness: 0.05
    });

    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    this.scene.add(ground);
  }

  buildPineForest() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x2b1e17, roughness: 0.9 });
    const foliageMat = new THREE.MeshStandardMaterial({ color: 0x1f3318, roughness: 0.8 });

    for (let i = 0; i < 60; i++) {
      const treeGroup = new THREE.Group();

      const height = 6 + Math.random() * 5;
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.4, height, 8), trunkMat);
      trunk.position.y = height / 2;
      treeGroup.add(trunk);

      // Camadas de Folha Cone (Pinheiro)
      for (let c = 0; c < 3; c++) {
        const coneHeight = 3 + c * 0.8;
        const coneRadius = 2.2 - c * 0.5;
        const foliage = new THREE.Mesh(new THREE.ConeGeometry(coneRadius, coneHeight, 8), foliageMat);
        foliage.position.y = height * 0.5 + c * 1.8;
        treeGroup.add(foliage);
      }

      const x = (Math.random() - 0.5) * 260;
      const z = (Math.random() - 0.5) * 260;
      if (Math.abs(x) > 15 || Math.abs(z) > 15) {
        treeGroup.position.set(x, 0, z);
        this.scene.add(treeGroup);
      }
    }
  }

  buildMilitaryVehicles() {
    const camoMat = new THREE.MeshStandardMaterial({ color: 0x2e3b2b, roughness: 0.7 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x1a1f1a, roughness: 0.5 });

    for (let i = 0; i < 8; i++) {
      const tank = new THREE.Group();

      // Chassi
      const body = new THREE.Mesh(new THREE.BoxGeometry(4.0, 1.4, 6.0), camoMat);
      body.position.y = 0.8;
      tank.add(body);

      // Torreta
      const turret = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.0, 3.2), camoMat);
      turret.position.set(0, 1.9, -0.4);
      tank.add(turret);

      // Canhão
      const cannon = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 4.0), metalMat);
      cannon.position.set(0, 1.9, -3.0);
      cannon.rotation.x = Math.PI / 2;
      tank.add(cannon);

      const x = (Math.random() - 0.5) * 200;
      const z = (Math.random() - 0.5) * 200;
      tank.position.set(x, 0, z);
      tank.rotation.y = Math.random() * Math.PI * 2;
      this.scene.add(tank);
    }
  }

  buildRuins() {
    const concreteMat = new THREE.MeshStandardMaterial({ color: 0x5a605c, roughness: 0.9 });
    for (let i = 0; i < 10; i++) {
      const wall = new THREE.Mesh(new THREE.BoxGeometry(8, 4, 1.0), concreteMat);
      const x = (Math.random() - 0.5) * 220;
      const z = (Math.random() - 0.5) * 220;
      wall.position.set(x, 2, z);
      wall.rotation.y = Math.random() * Math.PI;
      this.scene.add(wall);
    }
  }
}
