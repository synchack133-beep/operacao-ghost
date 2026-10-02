import os
import subprocess

# Criar estrutura de diretórios
os.makedirs('src/controls', exist_ok=True)
os.makedirs('src/audio', exist_ok=True)
os.makedirs('src/entities', exist_ok=True)
os.makedirs('src/effects', exist_ok=True)
os.makedirs('src/world', exist_ok=True)

# 1. JOYSTICK.JS - ISOLAMENTO MULTI-TOUCH COM DEADZONE
joystick_code = '''export class JoystickController {
  constructor(options = {}) {
    this.input = { leftX: 0, leftY: 0, rightX: 0, rightY: 0 };
    this.deadzone = options.deadzone || 0.08;
    this.setup(options);
  }

  setup(options) {
    const leftZone = document.getElementById(options.leftZoneId || 'zone-left');
    const rightZone = document.getElementById(options.rightZoneId || 'zone-right');
    const leftStick = document.getElementById(options.leftStickId || 'stick-left');
    const rightStick = document.getElementById(options.rightStickId || 'stick-right');

    this.bindJoystick(leftZone, leftStick, true);
    this.bindJoystick(rightZone, rightStick, false);
  }

  bindJoystick(zone, stick, isLeft) {
    if (!zone || !stick) return;

    let activePointerId = null;

    const handleMove = (e) => {
      if (e.pointerId !== activePointerId) return;

      const rect = zone.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const maxRadius = rect.width / 2;

      let dx = e.clientX - centerX;
      let dy = e.clientY - centerY;
      const dist = Math.hypot(dx, dy);

      if (dist > maxRadius) {
        dx = (dx / dist) * maxRadius;
        dy = (dy / dist) * maxRadius;
      }

      stick.style.transform = `translate(${dx}px, ${dy}px)`;

      let normX = dx / maxRadius;
      let normY = dy / maxRadius;

      if (Math.abs(normX) < this.deadzone) normX = 0;
      if (Math.abs(normY) < this.deadzone) normY = 0;

      if (isLeft) {
        this.input.leftX = normX;
        this.input.leftY = normY;
      } else {
        this.input.rightX = normX;
        this.input.rightY = normY;
      }
    };

    const handleUp = (e) => {
      if (e.pointerId !== activePointerId) return;

      activePointerId = null;
      stick.style.transform = 'translate(0px, 0px)';

      if (isLeft) {
        this.input.leftX = 0;
        this.input.leftY = 0;
      } else {
        this.input.rightX = 0;
        this.input.rightY = 0;
      }

      try { zone.releasePointerCapture(e.pointerId); } catch(err) {}
    };

    zone.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      if (activePointerId !== null) return;

      activePointerId = e.pointerId;
      try { zone.setPointerCapture(e.pointerId); } catch(err) {}

      handleMove(e);
    });

    zone.addEventListener('pointermove', (e) => {
      e.preventDefault();
      handleMove(e);
    });

    zone.addEventListener('pointerup', (e) => {
      e.preventDefault();
      handleUp(e);
    });

    zone.addEventListener('pointercancel', (e) => {
      e.preventDefault();
      handleUp(e);
    });
  }
}'''

with open('src/controls/Joystick.js', 'w', encoding='utf-8') as f:
    f.write(joystick_code)

# 2. SOUNDMANAGER.JS - SINTETIZADOR PROCEDURAL WEB AUDIO
sound_code = '''export class SoundManager {
  constructor() {
    this.ctx = null;
    this.isMuted = false;
    this.motorOsc = null;
    this.motorGain = null;
    this.isInitialized = false;
  }

  init() {
    if (this.isInitialized) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      this.ctx = new AudioCtx();

      this.motorOsc = this.ctx.createOscillator();
      this.motorGain = this.ctx.createGain();
      const filter = this.ctx.createBiquadFilter();

      this.motorOsc.type = 'sawtooth';
      this.motorOsc.frequency.setValueAtTime(60, this.ctx.currentTime);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(350, this.ctx.currentTime);

      this.motorGain.gain.setValueAtTime(0.08, this.ctx.currentTime);

      this.motorOsc.connect(filter);
      filter.connect(this.motorGain);
      this.motorGain.connect(this.ctx.destination);

      this.motorOsc.start();
      this.isInitialized = true;
    } catch (e) {
      console.warn('AudioContext init error', e);
    }
  }

  resume() {
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  updateMotor(throttle, speed) {
    if (!this.isInitialized || this.isMuted || !this.ctx) return;
    const baseFreq = 65 + Math.abs(throttle) * 70 + (speed / 60) * 80;
    this.motorOsc.frequency.setTargetAtTime(baseFreq, this.ctx.currentTime, 0.05);
  }

  playExplosion() {
    if (!this.isInitialized || this.isMuted || !this.ctx) return;
    const now = this.ctx.currentTime;
    
    const bufferSize = this.ctx.sampleRate * 0.8;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2 - 1;
    }

    const whiteNoise = this.ctx.createBufferSource();
    whiteNoise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(800, now);
    filter.frequency.exponentialRampToValueAtTime(40, now + 0.7);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.4, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);

    whiteNoise.connect(filter);
    filter.connect(gain);
    gain.connect(this.ctx.destination);

    whiteNoise.start(now);
  }

  playLaunch() {
    if (!this.isInitialized || this.isMuted || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(300, now);
    osc.frequency.exponentialRampToValueAtTime(1200, now + 0.25);

    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 0.3);
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    if (this.motorGain) {
      this.motorGain.gain.setValueAtTime(this.isMuted ? 0 : 0.08, this.ctx ? this.ctx.currentTime : 0);
    }
    return this.isMuted;
  }
}

export const soundManager = new SoundManager();'''

with open('src/audio/SoundManager.js', 'w', encoding='utf-8') as f:
    f.write(sound_code)

# 3. OPERATOR.JS
operator_code = '''import * as THREE from 'three';

export class Operator {
  constructor(scene, position) {
    this.scene = scene;
    this.position = position || new THREE.Vector3(0, 0, 70);
    this.buildOperator();
  }

  buildOperator() {
    this.group = new THREE.Group();
    this.group.position.copy(this.position);

    const tentMat = new THREE.MeshStandardMaterial({ color: 0x3d4f3d, roughness: 0.8 });
    const tent = new THREE.Mesh(new THREE.ConeGeometry(3, 2.5, 4), tentMat);
    tent.rotation.y = Math.PI / 4;
    tent.position.set(0, 1.25, 0);
    this.group.add(tent);

    const camoMat = new THREE.MeshStandardMaterial({ color: 0x2b3d2b, roughness: 0.7 });
    const skinMat = new THREE.MeshStandardMaterial({ color: 0xd2a679 });
    const gearMat = new THREE.MeshStandardMaterial({ color: 0x111111 });

    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.35, 1.1, 8), camoMat);
    body.position.set(2, 0.55, 1);
    this.group.add(body);

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 10), skinMat);
    head.position.set(2, 1.2, 1);
    this.group.add(head);

    const controller = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.15, 0.3), gearMat);
    controller.position.set(2, 0.7, 0.7);
    this.group.add(controller);

    const antenna = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.2, 6), gearMat);
    antenna.position.set(2.1, 1.3, 0.6);
    this.group.add(antenna);

    this.scene.add(this.group);
  }
}'''

with open('src/entities/Operator.js', 'w', encoding='utf-8') as f:
    f.write(operator_code)

# 4. SCENARIO.JS
scenario_code = '''import * as THREE from 'three';

export class Scenario {
  constructor(scene) {
    this.scene = scene;
    this.buildTerrain();
    this.buildOutpost();
    this.buildTrees();
    this.setupLighting();
  }

  buildTerrain() {
    const size = 600;
    const geometry = new THREE.PlaneGeometry(size, size, 80, 80);
    geometry.rotateX(-Math.PI / 2);

    const pos = geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      const elevation = Math.sin(x * 0.015) * Math.cos(z * 0.015) * 4 + Math.sin(x * 0.04) * 1.5;
      pos.setY(i, elevation);
    }
    geometry.computeVertexNormals();

    const terrainMat = new THREE.MeshStandardMaterial({
      color: 0x3a4d33,
      roughness: 0.95,
      metalness: 0.05,
      flatShading: true
    });

    this.terrain = new THREE.Mesh(geometry, terrainMat);
    this.scene.add(this.terrain);

    const roadGeo = new THREE.PlaneGeometry(16, 400);
    roadGeo.rotateX(-Math.PI / 2);
    roadGeo.rotateY(0.3);
    const roadMat = new THREE.MeshStandardMaterial({ color: 0x221d17, roughness: 0.9 });
    const road = new THREE.Mesh(roadGeo, roadMat);
    road.position.set(-20, 0.1, 0);
    this.scene.add(road);
  }

  buildOutpost() {
    const crateMat = new THREE.MeshStandardMaterial({ color: 0x6e563b, roughness: 0.8 });
    const metalCrateMat = new THREE.MeshStandardMaterial({ color: 0x4a554a, metalness: 0.5 });
    const bunkerMat = new THREE.MeshStandardMaterial({ color: 0x555555, roughness: 0.9 });

    const bunker = new THREE.Mesh(new THREE.BoxGeometry(10, 3, 8), bunkerMat);
    bunker.position.set(-40, 1.5, -60);
    this.scene.add(bunker);

    const towerLegMat = new THREE.MeshStandardMaterial({ color: 0x332211 });
    for (let i = 0; i < 4; i++) {
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 8), towerLegMat);
      const dx = (i % 2 === 0 ? 1 : -1) * 1.5;
      const dz = (i < 2 ? 1 : -1) * 1.5;
      leg.position.set(-50 + dx, 4, -40 + dz);
      this.scene.add(leg);
    }
    const towerTop = new THREE.Mesh(new THREE.BoxGeometry(4, 0.4, 4), bunkerMat);
    towerTop.position.set(-50, 8, -40);
    this.scene.add(towerTop);

    const crateCoords = [
      { x: -35, z: -55 }, { x: -33, z: -57 }, { x: -44, z: -68 },
      { x: 30, z: -20 }, { x: 32, z: -18 }, { x: -10, z: -80 }
    ];
    crateCoords.forEach(c => {
      const crate = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.5, 1.5), Math.random() > 0.5 ? crateMat : metalCrateMat);
      crate.position.set(c.x, 0.75, c.z);
      this.scene.add(crate);
    });
  }

  buildTrees() {
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x422a1d, roughness: 0.9 });
    const foliageMat = new THREE.MeshStandardMaterial({ color: 0x224422, roughness: 0.8, flatShading: true });

    const trunkGeo = new THREE.CylinderGeometry(0.2, 0.35, 2.5, 6);
    const foliageGeo = new THREE.ConeGeometry(2.0, 5.0, 6);

    for (let i = 0; i < 110; i++) {
      const x = (Math.random() - 0.5) * 450;
      const z = (Math.random() - 0.5) * 450;
      if (Math.hypot(x, z - 70) < 18) continue;

      const tree = new THREE.Group();
      const trunk = new THREE.Mesh(trunkGeo, trunkMat);
      trunk.position.y = 1.25;
      tree.add(trunk);

      const foliage = new THREE.Mesh(foliageGeo, foliageMat);
      foliage.position.y = 4.25;
      tree.add(foliage);

      const scale = 0.7 + Math.random() * 0.6;
      tree.scale.set(scale, scale, scale);
      tree.position.set(x, 0, z);

      this.scene.add(tree);
    }
  }

  setupLighting() {
    this.scene.fog = new THREE.FogExp2(0x18241b, 0.006);

    const ambientLight = new THREE.AmbientLight(0xd4e6d4, 0.7);
    this.scene.add(ambientLight);

    const sun = new THREE.DirectionalLight(0xfff5dd, 1.1);
    sun.position.set(100, 150, 80);
    this.scene.add(sun);
  }

  update(delta) {}
}'''

with open('src/world/Scenario.js', 'w', encoding='utf-8') as f:
    f.write(scenario_code)

# 5. SOLDIER.JS - ALVOS COM IA DE PATRULHA E DESTRUICÃO
soldier_code = '''import * as THREE from 'three';

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
}'''

with open('src/entities/Soldier.js', 'w', encoding='utf-8') as f:
    f.write(soldier_code)

# 6. EXPLOSIONS.JS
explosion_code = '''import * as THREE from 'three';

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
}'''

with open('src/effects/Explosions.js', 'w', encoding='utf-8') as f:
    f.write(explosion_code)

# 7. MISSILE.JS
missile_code = '''import * as THREE from 'three';
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
}'''

with open('src/entities/Missile.js', 'w', encoding='utf-8') as f:
    f.write(missile_code)

# 8. PLAYER.JS - DRONE FPV COM INÉRCIA E BATERIA 6S
player_code = '''import * as THREE from 'three';
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
}'''

with open('src/entities/Player.js', 'w', encoding='utf-8') as f:
    f.write(player_code)

# 9. INDEX.HTML
index_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>OPERAÇÃO GHOST — WAR ZONE FPV</title>
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; touch-action: none; }
    html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; color: #00ff96; }
    #canvas-container { width: 100%; height: 100%; position: absolute; top:0; left:0; z-index: 1; }

    #lens-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none;
      background: radial-gradient(circle, rgba(0,0,0,0) 65%, rgba(0,0,0,0.65) 100%);
    }

    #compass-container {
      position: absolute; top: 8px; left: 50%; transform: translateX(-50%);
      padding: 3px 12px; background: rgba(0, 0, 0, 0.65); border: 1px solid rgba(0, 255, 150, 0.4);
      border-radius: 4px; z-index: 10; font-size: 10px; font-weight: bold; color: #00ff96; text-shadow: 0 0 4px #00ff96;
    }

    .telemetry-left {
      position: absolute; top: 10px; left: 10px; z-index: 10; pointer-events: none;
      font-size: 9px; line-height: 1.4; color: #00ff96; text-shadow: 1px 1px 2px #000;
      background: rgba(0, 0, 0, 0.55); padding: 4px 8px; border-radius: 3px; border-left: 2px solid #00ff96;
    }

    .telemetry-right {
      position: absolute; top: 115px; right: 10px; z-index: 10; pointer-events: none;
      font-size: 9px; line-height: 1.4; color: #00ff96; text-shadow: 1px 1px 2px #000; text-align: right;
      background: rgba(0, 0, 0, 0.55); padding: 4px 8px; border-radius: 3px; border-right: 2px solid #00ff96;
    }

    .btn-top {
      position: absolute; top: 8px; height: 34px;
      background: rgba(0, 15, 8, 0.85); border: 1.5px solid #00ff96;
      color: #00ff96; font-size: 11px; font-weight: bold; border-radius: 4px; display: flex;
      justify-content: center; align-items: center; pointer-events: auto; z-index: 100; cursor: pointer;
      padding: 0 10px; box-shadow: 0 0 6px rgba(0,255,150,0.3);
    }
    .btn-top:active { background: #00ff96; color: #000; }
    #btn-fullscreen { right: 8px; width: 34px; padding: 0; }
    #btn-audio-toggle { right: 48px; width: 34px; padding: 0; }
    #btn-view-mode { right: 88px; }
    #btn-op-mode { right: 180px; }
    
    #pip-container {
      position: absolute; top: 10px; right: 275px; width: 110px; height: 82px;
      border: 1px solid rgba(0, 255, 150, 0.6); background: rgba(0, 10, 5, 0.85); z-index: 20; pointer-events: none;
      border-radius: 2px;
    }
    #pip-title {
      position: absolute; top: 2px; left: 4px; font-size: 7px; font-weight: bold; color: #00ff96;
      background: rgba(0,0,0,0.6); padding: 1px 3px; border-radius: 2px;
    }

    #reticle-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 8; pointer-events: none;
      display: flex; justify-content: center; align-items: center;
    }

    .joystick-zone {
      position: absolute; bottom: 12px; width: 100px; height: 100px; border-radius: 50%;
      background: rgba(255, 255, 255, 0.05); border: 1.5px solid rgba(0, 255, 150, 0.35);
      pointer-events: auto; z-index: 80; touch-action: none;
    }
    #zone-left { left: 12px; }
    #zone-right { right: 12px; }
    .joystick-stick {
      width: 38px; height: 38px; border-radius: 50%;
      background: rgba(0, 255, 150, 0.4); border: 1.5px solid #00ff96;
      position: absolute; top: 31px; left: 31px; pointer-events: none;
    }

    #btn-drop-missile {
      position: absolute; bottom: 125px; right: 18px; width: 56px; height: 56px; border-radius: 50%;
      background: rgba(255, 60, 60, 0.35); border: 2px solid #ff3c3c; color: #ff3c3c;
      font-size: 22px; display: flex; justify-content: center; align-items: center;
      pointer-events: auto; z-index: 90; transition: all 0.15s;
    }
    #btn-drop-missile:active { background: rgba(255, 60, 60, 0.9); color: #fff; transform: scale(0.92); }

    .modal {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5, 8, 5, 0.95);
      z-index: 200; display: flex; flex-direction: column; justify-content: center; align-items: center;
      text-align: center; padding: 20px;
    }
    .btn-main {
      pointer-events: auto; background: #00ff96; color: #000; border: none; padding: 12px 28px;
      font-size: 14px; font-weight: bold; border-radius: 3px; cursor: pointer; letter-spacing: 1px;
      box-shadow: 0 0 12px rgba(0,255,150,0.5);
    }
  </style>
  <script type="importmap">
    {
      "imports": {
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js"
      }
    }
  </script>
</head>
<body>
  <div id="canvas-container"></div>
  <div id="lens-overlay"></div>

  <div id="compass-container">
    <span id="compass-text">0° [ N ]</span>
  </div>

  <div class="telemetry-left">
    <div><b>BAT:</b> <span id="tele-bat">25.2V</span></div>
    <div><b>RSSI:</b> <span id="tele-rssi">-45dBm</span></div>
    <div><b>SAT:</b> 16 GPS</div>
    <div><b>KILLS:</b> <span id="tele-kills">0</span></div>
  </div>

  <div class="telemetry-right">
    <div><b>SPD:</b> <span id="tele-spd">0</span> km/h</div>
    <div><b>ALT:</b> <span id="tele-alt">12</span> m</div>
    <div><b>DIST:</b> <span id="tele-range">0.00</span> km</div>
  </div>

  <div id="pip-container">
    <div id="pip-title">ALVO 📷</div>
  </div>

  <button id="btn-op-mode" class="btn-top">⚔️ COMBATE</button>
  <button id="btn-view-mode" class="btn-top">🎥 FPV</button>
  <button id="btn-audio-toggle" class="btn-top" title="Áudio">🔊</button>
  <button id="btn-fullscreen" class="btn-top" title="Tela Cheia">⛶</button>

  <div id="reticle-overlay">
    <svg width="100%" height="100%" viewBox="0 0 800 450" preserveAspectRatio="none">
      <g id="pitch-ladder" transform="translate(400, 225)">
        <line x1="-25" y1="-30" x2="25" y2="-30" stroke="#00ff96" stroke-width="1" opacity="0.4"/>
        <line x1="-35" y1="0" x2="-12" y2="0" stroke="#00ff96" stroke-width="1.5" opacity="0.7"/>
        <line x1="12" y1="0" x2="35" y2="0" stroke="#00ff96" stroke-width="1.5" opacity="0.7"/>
        <line x1="-25" y1="30" x2="25" y2="30" stroke="#00ff96" stroke-width="1" opacity="0.4"/>
        <circle cx="0" cy="0" r="2.5" fill="#ff3c3c"/>
      </g>
    </svg>
  </div>

  <div id="zone-left" class="joystick-zone"><div id="stick-left" class="joystick-stick"></div></div>
  <div id="zone-right" class="joystick-zone"><div id="stick-right" class="joystick-stick"></div></div>

  <button id="btn-drop-missile">🚀</button>

  <div id="modal-start" class="modal">
    <h2 style="color:#00ff96; margin-bottom: 6px; letter-spacing: 2px;">OPERAÇÃO GHOST v1.0</h2>
    <p style="font-size: 11px; color: #88ffaa; margin-bottom: 15px;">WAR ZONE FPV SIMULATOR — RELEASE CANDIDATE</p>
    <p style="font-size: 12px; line-height: 1.6; max-width: 440px; color: #a3b8a3; margin-bottom: 22px;">
      🕹️ <b>Esquerda:</b> Altura (Sobe/Desce) & Rotação (Yaw)<br>
      🕹️ <b>Direita:</b> Deslocamento Horizontal (Frente/Trás/Lados)<br>
      🎥 <b>3ª Pessoa 360°:</b> Arraste o meio da tela para girar a câmera em volta do drone<br>
      ⚔️ <b>Ataque:</b> Mire com o marcador vermelho e aperte o botão 🚀
    </p>
    <button id="btn-start" class="btn-main">INICIAR MISSÃO</button>
  </div>

  <script type="module" src="./src/main.js"></script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 10. MAIN.JS
main_code = '''import * as THREE from 'three';
import { Player } from './entities/Player.js';
import { SoldierManager } from './entities/Soldier.js';
import { MissileSystem } from './entities/Missile.js';
import { ExplosionSystem } from './effects/Explosions.js';
import { soundManager } from './audio/SoundManager.js';
import { JoystickController } from './controls/Joystick.js';
import { Operator } from './entities/Operator.js';
import { Scenario } from './world/Scenario.js';

class Game {
  constructor() {
    this.container = document.getElementById('canvas-container');
    this.scene = new THREE.Scene();

    this.camera = new THREE.PerspectiveCamera(62, window.innerWidth / window.innerHeight, 0.1, 400);
    this.targetCamera = new THREE.OrthographicCamera(-14, 14, 14, -14, 0.1, 120);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    this.container.appendChild(this.renderer.domElement);

    const targetGeo = new THREE.RingGeometry(0.8, 1.4, 16);
    const targetMat = new THREE.MeshBasicMaterial({ color: 0xff3c3c, side: THREE.DoubleSide });
    this.targetMarker = new THREE.Mesh(targetGeo, targetMat);
    this.targetMarker.rotation.x = -Math.PI / 2;
    this.scene.add(this.targetMarker);

    this.scenario = new Scenario(this.scene);
    this.operator = new Operator(this.scene, new THREE.Vector3(0, 0, 70));

    this.player = new Player(this.scene, this.camera, this.operator.position);
    this.soldierManager = new SoldierManager(this.scene);
    this.missileSystem = new MissileSystem(this.scene);
    this.explosionSystem = new ExplosionSystem(this.scene);

    this.joysticks = new JoystickController({
      leftZoneId: 'zone-left',
      rightZoneId: 'zone-right',
      leftStickId: 'stick-left',
      rightStickId: 'stick-right'
    });

    this.setupEvents();
    this.setupOrbitTouch();
    this.clock = new THREE.Clock();
    this.isPlaying = false;

    window.addEventListener('resize', () => this.onResize());
  }

  bindButton(id, callback) {
    const btn = document.getElementById(id);
    if (!btn) return;
    const trigger = (e) => {
      e.preventDefault();
      e.stopPropagation();
      callback();
    };
    btn.addEventListener('pointerdown', trigger);
    btn.addEventListener('click', trigger);
  }

  setupEvents() {
    this.bindButton('btn-fullscreen', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });

    this.bindButton('btn-audio-toggle', () => {
      const muted = soundManager.toggleMute();
      const btn = document.getElementById('btn-audio-toggle');
      if (btn) btn.innerText = muted ? '🔇' : '🔊';
    });

    this.bindButton('btn-view-mode', () => {
      const mode = this.player.toggleViewMode();
      const btn = document.getElementById('btn-view-mode');
      if (btn) btn.innerText = mode === 'FPV' ? '🎥 FPV' : '🚁 3ª PESSOA';
    });

    this.bindButton('btn-op-mode', () => {
      const op = this.player.toggleOpMode();
      const btn = document.getElementById('btn-op-mode');
      if (btn) btn.innerText = op === 'COMBAT' ? '⚔️ COMBATE' : '👁️ VISUAL';

      const reticle = document.getElementById('reticle-overlay');
      const pip = document.getElementById('pip-container');
      const drop = document.getElementById('btn-drop-missile');

      if (op === 'VISUAL') {
        if (reticle) reticle.style.display = 'none';
        if (pip) pip.style.display = 'none';
        if (drop) drop.style.display = 'none';
        this.targetMarker.visible = false;
      } else {
        if (reticle) reticle.style.display = 'flex';
        if (pip) pip.style.display = 'block';
        if (drop) drop.style.display = 'flex';
        this.targetMarker.visible = true;
      }
    });

    this.bindButton('btn-drop-missile', () => {
      this.dropMissile();
    });

    this.bindButton('btn-start', () => {
      soundManager.init();
      soundManager.resume();

      document.getElementById('modal-start').style.display = 'none';
      this.isPlaying = true;
      this.clock.start();
      this.animate();
    });
  }

  setupOrbitTouch() {
    let lastX = 0, lastY = 0;
    let isDragging = false;

    window.addEventListener('pointerdown', (e) => {
      if (e.clientX > 120 && e.clientX < window.innerWidth - 120 && e.clientY < window.innerHeight - 120) {
        isDragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
      }
    });

    window.addEventListener('pointermove', (e) => {
      if (!isDragging || this.player.viewMode !== 'THIRD') return;
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      this.player.rotateOrbit(-dx * 0.008, -dy * 0.008);
      lastX = e.clientX;
      lastY = e.clientY;
    });

    window.addEventListener('pointerup', () => { isDragging = false; });
    window.addEventListener('pointercancel', () => { isDragging = false; });
  }

  getTargetImpactPosition() {
    const fwd = this.player.getForwardDirection();
    const impact = this.player.position.clone().add(fwd.multiplyScalar(this.player.position.y * 0.85));
    impact.y = 0.05;
    return impact;
  }

  dropMissile() {
    if (!this.isPlaying) return;
    const targetPos = this.getTargetImpactPosition();
    this.missileSystem.spawnMissile(this.player.position, targetPos);
  }

  updateCompassAndHUD() {
    const deg = Math.round(((-this.camera.rotation.y * 180 / Math.PI) % 360 + 360) % 360);
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const idx = Math.round(deg / 45) % 8;
    
    const compassText = document.getElementById('compass-text');
    if (compassText) {
      compassText.innerText = `${deg}° [ ${directions[idx]} ]`;
    }

    const pitchLadder = document.getElementById('pitch-ladder');
    if (pitchLadder) {
      const pitchDeg = (this.player.cameraTiltX * 180 / Math.PI) * 1.5;
      const rollDeg = (this.player.cameraRollZ * 180 / Math.PI);
      pitchLadder.setAttribute('transform', `translate(400, ${225 + pitchDeg}) rotate(${rollDeg})`);
    }
  }

  animate() {
    if (!this.isPlaying) return;
    requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();

    this.player.update(delta, this.joysticks.input);
    this.scenario.update(delta);
    this.soldierManager.update(delta);
    this.missileSystem.update(delta, this.explosionSystem, this.soldierManager);
    this.explosionSystem.update(delta);

    const targetPos = this.getTargetImpactPosition();
    this.targetMarker.position.copy(targetPos);

    this.targetCamera.position.set(targetPos.x, targetPos.y + 25, targetPos.z);
    this.targetCamera.lookAt(targetPos.x, targetPos.y, targetPos.z);

    const inputs = this.player.getInputs(this.joysticks.input);
    const speed = Math.round((Math.abs(inputs.ry) + Math.abs(inputs.rx)) * 52);
    const rangeInfo = this.player.getRangeStatus();

    const teleSpd = document.getElementById('tele-spd');
    const teleAlt = document.getElementById('tele-alt');
    const teleRange = document.getElementById('tele-range');
    const teleBat = document.getElementById('tele-bat');
    const teleRssi = document.getElementById('tele-rssi');
    const teleKills = document.getElementById('tele-kills');

    if (teleSpd) teleSpd.innerText = speed;
    if (teleAlt) teleAlt.innerText = Math.round(this.player.position.y);
    if (teleRange) teleRange.innerText = rangeInfo.km;
    if (teleBat) teleBat.innerText = `${this.player.batteryVoltage.toFixed(1)}V`;
    if (teleRssi) teleRssi.innerText = `${rangeInfo.rssi}dBm`;
    if (teleKills) teleKills.innerText = this.soldierManager.kills;

    this.updateCompassAndHUD();

    this.renderer.setScissorTest(false);
    this.renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
    this.renderer.render(this.scene, this.camera);

    if (this.player.opMode === 'COMBAT') {
      const pipW = 110;
      const pipH = 82;
      const pipX = window.innerWidth - pipW - 275;
      const pipY = window.innerHeight - pipH - 10;

      this.renderer.setScissorTest(true);
      this.renderer.setScissor(pipX, pipY, pipW, pipH);
      this.renderer.setViewport(pipX, pipY, pipW, pipH);
      this.renderer.render(this.scene, this.targetCamera);
    }
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  new Game();
});'''

with open('src/main.js', 'w', encoding='utf-8') as f:
    f.write(main_code)

print("Mega atualização compilada com sucesso!")
