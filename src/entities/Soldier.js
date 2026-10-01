import * as THREE from 'three';

export class SoldierManager {
  constructor(scene) {
    this.scene = scene;
    this.soldiers = [];
    this.initSoldiers(10);
  }

  initSoldiers(count) {
    const bodyGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.9, 8);
    const headGeo = new THREE.SphereGeometry(0.2, 8, 8);
    
    const matSoldier = new THREE.MeshStandardMaterial({ color: 0xeb3c3c, roughness: 0.5 });
    const matCover = new THREE.MeshStandardMaterial({ color: 0xff8c00 });

    for (let i = 0; i < count; i++) {
      const group = new THREE.Group();
      
      const body = new THREE.Mesh(bodyGeo, matSoldier);
      body.position.y = 0.45;
      group.add(body);

      const head = new THREE.Mesh(headGeo, matSoldier);
      head.position.y = 1.0;
      group.add(head);

      // Posicionamento aleatório pelo mapa
      const x = (Math.random() - 0.5) * 80;
      const z = (Math.random() - 0.5) * 80;
      group.position.set(x, 0, z);

      this.scene.add(group);

      this.soldiers.push({
        mesh: group,
        materials: [matSoldier, matCover],
        health: 100,
        alive: true,
        state: 'PATROL', // PATROL, COVER
        patrolTarget: new THREE.Vector3((Math.random() - 0.5) * 70, 0, (Math.random() - 0.5) * 70),
        timer: 0
      });
    }
  }

  update(delta, dronePos, explosions) {
    this.soldiers.forEach(s => {
      if (!s.alive) return;

      const distDrone = s.mesh.position.distanceTo(dronePos);

      // Reação a explosões próximas
      explosions.forEach(exp => {
        if (s.mesh.position.distanceTo(exp.position) < 12.0) {
          s.state = 'COVER';
          s.timer = 4.0; // Fuga por 4 segundos
        }
      });

      if (s.state === 'COVER') {
        s.timer -= delta;
        // Corre na direção oposta ao drone
        const escapeDir = new THREE.Vector3().subVectors(s.mesh.position, dronePos).normalize();
        escapeDir.y = 0;
        s.mesh.position.addScaledVector(escapeDir, delta * 4.5);

        if (s.timer <= 0) s.state = 'PATROL';
      } else {
        // Patrulha
        const dir = new THREE.Vector3().subVectors(s.patrolTarget, s.mesh.position);
        dir.y = 0;
        if (dir.length() < 1.0) {
          s.patrolTarget.set((Math.random() - 0.5) * 70, 0, (Math.random() - 0.5) * 70);
        } else {
          dir.normalize();
          s.mesh.position.addScaledVector(dir, delta * 1.8);
          s.mesh.lookAt(s.patrolTarget.x, s.mesh.position.y, s.patrolTarget.z);
        }
      }
    });
  }

  takeDamageAt(impactPos, radius, damage) {
    this.soldiers.forEach(s => {
      if (s.alive && s.mesh.position.distanceTo(impactPos) <= radius) {
        s.health -= damage;
        if (s.health <= 0) {
          s.alive = false;
          s.mesh.rotation.x = Math.PI / 2; // Soldado cai ao solo
          s.mesh.position.y = 0.1;
        }
      }
    });
  }

  getAliveCount() {
    return this.soldiers.filter(s => s.alive).length;
  }
}
