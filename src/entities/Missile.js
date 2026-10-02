import * as THREE from 'three';
import { soundManager } from '../audio/SoundManager.js';

export class MissileSystem {
  constructor(scene) {
    this.scene = scene;
    this.activeMissiles = [];

    const missileMat = new THREE.MeshStandardMaterial({ color: 0xdddddd, metalness: 0.6 });
    const finMat = new THREE.MeshStandardMaterial({ color: 0xff3c3c });

    this.missileGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.8, 8);
    this.missileGeo.rotateX(Math.PI / 2);
    this.missileMat = missileMat;
    this.finMat = finMat;
  }

  spawnMissile(startPos, targetPos, onHitCallback) {
    const group = new THREE.Group();

    const body = new THREE.Mesh(this.missileGeo, this.missileMat);
    group.add(body);

    const nose = new THREE.Mesh(new THREE.ConeGeometry(0.08, 0.25, 8), this.finMat);
    nose.rotation.x = -Math.PI / 2;
    nose.position.z = -0.5;
    group.add(nose);

    group.position.copy(startPos);
    group.lookAt(targetPos);

    this.scene.add(group);
    soundManager.playLaunch();

    this.activeMissiles.push({
      mesh: group,
      startPos: startPos.clone(),
      targetPos: targetPos.clone(),
      progress: 0,
      speed: 1.8,
      onHit: onHitCallback
    });
  }

  update(delta, explosionSystem, soldierManager) {
    for (let i = this.activeMissiles.length - 1; i >= 0; i--) {
      const m = this.activeMissiles[i];
      m.progress += delta * m.speed;

      if (m.progress >= 1.0) {
        const impactPos = m.targetPos.clone();
        explosionSystem.createExplosion(impactPos);
        soundManager.playExplosion();

        if (soldierManager) {
          soldierManager.checkExplosionHits(impactPos, 6.0);
        }

        if (m.onHit) m.onHit(impactPos);

        this.scene.remove(m.mesh);
        this.activeMissiles.splice(i, 1);
      } else {
        m.mesh.position.lerpVectors(m.startPos, m.targetPos, m.progress);
      }
    }
  }
}