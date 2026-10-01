import sys
import math
import random
import pygame

# Inicialização do Pygame
pygame.init()
pygame.font.init()

# Configurações de Tela
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador Tático de Guerra de Drones - FPV & Recon")
clock = pygame.time.Clock()

# Cores Táticas
COLOR_BG = (15, 20, 15)
COLOR_TRENCH = (60, 50, 40)
COLOR_DRONE = (0, 255, 120)
COLOR_HUD = (0, 255, 66)
COLOR_ENEMY = (235, 60, 60)
COLOR_MISSILE = (255, 200, 0)
COLOR_PIP_BORDER = (0, 200, 255)
COLOR_EXPLOSION = (255, 120, 0)

font_hud = pygame.font.SysFont("Courier", 14, bold=True)
font_title = pygame.font.SysFont("Courier", 18, bold=True)

# ---------------------------------------------------------
# IA DOS SOLDADOS INIMIGOS
# ---------------------------------------------------------
class SoldierAI:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = 1.2
        self.health = 100
        self.state = "PATROL"  # PATROL, COVER, SHOOT
        self.patrol_target = (x + random.randint(-80, 80), y + random.randint(-80, 80))
        self.timer = 0
        self.alive = True

    def update(self, drone_pos, explosion_events):
        if not self.alive:
            return

        # Distância em relação ao Drone
        dx = drone_pos[0] - self.x
        dy = drone_pos[1] - self.y
        dist_drone = math.hypot(dx, dy)

        # Reação a explosões próximas
        for exp in explosion_events:
            if math.hypot(exp[0] - self.x, exp[1] - self.y) < 150:
                self.state = "COVER"
                self.timer = 180  # Fica em pânico por 3 segundos

        # Lógica de Estados da IA
        if self.state == "COVER":
            self.timer -= 1
            if dist_drone > 0:
                self.x -= (dx / dist_drone) * (self.speed * 1.5)
                self.y -= (dy / dist_drone) * (self.speed * 1.5)
            if self.timer <= 0:
                self.state = "PATROL"

        elif self.state == "PATROL":
            tx, ty = self.patrol_target
            p_dx, p_dy = tx - self.x, ty - self.y
            p_dist = math.hypot(p_dx, p_dy)

            if p_dist < 5:
                self.patrol_target = (
                    max(100, min(WIDTH - 100, self.x + random.randint(-120, 120))),
                    max(100, min(HEIGHT - 100, self.y + random.randint(-120, 120)))
                )
            else:
                self.x += (p_dx / p_dist) * self.speed
                self.y += (p_dy / p_dist) * self.speed

            if dist_drone < 200:
                self.state = "SHOOT"

        elif self.state == "SHOOT":
            if dist_drone > 280:
                self.state = "PATROL"

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            pygame.draw.line(surface, (100, 30, 30), (self.x - 4, self.y - 4), (self.x + 4, self.y + 4), 2)
            pygame.draw.line(surface, (100, 30, 30), (self.x + 4, self.y - 4), (self.x - 4, self.y + 4), 2)
            return

        color = COLOR_ENEMY if self.state != "COVER" else (255, 140, 0)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 6)
        
        # Barra de vida
        pygame.draw.rect(surface, (50, 50, 50), (int(self.x) - 10, int(self.y) - 12, 20, 3))
        pygame.draw.rect(surface, (0, 255, 0), (int(self.x) - 10, int(self.y) - 12, int(20 * (self.health / 100)), 3))

# ---------------------------------------------------------
# MÍSSIL / BABA YAGA DROP MUNITION
# ---------------------------------------------------------
class Ordnance:
    def __init__(self, x, y, alt, target_x, target_y):
        self.x = float(x)
        self.y = float(y)
        self.altitude = float(alt)
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.speed = 8.0
        self.active = True

        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        self.vx = (dx / dist) * self.speed if dist > 0 else 0
        self.vy = (dy / dist) * self.speed if dist > 0 else 0

    def update(self):
        if not self.active:
            return None

        self.x += self.vx
        self.y += self.vy
        self.altitude -= 4.0

        if self.altitude <= 0 or math.hypot(self.target_x - self.x, self.target_y - self.y) < 6:
            self.active = False
            return (self.x, self.y)
        return None

    def draw(self, surface):
        if self.active:
            pygame.draw.circle(surface, COLOR_MISSILE, (int(self.x), int(self.y)), 4)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 2)

# ---------------------------------------------------------
# DRONE COM CÂMERA DE DESTINO (PiP)
# ---------------------------------------------------------
class TacticalDrone:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.altitude = 150.0
        self.speed = 3.5
        self.angle = 0
        self.battery = 100.0

    def move(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        if keys[pygame.K_q]:
            self.altitude = min(300.0, self.altitude + 1.5)
        if keys[pygame.K_e]:
            self.altitude = max(30.0, self.altitude - 1.5)

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            self.x += (dx / length) * self.speed
            self.y += (dy / length) * self.speed
            self.angle = math.degrees(math.atan2(-dy, dx))

        self.battery = max(0.0, self.battery - 0.005)

    def get_missile_target(self):
        rad = math.radians(-self.angle)
        offset = self.altitude * 0.4
        tx = self.x + math.cos(rad) * offset
        ty = self.y + math.sin(rad) * offset
        return tx, ty

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        pygame.draw.circle(surface, COLOR_DRONE, (px, py), 8)
        for dx, dy in [(-10, -10), (10, -10), (-10, 10), (10, 10)]:
            pygame.draw.circle(surface, (200, 200, 200), (px + dx, py + dy), 5, 1)

# ---------------------------------------------------------
# LOOP PRINCIPAL
# ---------------------------------------------------------
def main():
    drone = TacticalDrone(WIDTH // 2, HEIGHT // 2)
    soldiers = [SoldierAI(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)) for _ in range(8)]
    missiles = []
    explosions = []

    running = True
    while running:
        clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and drone.battery > 0:
                    tx, ty = drone.get_missile_target()
                    missiles.append(Ordnance(drone.x, drone.y, drone.altitude, tx, ty))

        drone.move(keys)

        explosion_coords = []
        for m in missiles[:]:
            exp_pos = m.update()
            if exp_pos:
                explosions.append([exp_pos[0], exp_pos[1], 5, 20])
                explosion_coords.append(exp_pos)
                missiles.remove(m)

        for exp in explosion_coords:
            for s in soldiers:
                if math.hypot(s.x - exp[0], s.y - exp[1]) < 45:
                    s.take_damage(80)

        for s in soldiers:
            s.update((drone.x, drone.y), explosion_coords)

        screen.fill(COLOR_BG)

        # Trincheiras
        pygame.draw.lines(screen, COLOR_TRENCH, False, [(100, 200), (300, 250), (500, 200), (800, 300)], 12)
        pygame.draw.lines(screen, COLOR_TRENCH, False, [(200, 500), (450, 480), (700, 600)], 12)

        for s in soldiers:
            s.draw(screen)

        for m in missiles:
            m.draw(screen)

        for exp in explosions[:]:
            pygame.draw.circle(screen, COLOR_EXPLOSION, (int(exp[0]), int(exp[1])), int(exp[2]))
            exp[2] += 2
            exp[3] -= 1
            if exp[3] <= 0:
                explosions.remove(exp)

        drone.draw(screen)

        # Retículo de impacto no solo
        tx, ty = drone.get_missile_target()
        pygame.draw.circle(screen, (255, 50, 50), (int(tx), int(ty)), 12, 1)
        pygame.draw.line(screen, (255, 50, 50), (int(tx) - 15, int(ty)), (int(tx) + 15, int(ty)), 1)
        pygame.draw.line(screen, (255, 50, 50), (int(tx), int(ty) - 15), (int(tx), int(ty) + 15), 1)

        # Câmera PiP
        pip_w, pip_h = 220, 180
        pip_x, pip_y = WIDTH - pip_w - 20, 20
        pip_surface = pygame.Surface((pip_w, pip_h))
        pip_surface.fill((10, 15, 10))

        zoom_factor = 1.8
        for s in soldiers:
            if s.alive:
                rel_x = (s.x - tx) * zoom_factor + pip_w / 2
                rel_y = (s.y - ty) * zoom_factor + pip_h / 2
                if 0 <= rel_x <= pip_w and 0 <= rel_y <= pip_h:
                    pygame.draw.circle(pip_surface, COLOR_ENEMY, (int(rel_x), int(rel_y)), 5)

        for m in missiles:
            rel_mx = (m.x - tx) * zoom_factor + pip_w / 2
            rel_my = (m.y - ty) * zoom_factor + pip_h / 2
            if 0 <= rel_mx <= pip_w and 0 <= rel_my <= pip_h:
                pygame.draw.circle(pip_surface, COLOR_MISSILE, (int(rel_mx), int(rel_my)), 3)

        pygame.draw.circle(pip_surface, COLOR_HUD, (pip_w // 2, pip_h // 2), 16, 1)
        pygame.draw.line(pip_surface, COLOR_HUD, (pip_w // 2 - 20, pip_h // 2), (pip_w // 2 + 20, pip_h // 2), 1)
        pygame.draw.line(pip_surface, COLOR_HUD, (pip_w // 2, pip_h // 2 - 20), (pip_w // 2, pip_h // 2 + 20), 1)

        screen.blit(pip_surface, (pip_x, pip_y))
        pygame.draw.rect(screen, COLOR_PIP_BORDER, (pip_x, pip_y, pip_w, pip_h), 2)
        txt_pip = font_title.render("CAM: DESTINO MÍSSIL (ZENITAL)", True, COLOR_PIP_BORDER)
        screen.blit(txt_pip, (pip_x, pip_y - 20))

        # HUD
        hud_lines = [
            f"DRONE ALTITUDE : {drone.altitude:.1f} m (Q/E)",
            f"BATERIA        : {drone.battery:.1f} %",
            f"MÍSSEIS ATIVOS : {len(missiles)}",
            f"INIMIGOS VIVOS : {sum(1 for s in soldiers if s.alive)}/8",
            "[WASD/Setas] Mover | [ESPAÇO] Soltar Míssil"
        ]

        for i, line in enumerate(hud_lines):
            t = font_hud.render(line, True, COLOR_HUD)
            screen.blit(t, (20, 20 + i * 18))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
