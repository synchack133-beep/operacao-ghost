import * as THREE from 'three';

export class Operator {
  constructor(scene, position = new THREE.Vector3(0, 0, 70)) {
    this.scene = scene;
    this.position = position;
    this.group = new THREE.Group();

    this.buildOperator();
    this.buildLauncherTube();
    this.buildBunker();

    this.group.position.copy(this.position);
    this.scene.add(this.group);
  }

  buildOperator() {
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0x2e3d2c });
    const gearMat = new THREE.MeshStandardMaterial({ color: 0x111111 });

    const bodyGeo = new THREE.BoxGeometry(0.8, 1.3, 0.5);
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 0.65;
    this.group.add(body);

    const headGeo = new THREE.BoxGeometry(0.45, 0.45, 0.45);
    const head = new THREE.Mesh(headGeo, bodyMat);
    head.position.set(0, 1.5, 0);

    const gogglesGeo = new THREE.BoxGeometry(0.5, 0.18, 0.22);
    const goggles = new THREE.Mesh(gogglesGeo, gearMat);
    goggles.position.set(0, 1.55, -0.2);

    this.group.add(head);
    this.group.add(goggles);

    const tabletGeo = new THREE.BoxGeometry(0.6, 0.05, 0.4);
    const tabletMat = new THREE.MeshBasicMaterial({ color: 0x00ff96 });
    const tablet = new THREE.Mesh(tabletGeo, tabletMat);
    tablet.position.set(0, 0.9, -0.4);
    tablet.rotation.x = 0.4;
    this.group.add(tablet);
  }

  buildLauncherTube() {
    const tubeGeo = new THREE.CylinderGeometry(0.22, 0.22, 2.0, 16);
    const tubeMat = new THREE.MeshStandardMaterial({ color: 0x1f261d, roughness: 0.8 });
    const tube = new THREE.Mesh(tubeGeo, tubeMat);
    tube.position.set(1.4, 0.8, -0.4);
    tube.rotation.x = -Math.PI / 4;
    this.group.add(tube);

    const legGeo = new THREE.CylinderGeometry(0.04, 0.04, 1.1);
    const legMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
    const leg1 = new THREE.Mesh(legGeo, legMat);
    leg1.position.set(1.1, 0.5, -0.2);
    leg1.rotation.z = 0.3;
    this.group.add(leg1);

    const leg2 = new THREE.Mesh(legGeo, legMat);
    leg2.position.set(1.7, 0.5, -0.2);
    leg2.rotation.z = -0.3;
    this.group.add(leg2);
  }

  buildBunker() {
    const sandbagMat = new THREE.MeshStandardMaterial({ color: 0x736551, roughness: 0.9 });
    for (let i = -1.8; i <= 1.8; i += 0.7) {
      const bag1 = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.28, 0.4), sandbagMat);
      bag1.position.set(i, 0.14, -0.9);
      this.group.add(bag1);

      const bag2 = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.28, 0.4), sandbagMat);
      bag2.position.set(i, 0.42, -0.9);
      this.group.add(bag2);
    }

    const poleGeo = new THREE.CylinderGeometry(0.04, 0.04, 3.8);
    const poleMat = new THREE.MeshStandardMaterial({ color: 0x444444 });
    const pole = new THREE.Mesh(poleGeo, poleMat);
    pole.position.set(-1.8, 1.9, 0);
    this.group.add(pole);

    const dishGeo = new THREE.ConeGeometry(0.5, 0.25, 16);
    const dish = new THREE.Mesh(dishGeo, poleMat);
    dish.position.set(-1.8, 3.6, -0.15);
    dish.rotation.x = Math.PI / 3;
    this.group.add(dish);
  }
}
