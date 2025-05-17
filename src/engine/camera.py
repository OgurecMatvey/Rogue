import pygame

class Camera:
    def __init__(self, map_width_pixels, map_height_pixels, screen_width, screen_height):
        self.camera_rect = pygame.Rect(0, 0, screen_width, screen_height)
        self.map_width_pixels = map_width_pixels
        self.map_height_pixels = map_height_pixels
        self.screen_width = screen_width
        self.screen_height = screen_height

    # Смещает переданный Rect на величину смещения камеры
    def apply(self, target_rect):
        return target_rect.move(-self.camera_rect.left, -self.camera_rect.top)

    # Обновляет положение камеры, чтобы цель (target_sprite) была в центре
    def update(self, target_sprite):
        # Идеальное положение камеры
        x = target_sprite.rect.centerx - self.screen_width // 2
        y = target_sprite.rect.centery - self.screen_height // 2

        # Ограничиваем по краям карты
        x = max(0, x)  # Не левее 0
        y = max(0, y)  # Не выше 0
        x = min(self.map_width_pixels - self.screen_width, x)   # Не правее края карты
        y = min(self.map_height_pixels - self.screen_height, y)  # Не ниже края карты

        # Обновляем Rect камеры
        self.camera_rect.topleft = (x, y)

    # Возвращает текущий видимый прямоугольник (может быть полезно для оптимизации)
    def get_viewport_world_rect(self):
        return self.camera_rect

    # Возвращает текущее смещение (для рендереров, которым нужен offset)
    def get_offset(self):
        return pygame.Vector2(self.camera_rect.topleft)