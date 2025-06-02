import pygame
import sys
import os
from entities.player import Player
from engine.camera import Camera
from entities.enemy import Enemy
from engine import map_utils
from ui.hud import draw_player_health

tmx_data = None
map_pixel_width = 0
map_pixel_height = 0
wall_rects = []
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
player = None
camera = None
kill_zones = []
portals_list = []
current_map_filename = ""

pygame.mixer.init()
pygame.init()
pygame.font.init()
SCREEN_WIDTH = 1520
SCREEN_HEIGHT = 900
TILE_SIZE = 32
pygame.mixer.music.set_volume(0.5)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rogue Game")
clock = pygame.time.Clock()

UI_FONT_SIZE = 16
UI_FONT = None
MENU_TITLE_FONT = None
MENU_BUTTON_FONT = None
font_filename = 'HPbar.ttf'
font_path = os.path.join('..', 'assets', 'fonts', font_filename)

try:
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Файл шрифта не найден по пути: {os.path.abspath(font_path)}")

    UI_FONT = pygame.font.Font(font_path, UI_FONT_SIZE)
    MENU_TITLE_FONT = pygame.font.Font(font_path, 70)
    MENU_BUTTON_FONT = pygame.font.Font(font_path, 40)
    print(f"Используется шрифт из файла: {font_filename}")
except (FileNotFoundError, pygame.error) as e:  #
    print(f"ОШИБКА загрузки шрифта '{font_filename}': {e}. Используется стандартный шрифт.")
    UI_FONT_SIZE_fallback = 24
    UI_FONT = pygame.font.Font(None, UI_FONT_SIZE_fallback)
    MENU_TITLE_FONT = pygame.font.Font(None, 72)
    MENU_BUTTON_FONT = pygame.font.Font(None, 50)
    print(f"Используется стандартный шрифт Pygame (Размер UI: {UI_FONT_SIZE_fallback})")

music_file_path = os.path.join('..', 'assets', 'music', 'background.mp3')


def draw_text_menu(text, font, color, surface, x, y, center_align=False):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center_align:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect


def main_menu():
    menu_active = True
    click = False

    button_start_text = "Play"
    button_quit_text = "Quit"

    text_start_surf = MENU_BUTTON_FONT.render(button_start_text, True, (255, 255, 255))
    text_quit_surf = MENU_BUTTON_FONT.render(button_quit_text, True, (255, 255, 255))

    button_padding = 20
    button_start_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - (text_start_surf.get_width() + button_padding) // 2,
        SCREEN_HEIGHT // 2 - 50,
        text_start_surf.get_width() + button_padding,
        text_start_surf.get_height() + button_padding
    )
    button_quit_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - (text_quit_surf.get_width() + button_padding) // 2,
        SCREEN_HEIGHT // 2 + 40,
        text_quit_surf.get_width() + button_padding,
        text_quit_surf.get_height() + button_padding
    )

    while menu_active:
        screen.fill((20, 20, 40))

        draw_text_menu('Rogue Game', MENU_TITLE_FONT, (200, 200, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4,
                       center_align=True)

        mx, my = pygame.mouse.get_pos()

        color_start_bg = (70, 70, 100)
        if button_start_rect.collidepoint((mx, my)):
            color_start_bg = (100, 100, 130)
        pygame.draw.rect(screen, color_start_bg, button_start_rect, border_radius=10)
        draw_text_menu(button_start_text, MENU_BUTTON_FONT, (230, 230, 255), screen, button_start_rect.centerx,
                       button_start_rect.centery, center_align=True)

        color_quit_bg = (70, 70, 100)
        if button_quit_rect.collidepoint((mx, my)):
            color_quit_bg = (100, 100, 130)
        pygame.draw.rect(screen, color_quit_bg, button_quit_rect, border_radius=10)
        draw_text_menu(button_quit_text, MENU_BUTTON_FONT, (230, 230, 255), screen, button_quit_rect.centerx,
                       button_quit_rect.centery, center_align=True)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        if button_start_rect.collidepoint((mx, my)):
            if click:
                return True
        if button_quit_rect.collidepoint((mx, my)):
            if click:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(60)


def run_game():
    global tmx_data, map_pixel_width, map_pixel_height, wall_rects, enemies, all_sprites, player, camera, kill_zones
    MAP = ['Level_1.tmx','Level_2.tmx','Level_3.tmx','Boss.tmx']
    for map in MAP:
        game_running = True
        MAP_FILENAME = '../assets/maps/' + map
        try:
            tmx_data = map_utils.load_tmx_data(MAP_FILENAME)
        except FileNotFoundError:
            print(f"ОШИБКА: Файл карты '{MAP_FILENAME}' не найден.")
            return

        map_pixel_width = tmx_data.width * tmx_data.tilewidth
        map_pixel_height = tmx_data.height * tmx_data.tileheight

        default_spawn = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        player_start_pos = map_utils.find_spawn_point(tmx_data, 'PlayerSpawn', default_spawn)
        print(f"Игрок спавнится в: {player_start_pos}")

        COLLISION_LAYER_INDEX = 1
        wall_rects = map_utils.get_collision_rects(tmx_data, COLLISION_LAYER_INDEX)
        if not wall_rects:  #
            print(f"Предупреждение: Прямоугольники коллизий не загружены со слоя {COLLISION_LAYER_INDEX}.")
        else:  #
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
        portal = map_utils.get_portal(tmx_data)

        try:
            if not os.path.exists(music_file_path):
                raise FileNotFoundError(f"Файл музыки не найден по пути: {os.path.abspath(music_file_path)}")
            pygame.mixer.music.load(music_file_path)
            print(f"Музыка для игры загружена из: {music_file_path}")
            pygame.mixer.music.play(-1)
        except (FileNotFoundError, pygame.error) as e:
            print(f"ОШИБКА загрузки музыки для игры: {e}. Музыка не будет воспроизводиться.")

        game_running = True
        while game_running:
            dt = clock.tick(120)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        player.take_damage(10)
                    if event.key == pygame.K_j:
                        player.heal(5)
                    if event.key == pygame.K_h and not player.is_jumping:
                        player.attack(enemies)
                    if event.key == pygame.K_ESCAPE:
                        game_running = False
                        pygame.mixer.music.stop()

            if not game_running:
                break

            player.update(dt, enemies)
            for enemy in enemies:
                enemy.update(dt)
            camera.update(player)

            if player.current_hp <= 0 and not player.is_jumping:
                print("Игрок погиб! Затемнение экрана и респавн...")
                pygame.mixer.music.fadeout(1000)

                fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                #fade_duration_ms = 700
                #fade_step_delay = fade_duration_ms // (256 // 15)

                #for alpha_val in range(0, 256, 15):
                    #fade_surface.fill((0, 0, 0, alpha_val))
                    #screen.blit(fade_surface, (0, 0))
                    #pygame.display.flip()
                    #pygame.time.delay(fade_step_delay)

                #fade_surface.fill((0, 0, 0, 255))
                #screen.blit(fade_surface, (0, 0))
                #pygame.display.flip()
                #pygame.time.wait(300)

                player.respawn(player_start_pos, wall_rects)
                camera.update(player)

                pygame.mixer.music.play(-1)

                fade_duration_ms_in = 700
                fade_step_delay_in = fade_duration_ms_in // (256 // 15)

                for alpha_val in range(255, -1, -15):
                    screen.fill((30, 30, 30))
                    map_utils.draw_map_with_camera(screen, tmx_data, camera)
                    for sprite_obj in all_sprites:
                        screen.blit(sprite_obj.image, camera.apply(sprite_obj.rect))

                    HP_BAR_WIDTH = 130
                    HP_BAR_HEIGHT = 25
                    HP_BAR_X = 10
                    HP_BAR_Y = SCREEN_HEIGHT - HP_BAR_HEIGHT - 10
                    draw_player_health(screen, HP_BAR_X, HP_BAR_Y, HP_BAR_WIDTH, HP_BAR_HEIGHT, player, UI_FONT)

                    fade_surface.fill((0, 0, 0, alpha_val))
                    screen.blit(fade_surface, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(fade_step_delay_in)

                continue

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

            game_running = player.in_portal(portal)
            pygame.display.flip()






def game_controller():
    while True:
        if main_menu():
            run_game()
        else:
            break


if __name__ == '__main__':
    game_controller()
    pygame.quit()
    sys.exit()