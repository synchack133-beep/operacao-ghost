export class JoystickController {
  constructor(options) {
    this.leftZone = document.getElementById(options.leftZoneId);
    this.rightZone = document.getElementById(options.rightZoneId);
    this.leftStick = document.getElementById(options.leftStickId);
    this.rightStick = document.getElementById(options.rightStickId);

    this.leftTouchId = null;
    this.rightTouchId = null;

    this.leftOrigin = { x: 0, y: 0 };
    this.rightOrigin = { x: 0, y: 0 };

    this.input = {
      throttle: 0, // Y esquerdo (-1 a 1)
      yaw: 0,      // X esquerdo (-1 a 1)
      pitch: 0,    // Y direito (-1 a 1)
      roll: 0      // X direito (-1 a 1)
    };

    this.maxRadius = 42; // Limite do analógico
    this.init();
  }

  init() {
    window.addEventListener('touchstart', (e) => this.onTouchStart(e), { passive: false });
    window.addEventListener('touchmove', (e) => this.onTouchMove(e), { passive: false });
    window.addEventListener('touchend', (e) => this.onTouchEnd(e), { passive: false });
    window.addEventListener('touchcancel', (e) => this.onTouchEnd(e), { passive: false });
  }

  onTouchStart(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      const target = document.elementFromPoint(touch.clientX, touch.clientY);
      
      if (target && target.closest('#btn-shoot, #btn-fullscreen, #btn-nightvision, .btn-main')) {
        continue; // Permite o disparo sem travar o analógico
      }

      const rectLeft = this.leftZone.getBoundingClientRect();
      const rectRight = this.rightZone.getBoundingClientRect();

      // Analógico Esquerdo (Subir/Descer + Girar)
      if (this.leftTouchId === null && 
          touch.clientX >= rectLeft.left && touch.clientX <= rectLeft.right &&
          touch.clientY >= rectLeft.top && touch.clientY <= rectLeft.bottom) {
        this.leftTouchId = touch.identifier;
        this.leftOrigin = { x: rectLeft.left + rectLeft.width / 2, y: rectLeft.top + rectLeft.height / 2 };
        this.updateLeft(touch.clientX, touch.clientY);
        e.preventDefault();
      }
      // Analógico Direito (Avançar/Recuar + Esquerda/Direita)
      else if (this.rightTouchId === null && 
               touch.clientX >= rectRight.left && touch.clientX <= rectRight.right &&
               touch.clientY >= rectRight.top && touch.clientY <= rectRight.bottom) {
        this.rightTouchId = touch.identifier;
        this.rightOrigin = { x: rectRight.left + rectRight.width / 2, y: rectRight.top + rectRight.height / 2 };
        this.updateRight(touch.clientX, touch.clientY);
        e.preventDefault();
      }
    }
  }

  onTouchMove(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      if (touch.identifier === this.leftTouchId) {
        this.updateLeft(touch.clientX, touch.clientY);
        e.preventDefault();
      } else if (touch.identifier === this.rightTouchId) {
        this.updateRight(touch.clientX, touch.clientY);
        e.preventDefault();
      }
    }
  }

  onTouchEnd(e) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      if (touch.identifier === this.leftTouchId) {
        this.leftTouchId = null;
        this.input.throttle = 0;
        this.input.yaw = 0;
        this.leftStick.style.transform = `translate(0px, 0px)`;
      } else if (touch.identifier === this.rightTouchId) {
        this.rightTouchId = null;
        this.input.pitch = 0;
        this.input.roll = 0;
        this.rightStick.style.transform = `translate(0px, 0px)`;
      }
    }
  }

  updateLeft(x, y) {
    let dx = x - this.leftOrigin.x;
    let dy = y - this.leftOrigin.y;
    let dist = Math.hypot(dx, dy);

    if (dist > this.maxRadius) {
      dx = (dx / dist) * this.maxRadius;
      dy = (dy / dist) * this.maxRadius;
    }

    this.leftStick.style.transform = `translate(${dx}px, ${dy}px)`;
    this.input.yaw = dx / this.maxRadius;
    this.input.throttle = -dy / this.maxRadius; // Empurrar para cima = subir
  }

  updateRight(x, y) {
    let dx = x - this.rightOrigin.x;
    let dy = y - this.rightOrigin.y;
    let dist = Math.hypot(dx, dy);

    if (dist > this.maxRadius) {
      dx = (dx / dist) * this.maxRadius;
      dy = (dy / dist) * this.maxRadius;
    }

    this.rightStick.style.transform = `translate(${dx}px, ${dy}px)`;
    this.input.roll = dx / this.maxRadius;
    this.input.pitch = -dy / this.maxRadius; // Empurrar para cima = frente
  }
}
