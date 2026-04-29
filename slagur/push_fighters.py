import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Push Fighters - 2 Player")
clock = pygame.time.Clock()

GRAVITY = 0.8
FPS = 60

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
RED = (220, 60, 60)
BLUE = (60, 120, 240)
GREEN = (80, 200, 120)
GRAY = (90, 90, 90)
YELLOW = (255, 220, 80)

platform = pygame.Rect(200, 430, 600, 40)


class Fighter:
    def __init__(self, x, y, color, controls, facing):
        self.rect = pygame.Rect(x, y, 55, 90)
        self.color = color
        self.controls = controls
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -16
        self.on_ground = False
        self.facing = facing
        self.attack_timer = 0
        self.hit_cooldown = 0
        self.score = 0
        self.walk_frame = 0

    def move(self, keys):
        self.vel_x = 0

        if keys[self.controls["left"]]:
            self.vel_x = -self.speed
            self.facing = -1
            self.walk_frame += 1

        if keys[self.controls["right"]]:
            self.vel_x = self.speed
            self.facing = 1
            self.walk_frame += 1

        if keys[self.controls["jump"]] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        if keys[self.controls["attack"]] and self.attack_timer == 0:
            self.attack_timer = 18

    def physics(self):
        self.vel_y += GRAVITY
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        self.on_ground = False

        if self.rect.colliderect(platform) and self.vel_y >= 0:
            if self.rect.bottom <= platform.top + 25:
                self.rect.bottom = platform.top
                self.vel_y = 0
                self.on_ground = True

        if self.attack_timer > 0:
            self.attack_timer -= 1

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def attack_box(self):
        if self.attack_timer > 6:
            if self.facing == 1:
                return pygame.Rect(self.rect.right, self.rect.y + 25, 45, 30)
            else:
                return pygame.Rect(self.rect.left - 45, self.rect.y + 25, 45, 30)
        return None

    def draw(self):
        x, y, w, h = self.rect

        # Body animation
        bob = 0
        if self.vel_x != 0 and self.on_ground:
            bob = 4 if (self.walk_frame // 8) % 2 == 0 else -2

        # Head
        pygame.draw.circle(screen, self.color, (x + w // 2, y + 18 + bob), 18)

        # Body
        pygame.draw.rect(screen, self.color, (x + 13, y + 35 + bob, 30, 35), border_radius=8)

        # Legs
        leg_offset = 6 if (self.walk_frame // 8) % 2 == 0 else -6
        pygame.draw.line(screen, self.color, (x + 23, y + 68 + bob), (x + 18 + leg_offset, y + 88), 7)
        pygame.draw.line(screen, self.color, (x + 33, y + 68 + bob), (x + 38 - leg_offset, y + 88), 7)

        # Arms
        if self.attack_timer > 6:
            arm_end_x = x + w // 2 + self.facing * 55
            pygame.draw.line(screen, YELLOW, (x + w // 2, y + 45 + bob), (arm_end_x, y + 45 + bob), 9)
        else:
            pygame.draw.line(screen, self.color, (x + 15, y + 45 + bob), (x - 5, y + 60 + bob), 6)
            pygame.draw.line(screen, self.color, (x + 40, y + 45 + bob), (x + 60, y + 60 + bob), 6)

        # Attack hitbox preview
        box = self.attack_box()
        if box:
            pygame.draw.rect(screen, YELLOW, box, 2)


def reset_round(winner=None):
    p1.rect.x, p1.rect.y = 280, 320
    p2.rect.x, p2.rect.y = 670, 320
    p1.vel_x = p1.vel_y = 0
    p2.vel_x = p2.vel_y = 0
    p1.facing = 1
    p2.facing = -1

    if winner == "p1":
        p1.score += 1
    elif winner == "p2":
        p2.score += 1


def handle_attacks(attacker, defender):
    box = attacker.attack_box()
    if box and box.colliderect(defender.rect) and defender.hit_cooldown == 0:
        defender.vel_x = attacker.facing * 14
        defender.vel_y = -7
        defender.hit_cooldown = 25


p1 = Fighter(
    280, 320, BLUE,
    {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "jump": pygame.K_w,
        "attack": pygame.K_f,
    },
    1
)

p2 = Fighter(
    670, 320, RED,
    {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "attack": pygame.K_l,
    },
    -1
)

font = pygame.font.SysFont(None, 42)
small_font = pygame.font.SysFont(None, 28)

reset_round()

while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    p1.move(keys)
    p2.move(keys)

    p1.physics()
    p2.physics()

    handle_attacks(p1, p2)
    handle_attacks(p2, p1)

    if p1.rect.top > HEIGHT:
        reset_round("p2")

    if p2.rect.top > HEIGHT:
        reset_round("p1")

    screen.fill((135, 200, 255))

    # Background
    pygame.draw.circle(screen, (255, 240, 130), (850, 100), 45)
    pygame.draw.rect(screen, (80, 170, 90), (0, 470, WIDTH, 130))

    # Platform
    pygame.draw.rect(screen, GRAY, platform, border_radius=10)
    pygame.draw.rect(screen, BLACK, platform, 3, border_radius=10)

    p1.draw()
    p2.draw()

    score_text = font.render(f"Blue {p1.score}  -  {p2.score} Red", True, BLACK)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 30))

    controls = small_font.render(
        "Blue: A/D move, W jump, F punch     Red: Arrows move, Up jump, L punch",
        True,
        BLACK
    )
    screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, 560))

    pygame.display.flip()
