import os

# 1. Sistema de Explosões e Partículas (src/effects/Explosions.js)
explosion_code = '''import * as THREE from 'three';

export class ExplosionSystem {
  constructor(scene) {
    this.scene = scene;
    this.particles = [];
  }

  createExplosion(position, color = 0xff5500, count = 35) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const velocities = [];

    for (let i = 0; i < count; i++) {
      positions[i * 3] = position.x;
      positions[i * 3 + 1] = position.y;
      positions[i * 3 + 2] = position.z;

      velocities.push(new THREE.Vector3(
        (Math.random() - 0.5) * 0.9,
        (Math.random() - 0.5) * 0.9,
        (Math.random() - 0.5) * 0.9
      ));
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({
      color: color,
      size: 0.5,
      transparent: true,
      opacity: 1
    });

    const pSystem = new THREE.Points(geometry, material);
    this.scene.add(pSystem);

    this.particles.push({
      system: pSystem,
      velocities: velocities,
      life: 1.0
    });
  }

  update(delta) {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life -= delta * 2.5;

      const posAttr = p.system.geometry.attributes.position;
      const posArray = posAttr.array;

      for (let j = 0; j < p.velocities.length; j++) {
        posArray[j * 3] += p.velocities[j].x;
        posArray[j * 3 + 1] += p.velocities[j].y;
        posArray[j * 3 + 2] += p.velocities[j].z;
      }

      posAttr.needsUpdate = true;
      p.system.material.opacity = Math.max(0, p.life);

      if (p.life <= 0) {
        this.scene.remove(p.system);
        p.system.geometry.dispose();
        p.system.material.dispose();
        this.particles.splice(i, 1);
      }
    }
  }
}
'''

os.makedirs('src/effects', exist_ok=True)
with open('src/effects/Explosions.js', 'w', encoding='utf-8') as f:
    f.write(explosion_code)

# 2. Inimigos em Modo Perseguição (src/entities/EnemyManager.js)
enemy_arcade_code = '''import * as THREE from 'three';
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
'''

with open('src/entities/EnemyManager.js', 'w', encoding='utf-8') as f:
    f.write(enemy_arcade_code)

print("Modo Arcade configurado e enviado!")
