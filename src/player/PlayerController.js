import * as THREE from 'three';
import { GAME_CONFIG } from '../config/gameConfig.js';
import { createDroneMesh } from './DroneModel.js';
import { eventBus } from '../core/EventBus.js';
import { gameStateMachine } from '../core/GameState.js';

export class PlayerController {
  constructor(scene) {
    this.scene = scene;
    this.mesh = createDroneMesh();
    this.mesh.position.set(
      GAME_CONFIG.PLAYER.startPosition.x,
      GAME_CONFIG.PLAYER.startPosition.y,
      GAME_CONFIG.PLAYER.startPosition.z
    );
    this.scene.add(this.mesh);

    this.velocity = new THREE.Vector3();
    this.energy = GAME_CONFIG.PLAYER.maxEnergy;
    this.health = GAME_CONFIG.PLAYER.maxHealth;
    this.yaw = Math.PI;

    eventBus.on('resetPlayer', () => this.reset());
  }

  reset() {
    this.mesh.position.set(
      GAME_CONFIG.PLAYER.startPosition.x,
      GAME_CONFIG.PLAYER.startPosition.y,
      GAME_CONFIG.PLAYER.startPosition.z
    );
    this.velocity.set(0, 0, 0);
    this.energy = GAME_CONFIG.PLAYER.maxEnergy;
    this.health = GAME_CONFIG.PLAYER.maxHealth;
    this.yaw = Math.PI;
    eventBus.emit('energyUpdated', this.energy);
    eventBus.emit('healthUpdated', this.health);
  }

  update(deltaTime, inputState, cameraRotation) {
    if (!gameStateMachine.isPlaying()) return;

    this.energy -= GAME_CONFIG.PLAYER.energyDepletionRate * deltaTime;
    if (this.energy <= 0) {
      this.energy = 0;
      eventBus.emit('playerDied', 'Bateria Esgotada!');
    }
    eventBus.emit('energyUpdated', this.energy);

    if (this.mesh.userData.rotors) {
      this.mesh.userData.rotors.forEach(r => r.rotation.y += 25 * deltaTime);
    }

    this.yaw = cameraRotation.yaw;

    const moveDir = new THREE.Vector3();
    if (inputState.forward) moveDir.z -= 1;
    if (inputState.backward) moveDir.z += 1;
    if (inputState.left) moveDir.x -= 1;
    if (inputState.right) moveDir.x += 1;
    moveDir.normalize();

    moveDir.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.yaw);

    const targetVelX = moveDir.x * GAME_CONFIG.PLAYER.speed;
    const targetVelZ = moveDir.z * GAME_CONFIG.PLAYER.speed;

    this.velocity.x += (targetVelX - this.velocity.x) * 0.1;
    this.velocity.z += (targetVelZ - this.velocity.z) * 0.1;

    if (inputState.up) this.velocity.y += GAME_CONFIG.PLAYER.ascendSpeed * deltaTime * 5;
    else if (inputState.down) this.velocity.y -= GAME_CONFIG.PLAYER.ascendSpeed * deltaTime * 5;
    else this.velocity.y *= 0.9;

    this.mesh.position.x += this.velocity.x * deltaTime;
    this.mesh.position.y += this.velocity.y * deltaTime;
    this.mesh.position.z += this.velocity.z * deltaTime;

    this.mesh.position.y = THREE.MathUtils.clamp(
      this.mesh.position.y,
      GAME_CONFIG.PLAYER.minAltitude,
      GAME_CONFIG.PLAYER.maxAltitude
    );

    const limit = GAME_CONFIG.WORLD.mapSize / 2 - 2;
    this.mesh.position.x = THREE.MathUtils.clamp(this.mesh.position.x, -limit, limit);
    this.mesh.position.z = THREE.MathUtils.clamp(this.mesh.position.z, -limit, limit);

    this.mesh.rotation.y = this.yaw;
    const tiltZ = -this.velocity.x * 0.02;
    const tiltX = this.velocity.z * 0.02;
    this.mesh.rotation.z = THREE.MathUtils.lerp(this.mesh.rotation.z, tiltZ, 0.1);
    this.mesh.rotation.x = THREE.MathUtils.lerp(this.mesh.rotation.x, tiltX, 0.1);
  }
}
