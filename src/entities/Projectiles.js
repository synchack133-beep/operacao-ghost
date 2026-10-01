import * as THREE from 'three';

export class ProjectileSystem {
  constructor(scene) {
    this.scene = scene;
    this.bullets = [];
    this.bulletGeo = new THREE.CylinderGeometry(0.08, 0.08, 1.2, 6);
    this.bulletGeo.rotateX(Math.PI / 2);
    this.bulletMat = new THREE.MeshBasicMaterial({ color: 0x00ffff });
  }

  spawnBullet(position, direction) {
    const mesh = new THREE.Mesh(this.bulletGeo, this.bulletMat);
    mesh.position.copy(position);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, -1), direction.clone().normalize());
    this.scene.add(mesh);

    this.bullets.push({
      mesh: mesh,
      velocity: direction.clone().normalize().multiplyScalar(1.3),
      life: 2.0
    });
  }

  update(delta, enemies, explosionSystem, soundManager) {
    for (let i = this.bullets.length - 1; i >= 0; i--) {
      const b = this.bullets[i];
      b.life -= delta;
      b.mesh.position.add(b.velocity);

      let hit = false;
      if (enemies) {
        for (let j = 0; j < enemies.length; j++) {
          const enemy = enemies[j];
          if (enemy.active && b.mesh.position.distanceTo(enemy.group.position) < 2.2) {
            enemy.active = false;
            enemy.group.visible = false;
            hit = true;
            if (explosionSystem) explosionSystem.createExplosion(enemy.group.position, 0xff0055, 45);
            if (soundManager) soundManager.playExplosion();
            break;
          }
        }
      }

      if (hit || b.life <= 0 || b.mesh.position.y < 0) {
        this.scene.remove(b.mesh);
        this.bullets.splice(i, 1);
      }
    }
  }

  reset() {
    this.bullets.forEach(b => this.scene.remove(b.mesh));
    this.bullets = [];
  }
}