import * as THREE from 'three';

export class Player {
  constructor(scene, camera) {
    this.scene = scene;
    this.camera = camera;
    
    this.position = new THREE.Vector3(0, 12, 25);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
    
    this.speed = 15;
    this.rotSpeed = 1.8;
    this.minAltitude = 1.2; // Impedir que o drone desça abaixo do chão
    this.maxAltitude = 50.0;

    const bodyGeo = new THREE.BoxGeometry(1.2, 0.2, 1.2);
    const mat = new THREE.MeshStandardMaterial({ color: 0x00ff96, wireframe: true });
    this.mesh = new THREE.Mesh(bodyGeo, mat);
    this.scene.add(this.mesh);
  }

  getForwardDirection() {
    const fwd = new THREE.Vector3(0, -0.4, -1);
    fwd.applyEuler(this.rotation);
    return fwd.normalize();
  }

  update(delta, input) {
    if (input.leftX) {
      this.rotation.y -= input.leftX * this.rotSpeed * delta;
    }

    if (input.leftY) {
      this.position.y -= input.leftY * this.speed * delta;
    }

    if (input.rightX || input.rightY) {
      const moveVec = new THREE.Vector3(input.rightX, 0, input.rightY);
      moveVec.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      this.position.addScaledVector(moveVec, this.speed * delta);
    }

    // BLOQUEIO DE COLISÃO COM O SOLO
    if (this.position.y < this.minAltitude) {
      this.position.y = this.minAltitude;
    }
    if (this.position.y > this.maxAltitude) {
      this.position.y = this.maxAltitude;
    }

    this.mesh.position.copy(this.position);
    this.mesh.rotation.copy(this.rotation);

    this.camera.position.copy(this.position);
    this.camera.rotation.copy(this.rotation);
  }
}
