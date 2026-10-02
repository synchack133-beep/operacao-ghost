import * as THREE from 'three';

export class SoldierManager {
  constructor(scene) {
    this.scene = scene;
    this.targets = [];
    this.kills = 0;

    this.spawnInitialTargets();
  }

  spawnInitialTargets() {
    const soldierWaypoints = [
      [{ x: -40, z: -50 }, { x: -20, z: -50 }, { x: -20, z: -70 }, { x: -40, z: -70 }],
      [{ x: 20, z: -30 }, { x: 40, z: -30 }, { x: 30, z: -10 }],
      [{ x: -60, z: -30 }, { x: -50, z: -10 }, { x: -70, z: -10 }],
      [{ x: 0, z: -100 }, { x: -30, z: -110 }, { x: 10, z: -120 }]
    ];

    soldierWaypoints.forEach(wp => {
      this.spawnSoldier(wp);
    });

    this.spawnTruck(new THREE.Vector3(-25, 0, -40), new THREE.Vector3(15, 0, -40));
  }

  spawnSoldier(waypoints) {
    const group = new THREE.Group();

    const uniformMat = new THREE.MeshStandardMaterial({ color: 0x5a4a3a, roughness: 0.8 });
    const skinMat = new THREE.MeshStandardMaterial({ color: 0xc89d7c });
    const vestMat = new THREE.MeshStandardMaterial({ color: 0x2d382d });

    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.3, 1.0, 8), uniformMat);
    body.position.y = 0.5;
    group.add(body);

    const vest = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.45, 0.35), vestMat);
    vest.position.y = 0.6;
    group.add(vest);

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 8, 8), skinMat);
    head.position.y = 1.15;
    group.add(head);

    const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 8), vestMat);
    helmet.position.y = 1.22;
    group.add(helmet);

    group.position.set(waypoints[0].x, 0, waypoints[0].z);
    this.scene.add(group);

    this.targets.push({
      mesh: group,
      type: 'SOLDIER',
      waypoints: waypoints,
      currentWpIndex: 0,
      speed: 1.8 + Math.random() * 0.8,
      alive: true,
      radius: 1.2
    });
  }

  spawnTruck(startPos, endPos) {
    const group = new THREE.Group();

    const truckMat = new THREE.MeshStandardMaterial({ color: 0x384534, roughness: 0.7 });
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.9 });

    const body = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.6, 5.0), truckMat);
    body.position.y = 1.2;
    group.add(body);

    const cabin = new THREE.Mesh(new THREE.BoxGeometry(2.3, 1.2, 1.8), truckMat);
    cabin.position.set(0, 2.0, -1.2);
    group.add(cabin);

    for (let x of [-1.2, 1.2]) {
      for (let z of [-1.8, 0, 1.8]) {
        const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.3, 12), wheelMat);
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(x, 0.45, z);
        group.add(wheel);
      }
    }

    group.position.copy(startPos);
    this.scene.add(group);

    this.targets.push({
      mesh: group,
      type: 'TRUCK',
      startPos: startPos,
      endPos: endPos,
      forward: true,
      speed: 3.5,
      alive: true,
      radius: 3.0
    });
  }

  update(delta) {
    this.targets.forEach(t => {
      if (!t.alive) return;

      if (t.type === 'SOLDIER') {
        const targetWp = t.waypoints[t.currentWpIndex];
        const currentPos = t.mesh.position;
        const dir = new THREE.Vector3(targetWp.x - currentPos.x, 0, targetWp.z - currentPos.z);
        const dist = dir.length();

        if (dist < 0.5) {
          t.currentWpIndex = (t.currentWpIndex + 1) % t.waypoints.length;
        } else {
          dir.normalize();
          currentPos.addScaledVector(dir, t.speed * delta);
          t.mesh.rotation.y = Math.atan2(dir.x, dir.z);
        }
      } else if (t.type === 'TRUCK') {
        const dest = t.forward ? t.endPos : t.startPos;
        const currentPos = t.mesh.position;
        const dir = new THREE.Vector3(dest.x - currentPos.x, 0, dest.z - currentPos.z);
        const dist = dir.length();

        if (dist < 0.8) {
          t.forward = !t.forward;
        } else {
          dir.normalize();
          currentPos.addScaledVector(dir, t.speed * delta);
          t.mesh.rotation.y = Math.atan2(dir.x, dir.z);
        }
      }
    });
  }

  checkExplosionHits(impactPos, blastRadius = 6.0) {
    let hitsCount = 0;
    this.targets.forEach(t => {
      if (!t.alive) return;

      const dist = impactPos.distanceTo(t.mesh.position);
      if (dist <= blastRadius + t.radius) {
        t.alive = false;
        hitsCount++;
        this.kills++;

        t.mesh.rotation.x = Math.PI / 2;
        t.mesh.position.y = 0.2;

        setTimeout(() => {
          if (t.type === 'SOLDIER') {
            t.mesh.rotation.x = 0;
            t.mesh.position.set(t.waypoints[0].x, 0, t.waypoints[0].z);
            t.alive = true;
          } else {
            t.mesh.rotation.x = 0;
            t.mesh.position.copy(t.startPos);
            t.alive = true;
          }
        }, 8000);
      }
    });
    return hitsCount;
  }
}