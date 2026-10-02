import * as THREE from 'three';

export class Operator {
  constructor(scene, position) {
    this.scene = scene;
    this.position = position || new THREE.Vector3(0, 0, 70);
    this.buildOperator();
  }

  buildOperator() {
    this.group = new THREE.Group();
    this.group.position.copy(this.position);

    const tentMat = new THREE.MeshStandardMaterial({ color: 0x3d4f3d, roughness: 0.8 });
    const tent = new THREE.Mesh(new THREE.ConeGeometry(3, 2.5, 4), tentMat);
    tent.rotation.y = Math.PI / 4;
    tent.position.set(0, 1.25, 0);
    this.group.add(tent);

    const camoMat = new THREE.MeshStandardMaterial({ color: 0x2b3d2b, roughness: 0.7 });
    const skinMat = new THREE.MeshStandardMaterial({ color: 0xd2a679 });
    const gearMat = new THREE.MeshStandardMaterial({ color: 0x111111 });

    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.35, 1.1, 8), camoMat);
    body.position.set(2, 0.55, 1);
    this.group.add(body);

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 10), skinMat);
    head.position.set(2, 1.2, 1);
    this.group.add(head);

    const controller = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.15, 0.3), gearMat);
    controller.position.set(2, 0.7, 0.7);
    this.group.add(controller);

    const antenna = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.2, 6), gearMat);
    antenna.position.set(2.1, 1.3, 0.6);
    this.group.add(antenna);

    this.scene.add(this.group);
  }
}