import pygame

HEALTH_BAR_BACKGROUND_COLOR = (100, 0, 0)
HEALTH_BAR_HEALTH_COLOR = (0, 200, 0)
HEALTH_BAR_BORDER_COLOR = (200, 200, 200)
TEXT_COLOR = (255, 255, 255)

def draw_player_health(surface, x, y, width, height, player, font):
    if player.max_hp <= 0:
        fill_ratio = 0
    else:
        fill_ratio = player.current_hp / player.max_hp
    fill_ratio = max(0, min(fill_ratio, 1))

    fill_width = int(width * fill_ratio)

    background_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill_width, height)

    border_radius = int(height * 0.6)
    border_thickness = 1

    pygame.draw.rect(surface, HEALTH_BAR_BACKGROUND_COLOR, background_rect, border_radius=border_radius)
    if fill_width > border_radius * 2:
        pygame.draw.rect(surface, HEALTH_BAR_HEALTH_COLOR, fill_rect, border_radius=border_radius)
    elif fill_width > 0:
        pygame.draw.rect(surface, HEALTH_BAR_HEALTH_COLOR, fill_rect)

    pygame.draw.rect(surface, HEALTH_BAR_BORDER_COLOR, background_rect, border_thickness, border_radius=border_radius)

    hp_text = f"{player.current_hp} / {player.max_hp}"
    text_surface = font.render(hp_text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=background_rect.center)
    surface.blit(text_surface, text_rect)

# --- Сюда можно будет добавить другие функции для HUD ---
# Например:
# def draw_score(surface, score, x, y, font):
#     pass
#
# def draw_ammo(surface, current_ammo, max_ammo, x, y, font):
#     pass