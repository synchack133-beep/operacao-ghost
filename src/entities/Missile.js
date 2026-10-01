import * as THREE from 'three';

export class MissileSystem {
  constructor(scene) {
    this.scene = scene;
    this.missiles = [];
    this.geo = new THREE.CylinderGeometry(0.08, 0.08, 0.6, 6);
    this.mat = new THREE.MeshBasicMaterial({ color: 0xffcc00 });
  }

  spawnMissile(startPos, targetPos) {
    const mesh = new THREE.Mesh(this.geo, this.mat);
    mesh.position.copy(startPos);
    this.scene.add(mesh);

    const dir = new THREE.Vector3().subVectors(targetPos, startPos).normalize();

    this.missiles.push({
      mesh: mesh,
      target: targetPos.clone(),
      dir: dir,
      speed: 25.0,
      active: true
    });
  }

  update(delta, soldierManager, explosionSystem, soundManager) {
    const impactEvents = [];

    this.missiles.forEach((m, index) => {
      if (!m.active) return;

      m.mesh.position.addScaledVector(m.dir, m.speed * delta);

      // Checa se atingiu o alvo ou o solo
      if (m.mesh.position.distanceTo(m.target) < 1.2 || m.mesh.position.y <= 0.2) {
        m.active = false;
        this.scene.remove(m.mesh);

        const impactPos = m.mesh.position.clone();
        impactPos.y = 0;

        // Dano em área nos soldados
        soldierManager.takeDamageAt(impactPos, 8.0, 100);
        explosionSystem.createExplosion(impactPos);
        if (soundManager) soundManager.playLaser();

        impactEvents.push({ position: impactPos });
        this.missiles.splice(index, 1);
      }
    });

    return impactEvents;
  }
}
