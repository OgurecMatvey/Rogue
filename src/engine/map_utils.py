import pygame
import pytmx
from pytmx.util_pygame import load_pygame

def load_tmx_data(filename):
    print(f"Загрузка карты: {filename}")
    return load_pygame(filename)

def find_spawn_points(tmx_data, layer_name):
    points = []
    try:
        object_layer = tmx_data.get_layer_by_name(layer_name)
        if isinstance(object_layer, pytmx.TiledObjectGroup):
            print(f"Поиск точек спавна на слое объектов '{layer_name}'...")
            for obj in object_layer:
                points.append((int(obj.x), int(obj.y)))
            print(f"Найдено {len(points)} точек.")
        else:
             print(f"Предупреждение: Слой '{layer_name}' найден, но не является слоем объектов (TiledObjectGroup).")

    except ValueError:
        print(f"Предупреждение: Слой объектов '{layer_name}' для спавна не найден на карте.")
    return points

def find_spawn_point(tmx_data, object_name, default_pos):
    for obj in tmx_data.objects:
        if obj.name == object_name:
            print(f"Найден объект '{object_name}' на X:{int(obj.x)} Y:{int(obj.y)}")
            return int(obj.x), int(obj.y)
    print(f"Предупреждение: Объект '{object_name}' не найден. Используется позиция по умолчанию {default_pos}.")
    return default_pos

def get_collision_rects(tmx_data, layer_index):
    wall_rects = []
    print(f"--- Поиск коллизий на слое с индексом {layer_index} ---")
    if len(tmx_data.layers) > layer_index:
        collision_layer = tmx_data.layers[layer_index]
        layer_name = getattr(collision_layer, 'name', f'Слой {layer_index}')

        if isinstance(collision_layer, pytmx.TiledTileLayer):
            tile_width = tmx_data.tilewidth
            tile_height = tmx_data.tileheight
            print(f"Проверка слоя '{layer_name}'...")
            for x, y, gid in collision_layer:
                if gid != 0:
                    wall_rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                    wall_rects.append(wall_rect)
            print(f"--- Конец проверки слоя '{layer_name}' ---")
        else:
            print(f"Предупреждение: Слой '{layer_name}' (индекс {layer_index}) не является слоем тайлов (TiledTileLayer). Коллизии не загружены с этого слоя.")
    else:
        print(f"Предупреждение: Слой с индексом {layer_index} не найден на карте. Должно быть как минимум {layer_index + 1} слоев.")

    return wall_rects

def draw_map_with_camera(surface, tmx_data, camera):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            tile_width = tmx_data.tilewidth
            tile_height = tmx_data.tileheight
            for x, y, gid in layer:
                tile_image = tmx_data.get_tile_image_by_gid(gid)
                if tile_image:
                    tile_rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)

                    if camera.get_viewport_world_rect().colliderect(tile_rect):
                        screen_pos_rect = camera.apply(tile_rect)
                        surface.blit(tile_image, screen_pos_rect)

def get_kill_zones(tmx_data):
    kill_zones = []
    for layer in tmx_data.layers:
        if layer.name == 'Dunger_zone':
            for obj in layer:
                if obj.properties.get('kill'):
                    kill_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
    return kill_zones

def get_portal(tmx_data):
    portal = []
    for layer in tmx_data.layers:
        if layer.name == 'Objects':
            for obj in layer:
                if obj.properties.get('portal'):
                    portal.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
    return portal