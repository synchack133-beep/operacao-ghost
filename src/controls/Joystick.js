export class JoystickController {
  constructor(options = {}) {
    this.input = { leftX: 0, leftY: 0, rightX: 0, rightY: 0 };
    this.setup(options);
  }

  setup(options) {
    const leftZone = document.getElementById(options.leftZoneId || 'zone-left');
    const rightZone = document.getElementById(options.rightZoneId || 'zone-right');
    const leftStick = document.getElementById(options.leftStickId || 'stick-left');
    const rightStick = document.getElementById(options.rightStickId || 'stick-right');

    const handleTouch = (zone, stick, isLeft, e) => {
      if (!zone || !stick || !e.touches || e.touches.length === 0) return;
      const rect = zone.getBoundingClientRect();
      const touch = e.touches[0];
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const maxRadius = rect.width / 2;

      let dx = touch.clientX - centerX;
      let dy = touch.clientY - centerY;
      const dist = Math.hypot(dx, dy);

      if (dist > maxRadius) {
        dx = (dx / dist) * maxRadius;
        dy = (dy / dist) * maxRadius;
      }

      stick.style.transform = `translate(${dx}px, ${dy}px)`;

      const normX = dx / maxRadius;
      const normY = dy / maxRadius;

      if (isLeft) {
        this.input.leftX = normX;
        this.input.leftY = normY;
      } else {
        this.input.rightX = normX;
        this.input.rightY = normY;
      }
    };

    const resetStick = (stick, isLeft) => {
      if (stick) stick.style.transform = 'translate(0px, 0px)';
      if (isLeft) {
        this.input.leftX = 0;
        this.input.leftY = 0;
      } else {
        this.input.rightX = 0;
        this.input.rightY = 0;
      }
    };

    if (leftZone) {
      leftZone.addEventListener('touchstart', (e) => handleTouch(leftZone, leftStick, true, e), { passive: true });
      leftZone.addEventListener('touchmove', (e) => handleTouch(leftZone, leftStick, true, e), { passive: true });
      leftZone.addEventListener('touchend', () => resetStick(leftStick, true));
      leftZone.addEventListener('touchcancel', () => resetStick(leftStick, true));
    }

    if (rightZone) {
      rightZone.addEventListener('touchstart', (e) => handleTouch(rightZone, rightStick, false, e), { passive: true });
      rightZone.addEventListener('touchmove', (e) => handleTouch(rightZone, rightStick, false, e), { passive: true });
      rightZone.addEventListener('touchend', () => resetStick(rightStick, false));
      rightZone.addEventListener('touchcancel', () => resetStick(rightStick, false));
    }
  }
}