import { GAME_CONFIG } from '../config/gameConfig.js';

export class TouchOverlay {
  constructor(inputState, cameraController) {
    this.inputState = inputState;
    this.cameraController = cameraController;
    this.touchLayer = document.getElementById('touch-layer');
    this.canvas = document.getElementById('touch-canvas');
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;

    this.joyId = null;
    this.joyBase = { x: 0, y: 0 };
    this.joyStick = { x: 0, y: 0 };
    this.maxRadius = 45;

    this.lookId = null;
    this.lastLook = { x: 0, y: 0 };

    this.init();
  }

  init() {
    if (!this.touchLayer) return;
    this.resize();
    window.addEventListener('resize', () => this.resize());

    window.addEventListener('touchstart', (e) => this.onTouchStart(e), { passive: false });
    window.addEventListener('touchmove', (e) => this.onTouchMove(e), { passive: false });
    window.addEventListener('touchend', (e) => this.onTouchEnd(e));
    window.addEventListener('touchcancel', (e) => this.onTouchEnd(e));

    this.bindBtn('btn-up', 'up');
    this.bindBtn('btn-down', 'down');
    this.bindBtn('btn-action', 'action');
    this.bindBtn('btn-fire', 'fire');
  }

  resize() {
    if (this.canvas) {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    }
  }

  bindBtn(id, key) {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener('touchstart', (e) => { e.preventDefault(); this.inputState[key] = true; });
    btn.addEventListener('touchend', (e) => { e.preventDefault(); this.inputState[key] = false; });
  }

  onTouchStart(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const t = e.changedTouches[i];
      if (t.clientX < window.innerWidth / 2 && this.joyId === null) {
        this.joyId = t.identifier;
        this.joyBase = { x: t.clientX, y: t.clientY };
        this.joyStick = { x: t.clientX, y: t.clientY };
        this.drawJoy();
      } else if (t.clientX >= window.innerWidth / 2 && this.lookId === null) {
        this.lookId = t.identifier;
        this.lastLook = { x: t.clientX, y: t.clientY };
      }
    }
  }

  onTouchMove(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const t = e.changedTouches[i];
      if (t.identifier === this.joyId) {
        let dx = t.clientX - this.joyBase.x;
        let dy = t.clientY - this.joyBase.y;
        const dist = Math.hypot(dx, dy);
        if (dist > this.maxRadius) {
          dx = (dx / dist) * this.maxRadius;
          dy = (dy / dist) * this.maxRadius;
        }
        this.joyStick = { x: this.joyBase.x + dx, y: this.joyBase.y + dy };

        this.inputState.forward = dy < -12;
        this.inputState.backward = dy > 12;
        this.inputState.left = dx < -12;
        this.inputState.right = dx > 12;

        this.drawJoy();
      } else if (t.identifier === this.lookId) {
        const dx = (t.clientX - this.lastLook.x) * GAME_CONFIG.CAMERA.sensitivityTouch;
        const dy = (t.clientY - this.lastLook.y) * GAME_CONFIG.CAMERA.sensitivityTouch;
        this.lastLook = { x: t.clientX, y: t.clientY };
        this.cameraController.handleLookDelta(dx, dy);
      }
    }
  }

  onTouchEnd(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const t = e.changedTouches[i];
      if (t.identifier === this.joyId) {
        this.joyId = null;
        this.inputState.forward = false;
        this.inputState.backward = false;
        this.inputState.left = false;
        this.inputState.right = false;
        if (this.ctx) this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      } else if (t.identifier === this.lookId) {
        this.lookId = null;
      }
    }
  }

  drawJoy() {
    if (!this.ctx) return;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.beginPath();
    this.ctx.arc(this.joyBase.x, this.joyBase.y, this.maxRadius, 0, Math.PI * 2);
    this.ctx.fillStyle = 'rgba(0, 255, 150, 0.12)';
    this.ctx.strokeStyle = 'rgba(0, 255, 150, 0.5)';
    this.ctx.lineWidth = 2;
    this.ctx.fill(); this.ctx.stroke();

    this.ctx.beginPath();
    this.ctx.arc(this.joyStick.x, this.joyStick.y, 18, 0, Math.PI * 2);
    this.ctx.fillStyle = 'rgba(0, 255, 150, 0.7)';
    this.ctx.fill();
  }

  show(visible) {
    if (this.touchLayer) this.touchLayer.style.display = visible ? 'block' : 'none';
  }
}
