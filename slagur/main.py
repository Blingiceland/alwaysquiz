import pygame
import sys
import random
import os
import asyncio
from questions import get_questions

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quiz Walker")
clock = pygame.time.Clock()

FPS = 60
GRAVITY = 0.8

SKY_TOP = (100, 180, 255)
SKY_BOT = (180, 220, 255)
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 190, 70)
DARK_GREEN = (30, 130, 50)
GRASS_TOP = (80, 200, 80)
BROWN = (160, 100, 50)
DARK_BROWN = (100, 60, 30)
GOLD = (255, 200, 0)
GHOST_COLOR = (220, 220, 255)
MOUNTAIN = (140, 160, 180)
MOUNTAIN_DARK = (100, 120, 140)
MOUNTAIN_SNOW = (230, 240, 255)
PIPE_GREEN = (50, 160, 50)
PIPE_DARK = (30, 100, 30)
TRUMP_SKIN = (255, 185, 100)
TRUMP_HAIR = (255, 210, 50)
TRUMP_SUIT = (30, 50, 100)
TRUMP_TIE = (200, 30, 30)

font = pygame.font.SysFont(None, 38)
big_font = pygame.font.SysFont(None, 68)
small_font = pygame.font.SysFont(None, 28)
rage_font = pygame.font.SysFont(None, 72)

# FIX: Relative paths for Pygbag
music_file = "bg_music.wav"
death_file = "death_sound.wav"
PICS = "pics"

def load_image(filename, scale=None):
    path = os.path.join(PICS, filename)
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            print(f"Mynd hlaðin: {filename}")
            return img
    except Exception as e:
        print(f"Gat ekki hlaðið mynd: {filename} — {e}")
    return None

# Hlaða myndum
trump_img_right = load_image("trump1-bg.png", scale=(52, 100))
trump_img_left = pygame.transform.flip(trump_img_right, True, False) if trump_img_right else None
trump_rage_img = load_image("trumprage.png", scale=(320, 370))

death_sound = None
try:
    if os.path.exists(death_file):
        death_sound = pygame.mixer.Sound(death_file)
except Exception as e:
    print("Dauða hljóð villa:", e)

def start_music():
    try:
        if os.path.exists(music_file):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)
    except Exception as e:
        print("Tónlistarvilla:", e)

start_music()

def correct(user, answers):
    return user.strip().lower() == answers[0].strip().lower()

RAGE_MESSAGES = [
    ("WRONG! TOTAL DISASTER!", "Nobody fails worse than you, believe me!"),
    ("FAKE ANSWER! SAD!", "Back to the beginning, loser!"),
    ("YOU'RE FIRED!", "That was the worst answer I've ever seen!"),
    ("WRONG! MANY PEOPLE...", "...are saying you're very bad at this!"),
    ("TOTAL LOSER!", "Go back to start, okay? Just go back!"),
    ("WRONG! DISGRACEFUL!", "I've seen smarter answers from a rock!"),
    ("NASTY ANSWER!", "Back to beginning — it's going to be YUGE!"),
    ("WRONG! BELIEVE ME!", "I know answers, the best answers. That wasn't one."),
    ("TREMENDOUS FAILURE!", "Nobody fails bigger than you, nobody!"),
    ("WRONG! RIGGED QUIZ!", "But you still have to go back to start!"),
]

WORLD_WIDTH = 5000
GROUND_Y = 500
TOTAL_QUESTIONS = 10
MAX_LEVEL = 10
BLOCK_SPACING = 450

question_blocks = []
ghost_y_offset = 0

def pick_question_for_step(step):
    level = min(step + 1, MAX_LEVEL)
    pool = get_questions(level)
    used = [b["question"] for b in question_blocks]
    available = [q for q in pool if q[0] not in used]
    if not available:
        available = pool
    return random.choice(available)

def build_game():
    global question_blocks
    question_blocks = []
    x = 400
    for i in range(TOTAL_QUESTIONS):
        q = pick_question_for_step(i)
        level = min(i + 1, MAX_LEVEL)
        question_blocks.append({
            "rect": pygame.Rect(x, 400, 70, 70),
            "question": q[0],
            "answers": q[1],
            "done": False,
            "level": level,
        })
        x += BLOCK_SPACING

build_game()

class Player:
    def __init__(self):
        self.rect = pygame.Rect(80, 400, 52, 100)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump = -16
        self.on_ground = False
        self.facing = 1
        self.walk_frame = 0

    def reset(self):
        self.rect.x = 80
        self.rect.y = 400
        self.vel_x = 0
        self.vel_y = 0

    def update(self, keys, can_move):
        self.vel_x = 0
        if can_move:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vel_x = -self.speed
                self.facing = -1
                self.walk_frame += 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vel_x = self.speed
                self.facing = 1
                self.walk_frame += 1
            if (keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
                self.vel_y = self.jump
        self.vel_y += GRAVITY
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - self.rect.width))

    def stop(self):
        self.vel_x = 0
        self.vel_y = 0

    def draw(self, camera_x, ghost=False, ghost_alpha=255):
        global ghost_y_offset
        x = self.rect.x - camera_x
        y = self.rect.y

        if ghost:
            if trump_img_right:
                img = trump_img_left if self.facing == -1 else trump_img_right
                ghost_surf = img.copy()
                tint = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                tint.fill((180, 180, 255, 120))
                ghost_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                alpha_surf = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                alpha_surf.fill((255, 255, 255, ghost_alpha))
                ghost_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(ghost_surf, (x, y + ghost_y_offset))
            else:
                surf = pygame.Surface((60, 100), pygame.SRCALPHA)
                gc = (*GHOST_COLOR, ghost_alpha)
                pygame.draw.rect(surf, gc, (6, 20, 30, 60))
                pygame.draw.circle(surf, gc, (21, 14), 14)
                ec = (255, 0, 0, ghost_alpha)
                pygame.draw.line(surf, ec, (13, 8), (20, 15), 3)
                pygame.draw.line(surf, ec, (20, 8), (13, 15), 3)
                pygame.draw.line(surf, ec, (27, 8), (34, 15), 3)
                pygame.draw.line(surf, ec, (34, 8), (27, 15), 3)
                screen.blit(surf, (x, y + ghost_y_offset))
        else:
            bob = 0
            if self.vel_x != 0 and self.on_ground:
                bob = 3 if (self.walk_frame // 8) % 2 == 0 else -2

            if trump_img_right:
                img = trump_img_left if self.facing == -1 else trump_img_right
                screen.blit(img, (x, y + bob))
            else:
                pygame.draw.rect(screen, TRUMP_SUIT, (x + 4, y + 24 + bob, 44, 50))
                pygame.draw.rect(screen, TRUMP_TIE, (x + 18, y + 28 + bob, 8, 30))
                pygame.draw.circle(screen, TRUMP_SKIN, (x + 26, y + 14 + bob), 14)
                pygame.draw.ellipse(screen, TRUMP_HAIR, (x + 8, y + bob, 36, 16))

player = Player()

state = "playing"
current_block = None
answer_text = ""
score = 0
message = "A/D eða örvar = labba | W/Space = hoppa"
rage_line1 = ""
rage_line2 = ""
fade_alpha = 0
death_timer = 0

def draw_text(text, f, color, x, y):
    screen.blit(f.render(text, True, color), (x, y))

def draw_text_centered(text, f, color, cy):
    surf = f.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, cy))

def draw_sky():
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * ratio)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * ratio)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def draw_mountains(camera_x):
    mountains_far = [
        (200, 420, 280), (450, 380, 250), (700, 410, 200),
        (900, 390, 230), (1150, 405, 210), (1400, 385, 260),
        (1650, 415, 220), (1900, 395, 240),
    ]
    for mx, my, mw in mountains_far:
        ox = mx - int(camera_x * 0.15)
        ox = ox % (WIDTH + 300) - 150
        pygame.draw.polygon(screen, MOUNTAIN, [
            (ox, GROUND_Y - 10), (ox + mw // 2, my), (ox + mw, GROUND_Y - 10)
        ])
        pygame.draw.polygon(screen, MOUNTAIN_SNOW, [
            (ox + mw // 2, my),
            (ox + mw // 2 - 25, my + 40),
            (ox + mw // 2 + 25, my + 40),
        ])
    mountains_near = [
        (100, 450, 320), (500, 430, 280), (850, 445, 300),
        (1200, 435, 290), (1600, 448, 310),
    ]
    for mx, my, mw in mountains_near:
        ox = mx - int(camera_x * 0.3)
        ox = ox % (WIDTH + 400) - 200
        pygame.draw.polygon(screen, MOUNTAIN_DARK, [
            (ox, GROUND_Y - 5), (ox + mw // 2, my), (ox + mw, GROUND_Y - 5)
        ])

def draw_clouds(camera_x):
    cloud_data = [
        (120, 80, 1.0), (350, 50, 0.8), (600, 90, 1.2),
        (850, 60, 0.9), (1100, 85, 1.1), (1400, 70, 0.7),
        (1700, 55, 1.0), (2000, 80, 0.85),
    ]
    for cx, cy, scale in cloud_data:
        ox = int(cx - camera_x * 0.2) % (WIDTH + 200) - 100
        s = int(scale * 100)
        pygame.draw.ellipse(screen, WHITE, (ox, cy, s, int(s * 0.5)))
        pygame.draw.ellipse(screen, WHITE, (ox + s // 4, cy - int(s * 0.25), int(s * 0.5), int(s * 0.5)))
        pygame.draw.ellipse(screen, WHITE, (ox + s // 2, cy - int(s * 0.15), int(s * 0.4), int(s * 0.4)))
        pygame.draw.ellipse(screen, (210, 230, 255), (ox + 4, cy + 4, s, int(s * 0.4)))

def draw_ground(camera_x):
    pygame.draw.rect(screen, GRASS_TOP, (0, GROUND_Y, WIDTH, 20))
    for i in range(-1, WIDTH // 20 + 2):
        gx = i * 20 - (int(camera_x) % 20)
        pygame.draw.polygon(screen, DARK_GREEN, [
            (gx + 4, GROUND_Y), (gx + 7, GROUND_Y - 8), (gx + 10, GROUND_Y),
        ])
        pygame.draw.polygon(screen, DARK_GREEN, [
            (gx + 11, GROUND_Y), (gx + 14, GROUND_Y - 6), (gx + 17, GROUND_Y),
        ])
    pygame.draw.rect(screen, BROWN, (0, GROUND_Y + 20, WIDTH, HEIGHT - GROUND_Y))
    for i in range(-1, WIDTH // 40 + 2):
        bx = i * 40 - (int(camera_x) % 40)
        pygame.draw.rect(screen, DARK_BROWN, (bx, GROUND_Y + 20, 38, 38), 2)

def draw_pipes(camera_x):
    pipe_positions = [300, 900, 1500, 2100, 2700, 3300, 3900]
    for px in pipe_positions:
        ox = px - int(camera_x)
        if -100 < ox < WIDTH + 100:
            h = random.Random(px).randint(60, 140)
            pygame.draw.rect(screen, PIPE_GREEN, (ox, GROUND_Y - h, 52, h))
            pygame.draw.rect(screen, PIPE_DARK, (ox, GROUND_Y - h, 52, h), 3)
            pygame.draw.rect(screen, PIPE_GREEN, (ox - 5, GROUND_Y - h - 20, 62, 22))
            pygame.draw.rect(screen, PIPE_DARK, (ox - 5, GROUND_Y - h - 20, 62, 22), 3)
            pygame.draw.rect(screen, (80, 200, 80), (ox + 8, GROUND_Y - h + 4, 8, h - 8))

def draw_question_block(rect, camera_x, done, level):
    x = rect.x - camera_x
    y = rect.y
    if done:
        pygame.draw.rect(screen, (50, 200, 80), (x, y, rect.width, rect.height))
        pygame.draw.rect(screen, (30, 140, 50), (x, y, rect.width, rect.height), 4)
        pygame.draw.rect(screen, (80, 230, 100), (x + 3, y + 3, rect.width - 6, 8))
        draw_text("OK", font, WHITE, x + 10, y + 22)
    else:
        colors = [
            (255, 230, 50), (255, 180, 30), (230, 120, 30),
            (210, 60, 30), (180, 30, 180), (120, 0, 200),
            (60, 0, 180), (20, 0, 150), (10, 0, 100), (5, 0, 50),
        ]
        color = colors[min(level - 1, 9)]
        dark = tuple(max(0, c - 60) for c in color)
        light = tuple(min(255, c + 60) for c in color)
        pygame.draw.rect(screen, color, (x, y, rect.width, rect.height))
        pygame.draw.rect(screen, dark, (x, y, rect.width, rect.height), 4)
        pygame.draw.rect(screen, light, (x + 3, y + 3, rect.width - 6, 8))
        txt_color = WHITE if level >= 6 else BLACK
        draw_text(str(level), big_font, txt_color, x + 22, y + 12)

async def main():
    global state, score, answer_text, current_block, message, rage_line1, rage_line2, fade_alpha, death_timer, ghost_y_offset
    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if state == "question":
                    if event.key == pygame.K_RETURN:
                        if correct(answer_text, current_block["answers"]):
                            score += 1
                            message = f"Rétt! {score}/{TOTAL_QUESTIONS}"
                            current_block["done"] = True
                            answer_text = ""
                            state = "playing"
                            player.rect.x += 90
                        else:
                            r = random.choice(RAGE_MESSAGES)
                            rage_line1 = r[0]
                            rage_line2 = r[1]
                            answer_text = ""
                            state = "dying"
                            ghost_y_offset = 0
                            fade_alpha = 0
                            death_timer = 0
                            pygame.mixer.music.stop()
                            if death_sound:
                                death_sound.play()
                    elif event.key == pygame.K_BACKSPACE:
                        answer_text = answer_text[:-1]
                    else:
                        if event.unicode and len(answer_text) < 30:
                            answer_text += event.unicode

                elif state == "winner":
                    if event.key == pygame.K_SPACE:
                        build_game()
                        player.reset()
                        score = 0
                        message = "A/D eða örvar = labba | W/Space = hoppa"
                        state = "playing"
                        start_music()

        # Dying animation
        if state == "dying":
            death_timer += 1
            if death_timer < 80:
                ghost_y_offset -= 3
            elif death_timer < 140:
                fade_alpha = min(255, int((death_timer - 80) / 60 * 255))
            elif death_timer > 190:
                build_game()
                player.reset()
                score = 0
                state = "playing"
                fade_alpha = 0
                ghost_y_offset = 0
                start_music()

        can_move = state == "playing"
        player.update(keys, can_move)

        if state == "playing":
            for block in question_blocks:
                if not block["done"] and player.rect.colliderect(block["rect"]):
                    current_block = block
                    answer_text = ""
                    player.rect.right = block["rect"].left
                    player.stop()
                    state = "question"
            if score >= TOTAL_QUESTIONS:
                state = "winner"

        camera_x = max(0, min(player.rect.x - 250, WORLD_WIDTH - WIDTH))

        # Teikna
        draw_sky()
        draw_mountains(camera_x)
        draw_clouds(camera_x)
        draw_pipes(camera_x)
        draw_ground(camera_x)

        for block in question_blocks:
            if -100 < block["rect"].x - camera_x < WIDTH + 100:
                draw_question_block(block["rect"], camera_x, block["done"], block["level"])

        # Leikmaður
        if state == "dying":
            orig_y = player.rect.y
            player.rect.y = orig_y
            alpha = max(0, 255 - int(death_timer * 2.5))
            player.draw(camera_x, ghost=True, ghost_alpha=alpha)
            player.rect.y = orig_y
        else:
            player.draw(camera_x)

        # HUD
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, 90))
        pygame.draw.rect(screen, GOLD, (0, 88, WIDTH, 3))
        draw_text(f"SPURNING: {score + 1}/{TOTAL_QUESTIONS}", font, WHITE, 30, 15)
        draw_text(f"RÉTT: {score}", font, GOLD, 320, 15)
        draw_text(f"STIG: {min(score + 1, MAX_LEVEL)}", font, (180, 180, 255), 560, 15)
        draw_text(message, small_font,
            GOLD if "Rétt" in message else (200, 200, 200), 30, 55)

        # Spurningagluggi
        if state == "question":
            pygame.draw.rect(screen, (20, 20, 60), (80, 130, 840, 310), border_radius=16)
            pygame.draw.rect(screen, GOLD, (80, 130, 840, 310), 4, border_radius=16)
            pygame.draw.rect(screen, (40, 40, 100), (88, 138, 824, 294), border_radius=12)
            level_colors = [
                (255, 220, 50), (255, 160, 30), (220, 100, 30),
                (200, 50, 30), (180, 30, 180), (120, 0, 200),
                (60, 0, 180), (20, 0, 150), (10, 0, 120), (200, 0, 0),
            ]
            lc = level_colors[min(current_block["level"] - 1, 9)]
            draw_text_centered(
                f"— SPURNING {score + 1}/10  •  STIG {current_block['level']} —",
                font, lc, 150)
            draw_text_centered(current_block["question"], font, WHITE, 220)
            pygame.draw.rect(screen, (10, 10, 40), (200, 285, 600, 55), border_radius=10)
            pygame.draw.rect(screen, GOLD, (200, 285, 600, 55), 2, border_radius=10)
            draw_text("▶", font, GOLD, 215, 298)
            cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            draw_text(answer_text + cursor, font, WHITE, 250, 298)
            draw_text("ENTER = svara  |  BACKSPACE = eyða", small_font,
                (150, 150, 200), 280, 355)

        # Fade to black og Trump rage
        if state == "dying" and death_timer >= 80:
            fade_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, min(255, fade_alpha)))
            screen.blit(fade_surf, (0, 0))

            if death_timer >= 110:
                if trump_rage_img:
                    rx = WIDTH // 2 - trump_rage_img.get_width() // 2
                    ry = HEIGHT // 2 - trump_rage_img.get_height() // 2 - 60
                    screen.blit(trump_rage_img, (rx, ry))
                draw_text_centered(rage_line1, rage_font, RED, HEIGHT // 2 + 130)
                draw_text_centered(rage_line2, font, WHITE, HEIGHT // 2 + 210)
                draw_text_centered("— AFTUR Í BYRJUN —", small_font,
                    (200, 200, 200), HEIGHT // 2 + 250)

        # Sigurvegari
        if state == "winner":
            pygame.draw.rect(screen, (20, 20, 60), (130, 140, 740, 300), border_radius=18)
            pygame.draw.rect(screen, GOLD, (130, 140, 740, 300), 5, border_radius=18)
            draw_text_centered("SIGURVEGARI!", big_font, GOLD, 170)
            draw_text_centered("Þú svaraðir öllum 10 rétt!", font, WHITE, 260)
            draw_text_centered("Hafðu samband við skipuleggjanda!", font, RED, 305)
            draw_text_centered("Even Trump is impressed... maybe.", small_font, (180, 180, 180), 350)
            draw_text_centered("SPACE = reyna aftur", small_font, (150, 150, 200), 390)

        pygame.display.flip()
        await asyncio.sleep(0)  # REQUIRED for pygbag/WebAssembly

if __name__ == "__main__":
    asyncio.run(main())
