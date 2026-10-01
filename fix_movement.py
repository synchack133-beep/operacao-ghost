import os

# 1. PLAYER.JS COM TRATAMENTO SEGURO DE JOYSTICK (PREVINE NaN)
player_code = '''import * as THREE from 'three';

export class Player {
  constructor(scene, camera, operatorPosition) {
    this.scene = scene;
    this.camera = camera;
    this.operatorPos = operatorPosition || new THREE.Vector3(0, 0, 70);
    
    this.position = new THREE.Vector3(0, 12, 60);
    this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
    
    this.cameraTiltX = 0;
    this.cameraRollZ = 0;

    this.speed = 22;
    this.rotSpeed = 2.0;
    this.minAltitude = 1.0;
    this.maxAltitude = 70.0;

    this.maxRangeMeters = 200;
    this.currentDistance = 0;

    const bodyGeo = new THREE.BoxGeometry(1.0, 0.15, 1.0);
    const mat = new THREE.MeshBasicMaterial({ color: 0x00ff96, wireframe: true });
    this.mesh = new THREE.Mesh(bodyGeo, mat);
    this.scene.add(this.mesh);
  }

  getForwardDirection() {
    const fwd = new THREE.Vector3(0, -0.3, -1);
    fwd.applyEuler(this.rotation);
    return fwd.normalize();
  }

  // Sanitiza leituras para garantir que nunca sejam NaN ou undefined
  getInputs(input) {
    let lx = 0, ly = 0, rx = 0, ry = 0;

    if (input) {
      if (typeof input.leftX === 'number') lx = input.leftX;
      else if (input.left && typeof input.left.x === 'number') lx = input.left.x;

      if (typeof input.leftY === 'number') ly = input.leftY;
      else if (input.left && typeof input.left.y === 'number') ly = input.left.y;

      if (typeof input.rightX === 'number') rx = input.rightX;
      else if (input.right && typeof input.right.x === 'number') rx = input.right.x;

      if (typeof input.rightY === 'number') ry = input.rightY;
      else if (input.right && typeof input.right.y === 'number') ry = input.right.y;
    }

    return {
      lx: isNaN(lx) ? 0 : lx,
      ly: isNaN(ly) ? 0 : ly,
      rx: isNaN(rx) ? 0 : rx,
      ry: isNaN(ry) ? 0 : ry
    };
  }

  update(delta, rawInput) {
    // Garante valores numéricos válidos
    const input = this.getInputs(rawInput);

    // Proteção se a posição atual virou NaN
    if (isNaN(this.position.x) || isNaN(this.position.y) || isNaN(this.position.z)) {
      this.position.set(0, 12, 60);
    }

    // Rotação YAW (Eixo X Esquerdo)
    if (input.lx !== 0) {
      this.rotation.y -= input.lx * this.rotSpeed * delta;
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, -input.lx * 0.25, delta * 5);
    } else {
      this.cameraRollZ = THREE.MathUtils.lerp(this.cameraRollZ, 0, delta * 5);
    }

    // Altitude / Pitch Vertical (Eixo Y Esquerdo)
    if (input.ly !== 0) {
      this.position.y -= input.ly * this.speed * delta;
    }

    // Movimentação FRENTE / TRÁS / LADOS (Analógico Direito)
    const nextPos = this.position.clone();
    if (input.rx !== 0 || input.ry !== 0) {
      const moveVec = new THREE.Vector3(input.rx, 0, input.ry);
      moveVec.applyAxisAngle(new THREE.Vector3(0, 1, 0), this.rotation.y);
      nextPos.addScaledVector(moveVec, this.speed * delta);

      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, -input.ry * 0.2, delta * 5);
    } else {
      this.cameraTiltX = THREE.MathUtils.lerp(this.cameraTiltX, 0, delta * 5);
    }

    // Checagem de raio do operador
    const distToOperator = new THREE.Vector2(nextPos.x - this.operatorPos.x, nextPos.z - this.operatorPos.z).length();
    if (!isNaN(distToOperator) && distToOperator <= this.maxRangeMeters) {
      this.position.copy(nextPos);
      this.currentDistance = distToOperator;
    }

    if (this.position.y < this.minAltitude) this.position.y = this.minAltitude;
    if (this.position.y > this.maxAltitude) this.position.y = this.maxAltitude;

    this.mesh.position.copy(this.position);
    this.mesh.rotation.copy(this.rotation);

    // Câmera FPV com rotação tratada
    this.camera.position.copy(this.position);
    this.camera.rotation.set(
      this.rotation.x + this.cameraTiltX,
      this.rotation.y,
      this.rotation.z + this.cameraRollZ,
      'YXZ'
    );
  }

  getRangeStatus() {
    const kmSimulated = ((this.currentDistance / this.maxRangeMeters) * 3.0).toFixed(2);
    const pct = (this.currentDistance / this.maxRangeMeters) * 100;
    return { km: kmSimulated, pct: pct, isWarning: pct > 80 };
  }
}
'''

with open('src/entities/Player.js', 'w', encoding='utf-8') as f:
    f.write(player_code)

# 2. MAIN.JS ATUALIZADO COM CÁLCULO SEGURO DE VELOCIDADE
with open('src/main.js', 'r', encoding='utf-8') as f:
    main_content = f.read()

# Substitui o cálculo da velocidade com checagem segura
old_spd_code = "const speed = Math.round((Math.abs(this.joysticks.input.rightY) + Math.abs(this.joysticks.input.rightX)) * 48);"
new_spd_code = """const inputVals = this.player.getInputs(this.joysticks.input);
    const speed = Math.round((Math.abs(inputVals.ry) + Math.abs(inputVals.rx)) * 48);"""

if old_spd_code in main_content:
    main_content = main_content.replace(old_spd_code, new_spd_code)

with open('src/main.js', 'w', encoding='utf-8') as f:
    f.write(main_content)

print("Correção aplicada com sucesso!")
