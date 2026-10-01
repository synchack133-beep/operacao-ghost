import * as THREE from 'three';

export function createDroneMesh() {
  const droneGroup = new THREE.Group();

  const bodyGeo = new THREE.ConeGeometry(0.5, 1.2, 5);
  bodyGeo.rotateX(Math.PI / 2);
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x111e18, roughness: 0.3, metalness: 0.8 });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.castShadow = true;
  droneGroup.add(body);

  const lensGeo = new THREE.SphereGeometry(0.12, 16, 16);
  const lensMat = new THREE.MeshBasicMaterial({ color: 0x00ff96 });
  const lens = new THREE.Mesh(lensGeo, lensMat);
  lens.position.set(0, 0, -0.6);
  droneGroup.add(lens);

  const spotLight = new THREE.SpotLight(0x00ffaa, 4, 25, Math.PI / 6, 0.5);
  spotLight.position.set(0, -0.1, -0.5);
  spotLight.target.position.set(0, -5, -15);
  droneGroup.add(spotLight);
  droneGroup.add(spotLight.target);

  const armMat = new THREE.MeshStandardMaterial({ color: 0x08140e, metalness: 0.9 });
  const propMat = new THREE.MeshBasicMaterial({ color: 0x00ff96, transparent: true, opacity: 0.6 });
  const rotors = [];

  const offsets = [
    { x: 0.7, z: -0.6 },
    { x: -0.7, z: -0.6 },
    { x: 0.8, z: 0.6 },
    { x: -0.8, z: 0.6 }
  ];

  offsets.forEach((off) => {
    const armGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.9);
    const arm = new THREE.Mesh(armGeo, armMat);
    arm.position.set(off.x / 2, 0, off.z / 2);
    arm.rotation.z = Math.atan2(off.x, off.z);
    arm.rotation.x = Math.PI / 2;
    droneGroup.add(arm);

    const propGeo = new THREE.BoxGeometry(0.7, 0.01, 0.08);
    const prop = new THREE.Mesh(propGeo, propMat);
    prop.position.set(off.x, 0.1, off.z);
    droneGroup.add(prop);
    rotors.push(prop);
  });

  droneGroup.userData.rotors = rotors;
  return droneGroup;
}
