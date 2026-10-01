export const GAME_CONFIG = {
  PLAYER: {
    speed: 18.0,
    ascendSpeed: 10.0,
    turnSpeed: 2.2,
    tiltAngleMax: 0.25,
    maxEnergy: 100,
    energyDepletionRate: 1.5,
    maxHealth: 100,
    startPosition: { x: 0, y: 3, z: 45 },
    minAltitude: 0.8,
    maxAltitude: 25.0
  },
  CAMERA: {
    distance: 4.5,
    height: 1.8,
    fov: 70,
    sensitivityMouse: 0.0025,
    sensitivityTouch: 0.004,
    damping: 0.1
  },
  WORLD: {
    mapSize: 120,
    fogColor: 0x030d08,
    fogNear: 15,
    fogFar: 90,
    clearColor: 0x030806
  },
  MISSION: {
    totalIntelCount: 4,
    intelLocations: [
      { id: 1, x: -25, z: -20, collected: false },
      { id: 2, x: 25, z: -25, collected: false },
      { id: 3, x: -30, z: 20, collected: false },
      { id: 4, x: 30, z: 15, collected: false }
    ],
    extractionZone: { x: 0, z: 45, radius: 6 }
  },
  AUDIO: {
    masterVolume: 0.7,
    sfxVolume: 0.8
  }
};
