import * as THREE from 'three';
import { eventBus } from '../core/EventBus.js';

export class EnemyManager {
  constructor(scene, player) {
    this.scene = scene;
    this.player = player;
    this.enemies = [];
    this.spawnEnemies();
  }

  spawnEnemies() {
    // Posições de patrulha dos drones hostis
    const patrolZones = [
      { x: 10, z: 10, radius: 7 },
      { x: -15, z: 15, radius: 9 },
      { x: 20, z: -15, radius: 8 },
      { x: -10, z: -20, radius: 6 }
    ];

    patrolZones.forEach((zone, idx) => {
      const group = new THREE.Group();

      # Geometria do drone inimigo (octaedro vermelho)
      const geo = new THREE.OctahedronGeometry(1.2, 0);
      const mat = new THREE.MeshBasicMaterial({ color: 0xff0055, wireframe: true });
      const mesh = new THREE.Mesh(geo, mat);
      group.add(mesh);

      # Anel de radar / deteção
      const ringGeo = new THREE.RingGeometry(0.8, 3.0, 16);
      const ringMat = new THREE.MeshBasicMaterial({ 
        color: 0xff0055, 
        wireframe: true, 
        side: THREE.DoubleSide, 
        transparent: true, 
        opacity: 0.4 
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2;
      group.add(ring);

      group.position.set(zone.x, 2, zone.z);
      this.scene.add(group);

      this.enemies.push({
        group: group,
        startX: zone.x,
        startZ: zone.z,
        angle: idx * 1.5,
        radius: zone.radius,
        speed: 0.018,
        detectionRadius: 4.5
      });
    });
  }

  update(delta) {
    if (!this.player) return;

    const playerPos = this.player.mesh ? this.player.mesh.position : this.player.position;
    if (!playerPos) return;

    this.enemies.forEach(enemy => {
      // Movimento de patrulha circular
      enemy.angle += enemy.speed;
      enemy.group.position.x = enemy.startX + Math.cos(enemy.angle) * enemy.radius;
      enemy.group.position.z = enemy.startZ + Math.sin(enemy.angle) * enemy.radius;
      enemy.group.rotation.y += 0.03;

      // Verificação de distância relativamente ao jogador
      const dist = enemy.group.position.distanceTo(playerPos);
      if (dist < enemy.detectionRadius) {
        // Reduz a integridade do drone quando detetado
        eventBus.emit('damagePlayer', 0.3);
      }
    });
  }

  reset() {
    this.enemies.forEach((enemy, idx) => {
      enemy.angle = idx * 1.5;
    });
  }
}
