import * as THREE from 'three';

export class Player {
  constructor(scene, camera, operatorPosition) {
    this.scene = scene;
    this.camera = camera;
    this.operatorPos = operatorPosition || new THREE.Vector3(0, 0, 70);
    
    this.position = new THREE.Vector3(0, 12, 60);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
    
    this.speed = 18;
    this.rotSpeed = 1.8;
    this.minAltitude = 1.2;
    this.maxAltitude = 60.0;

    // Alcance Máximo Rádio (Representando 3.00 km = 180 metros no espaço do jogo)
    this.maxRangeMeters = 180;
    this.currentDistance = 0;

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

    const nextPos = this.position.clone();
    if (input.rightX || input.rightY) {
      const moveVec = new THREE.Vector3(input.rightX, 0, input.rightY);
      moveVec.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      nextPos.addScaledVector(moveVec, this.speed * delta);
    }

    // Calcular distância até o Operador
    const distToOperator = new THREE.Vector2(nextPos.x - this.operatorPos.x, nextPos.z - this.operatorPos.z).length();
    
    // Bloquear movimento se exceder o alcance
    if (distToOperator <= this.maxRangeMeters) {
      this.position.copy(nextPos);
      this.currentDistance = distToOperator;
    }

    if (this.position.y < this.minAltitude) this.position.y = this.minAltitude;
    if (this.position.y > this.maxAltitude) this.position.y = this.maxAltitude;

    this.mesh.position.copy(this.position);
    this.mesh.rotation.copy(this.rotation);

    this.camera.position.copy(this.position);
    this.camera.rotation.copy(this.rotation);
  }

  getRangeStatus() {
    const kmSimulated = ((this.currentDistance / this.maxRangeMeters) * 3.0).toFixed(2);
    const pct = (this.currentDistance / this.maxRangeMeters) * 100;
    return { km: kmSimulated, pct: pct, isWarning: pct > 80 };
  }
}
