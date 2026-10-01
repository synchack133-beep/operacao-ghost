import { GAME_CONFIG } from '../config/gameConfig.js';
import { eventBus } from '../core/EventBus.js';

export class InputManager {
  constructor(cameraController) {
    this.cameraController = cameraController;
    this.state = {
      forward: false,
      backward: false,
      left: false,
      right: false,
      up: false,
      down: false,
      action: false,
      fire: false
    };

    this.initKeyboard();
    this.initMouse();
  }

  initKeyboard() {
    window.addEventListener('keydown', (e) => this.onKey(e, true));
    window.addEventListener('keyup', (e) => this.onKey(e, false));
  }

  onKey(e, isDown) {
    switch (e.code) {
      case 'KeyW': case 'ArrowUp': this.state.forward = isDown; break;
      case 'KeyS': case 'ArrowDown': this.state.backward = isDown; break;
      case 'KeyA': case 'ArrowLeft': this.state.left = isDown; break;
      case 'KeyD': case 'ArrowRight': this.state.right = isDown; break;
      case 'Space': this.state.up = isDown; break;
      case 'ShiftLeft': case 'ShiftRight': this.state.down = isDown; break;
      case 'KeyE':
        this.state.action = isDown;
        if (isDown) eventBus.emit('actionTriggered');
        break;
    }
  }

  initMouse() {
    let isDragging = false;
    let prevX = 0, prevY = 0;

    window.addEventListener('mousedown', (e) => {
      if (e.target.tagName === 'CANVAS') {
        isDragging = true;
        prevX = e.clientX;
        prevY = e.clientY;
      }
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const dx = (e.clientX - prevX) * GAME_CONFIG.CAMERA.sensitivityMouse;
      const dy = (e.clientY - prevY) * GAME_CONFIG.CAMERA.sensitivityMouse;
      prevX = e.clientX;
      prevY = e.clientY;
      this.cameraController.handleLookDelta(dx, dy);
    });

    window.addEventListener('mouseup', () => isDragging = false);
  }
}
