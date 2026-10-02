import * as THREE from 'three';
import { soundManager } from '../audio/SoundManager.js';

export class Player {
  constructor(scene, camera, operatorPosition) {
    this.scene = scene;
    this.camera = camera;
    this.operatorPos = operatorPosition || new THREE.Vector3(0, 0, 70);

    this.position = new THREE.Vector3(0, 12, 60);
    this.velocity = new THREE.Vector3(0, 0, 0);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');

    this.cameraTiltX = 0;
    this.cameraRollZ = 0;

    this.viewMode = 'FPV';
    this.opMode = 'COMBAT';

    this.orbitYaw = 0;
    this.orbitPitch = 0.3;
    this.orbitDistance = 4.8;

    this.speed = 24;
    this.rotSpeed = 2.2;
    this.minAltitude = 0.8;
    this.maxAltitude = 80.0;

    this.maxRangeMeters = 200;
    this.currentDistance = 0;

    this.batteryVoltage = 25.2;

    this.buildDroneMesh();
  }

  buildDroneMesh() {
    this.droneGroup = new THREE.Group();

    const carbonMat = new THREE.MeshStandardMaterial({ color: 0x151515, roughness: 0.4 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.8 });
    const propMat = new THREE.MeshBasicMaterial({ color: 0x00ff96, transparent: true, opacity: 0.65 });
    const batteryMat = new THREE.MeshStandardMaterial({ color: 0xffaa00, roughness: 0.5 });

    const body = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.1, 0.5), carbonMat);
    this.droneGroup.add(body);

    const battery = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.2, 0.5), batteryMat);
    battery.position.set(0, 0.15, 0);
    this.droneGroup.add(battery);

    const cam = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.16, 0.22), metalMat);
    cam.position.set(0, 0.02, -0.32);
    this.droneGroup.add(cam);

    this.props = [];
    const positions = [
      { x: 0.45, z: -0.45 },
      { x: -0.45, z: -0.45 },
      { x: 0.45, z: 0.45 },
      { x: -0.45, z: 0.45 }
    ];

    positions.forEach((p) => {
      const arm = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.035, 0.62), carbonMat);
      arm.position.set(p.x / 2, 0, p.z / 2);
      arm.rotation.y = Math.atan2(p.x, p.z);
      this.droneGroup.add(arm);

      const motor = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.1, 10), metalMat);
      motor.position.set(p.x, 0.05, p.z);
      this.droneGroup.add(motor);

      const propGroup = new THREE.Group();
      for (let b = 0; b < 3; b++) {
        const blade = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.01, 0.36), propMat);
        blade.rotation.y = (b * Math.PI * 2) / 3;
        blade.position.z = 0.14;
        propGroup.add(blade);
      }
      propGroup.position.set(p.x, 0.11, p.z);
      this.droneGroup.add(propGroup);
      this.props.push(propGroup);
    });

    this.droneGroup.visible = false;
    this.scene.add(this.droneGroup);
  }

  getForwardDirection() {
    const fwd = new THREE.Vector3(0, -0.28, -1);
    fwd.applyEuler(this.rotation);
    return fwd.normalize();
  }

  getInputs(input) {
    let lx = 0, ly = 0, rx = 0, ry = 0;
    if (input) {
      if (typeof input.leftX === 'number') lx = input.leftX;
      if (typeof input.leftY === 'number') ly = input.leftY;
      if (typeof input.rightX === 'number') rx = input.rightX;
      if (typeof input.rightY === 'number') ry = input.rightY;
    }
    return { lx, ly, rx, ry };
  }

  toggleViewMode() {
    this.viewMode = this.viewMode === 'FPV' ? 'THIRD' : 'FPV';
    return this.viewMode;
  }

  toggleOpMode() {
    this.opMode = this.opMode === 'COMBAT' ? 'VISUAL' : 'COMBAT';
    return this.opMode;
  }

  rotateOrbit(deltaYaw, deltaPitch) {
    this.orbitYaw += deltaYaw;
    this.orbitPitch = Math.max(-0.4, Math.min(1.1, this.orbitPitch + deltaPitch));
  }

  update(delta, rawInput) {
    const input = this.getInputs(rawInput);

    if (isNaN(this.position.x) || isNaN(this.position.y) || isNaN(this.position.z)) {
      this.position.set(0, 12, 60);
    }

    if (input.lx !== 0) {
      this.rotation.y -= input.lx * this.rotSpeed * delta;
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, -input.lx * 0.22, delta * 6);
    } else {
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, 0, delta * 6);
    }

    if (input.ly !== 0) {
      this.position.y -= input.ly * this.speed * delta;
    }

    const targetVel = new THREE.Vector3(0, 0, 0);
    if (input.rx !== 0 || input.ry !== 0) {
      targetVel.set(input.rx, 0, input.ry);
      targetVel.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      targetVel.multiplyScalar(this.speed);

      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, -input.ry * 0.22, delta * 6);
    } else {
      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, 0, delta * 6);
    }

    this.velocity.lerp(targetVel, delta * 6);
    const nextPos = this.position.clone().addScaledVector(this.velocity, delta);

    const distToOperator = new THREE.Vector2(nextPos.x - this.operatorPos.x, nextPos.z - this.operatorPos.z).length();
    if (!isNaN(distToOperator) && distToOperator <= this.maxRangeMeters) {
      this.position.copy(nextPos);
      this.currentDistance = distToOperator;
    }

    if (this.position.y < this.minAltitude) this.position.y = this.minAltitude;
    if (this.position.y > this.maxAltitude) this.position.y = this.maxAltitude;

    const throttleUsage = Math.abs(input.ly) + Math.abs(input.rx) + Math.abs(input.ry);
    this.batteryVoltage = Math.max(21.0, this.batteryVoltage - delta * (0.01 + throttleUsage * 0.02));

    soundManager.updateMotor(throttleUsage, this.velocity.length());

    this.props.forEach(p => { p.rotation.y += 35 * delta; });

    this.droneGroup.position.copy(this.position);
    this.droneGroup.rotation.set(
      this.rotation.x + this.cameraTiltX,
      this.rotation.y,
      this.rotation.z + this.cameraRollZ,
      'YXZ'
    );

    if (this.viewMode === 'FPV') {
      this.droneGroup.visible = false;
      this.camera.position.copy(this.position);
      this.camera.rotation.set(
        this.rotation.x + this.cameraTiltX,
        this.rotation.y,
        this.rotation.z + this.cameraRollZ,
        'YXZ'
      );
    } else {
      this.droneGroup.visible = true;
      const totalYaw = this.rotation.y + this.orbitYaw;
      const camOffset = new THREE.Vector3(
        Math.sin(totalYaw) * Math.cos(this.orbitPitch) * this.orbitDistance,
        Math.sin(this.orbitPitch) * this.orbitDistance + 0.6,
        Math.cos(totalYaw) * Math.cos(this.orbitPitch) * this.orbitDistance
      );
      this.camera.position.copy(this.position).add(camOffset);
      this.camera.lookAt(this.position);
    }
  }

  getRangeStatus() {
    const kmSimulated = ((this.currentDistance / this.maxRangeMeters) * 3.0).toFixed(2);
    const pct = (this.currentDistance / this.maxRangeMeters) * 100;
    const rssi = Math.round(-45 - (pct * 0.45));
    return { km: kmSimulated, pct: pct, rssi: rssi };
  }
}