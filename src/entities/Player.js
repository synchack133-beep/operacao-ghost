import * as THREE from 'three';

export class Player {
  constructor(scene, camera, operatorPosition) {
    this.scene = scene;
    this.camera = camera;
    this.operatorPos = operatorPosition || new THREE.Vector3(0, 0, 70);
    
    this.position = new THREE.Vector3(0, 12, 60);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
    
    // Tilt dinâmico da câmera para simular FPV real
    this.cameraTiltX = 0;
    this.cameraRollZ = 0;

    this.speed = 22;
    this.rotSpeed = 2.0;
    this.minAltitude = 1.0;
    this.maxAltitude = 70.0;

    this.maxRangeMeters = 200;
    this.currentDistance = 0;

    const bodyGeo = new THREE.BoxGeometry(1.0, 0.15, 1.0);
    const mat = new THREE.MeshBasicMaterial({ color: 0x00ff96, wireframe: true });
    this.mesh = new THREE.Mesh(bodyGeo, mat);
    this.scene.add(this.mesh);
  }

  getForwardDirection() {
    const fwd = new THREE.Vector3(0, -0.3, -1);
    fwd.applyEuler(this.rotation);
    return fwd.normalize();
  }

  update(delta, input) {
    // Rotação YAW
    if (input.leftX) {
      this.rotation.y -= input.leftX * this.rotSpeed * delta;
      // Inclinamento Lateral (Banking/Roll) ao virar
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, -input.leftX * 0.25, delta * 5);
    } else {
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, 0, delta * 5);
    }

    // Altitude
    if (input.leftY) {
      this.position.y -= input.leftY * this.speed * delta;
    }

    // Movimento para frente/trás/lados
    const nextPos = this.position.clone();
    if (input.rightX || input.rightY) {
      const moveVec = new THREE.Vector3(input.rightX, 0, input.rightY);
      moveVec.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      nextPos.addScaledVector(moveVec, this.speed * delta);

      // Inclinamento Pitch para frente/trás ao acelerar
      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, -input.rightY * 0.2, delta * 5);
    } else {
      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, 0, delta * 5);
    }

    // Limites de Alcance Rádio do Operador
    const distToOperator = new THREE.Vector2(nextPos.x - this.operatorPos.x, nextPos.z - this.operatorPos.z).length();
    if (distToOperator <= this.maxRangeMeters) {
      this.position.copy(nextPos);
      this.currentDistance = distToOperator;
    }

    if (this.position.y < this.minAltitude) this.position.y = this.minAltitude;
    if (this.position.y > this.maxAltitude) this.position.y = this.maxAltitude;

    this.mesh.position.copy(this.position);
    this.mesh.rotation.copy(this.rotation);

    // Câmera FPV com Tilt Tático
    this.camera.position.copy(this.position);
    this.camera.rotation.set(
      this.rotation.x + this.cameraTiltX,
      this.rotation.y,
      this.rotation.z + this.cameraRollZ,
      'YXZ'
    );
  }

  getRangeStatus() {
    const kmSimulated = ((this.currentDistance / this.maxRangeMeters) * 3.0).toFixed(2);
    const pct = (this.currentDistance / this.maxRangeMeters) * 100;
    return { km: kmSimulated, pct: pct, isWarning: pct > 80 };
  }
}
