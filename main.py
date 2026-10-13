import os

os.environ['SDL_WINDOWS_DPI_AWARENESS'] = 'permonitorv2'

import pygame
import sys
import random
import json


pygame.mixer.init()
pygame.init()

try:
    BUTTON_SFX = pygame.mixer.Sound("assets/buttonsound.mp3")
    BUTTON_SFX.set_volume(0.6)
except pygame.error:
    BUTTON_SFX = None
WIDTH, HEIGHT = 1280, 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))

FPS = 60
WHITE = (255, 255, 255)
BLACK = (10, 10, 20)
GREEN = (0, 255, 100)
RED = (255, 50, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 200, 0)
GOLD = (255, 215, 0)

pygame.display.set_caption("Galactic Defender: Boss Rush")
font = pygame.font.Font("assets/Bytesized-Regular.ttf", 32)
small_font = pygame.font.Font("assets/Bytesized-Regular.ttf", 26)
mini_font = pygame.font.Font("assets/Bytesized-Regular.ttf", 20)


class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, font_type=None):
        if font_type is None:
            font_type = font
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font_type = font_type

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        text_surf = self.font_type.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                if BUTTON_SFX:
                    BUTTON_SFX.play()
                return True
        return False

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.choice([1, 2, 3])
        self.speed = self.size * 0.8
        color_val = 100 + (self.size * 50)
        self.color = (color_val, color_val, color_val)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class FloatingReward(pygame.sprite.Sprite):
    def __init__(self, x, y, amount, icon):
        super().__init__()
        self.amount = amount
        text_surf = font.render(f"+{amount}", True, GOLD)
        self.image = pygame.Surface((text_surf.get_width() + 45, 40), pygame.SRCALPHA)
        self.image.blit(text_surf, (0, 5))
        self.image.blit(icon, (text_surf.get_width() + 5, 0))

        self.rect = self.image.get_rect(center=(x, y))
        self.target_x = 60
        self.target_y = 15
        self.reached_target = False

    def update(self):
        dx = self.target_x - self.rect.x
        dy = self.target_y - self.rect.y
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist < 15:
            self.reached_target = True
        else:
            self.rect.x += dx * 0.05
            self.rect.y += dy * 0.05


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.colors = [WHITE, YELLOW, (255, 150, 0), RED, (100, 100, 100), (50, 50, 50)]
        self.sizes = [10, 20, 35, 45, 50, 55]

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 40:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.sizes):
                self.kill()
            else:
                self.image.fill((0, 0, 0, 0))
                pygame.draw.circle(self.image, self.colors[self.frame], (50, 50), self.sizes[self.frame])
                for _ in range(5):
                    ox = random.randint(-30, 30)
                    oy = random.randint(-30, 30)
                    pygame.draw.circle(self.image, self.colors[self.frame], (50 + ox, 50 + oy), random.randint(3, 10))


class Phantom(pygame.sprite.Sprite):
    def __init__(self, image, center):
        super().__init__()
        self.image = image.copy()
        self.rect = self.image.get_rect(center=center)
        self.alpha = 80
        self.image.set_alpha(self.alpha)

    def update(self):
        self.alpha -= 5
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)


class SuperLaser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((160, 800), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y - 400))
        self.speed = -35
        self.has_hit_boss = False

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

        self.image.fill((0, 0, 0, 0))
        now = pygame.time.get_ticks()

        w1 = 100 + int(abs((now % 100) - 50) / 50 * 40)
        w2 = 60 + int(abs((now % 80) - 40) / 40 * 30)
        w3 = 20 + int(abs((now % 60) - 30) / 30 * 20)

        pygame.draw.ellipse(self.image, (255, 50, 0, 180), (80 - w1 // 2, 0, w1, 800))
        pygame.draw.ellipse(self.image, (255, 200, 0, 220), (80 - w2 // 2, 0, w2, 800))
        pygame.draw.ellipse(self.image, WHITE, (80 - w3 // 2, 0, w3, 800))


class Player(pygame.sprite.Sprite):
    def __init__(self, skin_image, game_upgrades, all_sprites_group, skin_index, game_instance):
        super().__init__()
        self.game = game_instance
        self.image = pygame.transform.scale(skin_image, (80, 80))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        self.skin_index = skin_index

        self.speed = 11 if skin_index == 1 else 7
        bonus_hp = 1 if skin_index == 2 else 0
        bonus_dmg = 5 if skin_index == 3 else 0
        bonus_fire = 1 if skin_index == 2 else 0

        self.upgrades = game_upgrades
        self.all_sprites = all_sprites_group
        self.can_shoot = True

        self.max_hp = 1 + self.upgrades["hp"] + bonus_hp
        self.hp = self.max_hp
        self.damage = 5 + (self.upgrades["damage"] * 5) + bonus_dmg

        fire_level = min(5, self.upgrades["fire_rate"] + bonus_fire)
        delay_map = {1: 700, 2: 550, 3: 400, 4: 250, 5: 250, 6: 150}
        self.shoot_delay = delay_map.get(fire_level, 250)
        self.last_shot = pygame.time.get_ticks()

        self.lasers = pygame.sprite.Group()
        self.super_lasers = pygame.sprite.Group()
        self.super_charge = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > HEIGHT // 2:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and self.can_shoot:
            self.last_shot = now
            self.shoot()

    def shoot(self):
        if self.upgrades["fire_rate"] == 5 or (self.skin_index == 2 and self.upgrades["fire_rate"] >= 4):
            laser1 = Laser(self.rect.centerx - 15, self.rect.top, self.skin_index)
            laser2 = Laser(self.rect.centerx + 15, self.rect.top, self.skin_index)
            self.lasers.add(laser1, laser2)
            self.all_sprites.add(laser1, laser2)
        else:
            laser = Laser(self.rect.centerx, self.rect.top, self.skin_index)
            self.lasers.add(laser)
            self.all_sprites.add(laser)

        if self.game.sfx_laser:
            self.game.sfx_laser.play()

    def activate_super(self):
        if self.skin_index == 3 and self.super_charge >= 100:
            self.super_charge = 0
            sl = SuperLaser(self.rect.centerx, self.rect.top)
            self.super_lasers.add(sl)
            self.all_sprites.add(sl)

            if self.game.sfx_super:
                self.game.sfx_super.play()


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, skin_index):
        super().__init__()
        self.image = pygame.Surface((14, 30), pygame.SRCALPHA)

        if skin_index == 0:
            pygame.draw.rect(self.image, YELLOW, (5, 5, 4, 20), border_radius=2)
        elif skin_index == 1:
            pygame.draw.ellipse(self.image, (100, 200, 255), (0, 5, 14, 20))
            pygame.draw.ellipse(self.image, WHITE, (4, 8, 6, 14))
        elif skin_index == 2:
            pygame.draw.circle(self.image, GREEN, (7, 15), 7)
            pygame.draw.circle(self.image, WHITE, (7, 15), 3)
        elif skin_index == 3:
            pygame.draw.rect(self.image, RED, (3, 0, 8, 30), border_radius=4)
            pygame.draw.rect(self.image, (255, 150, 150), (5, 5, 4, 20), border_radius=2)

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -25

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (150, 50, 255), (0, 0, 16, 24))
        pygame.draw.ellipse(self.image, (220, 150, 255), (4, 4, 8, 16))
        pygame.draw.ellipse(self.image, WHITE, (6, 8, 4, 8))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 800:
            self.kill()


class BossLaser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((24, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, RED, (0, 0, 24, 40))
        pygame.draw.ellipse(self.image, (255, 150, 0), (4, 6, 16, 28))
        pygame.draw.ellipse(self.image, WHITE, (8, 12, 8, 16))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 800:
            self.kill()


class Diamond(pygame.sprite.Sprite):
    def __init__(self, x, y, d_type, images_dict):
        super().__init__()
        self.type = d_type

        values = {"d3": 1, "d6": 2, "d4": 5, "d2": 10, "d7": 20, "d1": 50}
        self.value = values[d_type]

        self.base_image = images_dict[d_type].copy()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed

        if self.type == "d1":
            now = pygame.time.get_ticks()
            size = 30 + int(abs((now % 800) - 400) / 400 * 15)
            self.image = pygame.transform.scale(self.base_image, (size, size))
            self.rect = self.image.get_rect(center=self.rect.center)

        if self.rect.top > 800:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, difficulty):
        super().__init__()
        self.enemy_type = random.choice(["meteor", "nlo"])

        hp_boost = {"EASY": 0, "NORMAL": 10, "HARD": 20}[difficulty]
        shoot_mod = {"EASY": 1.0, "NORMAL": 0.7, "HARD": 0.4}[difficulty]

        if self.enemy_type == "meteor":
            meteor_img = pygame.image.load("assets/meteor.png").convert_alpha()
            self.image = pygame.transform.scale(meteor_img, (60, 60))
            self.max_hp = 20 + hp_boost
            self.hp = self.max_hp
            self.score_value = 1
        else:
            ufo_img = pygame.image.load("assets/ufo.png").convert_alpha()
            self.image = pygame.transform.scale(ufo_img, (60, 60))
            self.max_hp = 40 + hp_boost
            self.hp = self.max_hp
            self.score_value = 2

            base_delay = random.randint(1500, 3000)
            self.shoot_delay = int(base_delay * shoot_mod)
            self.last_shot = pygame.time.get_ticks()

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 800:
            self.kill()

    def draw_health_bar(self, surface):
        if self.hp > 0:
            bar_width = self.rect.width
            bar_height = 5
            x = self.rect.left
            y = self.rect.top - 10
            health_ratio = max(0, self.hp / self.max_hp)
            current_health_width = int(bar_width * health_ratio)
            pygame.draw.rect(surface, (200, 50, 50), (x, y, bar_width, bar_height))
            pygame.draw.rect(surface, (50, 200, 50), (x, y, current_health_width, bar_height))


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, target_y, difficulty):
        super().__init__()
        self.base_frames = []
        for i in range(1, 10):
            try:
                img = pygame.image.load(f"assets/boss_{i}.png").convert_alpha()
                img.set_colorkey((0, 0, 0))
                scaled_img = pygame.transform.scale(img, (250, 250))
                self.base_frames.append(scaled_img)
            except:
                pass

        if not self.base_frames:
            surf = pygame.Surface((250, 250))
            surf.fill(RED)
            self.base_frames.append(surf)

        self.enraged_frames = []
        for frame in self.base_frames:
            enlarged = pygame.transform.scale(frame, (320, 320))
            self.enraged_frames.append(enlarged)

        self.frames = self.base_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.animation_timer = pygame.time.get_ticks()
        self.frame_rate = 100

        self.rect = self.image.get_rect(center=(x, -250))
        self.target_y = target_y

        self.difficulty = difficulty
        self.state = "ENTERING"
        self.attack_state = "SHOOTING"
        self.phase = 1
        self.is_transitioning = False
        self.transition_start = 0

        self.max_hp = {"EASY": 600, "NORMAL": 1000, "HARD": 1500}[difficulty]
        self.hp = self.max_hp
        self.speed_x = {"EASY": 5, "NORMAL": 8, "HARD": 12}[difficulty]

        self.shoot_delay = {"EASY": 700, "NORMAL": 500, "HARD": 300}[difficulty]
        self.last_shot = pygame.time.get_ticks()
        self.warning_timer = 0

    def update(self):
        now = pygame.time.get_ticks()

        if self.is_transitioning:
            if now - self.transition_start < 2000:
                if (now // 100) % 2 == 0:
                    self.image.set_alpha(50)
                else:
                    self.image.set_alpha(255)
                return
            else:
                self.is_transitioning = False
                self.phase = 2
                self.frames = self.enraged_frames
                self.image = self.frames[self.current_frame]
                center = self.rect.center
                self.rect = self.image.get_rect(center=center)
                self.speed_x = int(self.speed_x * 1.5)

        if now - self.animation_timer > self.frame_rate:
            self.animation_timer = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

        if self.state == "ENTERING":
            if self.rect.centery < self.target_y:
                self.rect.y += 2
            else:
                self.state = "FIGHTING"

        elif self.state == "FIGHTING":
            if self.difficulty == "HARD" and self.hp <= self.max_hp // 2 and self.phase == 1 and not self.is_transitioning:
                self.is_transitioning = True
                self.transition_start = pygame.time.get_ticks()

            if self.attack_state == "SHOOTING":
                self.rect.x += self.speed_x
                if self.rect.right > WIDTH or self.rect.left < 0:
                    self.speed_x *= -1

                if self.phase == 2 and random.randint(1, 100) == 1:
                    self.attack_state = "WARNING"
                    self.warning_timer = pygame.time.get_ticks()

            elif self.attack_state == "WARNING":
                if pygame.time.get_ticks() - self.warning_timer > 800:
                    self.attack_state = "BITING"

            elif self.attack_state == "BITING":
                self.rect.y += 25
                if self.rect.bottom >= HEIGHT:
                    self.attack_state = "RETURNING"

            elif self.attack_state == "RETURNING":
                self.rect.y -= 5
                if self.rect.centery <= self.target_y:
                    self.attack_state = "SHOOTING"

        elif self.state == "DEFEATED":
            self.rect.y += 8

    def draw_health_bar(self, surface):
        if self.state == "DEFEATED":
            return

        bar_width = 600
        bar_height = 25
        x = (WIDTH // 2) - (bar_width // 2)
        y = 20
        health_ratio = max(0, self.hp / self.max_hp)
        current_width = int((bar_width - 8) * health_ratio)

        pygame.draw.rect(surface, (40, 40, 50), (x - 6, y - 6, bar_width + 12, bar_height + 12), border_radius=5)

        pygame.draw.rect(surface, (20, 20, 25), (x, y, bar_width, bar_height))

        if self.phase == 2:
            bar_color = (255, 100, 0) if (pygame.time.get_ticks() // 200) % 2 == 0 else (255, 0, 0)
        else:
            bar_color = (200, 0, 0)

        if current_width > 0:
            pygame.draw.rect(surface, bar_color, (x + 4, y + 4, current_width, bar_height - 8))

            segment_width = 40
            for i in range(x + 4 + segment_width, x + 4 + current_width, segment_width):
                pygame.draw.line(surface, (20, 20, 25), (i, y + 4), (i, y + bar_height - 5), 3)

        pygame.draw.rect(surface, (100, 100, 120), (x, y, bar_width, bar_height), 2)


class Game:
    def __init__(self):
        self.state = "AUTH"
        self.previous_state = "MENU"
        self.clock = pygame.time.Clock()
        self.stars = [Star() for _ in range(150)]
        self.is_fullscreen = False

        pygame.mixer.init()
        pygame.mixer.set_num_channels(32)

        self.music_on = True
        self.change_music("background_music.mp3")

        try:
            self.sfx_laser = pygame.mixer.Sound("assets/laserbulletsound.mp3")
            self.sfx_laser.set_volume(0.5)
        except pygame.error:
            self.sfx_laser = None

        try:
            self.sfx_super = pygame.mixer.Sound("assets/superlasersound.mp3")
            self.sfx_super.set_volume(0.8)
        except pygame.error:
            self.sfx_super = None

        try:
            self.sfx_win = pygame.mixer.Sound("assets/winsound.mp3")
            self.sfx_win.set_volume(0.8)
        except pygame.error:
            self.sfx_win = None

        try:
            self.sfx_lose = pygame.mixer.Sound("assets/loosesound.mp3")
            self.sfx_lose.set_volume(0.8)
        except pygame.error:
            self.sfx_lose = None

        self.end_sound_played = False

        self.username_text = ""
        self.password_text = ""
        self.active_input = "username"
        self.auth_msg = ""
        self.logged_in_user = None
        self.show_password = False
        self.eye_rect = pygame.Rect(895, 390, 40, 40)

        self.users_db = {}
        self.load_users_db()

        self.score = 0
        self.money = 0
        self.upgrades = {"fire_rate": 1, "damage": 1, "hp": 1}
        self.current_skin_index = 0
        self.unlocked_skins = [0]
        self.skin_costs = [0, 150, 300, 600]

        self.difficulty = "EASY"
        self.boss_transitioning = False
        self.boss_transition_timer = 0
        self.boss_defeated = False
        self.pause_start = 0

        self.upgrade_costs = {1: 10, 2: 25, 3: 50, 4: 100, 5: "MAX"}

        self.boss_lasers = pygame.sprite.Group()
        self.enemy_lasers = pygame.sprite.Group()
        self.diamonds_group = pygame.sprite.Group()
        self.floating_rewards = pygame.sprite.Group()

        self.skins = [
            pygame.image.load("assets/ship_1.png").convert_alpha(),
            pygame.image.load("assets/ship_2.png").convert_alpha(),
            pygame.image.load("assets/ship_3.png").convert_alpha(),
            pygame.image.load("assets/ship_4.png").convert_alpha()
        ]

        self.d_imgs = {
            "d1": pygame.transform.scale(pygame.image.load("assets/d1.png").convert_alpha(), (30, 30)),
            "d2": pygame.transform.scale(pygame.image.load("assets/d2.png").convert_alpha(), (30, 30)),
            "d3": pygame.transform.scale(pygame.image.load("assets/d3.png").convert_alpha(), (30, 30)),
            "d4": pygame.transform.scale(pygame.image.load("assets/d4.png").convert_alpha(), (30, 30)),
            "d6": pygame.transform.scale(pygame.image.load("assets/d6.png").convert_alpha(), (30, 30)),
            "d7": pygame.transform.scale(pygame.image.load("assets/d7.png").convert_alpha(), (30, 30))
        }
        self.icon_diamond = pygame.transform.scale(pygame.image.load("assets/diamond.png").convert_alpha(), (40, 40))

        self.pause_rect = pygame.Rect(WIDTH - 70, 20, 50, 50)

        self.texts = {
            "EN": {
                "title": "GALACTIC DEFENDER", "start": "Start Game", "skins": "Skins", "upgrades": "Upgrades",
                "options": "Options", "logout": "Logout", "lang_btn": "Language: English",
                "display_win": "Mode: Windowed", "display_full": "Mode: Fullscreen", "back": "Back",
                "score": "Score:", "equip": "Equip", "equipped": "Equipped", "boss_incoming": "BOSS INCOMING!",
                "easy": "Easy", "normal": "Normal", "hard": "Hard", "select_diff": "Select Difficulty",
                "game_over": "GAME OVER", "victory": "VICTORY!", "restart": "Restart", "main_menu": "Main Menu",
                "fire_rate": "Fire Rate", "damage": "Damage", "hp": "Health", "cost": "Cost:", "max": "MAX",
                "login": "Login", "register": "Register", "go_register": "Create Account",
                "back_login": "Back to Login", "resume": "Resume", "quit": "Quit Game", "buy": "Buy",
                "info_btn": "INFO", "super_btn": "SUPER [F]",
                "details_title": "SHIP SCHEMATICS", "click_close": "Click outside to close",
                "skin_name_0": "VANGUARD", "skin_name_1": "PHANTOM", "skin_name_2": "IRONCLAD",
                "skin_name_3": "ASTEROID DESTROYER",
                "skin_info_0": "Old Reliable", "skin_info_1": "Hyper-Agile",
                "skin_info_2": "Heavy Tank", "skin_info_3": "Lethal Weapon",
                "skin_stat_0": ["VANGUARD CLASS", "A balanced, reliable fighter.", "Pure skill. No crutches."],
                "skin_stat_1": ["PHANTOM CLASS", "Lightweight chassis.", "Maximum speed overdrive."],
                "skin_stat_2": ["IRONCLAD CLASS", "Reinforced armor plating.", "+1 HP & faster fire rate."],
                "skin_stat_3": ["ASTEROID DESTROYER", "Classified military tech.", "+5 DMG & SUPER LASER."],
                "music_on": "Music: ON", "music_off": "Music: OFF"
            },
            "LT": {
                "title": "GALAKTIKOS GYNĖJAS", "start": "Pradėti Žaidimą", "skins": "Skinai",
                "upgrades": "Tobulinimai", "options": "Nustatymai", "logout": "Atsijungti",
                "lang_btn": "Kalba: Lietuvių", "display_win": "Režimas: Lange",
                "display_full": "Režimas: Visas ekranas", "back": "Atgal", "score": "Taškai:",
                "equip": "Pasirinkti", "equipped": "Pasirinkta", "boss_incoming": "BOSAS ARTĖJA!",
                "easy": "Lengvas", "normal": "Vidutinis", "hard": "Sunkus", "select_diff": "Pasirinkti Sunkumą",
                "game_over": "ŽAIDIMO PABAIGA", "victory": "PERGALĖ!", "restart": "Iš naujo",
                "main_menu": "Pagrindinis Meniu", "fire_rate": "Šaudymo Greitis", "damage": "Žala",
                "hp": "Gyvybės", "cost": "Kaina:", "max": "MAX", "login": "Prisijungti", "register": "Registruotis",
                "go_register": "Sukurti Paskyrą", "back_login": "Atgal", "resume": "Tęsti", "quit": "Išeiti",
                "buy": "Pirkti", "info_btn": "APRAŠYMAS", "super_btn": "SUPER [F]",
                "details_title": "LAIVO BRĖŽINIAI", "click_close": "Spauskite šone, kad uždaryti",
                "skin_name_0": "AVANGARDAS", "skin_name_1": "FANTOMAS", "skin_name_2": "ŠARVUOTIS",
                "skin_name_3": "ASTEROIDŲ NAIKINTOJAS",
                "skin_info_0": "Patikimas", "skin_info_1": "Hiper-Vikrus",
                "skin_info_2": "Sunkusis Tankas", "skin_info_3": "Mirtinas Ginklas",
                "skin_stat_0": ["AVANGARDO KLASĖ", "Subalansuotas naikintuvas.", "Jokių palengvinimų."],
                "skin_stat_1": ["FANTOMO KLASĖ", "Lengvas korpusas.", "Maksimalus greitis."],
                "skin_stat_2": ["ŠARVUOČIO KLASĖ", "Sustiprinti šarvai.", "+1 Gyvybė ir greitas šaudymas."],
                "skin_stat_3": ["ASTEROIDŲ NAIKINTOJAS", "Įslaptinta technologija.", "+5 Žala & SUPER LAZERIS."],
                "music_on": "Muzika: ĮJUNGTA", "music_off": "Muzika: IŠJUNGTA"
            }
        }
        self.lang = "EN"

        b_w, b_h = 250, 60
        x_pos = WIDTH // 2 - b_w // 2

        self.btn_auth_login = Button(self.texts[self.lang]["login"], x_pos, 490, b_w, b_h, (30, 80, 40), (60, 150, 80))
        self.btn_go_reg = Button(self.texts[self.lang]["go_register"], x_pos, 560, b_w, b_h, (30, 40, 80),
                                 (60, 100, 150))
        self.btn_reg_confirm = Button(self.texts[self.lang]["register"], x_pos, 490, b_w, b_h, (30, 80, 40),
                                      (60, 150, 80))
        self.btn_back_login = Button(self.texts[self.lang]["back_login"], x_pos, 560, b_w, b_h, (100, 50, 50),
                                     (150, 80, 80))
        self.btn_auth_exit = Button(self.texts[self.lang]["quit"], x_pos, 630, b_w, b_h, (150, 40, 40), (200, 50, 50))

        self.btn_start = Button(self.texts[self.lang]["start"], x_pos, 220, b_w, b_h, (30, 40, 60), (60, 100, 200))
        self.btn_upgrades = Button(self.texts[self.lang]["upgrades"], x_pos, 290, b_w, b_h, (30, 40, 60),
                                   (60, 100, 200))
        self.btn_skins = Button(self.texts[self.lang]["skins"], x_pos, 360, b_w, b_h, (30, 40, 60), (60, 100, 200))
        self.btn_options = Button(self.texts[self.lang]["options"], x_pos, 430, b_w, b_h, (30, 40, 60), (60, 100, 200))
        self.btn_logout = Button(self.texts[self.lang]["logout"], x_pos, 500, b_w, b_h, (150, 100, 40), (200, 150, 60))
        self.btn_exit = Button(self.texts[self.lang]["quit"], x_pos, 570, b_w, b_h, (150, 40, 40), (200, 50, 50))

        self.btn_music = Button(self.texts[self.lang]["music_on"], x_pos, 250, b_w, b_h, (40, 100, 60), (60, 150, 80),
                                mini_font)
        self.btn_lang = Button(self.texts[self.lang]["lang_btn"], x_pos, 330, b_w, b_h, (40, 100, 60), (60, 150, 80),
                               mini_font)
        self.btn_fullscreen = Button(self.texts[self.lang]["display_win"], x_pos, 410, b_w, b_h, (40, 100, 60),
                                     (60, 150, 80), mini_font)
        self.btn_back = Button(self.texts[self.lang]["back"], x_pos, 490, b_w, b_h, (100, 50, 50), (150, 80, 80),
                               mini_font)

        self.btn_easy = Button(self.texts[self.lang]["easy"], x_pos, 250, b_w, b_h, (40, 100, 60), (60, 150, 80))
        self.btn_normal = Button(self.texts[self.lang]["normal"], x_pos, 330, b_w, b_h, (100, 100, 40), (150, 150, 60))
        self.btn_hard = Button(self.texts[self.lang]["hard"], x_pos, 410, b_w, b_h, (100, 40, 40), (150, 60, 60))
        self.btn_back_diff = Button(self.texts[self.lang]["back"], x_pos, 490, b_w, b_h, (100, 50, 50), (150, 80, 80),
                                    mini_font)

        self.btn_back_skins = Button(self.texts[self.lang]["back"], x_pos, 550, b_w, b_h, (100, 50, 50), (150, 80, 80),
                                     mini_font)
        self.btn_back_upgrades = Button(self.texts[self.lang]["back"], x_pos, 600, b_w, b_h, (100, 50, 50),
                                        (150, 80, 80), mini_font)

        self.btn_restart = Button(self.texts[self.lang]["restart"], x_pos, 250, b_w, b_h, (30, 80, 40), (60, 150, 80))
        self.btn_go_skins = Button(self.texts[self.lang]["skins"], x_pos, 330, b_w, b_h, (30, 40, 60), (60, 100, 200))
        self.btn_main_menu = Button(self.texts[self.lang]["main_menu"], x_pos, 410, b_w, b_h, (100, 50, 50),
                                    (150, 80, 80))

        self.btn_resume = Button(self.texts[self.lang]["resume"], x_pos, 250, b_w, b_h, (30, 80, 40), (60, 150, 80))
        self.btn_pause_options = Button(self.texts[self.lang]["options"], x_pos, 330, b_w, b_h, (30, 40, 60),
                                        (60, 100, 200))
        self.btn_pause_restart = Button(self.texts[self.lang]["restart"], x_pos, 410, b_w, b_h, (100, 100, 40),
                                        (150, 150, 60))
        self.btn_pause_menu = Button(self.texts[self.lang]["main_menu"], x_pos, 490, b_w, b_h, (100, 50, 50),
                                     (150, 80, 80))

        self.equip_buttons = []
        self.info_buttons = []
        spacing = WIDTH // 5
        for i in range(4):
            equip_btn = Button(self.texts[self.lang]["equip"], spacing * (i + 1) - 60, 400, 120, 40, (40, 100, 60),
                               (60, 150, 80), mini_font)
            info_btn = Button(self.texts[self.lang]["info_btn"], spacing * (i + 1) - 60, 350, 120, 40, (30, 40, 50),
                              (60, 100, 150), mini_font)
            self.equip_buttons.append(equip_btn)
            self.info_buttons.append(info_btn)

        self.active_info_index = -1

        self.upg_btns = {
            "fire_rate": Button("+", 800, 200, 50, 40, (40, 100, 60), (60, 150, 80), mini_font),
            "damage": Button("+", 800, 300, 50, 40, (40, 100, 60), (60, 150, 80), mini_font),
            "hp": Button("+", 800, 400, 50, 40, (40, 100, 60), (60, 150, 80), mini_font)
        }

        self.setup_level()

    def change_music(self, ingame):
        try:
            pygame.mixer.music.load(f"assets/{ingame}")
            pygame.mixer.music.set_volume(5)
            if self.music_on:
                pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def load_users_db(self):
        self.save_file = "save_data.json"
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    self.users_db = json.load(f)
            except:
                self.users_db = {}
        else:
            self.users_db = {}

    def save_users_db(self):
        if self.logged_in_user:
            self.users_db[self.logged_in_user] = {
                "password": self.users_db[self.logged_in_user]["password"],
                "money": self.money,
                "upgrades": self.upgrades,
                "skin": self.current_skin_index,
                "unlocked_skins": self.unlocked_skins
            }
        with open(self.save_file, "w") as f:
            json.dump(self.users_db, f)

    def load_active_user(self):
        data = self.users_db[self.logged_in_user]
        self.money = data.get("money", 0)
        self.upgrades = data.get("upgrades", {"fire_rate": 1, "damage": 1, "hp": 1})
        self.current_skin_index = data.get("skin", 0)
        self.unlocked_skins = data.get("unlocked_skins", [0])

    def toggle_fullscreen(self):
        global screen
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.update_language()

    def setup_level(self):
        self.boss_transitioning = False
        self.boss_transition_timer = 0
        self.boss_defeated = False
        self.end_sound_played = False

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.boss_lasers.empty()
        self.enemy_lasers.empty()
        self.diamonds_group.empty()
        self.floating_rewards.empty()

        self.player = Player(self.skins[self.current_skin_index], self.upgrades, self.all_sprites,
                             self.current_skin_index, self)
        self.all_sprites.add(self.player)
        self.player.can_shoot = True

        self.boss = None
        self.score = 0

    def spawn_enemies(self):
        target_score = {"EASY": 20, "NORMAL": 40, "HARD": 55}[self.difficulty]
        max_enemies = {"EASY": 6, "NORMAL": 8, "HARD": 10}[self.difficulty]

        if self.score < target_score:
            if len(self.enemies) < max_enemies:
                new_enemy = Enemy(random.randint(50, WIDTH - 50), -50, self.difficulty)
                self.enemies.add(new_enemy)
                self.all_sprites.add(new_enemy)
        elif self.score >= target_score and self.boss is None and not self.boss_transitioning and not self.boss_defeated:
            self.boss_transitioning = True
            self.boss_transition_timer = pygame.time.get_ticks()
            self.player.can_shoot = False
            for e in self.enemies:
                explosion = Explosion(e.rect.center)
                self.all_sprites.add(explosion)
                e.kill()
            for laser in self.enemy_lasers:
                laser.kill()

    def spawn_diamond(self, x, y, source):
        drop = None
        chance = random.randint(1, 100)

        if self.difficulty == "EASY":
            if source == "meteor" and chance <= 30:
                drop = "d3"
            elif source == "nlo" and chance <= 50:
                drop = random.choice(["d6", "d4"])

        elif self.difficulty == "NORMAL":
            if source == "meteor" and chance <= 35:
                drop = random.choice(["d6", "d4"])
            elif source == "nlo" and chance <= 55:
                drop = random.choice(["d2", "d7"])

        elif self.difficulty == "HARD":
            if source == "meteor" and chance <= 40:
                drop = random.choice(["d2", "d7"])
            elif source == "nlo":
                if chance <= 60:
                    if random.randint(1, 100) <= 20:
                        drop = "d1"
                    else:
                        drop = random.choice(["d2", "d7"])

        if drop:
            diamond = Diamond(x, y, drop, self.d_imgs)
            self.diamonds_group.add(diamond)
            self.all_sprites.add(diamond)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_users_db()
                pygame.quit()
                sys.exit()

            if self.state in ["AUTH", "REGISTER"]:
                mouse_pos = pygame.mouse.get_pos()
                self.btn_auth_exit.check_hover(mouse_pos)

                if self.state == "AUTH":
                    self.btn_auth_login.check_hover(mouse_pos)
                    self.btn_go_reg.check_hover(mouse_pos)
                else:
                    self.btn_reg_confirm.check_hover(mouse_pos)
                    self.btn_back_login.check_hover(mouse_pos)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if 400 <= mouse_pos[0] <= 880 and 250 <= mouse_pos[1] <= 310:
                        self.active_input = "username"
                    elif 400 <= mouse_pos[0] <= 880 and 380 <= mouse_pos[1] <= 440:
                        self.active_input = "password"
                    elif self.eye_rect.collidepoint(mouse_pos):
                        self.show_password = not self.show_password

                if self.btn_auth_exit.is_clicked(event):
                    self.save_users_db()
                    pygame.quit()
                    sys.exit()

                if self.state == "AUTH":
                    if self.btn_auth_login.is_clicked(event):
                        if self.username_text in self.users_db and self.users_db[self.username_text][
                            "password"] == self.password_text:
                            self.logged_in_user = self.username_text
                            self.load_active_user()
                            self.change_music("background_music.mp3")
                            self.state = "MENU"
                        else:
                            self.auth_msg = "Wrong Username/Password!"
                    if self.btn_go_reg.is_clicked(event):
                        self.state = "REGISTER"
                        self.username_text = ""
                        self.password_text = ""
                        self.auth_msg = ""
                        self.active_input = "username"
                        self.show_password = False

                elif self.state == "REGISTER":
                    if self.btn_reg_confirm.is_clicked(event):
                        if len(self.username_text) < 3 or len(self.password_text) < 3:
                            self.auth_msg = "Min 3 chars required!"
                        elif self.username_text in self.users_db:
                            self.auth_msg = "Username taken!"
                        else:
                            self.users_db[self.username_text] = {
                                "password": self.password_text,
                                "money": 0,
                                "upgrades": {"fire_rate": 1, "damage": 1, "hp": 1},
                                "skin": 0,
                                "unlocked_skins": [0]
                            }
                            self.save_users_db()
                            self.auth_msg = "Account created! Please Login."
                            self.state = "AUTH"
                            self.username_text = ""
                            self.password_text = ""
                            self.active_input = "username"
                            self.show_password = False

                    if self.btn_back_login.is_clicked(event):
                        self.state = "AUTH"
                        self.username_text = ""
                        self.password_text = ""
                        self.auth_msg = ""
                        self.active_input = "username"
                        self.show_password = False

                if event.type == pygame.KEYDOWN:
                    self.auth_msg = "" if "created" not in self.auth_msg else self.auth_msg
                    if event.key == pygame.K_BACKSPACE:
                        if self.active_input == "username":
                            self.username_text = self.username_text[:-1]
                        else:
                            self.password_text = self.password_text[:-1]
                    elif event.key == pygame.K_TAB:
                        self.active_input = "password" if self.active_input == "username" else "username"
                    else:
                        char = event.unicode
                        if char.isprintable() and len(
                                self.username_text if self.active_input == "username" else self.password_text) < 15:
                            if self.active_input == "username":
                                self.username_text += char
                            else:
                                self.password_text += char

            elif self.state == "MENU":
                mouse_pos = pygame.mouse.get_pos()
                self.btn_start.check_hover(mouse_pos)
                self.btn_upgrades.check_hover(mouse_pos)
                self.btn_skins.check_hover(mouse_pos)
                self.btn_options.check_hover(mouse_pos)
                self.btn_logout.check_hover(mouse_pos)
                self.btn_exit.check_hover(mouse_pos)

                if self.btn_start.is_clicked(event):
                    self.state = "DIFFICULTY"
                if self.btn_upgrades.is_clicked(event):
                    self.state = "UPGRADES"
                if self.btn_skins.is_clicked(event):
                    self.previous_state = "MENU"
                    self.state = "SKINS"
                if self.btn_options.is_clicked(event):
                    self.previous_state = "MENU"
                    self.state = "OPTIONS"
                if self.btn_logout.is_clicked(event):
                    self.save_users_db()
                    self.logged_in_user = None
                    self.username_text = ""
                    self.password_text = ""
                    self.show_password = False
                    self.money = 0
                    self.score = 0
                    self.upgrades = {"fire_rate": 1, "damage": 1, "hp": 1}
                    self.current_skin_index = 0
                    self.unlocked_skins = [0]

                    self.state = "AUTH"
                if self.btn_exit.is_clicked(event):
                    self.save_users_db()
                    pygame.quit()
                    sys.exit()

            elif self.state == "DIFFICULTY":
                mouse_pos = pygame.mouse.get_pos()
                self.btn_easy.check_hover(mouse_pos)
                self.btn_normal.check_hover(mouse_pos)
                self.btn_hard.check_hover(mouse_pos)
                self.btn_back_diff.check_hover(mouse_pos)

                if self.btn_easy.is_clicked(event):
                    self.difficulty = "EASY"
                    self.setup_level()
                    self.change_music("ingame.mp3")
                    self.state = "PLAYING"
                if self.btn_normal.is_clicked(event):
                    self.difficulty = "NORMAL"
                    self.setup_level()
                    self.change_music("ingame.mp3")
                    self.state = "PLAYING"
                if self.btn_hard.is_clicked(event):
                    self.difficulty = "HARD"
                    self.setup_level()
                    self.change_music("ingame.mp3")
                    self.state = "PLAYING"
                if self.btn_back_diff.is_clicked(event):
                    self.state = "MENU"

            elif self.state == "UPGRADES":
                mouse_pos = pygame.mouse.get_pos()
                self.btn_back_upgrades.check_hover(mouse_pos)
                for key, btn in self.upg_btns.items():
                    btn.check_hover(mouse_pos)
                    if btn.is_clicked(event):
                        level = self.upgrades[key]
                        if level < 5:
                            cost = self.upgrade_costs[level]
                            if self.money >= cost:
                                self.money -= cost
                                self.upgrades[key] += 1
                                self.save_users_db()

                if self.btn_back_upgrades.is_clicked(event):
                    self.state = "MENU"

            elif self.state in ["GAME_OVER", "VICTORY"]:
                mouse_pos = pygame.mouse.get_pos()
                self.btn_restart.check_hover(mouse_pos)
                self.btn_go_skins.check_hover(mouse_pos)
                self.btn_main_menu.check_hover(mouse_pos)

                if self.btn_restart.is_clicked(event):
                    self.setup_level()
                    self.change_music("ingame.mp3")
                    self.state = "PLAYING"
                if self.btn_go_skins.is_clicked(event):
                    self.previous_state = self.state
                    self.state = "SKINS"
                if self.btn_main_menu.is_clicked(event):
                    self.change_music("background_music.mp3")
                    self.state = "MENU"

            elif self.state == "SKINS":
                mouse_pos = pygame.mouse.get_pos()
                self.btn_back_skins.check_hover(mouse_pos)
                for btn in self.equip_buttons:
                    btn.check_hover(mouse_pos)
                for btn in self.info_buttons:
                    btn.check_hover(mouse_pos)

                if self.btn_back_skins.is_clicked(event):
                    self.state = self.previous_state

                info_clicked_now = False
                for i, btn in enumerate(self.info_buttons):
                    if btn.is_clicked(event):
                        self.active_info_index = i
                        info_clicked_now = True

                for i, btn in enumerate(self.equip_buttons):
                    if btn.is_clicked(event):
                        if i in self.unlocked_skins:
                            self.current_skin_index = i
                            self.save_users_db()
                        else:
                            if self.money >= self.skin_costs[i]:
                                self.money -= self.skin_costs[i]
                                self.unlocked_skins.append(i)
                                self.current_skin_index = i
                                self.save_users_db()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.active_info_index != -1 and not info_clicked_now:
                        if not pygame.Rect(400, 150, 480, 250).collidepoint(mouse_pos):
                            self.active_info_index = -1

            elif self.state == "OPTIONS":
                mouse_pos = pygame.mouse.get_pos()
                self.btn_music.check_hover(mouse_pos)
                self.btn_lang.check_hover(mouse_pos)
                self.btn_fullscreen.check_hover(mouse_pos)
                self.btn_back.check_hover(mouse_pos)

                if self.btn_music.is_clicked(event):
                    self.music_on = not self.music_on
                    if self.music_on:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()
                    self.update_language()
                if self.btn_lang.is_clicked(event):
                    self.lang = "LT" if self.lang == "EN" else "EN"
                    self.update_language()
                if self.btn_fullscreen.is_clicked(event):
                    self.toggle_fullscreen()
                if self.btn_back.is_clicked(event):
                    self.state = self.previous_state

            elif self.state == "PLAYING":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.pause_rect.collidepoint(event.pos):
                        self.pause_start = pygame.time.get_ticks()
                        self.state = "PAUSED"
                    elif self.player.skin_index == 3:
                        if WIDTH - 180 <= event.pos[0] <= WIDTH - 20 and HEIGHT - 80 <= event.pos[1] <= HEIGHT - 30:
                            self.player.activate_super()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause_start = pygame.time.get_ticks()
                        self.state = "PAUSED"
                    elif event.key == pygame.K_f:
                        self.player.activate_super()

            elif self.state == "PAUSED":
                mouse_pos = pygame.mouse.get_pos()
                self.btn_resume.check_hover(mouse_pos)
                self.btn_pause_options.check_hover(mouse_pos)
                self.btn_pause_restart.check_hover(mouse_pos)
                self.btn_pause_menu.check_hover(mouse_pos)

                if self.btn_resume.is_clicked(event):
                    pause_duration = pygame.time.get_ticks() - self.pause_start
                    self.player.last_shot += pause_duration
                    for e in self.enemies:
                        if hasattr(e, 'last_shot'):
                            e.last_shot += pause_duration
                    if self.boss:
                        self.boss.last_shot += pause_duration
                    if self.boss_transitioning:
                        self.boss_transition_timer += pause_duration
                    self.state = "PLAYING"
                if self.btn_pause_options.is_clicked(event):
                    self.previous_state = "PAUSED"
                    self.state = "OPTIONS"
                if self.btn_pause_restart.is_clicked(event):
                    self.setup_level()
                    self.change_music("ingame.mp3")
                    self.state = "PLAYING"
                if self.btn_pause_menu.is_clicked(event):
                    self.change_music("background_music.mp3")
                    self.state = "MENU"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pause_duration = pygame.time.get_ticks() - self.pause_start
                        self.player.last_shot += pause_duration
                        for e in self.enemies:
                            if hasattr(e, 'last_shot'):
                                e.last_shot += pause_duration
                        if self.boss:
                            self.boss.last_shot += pause_duration
                        if self.boss_transitioning:
                            self.boss_transition_timer += pause_duration
                        self.state = "PLAYING"

    def update(self):
        for star in self.stars:
            star.update()

        if self.state == "PLAYING":
            self.all_sprites.update()
            self.spawn_enemies()

            if self.boss_transitioning:
                if pygame.time.get_ticks() - self.boss_transition_timer > 3000:
                    self.boss = Boss(WIDTH // 2, 150, self.difficulty)
                    self.all_sprites.add(self.boss)
                    self.boss_transitioning = False
                    self.player.can_shoot = True

            if self.boss and self.boss.phase == 2 and not self.boss.is_transitioning and self.boss.state == "FIGHTING":
                if random.random() < 0.4:
                    phantom = Phantom(self.boss.image, self.boss.rect.center)
                    self.all_sprites.add(phantom)

            hits = pygame.sprite.groupcollide(self.enemies, self.player.lasers, False, True)
            for enemy, hit_lasers in hits.items():
                enemy.hp -= self.player.damage
                if enemy.hp <= 0:
                    if self.player.skin_index == 3:
                        self.player.super_charge = min(100, self.player.super_charge + 15)
                    self.spawn_diamond(enemy.rect.centerx, enemy.rect.centery, enemy.enemy_type)
                    explosion = Explosion(enemy.rect.center)
                    self.all_sprites.add(explosion)
                    enemy.kill()
                    self.score += enemy.score_value

            super_hits = pygame.sprite.groupcollide(self.enemies, self.player.super_lasers, False, False)
            for enemy, hit_lasers in super_hits.items():
                self.spawn_diamond(enemy.rect.centerx, enemy.rect.centery, enemy.enemy_type)
                explosion = Explosion(enemy.rect.center)
                self.all_sprites.add(explosion)
                enemy.kill()
                self.score += enemy.score_value

            now = pygame.time.get_ticks()
            for enemy in self.enemies:
                if enemy.enemy_type == "nlo":
                    if now - enemy.last_shot > enemy.shoot_delay:
                        enemy.last_shot = now
                        laser = EnemyLaser(enemy.rect.centerx, enemy.rect.bottom)
                        self.enemy_lasers.add(laser)
                        self.all_sprites.add(laser)

                        if self.sfx_laser:
                            self.sfx_laser.play()

            hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, True)
            for hit in hit_enemies:
                explosion = Explosion(hit.rect.center)
                self.all_sprites.add(explosion)
                self.player.hp -= 1
                if self.player.hp <= 0:
                    self.state = "GAME_OVER"

            hit_by_enemy_laser = pygame.sprite.spritecollide(self.player, self.enemy_lasers, True)
            for hit in hit_by_enemy_laser:
                explosion = Explosion(self.player.rect.center)
                self.all_sprites.add(explosion)
                self.player.hp -= 1
                if self.player.hp <= 0:
                    self.state = "GAME_OVER"

            diamond_hits = pygame.sprite.spritecollide(self.player, self.diamonds_group, True)
            for diamond in diamond_hits:
                self.money += diamond.value
                self.save_users_db()

            if self.boss:
                if self.boss.hp <= 0 and self.boss.state != "DEFEATED":
                    self.boss.state = "DEFEATED"
                    self.boss_defeated = True
                    self.player.can_shoot = False
                    for laser in self.boss_lasers:
                        laser.kill()

                    for _ in range(5):
                        ex_x = self.boss.rect.centerx + random.randint(-80, 80)
                        ex_y = self.boss.rect.centery + random.randint(-80, 80)
                        explosion = Explosion((ex_x, ex_y))
                        self.all_sprites.add(explosion)

                    reward_amt = {"EASY": 25, "NORMAL": 50, "HARD": 80}[self.difficulty]
                    reward = FloatingReward(self.boss.rect.centerx, self.boss.rect.centery, reward_amt,
                                            self.icon_diamond)
                    self.floating_rewards.add(reward)
                    self.all_sprites.add(reward)

                if self.boss.state == "DEFEATED" and self.boss.rect.top > HEIGHT:
                    self.boss.kill()
                    self.boss = None

            for reward in self.floating_rewards:
                if reward.reached_target:
                    self.money += reward.amount
                    self.save_users_db()
                    reward.kill()

            if self.boss_defeated and self.boss is None and len(self.floating_rewards) == 0:
                self.state = "VICTORY"

            if self.boss and self.boss.state != "DEFEATED":
                if pygame.sprite.collide_rect(self.player, self.boss):
                    self.player.hp = 0
                    self.state = "GAME_OVER"

                if self.boss.state != "ENTERING":
                    boss_hits = pygame.sprite.spritecollide(self.boss, self.player.lasers, True)
                    for hit in boss_hits:
                        if not self.boss.is_transitioning:
                            self.boss.hp -= self.player.damage
                            if self.player.skin_index == 3:
                                self.player.super_charge = min(100, self.player.super_charge + 5)

                    super_boss_hits = pygame.sprite.spritecollide(self.boss, self.player.super_lasers, False)
                    for hit in super_boss_hits:
                        if not hit.has_hit_boss and not self.boss.is_transitioning:
                            self.boss.hp -= 300
                            hit.has_hit_boss = True

                if self.boss.attack_state == "SHOOTING" and not self.boss.is_transitioning:
                    if self.boss.state == "FIGHTING" and now - self.boss.last_shot > self.boss.shoot_delay:
                        self.boss.last_shot = now

                        if self.boss.phase == 1:
                            laser = BossLaser(self.boss.rect.centerx, self.boss.rect.bottom)
                            self.boss_lasers.add(laser)
                            self.all_sprites.add(laser)
                        else:
                            laser1 = BossLaser(self.boss.rect.centerx - 50, self.boss.rect.bottom)
                            laser2 = BossLaser(self.boss.rect.centerx + 50, self.boss.rect.bottom)
                            self.boss_lasers.add(laser1, laser2)
                            self.all_sprites.add(laser1, laser2)

                        if self.sfx_laser:
                            self.sfx_laser.play()

            hit_by_boss = pygame.sprite.spritecollide(self.player, self.boss_lasers, True)
            for hit in hit_by_boss:
                explosion = Explosion(self.player.rect.center)
                self.all_sprites.add(explosion)
                self.player.hp -= 1
                if self.player.hp <= 0:
                    self.state = "GAME_OVER"

        if self.state in ["GAME_OVER", "VICTORY"] and not self.end_sound_played:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
            if self.state == "GAME_OVER" and self.sfx_lose:
                self.sfx_lose.play()
            elif self.state == "VICTORY" and self.sfx_win:
                self.sfx_win.play()
            self.end_sound_played = True

    def draw(self):
        screen.fill(BLACK)
        for star in self.stars:
            star.draw(screen)

        current_title_text = self.texts[self.lang]["title"]
        title_font = pygame.font.Font("assets/Jersey15-Regular.ttf", 100)

        if self.state not in ["AUTH", "REGISTER"]:
            screen.blit(self.icon_diamond, (10, 10))
            money_text = font.render(str(self.money), True, WHITE)
            screen.blit(money_text, (60, 15))

        if self.state in ["AUTH", "REGISTER"]:
            title_str = "LOGIN" if self.state == "AUTH" else "CREATE ACCOUNT"
            title = title_font.render(title_str, True, (200, 200, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

            user_label = font.render("Username:", True, WHITE)
            screen.blit(user_label, (400, 210))
            user_color = GREEN if self.active_input == "username" else (100, 100, 100)
            pygame.draw.rect(screen, user_color, (400, 250, 480, 60), 3)
            user_surf = font.render(self.username_text, True, WHITE)
            screen.blit(user_surf, (415, 265))

            pass_label = font.render("Password:", True, WHITE)
            screen.blit(pass_label, (400, 340))
            pass_color = GREEN if self.active_input == "password" else (100, 100, 100)
            pygame.draw.rect(screen, pass_color, (400, 380, 480, 60), 3)

            display_pass = self.password_text if self.show_password else "*" * len(self.password_text)
            pass_surf = font.render(display_pass, True, WHITE)
            screen.blit(pass_surf, (415, 395))

            eye_hover = self.eye_rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (60, 100, 150) if eye_hover else (40, 60, 80), self.eye_rect, border_radius=8)
            ex, ey = self.eye_rect.x, self.eye_rect.y
            pygame.draw.ellipse(screen, WHITE, (ex + 6, ey + 12, 28, 16), 2)
            pygame.draw.circle(screen, WHITE, (ex + 20, ey + 20), 4)
            if not self.show_password:
                pygame.draw.line(screen, RED, (ex + 6, ey + 6), (ex + 34, ey + 34), 3)

            if self.auth_msg:
                msg_color = GREEN if "created" in self.auth_msg else RED
                msg_surf = font.render(self.auth_msg, True, msg_color)
                screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, 460))

            if self.state == "AUTH":
                self.btn_auth_login.draw(screen)
                self.btn_go_reg.draw(screen)
            else:
                self.btn_reg_confirm.draw(screen)
                self.btn_back_login.draw(screen)

            self.btn_auth_exit.draw(screen)

        elif self.state == "MENU":
            title_shadow = title_font.render(current_title_text, True, (50, 0, 100))
            screen.blit(title_shadow, (WIDTH // 2 - title_shadow.get_width() // 2 + 4, 84))
            title = title_font.render(current_title_text, True, (200, 200, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

            self.btn_start.draw(screen)
            self.btn_upgrades.draw(screen)
            self.btn_skins.draw(screen)
            self.btn_options.draw(screen)
            self.btn_logout.draw(screen)
            self.btn_exit.draw(screen)

        elif self.state == "DIFFICULTY":
            header_text = self.texts[self.lang]["select_diff"].upper()
            header = title_font.render(header_text, True, (200, 200, 255))
            screen.blit(header, (WIDTH // 2 - header.get_width() // 2, 60))

            self.btn_easy.draw(screen)
            self.btn_normal.draw(screen)
            self.btn_hard.draw(screen)
            self.btn_back_diff.draw(screen)

        elif self.state == "UPGRADES":
            header_text = self.texts[self.lang]["upgrades"].upper()
            header = title_font.render(header_text, True, (200, 200, 255))
            screen.blit(header, (WIDTH // 2 - header.get_width() // 2, 60))

            y_pos = 200
            for key in ["fire_rate", "damage", "hp"]:
                label = font.render(self.texts[self.lang][key] + ":", True, WHITE)
                screen.blit(label, (300, y_pos))

                level = self.upgrades[key]
                for i in range(5):
                    box_rect = pygame.Rect(550 + (i * 40), y_pos + 5, 30, 30)
                    pygame.draw.rect(screen, (100, 100, 100), box_rect, 2)
                    if i < level:
                        pygame.draw.rect(screen, GREEN, box_rect.inflate(-4, -4))

                cost_txt = self.texts[self.lang]["cost"]
                if level < 5:
                    cost_str = f"{cost_txt} {self.upgrade_costs[level]}"
                    c_color = WHITE if self.money >= self.upgrade_costs[level] else RED
                else:
                    cost_str = self.texts[self.lang]["max"]
                    c_color = GOLD
                cost_surface = font.render(cost_str, True, c_color)
                screen.blit(cost_surface, (870, y_pos))

                if level < 5:
                    self.upg_btns[key].draw(screen)

                y_pos += 100

            self.btn_back_upgrades.draw(screen)

        elif self.state in ["GAME_OVER", "VICTORY"]:
            title_str = self.texts[self.lang]["game_over"] if self.state == "GAME_OVER" else self.texts[self.lang][
                "victory"]
            color = RED if self.state == "GAME_OVER" else GREEN

            header_shadow = title_font.render(title_str, True, (50, 0, 0) if self.state == "GAME_OVER" else (0, 50, 0))
            screen.blit(header_shadow, (WIDTH // 2 - header_shadow.get_width() // 2 + 4, 64))
            header = title_font.render(title_str, True, color)
            screen.blit(header, (WIDTH // 2 - header.get_width() // 2, 60))

            score_word = self.texts[self.lang]["score"]
            score_text = font.render(f"{score_word} {self.score}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 160))

            self.btn_restart.draw(screen)
            self.btn_go_skins.draw(screen)
            self.btn_main_menu.draw(screen)

        elif self.state == "SKINS":
            header_text = self.texts[self.lang]["skins"].upper()
            header = title_font.render(header_text, True, (200, 200, 255))
            screen.blit(header, (WIDTH // 2 - header.get_width() // 2, 30))

            spacing = WIDTH // 5
            ship_colors = [
                (100, 200, 255),
                (180, 100, 255),
                (150, 255, 100),
                (255, 80, 0)
            ]

            for i, skin_img in enumerate(self.skins):
                x = spacing * (i + 1)

                name_key = f"skin_name_{i}"
                name_str = self.texts[self.lang][name_key]

                shadow = small_font.render(name_str, True, (20, 20, 20))
                screen.blit(shadow, (x - shadow.get_width() // 2 + 3, 133))

                name_surf = small_font.render(name_str, True, ship_colors[i])
                screen.blit(name_surf, (x - name_surf.get_width() // 2, 130))

                frame_rect = pygame.Rect(0, 0, 140, 140)
                frame_rect.center = (x, 240)
                frame_color = GOLD if self.current_skin_index == i else (80, 80, 85)
                pygame.draw.rect(screen, frame_color, frame_rect, 4, border_radius=12)

                scaled_skin = pygame.transform.scale(skin_img, (110, 110))

                img_offset_x = -3 if i == 3 else 0

                skin_rect = scaled_skin.get_rect(center=(x + img_offset_x, 240))
                screen.blit(scaled_skin, skin_rect)

                info_text_key = f"skin_info_{i}"
                info_surf = mini_font.render(self.texts[self.lang][info_text_key], True, (180, 180, 180))
                screen.blit(info_surf, (x - info_surf.get_width() // 2, 330))

                self.info_buttons[i].rect.centerx = x
                self.info_buttons[i].rect.y = 370
                self.info_buttons[i].text = self.texts[self.lang]["info_btn"]
                self.info_buttons[i].draw(screen)

                self.equip_buttons[i].rect.centerx = x
                self.equip_buttons[i].rect.y = 420

                if i in self.unlocked_skins:
                    if self.current_skin_index == i:
                        self.equip_buttons[i].text = self.texts[self.lang]["equipped"]
                        self.equip_buttons[i].color = (80, 80, 80)
                    else:
                        self.equip_buttons[i].text = self.texts[self.lang]["equip"]
                        self.equip_buttons[i].color = (40, 100, 60)
                else:
                    cost = self.skin_costs[i]
                    self.equip_buttons[i].text = f"{self.texts[self.lang]['buy']}: {cost}"
                    self.equip_buttons[i].color = (180, 120, 0) if self.money >= cost else (120, 40, 40)

                self.equip_buttons[i].draw(screen)

            if self.active_info_index != -1:
                info_rect = pygame.Rect(400, 150, 480, 250)
                pygame.draw.rect(screen, (30, 40, 50), info_rect, border_radius=10)
                pygame.draw.rect(screen, GOLD, info_rect, 4, border_radius=10)

                info_text = font.render(self.texts[self.lang]["details_title"], True, WHITE)
                screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 170))

                stat_key = f"skin_stat_{self.active_info_index}"
                for j, line in enumerate(self.texts[self.lang][stat_key]):
                    line_surf = mini_font.render(line, True, WHITE)
                    screen.blit(line_surf, (430, 225 + j * 30))

                lbl = mini_font.render(self.texts[self.lang]["click_close"], True, (150, 150, 150))
                screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, 360))

            self.btn_back_skins.draw(screen)

        elif self.state == "OPTIONS":
            header_text = self.texts[self.lang]["options"].upper()
            header = title_font.render(header_text, True, (200, 200, 255))
            screen.blit(header, (WIDTH // 2 - header.get_width() // 2, 60))

            self.btn_music.draw(screen)
            self.btn_lang.draw(screen)
            self.btn_fullscreen.draw(screen)
            self.btn_back.draw(screen)

        elif self.state in ["PLAYING", "PAUSED"]:
            if self.boss and self.boss.attack_state == "WARNING" and self.boss.state != "DEFEATED":
                warning_surface = pygame.Surface((250, HEIGHT), pygame.SRCALPHA)
                warning_surface.fill((255, 0, 0, 100))
                screen.blit(warning_surface, (self.boss.rect.x, self.boss.rect.bottom))

            now = pygame.time.get_ticks()
            if self.player.skin_index == 3 and self.player.super_charge >= 100 and self.state == "PLAYING":
                for _ in range(3):
                    px = self.player.rect.centerx + random.randint(-40, 40)
                    py = self.player.rect.centery + random.randint(-40, 40)
                    pygame.draw.circle(screen, YELLOW, (px, py), random.randint(1, 4))
                if (now // 150) % 2 == 0:
                    screen.blit(self.icon_diamond, (self.player.rect.centerx - 20, self.player.rect.centery - 20))

            self.all_sprites.draw(screen)

            for enemy in self.enemies:
                enemy.draw_health_bar(screen)

            if self.boss_transitioning:
                warning_msg = self.texts[self.lang]["boss_incoming"]
                warning_text = title_font.render(warning_msg, True, RED)
                text_rect = warning_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(warning_text, text_rect)

            if self.boss:
                self.boss.draw_health_bar(screen)

            score_word = self.texts[self.lang]["score"]
            score_text = small_font.render(f"{score_word} {self.score}", True, WHITE)
            screen.blit(score_text, (10, 60))

            if self.player.hp > 0:
                bar_w = 80
                bar_h = 8
                fill_w = max(0, (self.player.hp / self.player.max_hp) * bar_w)

                bar_x = self.player.rect.centerx - bar_w // 2
                bar_y = self.player.rect.bottom + 12

                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, fill_w, bar_h))
                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 1)

            if self.player.skin_index == 3:
                bg_rect = pygame.Rect(WIDTH - 200, HEIGHT - 130, 190, 110)
                pygame.draw.rect(screen, (30, 40, 50), bg_rect, border_radius=10)
                pygame.draw.rect(screen, (100, 100, 120), bg_rect, 4, border_radius=10)

                pygame.draw.rect(screen, (20, 20, 25), (WIDTH - 180, HEIGHT - 110, 160, 20), border_radius=5)
                charge_w = int(160 * (self.player.super_charge / 100))
                if charge_w > 0:
                    bar_color = YELLOW if self.player.super_charge >= 100 else (200, 100, 0)
                    pygame.draw.rect(screen, bar_color, (WIDTH - 180, HEIGHT - 110, charge_w, 20), border_radius=5)

                segment_width = 16
                for i in range(WIDTH - 180 + segment_width, WIDTH - 180 + 160, segment_width):
                    pygame.draw.line(screen, (30, 40, 50), (i, HEIGHT - 110), (i, HEIGHT - 91), 2)

                is_ready = self.player.super_charge >= 100
                btn_color = (255, 100, 0) if is_ready else (100, 50, 0)
                btn_border = GOLD if is_ready else btn_color
                pygame.draw.rect(screen, btn_color, (WIDTH - 180, HEIGHT - 80, 160, 50), border_radius=8)
                pygame.draw.rect(screen, btn_border, (WIDTH - 180, HEIGHT - 80, 160, 50), 4, border_radius=8)

                lbl = mini_font.render(self.texts[self.lang]["super_btn"], True, WHITE)
                screen.blit(lbl, (WIDTH - 150, HEIGHT - 65))

            pygame.draw.rect(screen, (200, 200, 200), self.pause_rect, border_radius=5)
            pygame.draw.rect(screen, (50, 50, 50), (WIDTH - 58, 30, 8, 30))
            pygame.draw.rect(screen, (50, 50, 50), (WIDTH - 40, 30, 8, 30))

            if self.state == "PAUSED":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))

                self.btn_resume.draw(screen)
                self.btn_pause_options.draw(screen)
                self.btn_pause_restart.draw(screen)
                self.btn_pause_menu.draw(screen)

        pygame.display.flip()

    def update_language(self):
        self.btn_auth_exit.text = self.texts[self.lang]["quit"]
        self.btn_auth_login.text = self.texts[self.lang]["login"]
        self.btn_go_reg.text = self.texts[self.lang]["go_register"]
        self.btn_reg_confirm.text = self.texts[self.lang]["register"]
        self.btn_back_login.text = self.texts[self.lang]["back_login"]
        self.btn_start.text = self.texts[self.lang]["start"]
        self.btn_upgrades.text = self.texts[self.lang]["upgrades"]
        self.btn_skins.text = self.texts[self.lang]["skins"]
        self.btn_options.text = self.texts[self.lang]["options"]
        self.btn_logout.text = self.texts[self.lang]["logout"]
        self.btn_exit.text = self.texts[self.lang]["quit"]
        self.btn_lang.text = self.texts[self.lang]["lang_btn"]
        self.btn_back.text = self.texts[self.lang]["back"]
        self.btn_back_skins.text = self.texts[self.lang]["back"]
        self.btn_back_diff.text = self.texts[self.lang]["back"]
        self.btn_back_upgrades.text = self.texts[self.lang]["back"]
        self.btn_easy.text = self.texts[self.lang]["easy"]
        self.btn_normal.text = self.texts[self.lang]["normal"]
        self.btn_hard.text = self.texts[self.lang]["hard"]
        self.btn_restart.text = self.texts[self.lang]["restart"]
        self.btn_go_skins.text = self.texts[self.lang]["skins"]
        self.btn_main_menu.text = self.texts[self.lang]["main_menu"]
        self.btn_resume.text = self.texts[self.lang]["resume"]
        self.btn_pause_options.text = self.texts[self.lang]["options"]
        self.btn_pause_restart.text = self.texts[self.lang]["restart"]
        self.btn_pause_menu.text = self.texts[self.lang]["main_menu"]

        for btn in self.info_buttons:
            btn.text = self.texts[self.lang]["info_btn"]

        if self.is_fullscreen:
            self.btn_fullscreen.text = self.texts[self.lang]["display_full"]
        else:
            self.btn_fullscreen.text = self.texts[self.lang]["display_win"]

        if hasattr(self, 'music_on'):
            if self.music_on:
                self.btn_music.text = self.texts[self.lang]["music_on"]
            else:
                self.btn_music.text = self.texts[self.lang]["music_off"]

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()