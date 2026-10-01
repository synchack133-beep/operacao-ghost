import * as THREE from 'three';

export class Player {
  constructor(scene, camera) {
    this.scene = scene;
    this.camera = camera;
    
    this.mesh = new THREE.Group();
    
    // Corpo do Drone 3D estilo Tático
    const bodyGeo = new THREE.BoxGeometry(0.9, 0.2, 0.9);
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0x00ff96, wireframe: true });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    this.mesh.add(body);

    // Hélices nas pontas
    const propGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.05, 8);
    const propMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, wireframe: true });
    const offsets = [
      { x: 0.6, z: 0.6 }, { x: -0.6, z: 0.6 },
      { x: 0.6, z: -0.6 }, { x: -0.6, z: -0.6 }
    ];

    this.props = [];
    offsets.forEach(off => {
      const p = new THREE.Mesh(propGeo, propMat);
      p.position.set(off.x, 0.15, off.z);
      this.mesh.add(p);
      this.props.push(p);
    });

    this.mesh.position.set(0, 3, 0);
    this.scene.add(this.mesh);

    this.health = 100;
    this.battery = 100;
    this.velocity = new THREE.Vector3();

    this.moveSpeed = 18.0;
    this.turnSpeed = 2.4;
    this.verticalSpeed = 12.0;
  }

  get position() { return this.mesh.position; }

  getForwardDirection() {
    const dir = new THREE.Vector3(0, 0, -1);
    dir.applyQuaternion(this.mesh.quaternion);
    return dir;
  }

  update(delta, input) {
    if (this.battery > 0) {
      this.battery -= delta * 0.25;
    }

    // 1. Giro (Yaw)
    if (Math.abs(input.yaw) > 0.05) {
      this.mesh.rotation.y -= input.yaw * this.turnSpeed * delta;
    }

    // 2. Altitude (Throttle)
    if (Math.abs(input.throttle) > 0.05) {
      this.mesh.position.y += input.throttle * this.verticalSpeed * delta;
      this.mesh.position.y = Math.max(1.0, Math.min(35.0, this.mesh.position.y));
    }

    // 3. Movimento Relativo de Voo (Pitch & Roll)
    const moveDir = new THREE.Vector3(input.roll, 0, -input.pitch);
    if (moveDir.lengthSq() > 0.002) {
      moveDir.clampLength(0, 1);
      moveDir.applyQuaternion(this.mesh.quaternion);
      this.mesh.position.addScaledVector(moveDir, this.moveSpeed * delta);
    }

    // Animação das Hélices
    this.props.forEach(p => p.rotation.y += 0.4);

    // Inclinação visual dinâmica ao voar (Tilt Effect)
    this.mesh.rotation.z = THREE.MathUtils.lerp(this.mesh.rotation.z, -input.roll * 0.35, delta * 10);
    this.mesh.rotation.x = THREE.MathUtils.lerp(this.mesh.rotation.x, input.pitch * 0.3, delta * 10);

    // Posicionamento suave da câmera atrás do drone
    const camOffset = new THREE.Vector3(0, 1.4, 3.8).applyQuaternion(this.mesh.quaternion);
    this.camera.position.lerp(this.mesh.position.clone().add(camOffset), delta * 14);
    const lookTarget = this.mesh.position.clone().add(this.getForwardDirection().multiplyScalar(10));
    this.camera.lookAt(lookTarget);
  }

  reset() {
    this.mesh.position.set(0, 3, 0);
    this.mesh.rotation.set(0, 0, 0);
    this.health = 100;
    this.battery = 100;
  }
}
