import pygame

class Camera:
    def __init__(self, map_width_pixels, map_height_pixels, screen_width, screen_height):
        self.camera_rect = pygame.Rect(0, 0, screen_width, screen_height)
        self.map_width_pixels = map_width_pixels
        self.map_height_pixels = map_height_pixels
        self.screen_width = screen_width
        self.screen_height = screen_height

    def apply(self, target_rect):
        return target_rect.move(-self.camera_rect.left, -self.camera_rect.top)

    def update(self, target_sprite):
        x = target_sprite.rect.centerx - self.screen_width // 2
        y = target_sprite.rect.centery - self.screen_height // 2

        x = max(0, x)
        y = max(0, y)
        x = min(self.map_width_pixels - self.screen_width, x)
        y = min(self.map_height_pixels - self.screen_height, y)
        self.camera_rect.topleft = (x, y)

    def get_viewport_world_rect(self):
        return self.camera_rect

    def get_offset(self):
        return pygame.Vector2(self.camera_rect.topleft)