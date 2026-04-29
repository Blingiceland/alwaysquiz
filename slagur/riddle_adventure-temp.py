import pygame
import sys
import random
import os
import json
import time
from questions import get_questions

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quiz Walker")
clock = pygame.time.Clock()

FPS = 60
GRAVITY = 0.8

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
PIPE_GREEN = (50, 160, 50)
PIPE_DARK = (30, 100, 30)
TRUMP_SKIN = (255, 185, 100)
TRUMP_HAIR = (255, 210, 50)
TRUMP_SUIT = (30, 50, 100)
TRUMP_TIE = (200, 30, 30)

font = pygame.font.SysFont(None, 38)
big_font = pygame.font.SysFont(None, 68)
small_font = pygame.font.SysFont(None, 28)
rage_font = pygame.font.SysFont(None, 65)
title_font = pygame.font.SysFont(None, 80)
intro_font = pygame.font.SysFont(None, 52)

music_file = r"always.mp3"  # Í rótinni
death_file = r"C:\Users\Lenovo\slagur\death_sound.wav"
SCORES_FILE = "highscores.json"
PICS = "pics"

INTRO_DURATION = 15.0  # Sekúndur sem þarf að hlusta

def load_image(filename, scale=None):
    path = os.path.join(PICS, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except Exception as e:
        print(f"Gat ekki hlaðið mynd: {filename} — {e}")
        return None

trump_img_right = load_image("trump1-bg.png", scale=(80, 155))
trump_img_left = pygame.transform.flip(trump_img_right, True, False) if trump_img_right else None
trump_rage_img = load_image("trumprage.png", scale=(280, 320))
background_img = load_image("bakgrunnur1.png", scale=(WIDTH, HEIGHT))
block_img = load_image("kubbur.png", scale=(70, 70))
ground_tile_img = load_image("jord1.png", scale=(50, 100))

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

def load_scores():
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"winners": [], "best_scores": []}

def save_scores(scores):
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Villa við að vista skor:", e)

def add_score(name, email, correct_count, finish_time=None):
    scores = load_scores()
    entry = {
        "name": name,
        "email": email,
        "date": time.strftime("%d.%m.%Y %H:%M")
    }
    if finish_time is not None:
        entry["time"] = finish_time
        scores["winners"].append(entry)
        scores["winners"].sort(key=lambda x: x["time"])
        scores["winners"] = scores["winners"][:10]
    else:
        entry["score"] = correct_count
        scores["best_scores"].append(entry)
        scores["best_scores"].sort(key=lambda x: x["score"], reverse=True)
        scores["best_scores"] = scores["best_scores"][:10]
    save_scores(scores)

def correct(user, answers):
    return user.strip().lower() == answers[0].strip().lower()

def get_rage_message(player_name):
    name = player_name.upper() if player_name else "LOSER"
    messages = [
        (f"WRONG, {name}! TOTAL DISASTER!", "Nobody fails worse than you, believe me!"),
        (f"FAKE ANSWER, {name}! SAD!", "Back to the beginning, loser!"),
        (f"{name}, YOU'RE FIRED!", "That was the worst answer I've ever seen!"),
        (f"WRONG, {name}! MANY PEOPLE...", "...are saying you're very bad at this!"),
        (f"TOTAL LOSER, {name}!", "Go back to start, okay? Just go back!"),
        (f"WRONG, {name}! DISGRACEFUL!", "I've seen smarter answers from a rock!"),
        (f"NASTY ANSWER, {name}!", "Back to beginning — it's going to be YUGE!"),
        (f"WRONG, {name}! BELIEVE ME!", "I know answers, the best. That wasn't one."),
        (f"TREMENDOUS FAILURE, {name}!", "Nobody fails bigger than you, nobody!"),
    ]
    return random.choice(messages)

def get_timeout_message(player_name):
    name = player_name.upper() if player_name else "LOSER"
    return (f"TOO SLOW, {name}! RIGGED!", "You couldn't even type in time. Sad!")

TIME_TO_START = 6.0
TIME_TO_FINISH = 7.0
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
            "rect": pygame.Rect(x, 345, 70, 70),
            "question": q[0],
            "answers": q[1],
            "done": False,
            "level": level,
        })
        x += BLOCK_SPACING

build_game()

class Player:
    def __init__(self):
        self.rect = pygame.Rect(80, 345, 80, 155)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump = -16
        self.on_ground = False
        self.facing = 1
        self.walk_frame = 0

    def reset(self):
        self.rect.x = 80
        self.rect.y = 345
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
            bob = 0
            if self.vel_x != 0 and self.on_ground:
                bob = 3 if (self.walk_frame // 8) % 2 == 0 else -2
            if trump_img_right:
                img = trump_img_left if self.facing == -1 else trump_img_right
                screen.blit(img, (x, y + bob))
            else:
                pygame.draw.rect(screen, TRUMP_SUIT, (x+6, y+36+bob, 68, 80))
                pygame.draw.circle(screen, TRUMP_SKIN, (x+40, y+22+bob), 22)
                pygame.draw.ellipse(screen, TRUMP_HAIR, (x+12, y+bob, 56, 24))

player = Player()

# Leikur staða
state = "intro"  # intro, name_entry, playing, question, dying, winner, highscores
intro_start_time = 0
player_name = ""
player_email = ""
name_field_active = True
current_block = None
answer_text = ""
score = 0
message = ""
rage_line1 = ""
rage_line2 = ""
fade_alpha = 0
death_timer = 0
death_animation_done = False
question_start_time = 0
typing_start_time = 0
has_started_typing = False
game_start_time = 0
finish_time = 0

# Unicorn particles fyrir intro
particles = []
def spawn_particles():
    for _ in range(3):
        particles.append({
            "x": random.randint(0, WIDTH),
            "y": random.randint(0, HEIGHT),
            "vx": random.uniform(-2, 2),
            "vy": random.uniform(-3, -1),
            "size": random.randint(4, 12),
            "color": random.choice([
                (255, 100, 200), (100, 200, 255), (200, 255, 100),
                (255, 200, 100), (200, 100, 255), (100, 255, 200)
            ]),
            "life": 60
        })

def update_particles():
    global particles
    for p in particles:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
    particles = [p for p in particles if p["life"] > 0]

def draw_particles():
    for p in particles:
        alpha = int(255 * p["life"] / 60)
        surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*p["color"], alpha), (p["size"], p["size"]), p["size"])
        screen.blit(surf, (int(p["x"]-p["size"]), int(p["y"]-p["size"])))

def draw_intro(now):
    """15 sekúndna intro skjár — Robot Unicorn Attack tribute"""
    elapsed = now - intro_start_time
    remaining = max(0.0, INTRO_DURATION - elapsed)
    ratio = elapsed / INTRO_DURATION

    # Bakgrunnur — gradient sem breytist
    r = int(20 + 60 * ratio)
    g = int(10 + 20 * ratio)
    b = int(80 + 100 * ratio)
    screen.fill((r, g, b))

    # Rainbow stripes
    for i in range(7):
        colors = [(255,0,0),(255,127,0),(255,255,0),(0,255,0),(0,0,255),(75,0,130),(148,0,211)]
        stripe_y = int((i / 7) * HEIGHT + (now * 30) % (HEIGHT/7))
        pygame.draw.rect(screen, colors[i], (0, stripe_y % HEIGHT, WIDTH, 8), 2)

    # Particles
    if random.random() < 0.3:
        spawn_particles()
    update_particles()
    draw_particles()

    # Trump andlit — dansandi
    if trump_rage_img:
        dance_bob = int(20 * abs(pygame.math.Vector2(1, 0).rotate(now * 180).y))
        small = pygame.transform.scale(trump_rage_img, (200, 220))
        screen.blit(small, (WIDTH//2 - 100, 30 + dance_bob))

    # ALWAYS texti — stór og glæsilegur
    always_colors = [(255,100,200), (100,200,255), GOLD]
    ac = always_colors[int(now * 2) % 3]
    draw_text_centered("♫ ALWAYS ♫", title_font, ac, 265)
    draw_text_centered("Erasure", font, WHITE, 335)

    # Countdown
    if remaining > 0:
        draw_text_centered(f"Leikurinn byrjar eftir  {remaining:.0f}  sekúndur...", font, WHITE, 390)

        # Progress bar
        bar_w = 600
        bar_x = WIDTH//2 - bar_w//2
        pygame.draw.rect(screen, (50, 30, 80), (bar_x, 430, bar_w, 20), border_radius=10)
        fill_color = [(255,100,200), (100,200,255), GOLD][int(now*3)%3]
        pygame.draw.rect(screen, fill_color,
            (bar_x, 430, int(bar_w * (elapsed/INTRO_DURATION)), 20), border_radius=10)

        draw_text_centered("🦄  Tribute to Robot Unicorn Attack  🦄", small_font, (200,150,255), 465)
    else:
        # Tilbúið!
        if (pygame.time.get_ticks()//400)%2==0:
            draw_text_centered("► SMELLTU HVAR SEM ER TIL AÐ BYRJA ◄", font, GREEN, 410)

def trigger_death(player_name, timeout=False):
    global state, rage_line1, rage_line2, fade_alpha, death_timer
    global death_animation_done, ghost_y_offset, answer_text
    if timeout:
        rage_line1, rage_line2 = get_timeout_message(player_name)
    else:
        r = get_rage_message(player_name)
        rage_line1, rage_line2 = r[0], r[1]
    answer_text = ""
    state = "dying"
    ghost_y_offset = 0
    fade_alpha = 0
    death_timer = 0
    death_animation_done = False
    pygame.mixer.music.stop()
    if death_sound:
        death_sound.play()
    # Byrja lagið aftur
    start_music()

def draw_text(text, f, color, x, y):
    screen.blit(f.render(text, True, color), (x, y))

def draw_text_centered(text, f, color, cy):
    surf = f.render(text, True, color)
    screen.blit(surf, (WIDTH//2 - surf.get_width()//2, cy))

def draw_background(camera_x):
    if background_img:
        bg_offset = int(camera_x * 0.3) % WIDTH
        screen.blit(background_img, (-bg_offset, 0))
        screen.blit(background_img, (WIDTH - bg_offset, 0))
    else:
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            pygame.draw.line(screen, (int(100+80*ratio), int(180+40*ratio), 255), (0, y), (WIDTH, y))

def draw_ground(camera_x):
    if ground_tile_img:
        tile_w = ground_tile_img.get_width()
        ground_h = ground_tile_img.get_height()
        start_x = -(int(camera_x) % tile_w)
        for tx in range(start_x, WIDTH + tile_w, tile_w):
            screen.blit(ground_tile_img, (tx, GROUND_Y))
        pygame.draw.rect(screen, DARK_BROWN,
            (0, GROUND_Y+ground_h, WIDTH, HEIGHT-GROUND_Y-ground_h))
    else:
        pygame.draw.rect(screen, GRASS_TOP, (0, GROUND_Y, WIDTH, 20))
        pygame.draw.rect(screen, BROWN, (0, GROUND_Y+20, WIDTH, HEIGHT-GROUND_Y))

def draw_pipes(camera_x):
    for px in [300, 900, 1500, 2100, 2700, 3300, 3900]:
        ox = px - int(camera_x)
        if -100 < ox < WIDTH + 100:
            h = random.Random(px).randint(60, 140)
            pygame.draw.rect(screen, PIPE_GREEN, (ox, GROUND_Y-h, 52, h))
            pygame.draw.rect(screen, PIPE_DARK, (ox, GROUND_Y-h, 52, h), 3)
            pygame.draw.rect(screen, PIPE_GREEN, (ox-5, GROUND_Y-h-20, 62, 22))
            pygame.draw.rect(screen, PIPE_DARK, (ox-5, GROUND_Y-h-20, 62, 22), 3)

def draw_question_block(rect, camera_x, done, level):
    x = rect.x - camera_x
    y = rect.y
    if done:
        if block_img:
            done_surf = block_img.copy()
            grey = pygame.Surface(block_img.get_size(), pygame.SRCALPHA)
            grey.fill((100, 100, 100, 160))
            done_surf.blit(grey, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(done_surf, (x, y))
        draw_text("OK", font, WHITE, x+10, y+22)
    else:
        if block_img:
            block_surf = block_img.copy()
            level_tints = [
                (255,255,200,0),(255,200,100,80),(255,120,50,120),(255,50,50,150),
                (200,50,255,150),(120,0,255,170),(50,0,200,180),(20,0,150,190),
                (10,0,100,200),(5,0,20,220),
            ]
            tint = pygame.Surface(block_img.get_size(), pygame.SRCALPHA)
            tint.fill(level_tints[min(level-1, 9)])
            block_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(block_surf, (x, y))
        txt_color = WHITE if level >= 6 else BLACK
        draw_text(str(level), big_font, txt_color, x+22, y+12)

BOX_X, BOX_Y, BOX_W, BOX_H = 80, 115, 840, 340

def draw_question_box(now):
    pygame.draw.rect(screen, (20,20,60), (BOX_X,BOX_Y,BOX_W,BOX_H), border_radius=16)
    pygame.draw.rect(screen, GOLD, (BOX_X,BOX_Y,BOX_W,BOX_H), 4, border_radius=16)
    pygame.draw.rect(screen, (40,40,100), (BOX_X+8,BOX_Y+8,BOX_W-16,BOX_H-16), border_radius=12)
    level_colors = [
        (255,220,50),(255,160,30),(220,100,30),(200,50,30),(180,30,180),
        (120,0,200),(60,0,180),(20,0,150),(10,0,120),(200,0,0),
    ]
    lc = level_colors[min(current_block["level"]-1, 9)]
    draw_text_centered(f"— SPURNING {score+1}/10  •  STIG {current_block['level']} —", font, lc, BOX_Y+22)
    q_surf = font.render(current_block["question"], True, WHITE)
    screen.blit(q_surf, (WIDTH//2 - q_surf.get_width()//2, BOX_Y+75))
    input_y = BOX_Y+140
    pygame.draw.rect(screen, (10,10,40), (BOX_X+20,input_y,BOX_W-40,55), border_radius=10)
    pygame.draw.rect(screen, GOLD, (BOX_X+20,input_y,BOX_W-40,55), 2, border_radius=10)
    draw_text("▶", font, GOLD, BOX_X+35, input_y+12)
    cursor = "_" if (pygame.time.get_ticks()//500)%2==0 else ""
    draw_text(answer_text+cursor, font, WHITE, BOX_X+65, input_y+12)
    draw_text("ENTER = svara  |  BACKSPACE = eyða", small_font, (150,150,200), BOX_X+240, input_y+65)
    if not has_started_typing:
        elapsed = now - question_start_time
        remaining = max(0.0, TIME_TO_START - elapsed)
        ratio = remaining / TIME_TO_START
        label = f"Byrjaðu að skrifa:  {remaining:.1f}s"
    else:
        elapsed = now - typing_start_time
        remaining = max(0.0, TIME_TO_FINISH - elapsed)
        ratio = remaining / TIME_TO_FINISH
        label = f"Tími eftir:  {remaining:.1f}s"
    if ratio > 0.5:
        bar_color = txt_color = GREEN
    elif ratio > 0.25:
        bar_color = txt_color = (255, 165, 0)
    else:
        bar_color = txt_color = RED
    draw_text(label, small_font, txt_color, BOX_X+25, BOX_Y+BOX_H-52)
    bar_y = BOX_Y+BOX_H-28
    pygame.draw.rect(screen, (30,30,70), (BOX_X+8,bar_y,BOX_W-16,14), border_radius=7)
    pygame.draw.rect(screen, bar_color, (BOX_X+8,bar_y,int((BOX_W-16)*ratio),14), border_radius=7)

def draw_name_entry():
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill((20, 30, 80))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 20, 160))
    screen.blit(overlay, (0, 0))
    if trump_rage_img:
        small_rage = pygame.transform.scale(trump_rage_img, (160, 180))
        screen.blit(small_rage, (WIDTH//2 - 80, 15))
    draw_text_centered("QUIZ WALKER", title_font, GOLD, 205)
    draw_text_centered("Trump er að bíða eftir þér... 😈", small_font, (255, 150, 150), 278)
    name_border = GOLD if name_field_active else (80, 80, 120)
    pygame.draw.rect(screen, (20,20,60), (200,315,600,58), border_radius=10)
    pygame.draw.rect(screen, name_border, (200,315,600,58), 3, border_radius=10)
    draw_text("👤 Nafn:", small_font, (180,180,255), 215, 320)
    cursor_n = "_" if name_field_active and (pygame.time.get_ticks()//500)%2==0 else ""
    draw_text(player_name + cursor_n, font, WHITE, 330, 322)
    email_border = GOLD if not name_field_active else (80, 80, 120)
    pygame.draw.rect(screen, (20,20,60), (200,385,600,58), border_radius=10)
    pygame.draw.rect(screen, email_border, (200,385,600,58), 3, border_radius=10)
    draw_text("✉ Email:", small_font, (180,180,255), 215, 390)
    cursor_e = "_" if not name_field_active and (pygame.time.get_ticks()//500)%2==0 else ""
    draw_text(player_email + cursor_e, font, WHITE, 330, 392)
    draw_text_centered("TAB = skipta á milli reita", small_font, (120,120,160), 455)
    if player_name.strip() and player_email.strip():
        if (pygame.time.get_ticks()//600)%2==0:
            draw_text_centered("► ENTER TIL AÐ BYRJA ◄", font, GREEN, 490)
    elif player_name.strip():
        draw_text_centered("Skrifaðu email...", small_font, (120,120,160), 493)
    else:
        draw_text_centered("Skrifaðu nafnið þitt...", small_font, (120,120,160), 493)
    draw_text_centered("H = High Score listi", small_font, (150,150,200), 535)

def draw_highscores():
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill((10, 10, 40))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 20, 180))
    screen.blit(overlay, (0, 0))
    draw_text_centered("🏆 HIGH SCORE LISTI 🏆", big_font, GOLD, 20)
    scores = load_scores()
    pygame.draw.rect(screen, (20,20,60), (20,80,470,470), border_radius=12)
    pygame.draw.rect(screen, GOLD, (20,80,470,470), 3, border_radius=12)
    draw_text("  🥇 SIGURVEGARI — BESTUR TÍMI", small_font, GOLD, 30, 90)
    pygame.draw.line(screen, GOLD, (30, 115), (480, 115), 1)
    winners = scores.get("winners", [])
    if winners:
        for i, w in enumerate(winners[:7]):
            mins = int(w["time"])//60
            secs = w["time"]%60
            time_str = f"{mins}:{secs:05.2f}" if mins > 0 else f"{secs:.2f}s"
            medal = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
            color = [GOLD,(192,192,192),(205,127,50)][i] if i < 3 else WHITE
            draw_text(f"{medal} {w['name']}", font, color, 35, 125+i*48)
            draw_text(time_str, small_font, color, 310, 133+i*48)
            draw_text(w.get("email",""), small_font, (120,160,200), 35, 152+i*48)
    else:
        draw_text_centered("Enginn hefur unnið ennþá!", small_font, (150,150,200), 220)
    pygame.draw.rect(screen, (20,20,60), (510,80,470,470), border_radius=12)
    pygame.draw.rect(screen, (150,100,200), (510,80,470,470), 3, border_radius=12)
    draw_text("  📊 FLESTAR RÉTTAR SPURNINGAR", small_font, (200,150,255), 520, 90)
    pygame.draw.line(screen, (150,100,200), (520,115), (970,115), 1)
    best_scores = scores.get("best_scores", [])
    if best_scores:
        for i, s in enumerate(best_scores[:7]):
            color = GOLD if i == 0 else WHITE
            draw_text(f"#{i+1} {s['name']}", font, color, 525, 125+i*48)
            draw_text(f"{s['score']}/10", small_font, color, 830, 133+i*48)
            draw_text(s.get("email",""), small_font, (120,160,200), 525, 152+i*48)
    else:
        draw_text("  Enginn hefur spilað ennþá!", small_font, (150,150,200), 525, 220)
    if (pygame.time.get_ticks()//700)%2==0:
        draw_text_centered("► SPACE = Til baka ◄", font, (150,200,255), 565)

# Byrja tónlist og intro
start_music()
intro_start_time = pygame.time.get_ticks() / 1000.0

while True:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()
    now = pygame.time.get_ticks() / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:

            if state == "intro":
                elapsed = now - intro_start_time
                if elapsed >= INTRO_DURATION:
                    state = "name_entry"

            elif state == "name_entry":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        name_field_active = not name_field_active
                    elif event.key == pygame.K_RETURN:
                        if player_name.strip() and player_email.strip():
                            state = "playing"
                            game_start_time = now
                            build_game()
                            player.reset()
                            score = 0
                    elif event.key == pygame.K_h:
                        state = "highscores"
                    elif event.key == pygame.K_BACKSPACE:
                        if name_field_active:
                            player_name = player_name[:-1]
                        else:
                            player_email = player_email[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            if name_field_active and len(player_name) < 16:
                                player_name += event.unicode
                            elif not name_field_active and len(player_email) < 40:
                                player_email += event.unicode

            elif state == "highscores":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    state = "name_entry"

            elif state == "question":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if answer_text.strip():
                            if correct(answer_text, current_block["answers"]):
                                score += 1
                                message = f"Rétt, {player_name}! {score}/{TOTAL_QUESTIONS}"
                                current_block["done"] = True
                                answer_text = ""
                                state = "playing"
                                player.rect.x += 90
                            else:
                                add_score(player_name, player_email, score)
                                trigger_death(player_name, timeout=False)
                    elif event.key == pygame.K_BACKSPACE:
                        answer_text = answer_text[:-1]
                    else:
                        if event.unicode and len(answer_text) < 30:
                            if not has_started_typing and event.unicode.strip():
                                has_started_typing = True
                                typing_start_time = now
                            answer_text += event.unicode

            elif state == "dying" and death_animation_done:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    build_game()
                    player.reset()
                    score = 0
                    game_start_time = now
                    state = "playing"
                    fade_alpha = 0
                    ghost_y_offset = 0
                    message = ""

            elif state == "winner":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        state = "highscores"
                    elif event.key == pygame.K_r:
                        build_game()
                        player.reset()
                        score = 0
                        game_start_time = now
                        state = "playing"
                        message = ""
                        start_music()

    # Timeout
    if state == "question":
        if not has_started_typing:
            if now - question_start_time >= TIME_TO_START:
                add_score(player_name, player_email, score)
                trigger_death(player_name, timeout=True)
        else:
            if now - typing_start_time >= TIME_TO_FINISH:
                add_score(player_name, player_email, score)
                trigger_death(player_name, timeout=True)

    # Dying animation
    if state == "dying" and not death_animation_done:
        death_timer += 1
        if death_timer < 80:
            ghost_y_offset -= 3
        elif death_timer < 140:
            fade_alpha = min(255, int((death_timer-80)/60*255))
        elif death_timer >= 160:
            death_animation_done = True
            fade_alpha = 255

    can_move = state == "playing"
    player.update(keys, can_move)

    if state == "playing":
        for block in question_blocks:
            if not block["done"] and player.rect.colliderect(block["rect"]):
                current_block = block
                answer_text = ""
                question_start_time = now
                has_started_typing = False
                typing_start_time = 0
                player.rect.right = block["rect"].left
                player.stop()
                state = "question"
        if score >= TOTAL_QUESTIONS:
            finish_time = now - game_start_time
            add_score(player_name, player_email, score, finish_time=finish_time)
            state = "winner"

    camera_x = max(0, min(player.rect.x - 250, WORLD_WIDTH - WIDTH))

    # --- TEIKNA ---
    if state == "intro":
        draw_intro(now)

    elif state == "name_entry":
        draw_name_entry()

    elif state == "highscores":
        draw_highscores()

    else:
        draw_background(camera_x)
        draw_pipes(camera_x)
        draw_ground(camera_x)

        for block in question_blocks:
            if -100 < block["rect"].x - camera_x < WIDTH + 100:
                draw_question_block(block["rect"], camera_x, block["done"], block["level"])

        if state == "dying":
            alpha = max(0, 255 - int(death_timer * 2.5))
            player.draw(camera_x, ghost=True, ghost_alpha=alpha)
        else:
            player.draw(camera_x)

        # HUD
        pygame.draw.rect(screen, (40,40,40), (0,0,WIDTH,90))
        pygame.draw.rect(screen, GOLD, (0,88,WIDTH,3))
        draw_text(f"SPURNING: {score+1}/{TOTAL_QUESTIONS}", font, WHITE, 30, 15)
        draw_text(f"RÉTT: {score}", font, GOLD, 300, 15)
        draw_text(f"STIG: {min(score+1,MAX_LEVEL)}", font, (180,180,255), 490, 15)
        elapsed_game = now - game_start_time
        mins = int(elapsed_game)//60
        secs = elapsed_game%60
        time_str = f"{mins}:{secs:05.2f}" if mins > 0 else f"{secs:.2f}s"
        draw_text(f"⏱ {time_str}", font, WHITE, 700, 15)
        draw_text(f"👤 {player_name}", font, (180,220,255), 30, 55)
        if message:
            draw_text(message, small_font,
                GOLD if "Rétt" in message else (200,200,200), 280, 58)

        if state == "question":
            draw_question_box(now)

        # Fade og Trump rage
        if state == "dying" and death_timer >= 80:
            fade_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, min(255, fade_alpha)))
            screen.blit(fade_surf, (0, 0))
            if death_timer >= 110:
                if trump_rage_img:
                    rx = WIDTH//2 - trump_rage_img.get_width()//2
                    screen.blit(trump_rage_img, (rx, 10))
                draw_text_centered(rage_line1, rage_font, RED, 345)
                draw_text_centered(rage_line2, font, WHITE, 420)
                if death_animation_done:
                    if (pygame.time.get_ticks()//600)%2==0:
                        draw_text_centered("► ÝTTU Á SPACE TIL AÐ REYNA AFTUR ◄",
                            font, GOLD, 490)

        # Sigurvegari
        if state == "winner":
            pygame.draw.rect(screen, (10,10,40), (100,100,800,380), border_radius=18)
            pygame.draw.rect(screen, GOLD, (100,100,800,380), 5, border_radius=18)
            draw_text_centered("🏆 SIGURVEGARI! 🏆", big_font, GOLD, 130)
            draw_text_centered(f"{player_name} — ÓTRÚLEGT!", font, WHITE, 215)
            mins = int(finish_time)//60
            secs = finish_time%60
            time_str = f"{mins}:{secs:05.2f}" if mins > 0 else f"{secs:.2f} sekúndur"
            draw_text_centered(f"Tíminn þinn: {time_str}", font, GOLD, 265)
            draw_text_centered("Hafðu samband við skipuleggjanda!", font, RED, 320)
            draw_text_centered("Even Trump is impressed... maybe.", small_font, (180,180,180), 365)
            draw_text_centered("SPACE = Sjá high score  |  R = Reyna aftur",
                small_font, (150,200,255), 435)

    pygame.display.flip()
