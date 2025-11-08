#!/usr/bin/env python3
"""
Gusen Platformer Game - Native PyGame Version
Optimized for Anbernic RG34XXSP (3:2 aspect ratio - 640x480)
"""

import pygame
import math
import random
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Configuration for Anbernic RG34XXSP (3:2 aspect ratio)
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
WORLD_WIDTH = 6400
WORLD_HEIGHT = 480
FPS = 60

# Physics
GRAVITY = 0.4
TERMINAL_VELOCITY = 15
PLAYER_SPEED = 2.2
NPC_SPEED = 0.8
PLAYER_JUMP_POWER = -9
NPC_JUMP_POWER = -8

# Colors
SKY_COLOR = (95, 205, 228)
GROUND_COLOR = (34, 153, 84)
PLATFORM_COLOR = (211, 84, 0)
PLATFORM_BORDER = (120, 66, 18)
PLATFORM_HIGHLIGHT = (255, 140, 66)
PLATFORM_SHADOW = (82, 29, 10)
TREE_BG_COLOR = (20, 143, 119)
TREE_FG_COLOR = (39, 174, 96)
TREE_TRUNK = (110, 76, 48)
TREE_TRUNK_SHADOW = (61, 40, 23)
BUSH_COLOR = (39, 174, 96)
BUSH_DARK = (30, 132, 73)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (244, 208, 63)
RED = (255, 0, 0)
BLUE = (52, 152, 219)
GREEN = (46, 204, 113)
GOLD = (212, 175, 55)
DARK_RED = (139, 0, 0)

# Sprite settings
SPRITE_SCALE = 3  # Smaller scale for 640x480
DEFAULT_SPRITE_SIZE = 64

# Player settings
PLAYER_START_X = 100
PLAYER_START_Y = 380
PLAYER_LIVES = 3
INVINCIBILITY_FRAMES = 180

# Goal
GOAL_X = 6300
GOAL_Y = 370
GOAL_WIDTH = 60
GOAL_HEIGHT = 80

# Parallax
PARALLAX_CLOUDS = 0.3
PARALLAX_BG_TREES = 0.5
PARALLAX_FG_TREES = 0.8


class Platform:
    """Platform class for various platform types"""

    def __init__(self, x, y, width, height, is_ground=False, moving=False, style='normal'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_ground = is_ground
        self.moving = moving
        self.style = style

        if moving:
            self.start_x = x
            self.speed = 1.5
            self.range = 150
            self.direction = 1

    def update(self):
        if self.moving:
            self.x += self.speed * self.direction
            if abs(self.x - self.start_x) > self.range:
                self.direction *= -1
                self.x = self.start_x + (self.range * self.direction)

    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        # Viewport culling
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return

        if self.is_ground:
            self.draw_ground(surface, screen_x, screen_y)
        elif self.style == 'wood':
            self.draw_wood(surface, screen_x, screen_y)
        elif self.style == 'crystal':
            self.draw_crystal(surface, screen_x, screen_y)
        elif self.style == 'metal':
            self.draw_metal(surface, screen_x, screen_y)
        elif self.style == 'cloud':
            self.draw_cloud(surface, screen_x, screen_y)
        else:
            self.draw_normal(surface, screen_x, screen_y)

    def draw_ground(self, surface, screen_x, screen_y):
        # Grass top
        pygame.draw.rect(surface, (82, 190, 128), (screen_x, screen_y, self.width, 8))
        # Dirt base
        pygame.draw.rect(surface, (58, 90, 42), (screen_x, screen_y + 8, self.width, self.height - 8))
        # Grass tufts
        for i in range(0, self.width, 10):
            if (i // 10) % 2 == 0:
                pygame.draw.rect(surface, (106, 216, 151), (screen_x + i, screen_y - 2, 2, 3))

    def draw_normal(self, surface, screen_x, screen_y):
        pygame.draw.rect(surface, PLATFORM_COLOR, (screen_x, screen_y, self.width, self.height))
        pygame.draw.rect(surface, PLATFORM_HIGHLIGHT, (screen_x, screen_y, self.width, 3))
        pygame.draw.rect(surface, PLATFORM_SHADOW, (screen_x, screen_y + self.height - 3, self.width, 3))
        pygame.draw.rect(surface, PLATFORM_BORDER, (screen_x, screen_y, self.width, self.height), 2)

    def draw_wood(self, surface, screen_x, screen_y):
        pygame.draw.rect(surface, (139, 111, 71), (screen_x, screen_y, self.width, self.height))
        for i in range(0, self.width, 16):
            pygame.draw.rect(surface, (111, 87, 57), (screen_x + i, screen_y, 2, self.height))
        pygame.draw.rect(surface, (90, 66, 40), (screen_x, screen_y, self.width, self.height), 2)

    def draw_crystal(self, surface, screen_x, screen_y):
        pygame.draw.rect(surface, (74, 144, 226), (screen_x, screen_y, self.width, self.height))
        for i in range(0, self.width, 20):
            pygame.draw.rect(surface, WHITE, (screen_x + i, screen_y + 2, 3, 3))
        pygame.draw.rect(surface, (46, 92, 138), (screen_x, screen_y, self.width, self.height), 2)

    def draw_metal(self, surface, screen_x, screen_y):
        pygame.draw.rect(surface, (127, 140, 141), (screen_x, screen_y, self.width, self.height))
        for i in range(0, self.width, 20):
            pygame.draw.rect(surface, (74, 84, 86), (screen_x + i, screen_y, 2, self.height))
            pygame.draw.circle(surface, (52, 73, 94), (screen_x + i + 5, screen_y + 5), 2)
        pygame.draw.rect(surface, (52, 73, 94), (screen_x, screen_y, self.width, self.height), 2)

    def draw_cloud(self, surface, screen_x, screen_y):
        cloud_color = (255, 255, 255, 230)
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(s, cloud_color, (0, 0, self.width, self.height))
        surface.blit(s, (screen_x, screen_y))

    def check_collision(self, character):
        return (character.x < self.x + self.width and
                character.x + character.width > self.x and
                character.y < self.y + self.height and
                character.y + character.height > self.y)


class Collectible:
    """Collectible items (coins and gems)"""

    def __init__(self, x, y, col_type='coin'):
        self.x = x
        self.y = y
        self.type = col_type
        self.size = 20
        self.collected = False
        self.bob_offset = 0
        self.start_y = y
        self.bob_counter = random.uniform(0, math.pi * 2)

    def update(self, frame):
        self.bob_counter += 0.05
        self.bob_offset = math.sin(self.bob_counter) * 5

    def draw(self, surface, camera_x, camera_y):
        if self.collected:
            return

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y + self.bob_offset - camera_y)

        if screen_x < -50 or screen_x > SCREEN_WIDTH + 50:
            return

        if self.type == 'coin':
            pygame.draw.circle(surface, YELLOW, (screen_x, screen_y), self.size // 2)
            pygame.draw.circle(surface, GOLD, (screen_x, screen_y), self.size // 3)
            pygame.draw.circle(surface, (153, 101, 21), (screen_x, screen_y), self.size // 2, 2)
        else:  # gem
            points = [
                (screen_x, screen_y - self.size // 2),
                (screen_x + self.size // 3, screen_y),
                (screen_x, screen_y + self.size // 2),
                (screen_x - self.size // 3, screen_y)
            ]
            pygame.draw.polygon(surface, BLUE, points)
            pygame.draw.polygon(surface, (26, 82, 118), points, 2)


class Particle:
    """Particle effects"""

    def __init__(self, x, y, p_type='dust'):
        self.x = x
        self.y = y
        self.type = p_type
        self.life = 30 if p_type != 'blood' else 40
        self.max_life = self.life
        self.vx = (random.random() - 0.5) * 4
        self.vy = (random.random() - 0.5) * 4 - 2
        self.size = random.randint(2, 6) if p_type != 'blood' else random.randint(3, 9)

        if p_type == 'dust':
            self.color = (170, 170, 170)
        elif p_type == 'sparkle':
            self.color = YELLOW
        elif p_type == 'damage':
            self.color = RED
        elif p_type == 'blood':
            self.color = DARK_RED
            self.vx = (random.random() - 0.5) * 6
            self.vy = (random.random() - 0.5) * 6
        else:
            self.color = WHITE

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # gravity
        self.life -= 1

    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        alpha = int(255 * (self.life / self.max_life))
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        color = (*self.color, alpha)
        pygame.draw.rect(s, color, (0, 0, self.size, self.size))
        surface.blit(s, (screen_x, screen_y))

    def is_dead(self):
        return self.life <= 0


class Character:
    """Character class for player and NPCs"""

    def __init__(self, image_path, x, y, is_player=False, enemy_type='walking'):
        self.x = x
        self.y = y
        self.width = DEFAULT_SPRITE_SIZE * SPRITE_SCALE
        self.height = DEFAULT_SPRITE_SIZE * SPRITE_SCALE
        self.vx = 0
        self.vy = 0
        self.is_player = is_player
        self.on_ground = False
        self.facing_right = True
        self.current_frame = 1
        self.dead = False
        self.enemy_type = enemy_type

        # Load sprite
        self.image = None
        self.loaded = False
        if os.path.exists(image_path):
            try:
                img = pygame.image.load(image_path).convert_alpha()
                self.frame_height = img.get_height() // 2
                self.frame_width = img.get_width()
                self.width = self.frame_width * SPRITE_SCALE
                self.height = self.frame_height * SPRITE_SCALE
                self.image = img
                self.loaded = True
            except:
                print(f"Failed to load: {image_path}")

        if is_player:
            self.jump_count = 0
            self.jump_pressed = False
            self.is_stomping = False
            self.stomp_velocity = -12

            # Sword
            self.has_sword = True
            self.sword_attacking = False
            self.sword_attack_duration = 20
            self.sword_cooldown = 90
            self.sword_attack_timer = 0
            self.sword_cooldown_timer = 0
            self.sword_range = 60
            self.sword_width = 45
            self.sword_height = 45

            # Load sword image
            self.sword_image = None
            self.sword_loaded = False
            if os.path.exists('sword.png'):
                try:
                    sword_img = pygame.image.load('sword.png').convert_alpha()
                    self.sword_frame_height = sword_img.get_height() // 2
                    self.sword_frame_width = sword_img.get_width()
                    self.sword_image = sword_img
                    self.sword_loaded = True
                except:
                    print("Failed to load sword.png")
        else:
            # NPC settings
            self.move_direction = 1 if random.random() > 0.5 else -1
            self.jump_timer = random.randint(30, 90)
            self.is_idle = False
            self.idle_timer = 0
            self.idle_cycle_duration = 120

            if enemy_type == 'flying':
                self.fly_height = y
                self.fly_amplitude = 40
                self.fly_speed = 0.03
                self.fly_counter = random.uniform(0, math.pi * 2)
            elif enemy_type == 'patrolling':
                self.patrol_start = x
                self.patrol_end = x + 200
                self.patrol_speed = 1

    def update(self, keys, platforms, frame):
        self.vy += GRAVITY

        if self.is_player:
            self.update_player(keys, platforms)
        else:
            self.update_npc(platforms, frame)

        # Apply velocity
        self.x += self.vx
        self.y += self.vy

        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.check_platform_collision(platform):
                if self.vy > 0 and self.y + self.height - self.vy <= platform.y + 10:
                    self.y = platform.y - self.height
                    self.vy = 0
                    self.on_ground = True
                    if self.is_player:
                        self.jump_count = 0

        # World bounds
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))

        # Terminal velocity
        if self.vy > TERMINAL_VELOCITY:
            self.vy = TERMINAL_VELOCITY

    def update_player(self, keys, platforms):
        self.vx = 0

        # Movement
        if keys.get(pygame.K_LEFT, False) or keys.get(pygame.K_a, False):
            self.vx = -PLAYER_SPEED
            self.facing_right = False
            self.current_frame = 0
        if keys.get(pygame.K_RIGHT, False) or keys.get(pygame.K_d, False):
            self.vx = PLAYER_SPEED
            self.facing_right = True
            self.current_frame = 1

        # Jumping
        jump_key = keys.get(pygame.K_UP, False) or keys.get(pygame.K_w, False) or keys.get(pygame.K_SPACE, False)
        if jump_key and self.jump_count < 2:
            if not self.jump_pressed:
                self.vy = PLAYER_JUMP_POWER
                self.jump_count += 1
                self.on_ground = False
                self.jump_pressed = True

        if not jump_key:
            self.jump_pressed = False

        # Stomp
        if self.vy > 0 and (keys.get(pygame.K_DOWN, False) or keys.get(pygame.K_s, False)):
            self.vy = max(self.vy, 15)
            self.is_stomping = True
        else:
            self.is_stomping = False

        # Sword attack
        if keys.get(pygame.K_x, False) or keys.get(pygame.K_X, False):
            if not self.sword_attacking and self.sword_cooldown_timer <= 0:
                self.sword_attacking = True
                self.sword_attack_timer = self.sword_attack_duration
                self.sword_cooldown_timer = self.sword_cooldown

        # Update timers
        if self.sword_attack_timer > 0:
            self.sword_attack_timer -= 1
            if self.sword_attack_timer <= 0:
                self.sword_attacking = False

        if self.sword_cooldown_timer > 0:
            self.sword_cooldown_timer -= 1

    def update_npc(self, platforms, frame):
        if self.enemy_type == 'flying':
            self.fly_counter += self.fly_speed
            self.y = self.fly_height + math.sin(self.fly_counter) * self.fly_amplitude
            self.vx = self.move_direction * NPC_SPEED
            self.vy = 0
            self.current_frame = 1 if self.move_direction > 0 else 0

            # Turn around at world bounds
            if self.x <= 50 and self.move_direction < 0:
                self.move_direction = 1
            elif self.x >= WORLD_WIDTH - self.width - 50 and self.move_direction > 0:
                self.move_direction = -1
            return

        if self.enemy_type == 'patrolling':
            if self.x >= self.patrol_end:
                self.move_direction = -1
            elif self.x <= self.patrol_start:
                self.move_direction = 1
            self.vx = self.move_direction * self.patrol_speed
            self.current_frame = 1 if self.move_direction > 0 else 0
            self.facing_right = self.move_direction > 0
            return

        # Walking enemy
        if self.is_idle:
            self.idle_timer += 1
            self.vx = 0
            self.current_frame = 0 if self.idle_timer < 60 else 1
            if self.idle_timer >= self.idle_cycle_duration:
                self.is_idle = False
                self.idle_timer = 0
                self.move_direction *= -1
            return

        # Edge detection
        if self.on_ground:
            check_x = self.x + self.width + 30 if self.move_direction > 0 else self.x - 30
            check_y = self.y + self.height + 10
            platform_ahead = False

            for platform in platforms:
                if (check_x > platform.x and check_x < platform.x + platform.width and
                    check_y > platform.y and check_y < platform.y + platform.height + 20):
                    platform_ahead = True
                    break

            if not platform_ahead or self.x <= 0 or self.x >= WORLD_WIDTH - self.width:
                self.is_idle = True
                self.idle_timer = 0
                return

        # Normal movement
        self.vx = self.move_direction * NPC_SPEED
        self.current_frame = 1 if self.move_direction > 0 else 0
        self.facing_right = self.move_direction > 0

        self.jump_timer -= 1
        if self.jump_timer <= 0 and self.on_ground:
            self.vy = NPC_JUMP_POWER
            self.jump_timer = random.randint(60, 180)

    def check_platform_collision(self, platform):
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y)

    def draw(self, surface, camera_x, camera_y, invincibility_timer=0):
        if not self.loaded:
            # Draw placeholder
            screen_x = int(self.x - camera_x)
            screen_y = int(self.y - camera_y)
            pygame.draw.rect(surface, BLUE if self.is_player else RED,
                           (screen_x, screen_y, self.width, self.height))
            return

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        # Viewport culling
        if screen_x + self.width < -100 or screen_x > SCREEN_WIDTH + 100:
            return

        # Draw character sprite
        src_rect = pygame.Rect(0, self.current_frame * self.frame_height,
                              self.frame_width, self.frame_height)
        dest_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)

        if self.is_player and invincibility_timer > 0 and (invincibility_timer // 10) % 2 == 0:
            # Flash during invincibility
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.transform.scale(self.image.subsurface(src_rect), (self.width, self.height), temp_surface)
            temp_surface.set_alpha(128)
            surface.blit(temp_surface, dest_rect)
        else:
            surface.blit(pygame.transform.scale(self.image.subsurface(src_rect),
                                               (self.width, self.height)), dest_rect)

        # Draw sword if attacking
        if self.is_player and self.sword_attacking and self.sword_loaded:
            self.draw_sword(surface, screen_x, screen_y)

        # Player name tag
        if self.is_player:
            font = pygame.font.Font(None, 18)
            tag_color = YELLOW if invincibility_timer > 0 else YELLOW
            text = font.render('PLAYER', True, tag_color)
            text_rect = text.get_rect(center=(screen_x + self.width // 2, screen_y - 10))
            pygame.draw.rect(surface, BLACK, text_rect.inflate(10, 4))
            pygame.draw.rect(surface, WHITE, text_rect.inflate(10, 4), 2)
            surface.blit(text, text_rect)

    def draw_sword(self, surface, screen_x, screen_y):
        swing_progress = 1 - (self.sword_attack_timer / self.sword_attack_duration)
        start_angle = -math.pi / 2
        end_angle = math.pi / 2
        current_angle = start_angle + (end_angle - start_angle) * swing_progress

        sword_frame = 1 if swing_progress < 0.5 else 0

        pivot_x = screen_x + (self.width * 0.8 if self.facing_right else self.width * 0.2)
        pivot_y = screen_y + self.height * 0.3

        # Get sword surface
        src_rect = pygame.Rect(0, sword_frame * self.sword_frame_height,
                              self.sword_frame_width, self.sword_frame_height)
        sword_surf = pygame.transform.scale(self.image.subsurface(src_rect) if not self.sword_loaded
                                           else self.sword_image.subsurface(src_rect),
                                           (self.sword_width, self.sword_height))

        # Rotate and flip
        angle_deg = math.degrees(current_angle if self.facing_right else -current_angle)
        rotated = pygame.transform.rotate(sword_surf, -angle_deg)
        if not self.facing_right:
            rotated = pygame.transform.flip(rotated, True, False)

        rect = rotated.get_rect(center=(int(pivot_x), int(pivot_y)))
        surface.blit(rotated, rect)

    def get_sword_hitbox(self):
        if not self.sword_attacking:
            return None

        sword_x = self.x + self.width if self.facing_right else self.x - self.sword_range
        sword_y = self.y + self.height / 2 - self.sword_height / 2

        return pygame.Rect(sword_x, sword_y, self.sword_range, self.sword_height)

    def check_collision(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)


class Game:
    """Main game class"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Gusen Platformer - Anbernic RG34XXSP")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize gamepad
        self.gamepad = None
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            print(f"Gamepad detected: {self.gamepad.get_name()}")

        # Game state
        self.frame = 0
        self.score = 0
        self.lives = PLAYER_LIVES
        self.invincibility_timer = 0
        self.has_won = False
        self.is_dead = False
        self.coins_collected = 0
        self.gems_collected = 0

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # Game objects
        self.platforms = []
        self.characters = []
        self.collectibles = []
        self.particles = []
        self.player = None

        # Font
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)

        # Keys state
        self.keys = {}

        self.init_level()

    def init_level(self):
        """Initialize level data"""
        # Ground platforms
        ground_platforms = [
            (0, 430, 500), (700, 430, 600), (1500, 430, 500),
            (2200, 430, 600), (3000, 430, 500), (3700, 430, 600),
            (4500, 430, 500), (5200, 430, 600), (6000, 430, 400)
        ]

        for x, y, w in ground_platforms:
            self.platforms.append(Platform(x, y, w, 50, is_ground=True))

        # Section platforms
        sections = [
            # Tutorial - wood
            [(100, 360, 120, 'wood'), (450, 280, 120, 'wood')],
            # Clouds
            [(850, 350, 90, 'cloud'), (1150, 270, 90, 'cloud')],
            # Crystal
            [(1550, 360, 120, 'crystal'), (1730, 320, 100, 'crystal'),
             (1880, 260, 120, 'crystal')],
            # Metal tower
            [(2250, 360, 100, 'metal'), (2380, 320, 90, 'metal'),
             (2320, 180, 100, 'metal'), (2480, 40, 120, 'metal'),
             (2750, 180, 110, 'metal')],
            # Mixed
            [(2950, 320, 90, 'wood'), (3250, 250, 90, 'metal'),
             (3500, 300, 100, 'crystal')],
            # Sky
            [(3650, 360, 120, 'cloud'), (3980, 280, 110, 'cloud'),
             (4050, 160, 100, 'cloud'), (4250, 140, 120, 'cloud')],
            # Industrial
            [(4400, 240, 100, 'metal'), (4570, 300, 120, 'metal'),
             (4870, 220, 100, 'metal')],
            # Crystal paradise
            [(5050, 360, 100, 'crystal'), (5350, 280, 100, 'crystal'),
             (5400, 180, 100, 'crystal')],
            # Final
            [(5730, 360, 100, 'wood'), (5870, 320, 110, 'metal'),
             (6030, 280, 100, 'crystal'), (6200, 220, 120, 'metal')]
        ]

        for section in sections:
            for x, y, w, style in section:
                self.platforms.append(Platform(x, y, w, 15, style=style))

        # Create player
        self.player = Character('player.png', PLAYER_START_X, PLAYER_START_Y, is_player=True)
        self.characters.append(self.player)

        # Create NPCs
        npc_sprites = ['npc1.png', 'npc2.png', 'sprite.png', 'sprite2.png',
                      'sprite3.png', 'sprite4.png', 'sprite5.png', 'dinggusen.png',
                      'gressgusen.png', 'lanternegusen.png', 'lunagusen.png',
                      'spaghettigusen.png', 'wirelessgusen.png', 'generatorgusen.png']

        npc_positions = [
            (600, 320), (900, 320), (1250, 240), (1700, 300), (2000, 240),
            (2350, 160), (2650, 130), (3050, 270), (3350, 220), (3800, 270),
            (4150, 90), (4500, 210), (4800, 290), (5150, 270), (5450, 160),
            (5800, 270)
        ]

        enemy_types = ['walking', 'walking', 'patrolling', 'walking', 'flying',
                      'walking', 'patrolling', 'walking', 'walking', 'flying',
                      'walking', 'patrolling', 'walking', 'walking', 'flying', 'walking']

        for i, (x, y) in enumerate(npc_positions):
            sprite = npc_sprites[i % len(npc_sprites)]
            enemy_type = enemy_types[i % len(enemy_types)]
            self.characters.append(Character(sprite, x, y, is_player=False, enemy_type=enemy_type))

        # Create collectibles
        collectible_data = [
            (160, 330, 'coin'), (510, 250, 'coin'), (895, 320, 'coin'),
            (1195, 240, 'coin'), (1195, 210, 'gem'), (1610, 330, 'coin'),
            (1780, 290, 'coin'), (1940, 230, 'coin'), (1780, 270, 'gem'),
            (2300, 330, 'coin'), (2425, 290, 'coin'), (2370, 150, 'coin'),
            (2540, 10, 'gem'), (2805, 150, 'coin'), (2995, 290, 'coin'),
            (3295, 220, 'coin'), (3550, 270, 'coin'), (3710, 330, 'coin'),
            (4035, 250, 'coin'), (4100, 130, 'coin'), (4310, 110, 'gem'),
            (4450, 210, 'coin'), (4630, 270, 'coin'), (4920, 190, 'coin'),
            (4630, 240, 'gem'), (5100, 330, 'coin'), (5400, 250, 'coin'),
            (5450, 150, 'gem'), (5780, 330, 'coin'), (5925, 290, 'coin'),
            (6080, 250, 'coin'), (6260, 190, 'gem')
        ]

        for x, y, c_type in collectible_data:
            self.collectibles.append(Collectible(x, y, c_type))

    def handle_input(self):
        """Handle keyboard and gamepad input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys[event.key] = True
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.KEYUP:
                self.keys[event.key] = False

        # Gamepad input mapping for Anbernic
        if self.gamepad:
            # D-pad or left analog stick for movement
            axes_x = self.gamepad.get_axis(0)
            if axes_x < -0.3:
                self.keys[pygame.K_LEFT] = True
                self.keys[pygame.K_RIGHT] = False
            elif axes_x > 0.3:
                self.keys[pygame.K_RIGHT] = True
                self.keys[pygame.K_LEFT] = False
            else:
                self.keys[pygame.K_LEFT] = False
                self.keys[pygame.K_RIGHT] = False

            # A button (button 0) for jump
            if self.gamepad.get_button(0):
                self.keys[pygame.K_SPACE] = True
            else:
                self.keys[pygame.K_SPACE] = False

            # B button (button 1) for sword
            if self.gamepad.get_button(1):
                self.keys[pygame.K_x] = True
            else:
                self.keys[pygame.K_x] = False

            # Down on D-pad for stomp
            axes_y = self.gamepad.get_axis(1)
            if axes_y > 0.3:
                self.keys[pygame.K_DOWN] = True
            else:
                self.keys[pygame.K_DOWN] = False

            # Start button (usually button 7) to exit
            if self.gamepad.get_button(7):
                self.running = False

    def update(self):
        """Update game state"""
        if self.is_dead or self.has_won:
            return

        # Update timers
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        # Update platforms
        for platform in self.platforms:
            platform.update()

        # Update characters
        for char in self.characters:
            if char.is_player or not char.dead:
                char.update(self.keys, self.platforms, self.frame)

        # Update collectibles
        for collectible in self.collectibles:
            collectible.update(self.frame)

        # Update particles
        self.particles = [p for p in self.particles if not p.is_dead()]
        for particle in self.particles:
            particle.update()

        # Collectible collection
        for collectible in self.collectibles:
            if not collectible.collected:
                dist = math.sqrt((self.player.x + self.player.width/2 - collectible.x)**2 +
                               (self.player.y + self.player.height/2 - collectible.y)**2)
                if dist < collectible.size * 2:
                    collectible.collected = True
                    if collectible.type == 'coin':
                        self.score += 10
                        self.coins_collected += 1
                    else:
                        self.score += 50
                        self.gems_collected += 1

                    for _ in range(8):
                        self.particles.append(Particle(collectible.x, collectible.y, 'sparkle'))

        # Win detection
        if (self.player.x < GOAL_X + GOAL_WIDTH and
            self.player.x + self.player.width > GOAL_X and
            self.player.y < GOAL_Y + GOAL_HEIGHT and
            self.player.y + self.player.height > GOAL_Y):
            self.has_won = True
            self.score += 1000

        # Falling off world
        if self.player.y > WORLD_HEIGHT + 100:
            self.damage_player()
            if not self.is_dead:
                self.player.x = PLAYER_START_X
                self.player.y = PLAYER_START_Y
                self.player.vx = 0
                self.player.vy = 0

        # Sword collision
        sword_hitbox = self.player.get_sword_hitbox()
        if sword_hitbox:
            for char in self.characters:
                if not char.is_player and not char.dead:
                    char_rect = pygame.Rect(char.x, char.y, char.width, char.height)
                    if sword_hitbox.colliderect(char_rect):
                        char.dead = True
                        self.score += 75
                        for _ in range(20):
                            self.particles.append(Particle(char.x + char.width/2,
                                                          char.y + char.height/2, 'blood'))

        # Enemy collision
        if self.invincibility_timer == 0:
            for char in self.characters:
                if not char.is_player and not char.dead and self.player.check_collision(char):
                    # Stomp attack
                    if self.player.is_stomping and self.player.y + self.player.height/2 < char.y:
                        char.dead = True
                        self.score += 50
                        self.player.vy = self.player.stomp_velocity
                        for _ in range(15):
                            self.particles.append(Particle(char.x + char.width/2,
                                                          char.y + char.height/2, 'sparkle'))
                    else:
                        self.damage_player()

        # Update camera
        self.camera_x = max(0, min(self.player.x - SCREEN_WIDTH/2 + self.player.width/2,
                                   WORLD_WIDTH - SCREEN_WIDTH))
        self.camera_y = 0

    def damage_player(self):
        """Damage the player"""
        if self.invincibility_timer > 0 or self.is_dead:
            return

        self.lives -= 1
        for _ in range(10):
            self.particles.append(Particle(self.player.x + self.player.width/2,
                                          self.player.y + self.player.height/2, 'damage'))

        self.invincibility_timer = INVINCIBILITY_FRAMES

        if self.lives <= 0:
            self.is_dead = True

    def draw(self):
        """Draw everything"""
        # Sky
        self.screen.fill(SKY_COLOR)

        # Draw forest background
        self.draw_forest()

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x, self.camera_y)

        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(self.screen, self.camera_x, self.camera_y)

        # Draw goal
        self.draw_goal()

        # Draw characters
        for char in self.characters:
            if char.is_player or not char.dead:
                char.draw(self.screen, self.camera_x, self.camera_y, self.invincibility_timer)

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen, self.camera_x, self.camera_y)

        # Draw UI
        self.draw_ui()

        pygame.display.flip()

    def draw_forest(self):
        """Draw forest background"""
        # Simple tree rendering
        parallax_bg = self.camera_x * PARALLAX_BG_TREES
        for i in range(20):
            x = int(i * 400 - parallax_bg)
            if x < -100 or x > SCREEN_WIDTH + 100:
                continue
            pygame.draw.rect(self.screen, TREE_TRUNK, (x, SCREEN_HEIGHT - 120, 25, 120))
            pygame.draw.circle(self.screen, TREE_BG_COLOR, (x + 12, SCREEN_HEIGHT - 110), 40)

    def draw_goal(self):
        """Draw goal flag"""
        screen_x = int(GOAL_X - self.camera_x)
        screen_y = int(GOAL_Y - self.camera_y)

        if screen_x < -100 or screen_x > SCREEN_WIDTH + 100:
            return

        # Flag pole
        pygame.draw.rect(self.screen, (102, 102, 102), (screen_x + 25, screen_y, 8, GOAL_HEIGHT))

        # Flag
        wave = int(math.sin(self.frame * 0.1) * 3)
        pygame.draw.rect(self.screen, YELLOW, (screen_x + 33, screen_y + 10, 35 + wave, 30))

        # Text
        text = self.font.render('GOAL', True, YELLOW)
        self.screen.blit(text, (screen_x + 5, screen_y + GOAL_HEIGHT + 5))

    def draw_ui(self):
        """Draw UI elements"""
        # Score box
        pygame.draw.rect(self.screen, BLACK, (10, 10, 220, 70))
        pygame.draw.rect(self.screen, WHITE, (10, 10, 220, 70), 2)

        score_text = self.font.render(f'Score: {self.score}', True, YELLOW)
        self.screen.blit(score_text, (20, 20))

        coins_text = self.font.render(f'Coins: {self.coins_collected}', True, YELLOW)
        self.screen.blit(coins_text, (20, 40))

        gems_text = self.font.render(f'Gems: {self.gems_collected}', True, BLUE)
        self.screen.blit(gems_text, (20, 60))

        # Health
        hearts = '♥' * max(0, self.lives)
        health_text = self.big_font.render(hearts or '💀', True, RED)
        self.screen.blit(health_text, (SCREEN_WIDTH - 100, 10))

        # Invincibility bar
        if self.invincibility_timer > 0:
            progress = (self.invincibility_timer / INVINCIBILITY_FRAMES) * SCREEN_WIDTH
            pygame.draw.rect(self.screen, YELLOW, (0, SCREEN_HEIGHT - 10, progress, 10))

        # Victory screen
        if self.has_won:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            self.screen.blit(s, (0, 0))

            victory_text = self.big_font.render('VICTORY!', True, YELLOW)
            rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(victory_text, rect)

            score_text = self.font.render(f'Final Score: {self.score}', True, WHITE)
            rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            self.screen.blit(score_text, rect)

        # Game over screen
        if self.is_dead:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 220))
            self.screen.blit(s, (0, 0))

            game_over_text = self.big_font.render('GAME OVER!', True, RED)
            rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(game_over_text, rect)

            score_text = self.font.render(f'Final Score: {self.score}', True, YELLOW)
            rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            self.screen.blit(score_text, rect)

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            self.frame += 1

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
