import * as THREE from 'three';
import { GAME_CONFIG } from '../config/gameConfig.js';

export class CameraController {
  constructor(camera) {
    this.camera = camera;
    this.yaw = Math.PI;
    this.pitch = -0.2;

    this.targetPosition = new THREE.Vector3();
    this.currentPosition = new THREE.Vector3();
  }

  handleLookDelta(dx, dy) {
    this.yaw -= dx;
    this.pitch -= dy;
    this.pitch = THREE.MathUtils.clamp(this.pitch, -Math.PI / 3, Math.PI / 4);
  }

  update(targetMesh) {
    if (!targetMesh) return;

    const dist = GAME_CONFIG.CAMERA.distance;
    const height = GAME_CONFIG.CAMERA.height;

    const offsetX = Math.sin(this.yaw) * Math.cos(this.pitch) * dist;
    const offsetZ = Math.cos(this.yaw) * Math.cos(this.pitch) * dist;
    const offsetY = Math.sin(-this.pitch) * dist + height;

    this.targetPosition.set(
      targetMesh.position.x + offsetX,
      targetMesh.position.y + offsetY,
      targetMesh.position.z + offsetZ
    );

    this.currentPosition.lerp(this.targetPosition, GAME_CONFIG.CAMERA.damping);
    this.camera.position.copy(this.currentPosition);

    const lookTarget = targetMesh.position.clone().add(new THREE.Vector3(0, 0.3, 0));
    this.camera.lookAt(lookTarget);
  }
}
