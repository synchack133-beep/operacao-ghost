import os

joystick_code = '''export class JoystickController {
  constructor(options = {}) {
    this.input = { leftX: 0, leftY: 0, rightX: 0, rightY: 0 };
    this.leftTouchId = null;
    this.rightTouchId = null;
    this.setup(options);
  }

  setup(options) {
    const leftZone = document.getElementById(options.leftZoneId || 'zone-left');
    const rightZone = document.getElementById(options.rightZoneId || 'zone-right');
    const leftStick = document.getElementById(options.leftStickId || 'stick-left');
    const rightStick = document.getElementById(options.rightStickId || 'stick-right');

    const updateStick = (zone, stick, touch, isLeft) => {
      const rect = zone.getBoundingClientRect();
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
        this.leftTouchId = null;
      } else {
        this.input.rightX = 0;
        this.input.rightY = 0;
        this.rightTouchId = null;
      }
    };

    const setupZone = (zone, stick, isLeft) => {
      if (!zone) return;

      zone.addEventListener('touchstart', (e) => {
        for (let i = 0; i < e.changedTouches.length; i++) {
          const touch = e.changedTouches[i];
          const activeId = isLeft ? this.leftTouchId : this.rightTouchId;
          
          if (activeId === null) {
            if (isLeft) this.leftTouchId = touch.identifier;
            else this.rightTouchId = touch.identifier;
            
            updateStick(zone, stick, touch, isLeft);
            break;
          }
        }
      }, { passive: true });

      window.addEventListener('touchmove', (e) => {
        const activeId = isLeft ? this.leftTouchId : this.rightTouchId;
        if (activeId === null) return;

        for (let i = 0; i < e.touches.length; i++) {
          if (e.touches[i].identifier === activeId) {
            updateStick(zone, stick, e.touches[i], isLeft);
            break;
          }
        }
      }, { passive: true });

      const handleEnd = (e) => {
        const activeId = isLeft ? this.leftTouchId : this.rightTouchId;
        if (activeId === null) return;

        for (let i = 0; i < e.changedTouches.length; i++) {
          if (e.changedTouches[i].identifier === activeId) {
            resetStick(stick, isLeft);
            break;
          }
        }
      };

      window.addEventListener('touchend', handleEnd);
      window.addEventListener('touchcancel', handleEnd);
    };

    setupZone(leftZone, leftStick, true);
    setupZone(rightZone, rightStick, false);
  }
}'''

with open('src/controls/Joystick.js', 'w', encoding='utf-8') as f:
    f.write(joystick_code)

print("Correção de multi-touch aplicada!")
