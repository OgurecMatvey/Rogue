# entities/entity.py
import pygame

class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image_path, wall_rects):
        super().__init__()

        self.position = pygame.math.Vector2(x, y)
        self.walls = wall_rects if wall_rects else []

        self.image = None
        self.rect = None

        if image_path:
            try:
                self._original_image = pygame.image.load(image_path).convert_alpha()
            except pygame.error as e:
                print(f"ОШИБКА (Entity): Не удалось загрузить изображение {image_path}: {e}")
                self._original_image = pygame.Surface((32, 32))
                self._original_image.fill((255, 0, 255))
        else:
            self._original_image = pygame.Surface((32, 32), pygame.SRCALPHA)

        self.image = self._original_image.copy()

        self.rect = self.image.get_rect(center=self.position)

        self.health = 100
        self.max_health = 100
        self.speed = 0
        self.velocity_y = 0.0  # Текущая вертикальная скорость
        self.gravity = 0.8     # Сила гравитации (пикселей на кадр в квадрате)
        self.on_ground = False

    def check_collision(self, rect):
        for wall in self.walls:
            if rect.colliderect(wall):
                return True
        return False

    def move(self, dx, dy):
        self.position.x += dx
        self.rect.centerx = round(self.position.x)
        collided_wall_x = self.get_colliding_wall(self.rect)
        if collided_wall_x:
            if dx > 0:
                self.rect.right = collided_wall_x.left
            elif dx < 0:
                 self.rect.left = collided_wall_x.right
            self.position.x = self.rect.centerx
        self.on_ground = False
        self.position.y += dy
        self.rect.centery = round(self.position.y)
        collided_wall_y = self.get_colliding_wall(self.rect)
        if collided_wall_y:
            if dy > 0:
                self.rect.bottom = collided_wall_y.top
                self.velocity_y = 0
                self.on_ground = True
            elif dy < 0:
                 self.rect.top = collided_wall_y.bottom
                 self.velocity_y = 0
            self.position.y = self.rect.centery

    def get_colliding_wall(self, rect):
         for wall in self.walls:
             if rect.colliderect(wall):
                 return wall
         return None

    def update(self, *args, **kwargs):
        pass

    def take_damage(self, amount):
        self.health -= amount
        print(f"{self.__class__.__name__} [{id(self)}] получил {amount} урона, осталось {self.health}/{self.max_health}")
        if self.health <= 0:
            self.health = 0
            print(f"{self.__class__.__name__} [{id(self)}] уничтожен.")
            self.kill()

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        print(f"{self.__class__.__name__} [{id(self)}] восстановил {amount} здоровья, стало {self.health}/{self.max_health}")