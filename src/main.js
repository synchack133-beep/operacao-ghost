import { Engine } from './core/Engine.js';
import { CameraController } from './camera/CameraController.js';
import { InputManager } from './input/InputManager.js';
import { TouchOverlay } from './input/TouchOverlay.js';
import { PlayerController } from './player/PlayerController.js';
import { Environment } from './world/Environment.js';
import { MissionManager } from './gameplay/MissionManager.js';
import { UIManager } from './ui/UIManager.js';
import { eventBus } from './core/EventBus.js';

window.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('game-container');

  const engine = new Engine(container);
  engine.addLighting();

  const cameraController = new CameraController(engine.camera);
  const inputManager = new InputManager(cameraController);
  const touchOverlay = new TouchOverlay(inputManager.state, cameraController);

  const environment = new Environment(engine.scene);
  const playerController = new PlayerController(engine.scene);
  const missionManager = new MissionManager(environment);
  const uiManager = new UIManager(touchOverlay);

  eventBus.on('checkProximityAndCollect', () => {
    const pos = playerController.mesh.position;
    environment.intelMeshes.forEach(mesh => {
      if (mesh.visible) {
        const dist = Math.hypot(pos.x - mesh.position.x, pos.z - mesh.position.z);
        if (dist < 3.8) {
          missionManager.collect(mesh.userData.id);
        }
      }
    });
  });

  eventBus.on('resetMission', () => {
    environment.intelMeshes.forEach(m => m.visible = true);
    missionManager.reset();
  });

  engine.onRegisterUpdate((deltaTime) => {
    playerController.update(deltaTime, inputManager.state, { yaw: cameraController.yaw });
    cameraController.update(playerController.mesh);
    environment.update(deltaTime);
    missionManager.checkPlayerProximity(playerController.mesh.position);
  });

  engine.start();
});
