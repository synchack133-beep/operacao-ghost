export class JoystickController {
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
}