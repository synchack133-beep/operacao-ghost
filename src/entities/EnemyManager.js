import * as THREE from 'three';
import { eventBus } from '../core/EventBus.js';

export class EnemyManager {
  constructor(scene, player, explosionSystem) {
    this.scene = scene;
    this.player = player;
    this.explosionSystem = explosionSystem;
    this.enemies = [];
    this.spawnEnemies();
  }

  spawnEnemies() {
    const spawnPoints = [
      { x: 15, z: 15 },
      { x: -20, z: 20 },
      { x: 25, z: -20 },
      { x: -15, z: -25 },
      { x: 0, z: 30 }
    ];

    spawnPoints.forEach((pt, idx) => {
      const group = new THREE.Group();

      // Geometria estilo caça de combate
      const bodyGeo = new THREE.ConeGeometry(0.8, 2.5, 5);
      bodyGeo.rotateX(Math.PI / 2);
      const mat = new THREE.MeshBasicMaterial({ color: 0xff0044, wireframe: true });
      const mesh = new THREE.Mesh(bodyGeo, mat);
      group.add(mesh);

      const wingGeo = new THREE.BoxGeometry(2.5, 0.1, 0.8);
      const wingMesh = new THREE.Mesh(wingGeo, mat);
      group.add(wingMesh);

      group.position.set(pt.x, 3, pt.z);
      this.scene.add(group);

      this.enemies.push({
        group: group,
        speed: 0.07,
        active: true,
        detectionRange: 18,
        attackRange: 3.2
      });
    });
  }

  update(delta) {
    if (!this.player) return;
    const playerPos = this.player.mesh ? this.player.mesh.position : this.player.position;
    if (!playerPos) return;

    this.enemies.forEach((enemy) => {
      if (!enemy.active) return;

      const dist = enemy.group.position.distanceTo(playerPos);

      // Inteligência de perseguição arcade
      if (dist < enemy.detectionRange) {
        const dir = new THREE.Vector3().subVectors(playerPos, enemy.group.position).normalize();
        enemy.group.position.addScaledVector(dir, enemy.speed);
        enemy.group.lookAt(playerPos);

        // Colisão com o drone do jogador
        if (dist < enemy.attackRange) {
          if (this.explosionSystem) {
            this.explosionSystem.createExplosion(enemy.group.position, 0xff0055, 40);
          }
          eventBus.emit('damagePlayer', 0.8);
        }
      } else {
        enemy.group.position.y = 3 + Math.sin(Date.now() * 0.003) * 0.5;
        enemy.group.rotation.y += 0.02;
      }
    });
  }

  reset() {
    this.enemies.forEach((enemy) => {
      enemy.active = true;
    });
  }
}
