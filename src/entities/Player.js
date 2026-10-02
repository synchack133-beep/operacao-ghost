import * as THREE from 'three';

export class Player {
  constructor(scene, camera, operatorPosition) {
    this.scene = scene;
    this.camera = camera;
    this.operatorPos = operatorPosition || new THREE.Vector3(0, 0, 70);

    this.position = new THREE.Vector3(0, 12, 60);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');

    this.cameraTiltX = 0;
    this.cameraRollZ = 0;

    // Modos de Voo e Câmera
    this.viewMode = 'FPV'; // 'FPV' ou 'THIRD'
    this.opMode = 'COMBAT'; // 'COMBAT' ou 'VISUAL'

    // Ângulos da Câmera em 3ª Pessoa (Órbita 360)
    this.orbitYaw = 0;
    this.orbitPitch = 0.3;
    this.orbitDistance = 4.5;

    this.speed = 22;
    this.rotSpeed = 2.0;
    this.minAltitude = 1.0;
    this.maxAltitude = 70.0;

    this.maxRangeMeters = 200;
    this.currentDistance = 0;

    this.buildDroneMesh();
  }

  buildDroneMesh() {
    this.droneGroup = new THREE.Group();

    const carbonMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.5 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x777777, metalness: 0.8, roughness: 0.2 });
    const propMat = new THREE.MeshBasicMaterial({ color: 0x00ff96, transparent: true, opacity: 0.6 });
    const batteryMat = new THREE.MeshStandardMaterial({ color: 0xffaa00, roughness: 0.6 });
    const lensMat = new THREE.MeshBasicMaterial({ color: 0x000000 });

    // Chassi Central X-Frame
    const centerPlate = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.5), carbonMat);
    this.droneGroup.add(centerPlate);

    // Bateria LiPo no Topo
    const battery = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.2, 0.55), batteryMat);
    battery.position.set(0, 0.14, 0);
    this.droneGroup.add(battery);

    // Câmera FPV na Frente
    const camMount = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.18, 0.2), carbonMat);
    camMount.position.set(0, 0.05, -0.3);
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.1, 12), lensMat);
    lens.rotation.x = Math.PI / 2;
    lens.position.set(0, 0.05, -0.38);
    this.droneGroup.add(camMount);
    this.droneGroup.add(lens);

    // 4 Braços e Motores com Hélices
    this.props = [];
    const armPositions = [
      { x: 0.45, z: -0.45, cw: true },
      { x: -0.45, z: -0.45, cw: false },
      { x: 0.45, z: 0.45, cw: false },
      { x: -0.45, z: 0.45, cw: true }
    ];

    armPositions.forEach(p => {
      // Braço de Carbono
      const armGeo = new THREE.BoxGeometry(0.08, 0.04, 0.65);
      const arm = new THREE.Mesh(armGeo, carbonMat);
      arm.position.set(p.x / 2, 0, p.z / 2);
      arm.rotation.y = Math.atan2(p.x, p.z);
      this.droneGroup.add(arm);

      // Motor Metálico
      const motor = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.12, 12), metalMat);
      motor.position.set(p.x, 0.06, p.z);
      this.droneGroup.add(motor);

      // Hélice de 3 Pás
      const propGroup = new THREE.Group();
      for (let b = 0; b < 3; b++) {
        const blade = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.01, 0.38), propMat);
        blade.rotation.y = (b * Math.PI * 2) / 3;
        blade.position.z = 0.15;
        propGroup.add(blade);
      }
      propGroup.position.set(p.x, 0.13, p.z);
      this.droneGroup.add(propGroup);
      this.props.push({ mesh: propGroup, cw: p.cw });
    });

    // Antena VTX na Traseira
    const antennaStem = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.3, 8), carbonMat);
    antennaStem.position.set(0, 0.18, 0.35);
    antennaStem.rotation.x = -0.3;
    const antennaTop = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), metalMat);
    antennaTop.position.set(0, 0.3, 0.42);
    this.droneGroup.add(antennaStem);
    this.droneGroup.add(antennaTop);

    this.scene.add(this.droneGroup);
  }

  getForwardDirection() {
    const fwd = new THREE.Vector3(0, -0.3, -1);
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
    return {
      lx: isNaN(lx) ? 0 : lx,
      ly: isNaN(ly) ? 0 : ly,
      rx: isNaN(rx) ? 0 : rx,
      ry: isNaN(ry) ? 0 : ry
    };
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
    this.orbitPitch = Math.max(-0.5, Math.min(1.2, this.orbitPitch + deltaPitch));
  }

  update(delta, rawInput) {
    const input = this.getInputs(rawInput);

    if (isNaN(this.position.x) || isNaN(this.position.y) || isNaN(this.position.z)) {
      this.position.set(0, 12, 60);
    }

    // Rotação YAW
    if (input.lx !== 0) {
      this.rotation.y -= input.lx * this.rotSpeed * delta;
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, -input.lx * 0.25, delta * 5);
    } else {
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, 0, delta * 5);
    }

    // Altitude / Pitch Vertical
    if (input.ly !== 0) {
      this.position.y -= input.ly * this.speed * delta;
    }

    // Movimentação Horizontal
    const nextPos = this.position.clone();
    if (input.rx !== 0 || input.ry !== 0) {
      const moveVec = new THREE.Vector3(input.rx, 0, input.ry);
      moveVec.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      nextPos.addScaledVector(moveVec, this.speed * delta);

      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, -input.ry * 0.2, delta * 5);
    } else {
      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, 0, delta * 5);
    }

    const distToOperator = new THREE.Vector2(nextPos.x - this.operatorPos.x, nextPos.z - this.operatorPos.z).length();
    if (!isNaN(distToOperator) && distToOperator <= this.maxRangeMeters) {
      this.position.copy(nextPos);
      this.currentDistance = distToOperator;
    }

    if (this.position.y < this.minAltitude) this.position.y = this.minAltitude;
    if (this.position.y > this.maxAltitude) this.position.y = this.maxAltitude;

    // Animação de rotação contínua das hélices
    this.props.forEach(p => {
      p.mesh.rotation.y += (p.cw ? 35 : -35) * delta;
    });

    this.droneGroup.position.copy(this.position);
    this.droneGroup.rotation.set(
      this.rotation.x + this.cameraTiltX,
      this.rotation.y,
      this.rotation.z + this.cameraRollZ,
      'YXZ'
    );

    // Ajuste da Câmera (1ªP vs 3ªP Órbita 360)
    if (this.viewMode === 'FPV') {
      this.droneGroup.visible = false; // Esconde o modelo próprio em FPV
      this.camera.position.copy(this.position);
      this.camera.rotation.set(
        this.rotation.x + this.cameraTiltX,
        this.rotation.y,
        this.rotation.z + this.cameraRollZ,
        'YXZ'
      );
    } else {
      this.droneGroup.visible = true; // Mostra o drone em 3ª pessoa
      const totalYaw = this.rotation.y + this.orbitYaw;
      const camOffset = new THREE.Vector3(
        Math.sin(totalYaw) * Math.cos(this.orbitPitch) * this.orbitDistance,
        Math.sin(this.orbitPitch) * this.orbitDistance + 0.5,
        Math.cos(totalYaw) * Math.cos(this.orbitPitch) * this.orbitDistance
      );
      this.camera.position.copy(this.position).add(camOffset);
      this.camera.lookAt(this.position);
    }
  }

  getRangeStatus() {
    const kmSimulated = ((this.currentDistance / this.maxRangeMeters) * 3.0).toFixed(2);
    const pct = (this.currentDistance / this.maxRangeMeters) * 100;
    return { km: kmSimulated, pct: pct, isWarning: pct > 80 };
  }
}
