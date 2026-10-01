export class Radar {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (this.canvas) this.ctx = this.canvas.getContext('2d');
  }

  draw(player, enemies, dataModules) {
    if (!this.ctx) return;
    const w = this.canvas.width;
    const h = this.canvas.height;
    const cx = w / 2;
    const cy = h / 2;
    const scale = 1.3;

    this.ctx.clearRect(0, 0, w, h);

    this.ctx.strokeStyle = 'rgba(0, 255, 150, 0.3)';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, 18, 0, Math.PI * 2);
    this.ctx.arc(cx, cy, 34, 0, Math.PI * 2);
    this.ctx.stroke();

    if (!player) return;

    if (dataModules) {
      this.ctx.fillStyle = '#00ff96';
      dataModules.forEach(mod => {
        if (!mod.collected) {
          const dx = (mod.mesh.position.x - player.position.x) * scale;
          const dz = (mod.mesh.position.z - player.position.z) * scale;
          if (Math.hypot(dx, dz) < cx - 4) {
            this.ctx.fillRect(cx + dx - 2, cy + dz - 2, 4, 4);
          }
        }
      });
    }

    if (enemies) {
      this.ctx.fillStyle = '#ff0055';
      enemies.forEach(e => {
        if (e.active) {
          const dx = (e.group.position.x - player.position.x) * scale;
          const dz = (e.group.position.z - player.position.z) * scale;
          if (Math.hypot(dx, dz) < cx - 4) {
            this.ctx.beginPath();
            this.ctx.arc(cx + dx, cy + dz, 3, 0, Math.PI * 2);
            this.ctx.fill();
          }
        }
      });
    }

    this.ctx.fillStyle = '#00ffff';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    this.ctx.fill();
  }
}