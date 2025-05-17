import pygame
import sys
import os
from entities.player import Player
from engine.camera import Camera
from entities.enemy import Enemy
from engine import map_utils
from ui.hud import draw_player_health

pygame.mixer.init()
pygame.init()
pygame.font.init()
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
TILE_SIZE = 32
pygame.mixer.music.set_volume(0.1)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rogue Game")
clock = pygame.time.Clock()
UI_FONT_SIZE = 16
try:
    font_filename = 'HPbar.ttf'
    font_path = os.path.join('..', 'assets', 'fonts', font_filename)
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Файл шрифта не найден по пути: {os.path.abspath(font_path)}")

    UI_FONT = pygame.font.Font(font_path, UI_FONT_SIZE)
    print(f"Используется шрифт из файла: {font_filename}, Размер: {UI_FONT_SIZE}")
except (FileNotFoundError, pygame.error) as e:
    print(f"ОШИБКА загрузки шрифта '{font_filename}': {e}. Используется стандартный шрифт.")
    UI_FONT_SIZE = 24
    UI_FONT = pygame.font.Font(None, UI_FONT_SIZE)
    print(f"Используется стандартный шрифт Pygame (Размер: {UI_FONT_SIZE})")
print(f"Используется шрифт для UI (Размер: {UI_FONT_SIZE})")

try:
    music_file_path = os.path.join('..', 'assets', 'music', 'background.mp3')
    if not os.path.exists(music_file_path):
        raise FileNotFoundError(f"Файл музыки не найден по пути: {os.path.abspath(music_file_path)}")
    pygame.mixer.music.load(music_file_path)
    print(f"Музыка загружена из: {music_file_path}")
except (FileNotFoundError, pygame.error) as e:
    print(f"ОШИБКА загрузки музыки: {e}. Музыка не будет воспроизводиться.")

MAP_FILENAME = '../assets/maps/Level_1.tmx'

try:
    tmx_data = map_utils.load_tmx_data(MAP_FILENAME)
except FileNotFoundError:
    print(f"ОШИБКА: Файл карты '{MAP_FILENAME}' не найден.")
    pygame.quit()
    sys.exit()

map_pixel_width = tmx_data.width * tmx_data.tilewidth
map_pixel_height = tmx_data.height * tmx_data.tileheight

default_spawn = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
player_start_pos = map_utils.find_spawn_point(tmx_data, 'PlayerSpawn', default_spawn)
print(f"Игрок спавнится в: {player_start_pos}")

COLLISION_LAYER_INDEX = 1
COLLISION_LAYER_NAME = 'Collision'
wall_rects = map_utils.get_collision_rects(tmx_data, COLLISION_LAYER_INDEX)
if not wall_rects:
     print(f"Предупреждение: Прямоугольники коллизий не загружены со слоя {COLLISION_LAYER_INDEX}.")
else:
     print(f"Загружено {len(wall_rects)} прямоугольников коллизий со слоя {COLLISION_LAYER_INDEX}.")


player = Player(player_start_pos[0], player_start_pos[1], wall_rects)
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
all_sprites.add(player)

ENEMY_SPAWN_LAYER_NAME = 'EnemySpawns'
enemy_spawn_points = map_utils.find_spawn_points(tmx_data, ENEMY_SPAWN_LAYER_NAME)

if not enemy_spawn_points:
    print(f"Предупреждение: Точки спавна врагов не найдены на слое объектов '{ENEMY_SPAWN_LAYER_NAME}'.")
else:
    print(f"Найдено {len(enemy_spawn_points)} точек спавна врагов.")
    for pos in enemy_spawn_points:
        enemy = Enemy(pos[0], pos[1], wall_rects, player)
        all_sprites.add(enemy)
        enemies.add(enemy)
        print(f"Враг создан в: {pos}")

camera = Camera(map_pixel_width, map_pixel_height, SCREEN_WIDTH, SCREEN_HEIGHT)

kill_zones = map_utils.get_kill_zones(tmx_data)

if 'music_file_path' in locals() and os.path.exists(music_file_path):
    pygame.mixer.music.play(-1)

running = True
while running:
    dt = clock.tick(120)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
             if event.key == pygame.K_x:
                 player.take_damage(10)
             if event.key == pygame.K_j:
                 player.heal(5)
             if event.key == pygame.K_h:
                 player.attack(enemies)

    player.update(dt, enemies)
    for enemy in enemies:
        enemy.update(dt)

    camera.update(player)
    player.dunger_zone(kill_zones)

    screen.fill((30, 30, 30))

    map_utils.draw_map_with_camera(screen, tmx_data, camera)

    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite.rect))

    HP_BAR_WIDTH = 130
    HP_BAR_HEIGHT = 25
    HP_BAR_X = 10
    HP_BAR_Y = SCREEN_HEIGHT - HP_BAR_HEIGHT - 10
    draw_player_health(screen, HP_BAR_X, HP_BAR_Y, HP_BAR_WIDTH, HP_BAR_HEIGHT, player, UI_FONT)
    if enemies:
        for an_enemy in enemies:
            if hasattr(an_enemy, 'rect') and an_enemy.rect is not None:
                enemy_screen_pos = camera.apply(an_enemy.rect).center
            if hasattr(an_enemy, 'position'):
                pass
    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()
sys.exit()