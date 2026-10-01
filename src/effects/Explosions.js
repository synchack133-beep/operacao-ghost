import * as THREE from 'three';

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
