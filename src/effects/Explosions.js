import * as THREE from 'three';

export class ExplosionSystem {
  constructor(scene) {
    this.scene = scene;
    this.particles = [];

    const pGeo = new THREE.SphereGeometry(0.3, 6, 6);
    this.fireMat = new THREE.MeshBasicMaterial({ color: 0xffa500 });
    this.smokeMat = new THREE.MeshBasicMaterial({ color: 0x444444, transparent: true, opacity: 0.7 });
    this.pGeo = pGeo;
  }

  createExplosion(position) {
    const count = 28;
    const group = new THREE.Group();
    group.position.copy(position);

    const activeParts = [];

    for (let i = 0; i < count; i++) {
      const isFire = i < 16;
      const p = new THREE.Mesh(this.pGeo, isFire ? this.fireMat.clone() : this.smokeMat.clone());

      const velocity = new THREE.Vector3(
        (Math.random() - 0.5) * 14,
        Math.random() * 12 + 2,
        (Math.random() - 0.5) * 14
      );

      const scale = isFire ? (0.8 + Math.random() * 1.2) : (1.2 + Math.random() * 1.8);
      p.scale.set(scale, scale, scale);

      group.add(p);
      activeParts.push({ mesh: p, velocity: velocity, isFire: isFire, life: 1.0 });
    }

    const light = new THREE.PointLight(0xffaa00, 5, 30);
    light.position.set(0, 2, 0);
    group.add(light);

    this.scene.add(group);
    this.particles.push({ group: group, light: light, parts: activeParts, time: 0 });
  }

  update(delta) {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const exp = this.particles[i];
      exp.time += delta;

      if (exp.light) {
        exp.light.intensity = Math.max(0, 5 - exp.time * 8);
      }

      let allDead = true;
      exp.parts.forEach(p => {
        p.life -= delta * 1.4;
        if (p.life > 0) {
          allDead = false;
          p.mesh.position.addScaledVector(p.velocity, delta);
          p.mesh.scale.multiplyScalar(1 + delta * 0.8);

          if (p.mesh.material.opacity) {
            p.mesh.material.opacity = p.life;
          }
        } else {
          p.mesh.visible = false;
        }
      });

      if (allDead || exp.time > 1.2) {
        this.scene.remove(exp.group);
        this.particles.splice(i, 1);
      }
    }
  }
}