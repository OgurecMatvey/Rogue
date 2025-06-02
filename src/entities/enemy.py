import pygame
import random
import math
import os
from .entity import Entity

def load_animation_frames(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Ошибка: Папка с анимацией не найдена: {folder_path}")
        return []
    frames = []
    try:
        filenames = sorted(os.listdir(folder_path))
        print(f"Найдены файлы в {folder_path}: {filenames}")
        for filename in filenames:
            if filename.lower().endswith('.png'):
                img_path = os.path.join(folder_path, filename)
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    frames.append(img)
                except pygame.error as e:
                    print(f"Ошибка загрузки изображения {img_path}: {e}")
    except Exception as e:
        print(f"Ошибка при чтении папки {folder_path}: {e}")

    if not frames:
        print(f"Предупреждение: Не найдено кадров PNG в {folder_path}")
    else:
         print(f"Загружено {len(frames)} кадров из {folder_path}")
    return frames

class Enemy(Entity):
    def __init__(self, x, y, wall_rects, player):
        super().__init__(x, y, None, wall_rects)

        self.position = pygame.math.Vector2(x, y)
        self.walls = wall_rects
        self.player = player

        self.is_hurting = False
        self.hurt_start_time = 0
        self.hurt_duration = 300

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.animation_base_folder = os.path.abspath(os.path.join(script_dir, '..', '..', 'assets', 'images', 'characters', 'Golem', 'Golem_1', 'PNG', 'PNG_Sequences'))
        print(f"DEBUG [Enemy]: Базовая папка анимаций: {self.animation_base_folder}")

        self.animations = {
            'idle': load_animation_frames(os.path.join(self.animation_base_folder, 'Idle')),
            'walking': load_animation_frames(os.path.join(self.animation_base_folder, 'Walking')),
            'running': load_animation_frames(os.path.join(self.animation_base_folder, 'Running')),
            'slashing': load_animation_frames(os.path.join(self.animation_base_folder, 'Slashing')),
            'hurt': load_animation_frames(os.path.join(self.animation_base_folder, 'Hurt')),
        }

        self.current_animation_name = 'idle'
        self.current_animation = self.animations.get(self.current_animation_name, [])
        self.frame_index = 0
        self.animation_speed_ms = 50
        self.last_frame_update = pygame.time.get_ticks()
        self.image = None
        self.rect = None

        if self.current_animation:
            self.image = self.current_animation[self.frame_index]
            self.rect = self.image.get_rect(center=self.position)
        else:
            print("ПРЕДУПРЕЖДЕНИЕ: Анимация 'idle' не найдена или пуста!")


        self.max_hp = 50
        self.current_hp = self.max_hp
        self.speed = 1.5
        self.facing_right = True

        self.state = 'idle'
        self.detection_radius = 250
        self.attack_radius = 50
        self.attack_damage = 10
        self.attack_cooldown_ms = 1000
        self.last_attack_time = 0
        self.lose_aggro_radius = 350
        self.max_fall_speed = 10

        self.idle_timer = 0
        self.idle_move_interval = random.randint(2000, 5000)
        self.idle_target_pos = None

    def set_animation(self, name):
        if name != self.current_animation_name and name in self.animations:
            self.current_animation_name = name
            self.current_animation = self.animations[name]
            if self.current_animation:
                self.frame_index = 0
                self.image = self.current_animation[self.frame_index]
            else:
                 print(f"Предупреждение: Анимация '{name}' пуста или не найдена.")
                 self.current_animation_name = 'idle'
                 self.current_animation = self.animations.get('idle', [])
                 self.frame_index = 0


    def animate(self):
        if not self.current_animation:
            return

        now = pygame.time.get_ticks()
        if now - self.last_frame_update > self.animation_speed_ms:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_animation)
            base_image = self.current_animation[self.frame_index]

            if self.facing_right:
                self.image = base_image
            else:
                self.image = pygame.transform.flip(base_image, True, False)

    def update(self, dt):
        now = pygame.time.get_ticks()
        self.velocity_y += self.gravity
        if self.velocity_y > self.max_fall_speed:
             self.velocity_y = self.max_fall_speed

        intended_dx = 0

        if self.is_hurting:
            if now - self.hurt_start_time > self.hurt_duration:
                self.is_hurting = False
            else:
                self.move(intended_dx, self.velocity_y)
                self.animate()
                return
        distance_to_player = self.position.distance_to(self.player.position)
        new_state = self.state


        if self.state == 'idle':
            if distance_to_player <= self.detection_radius:
                new_state = 'chasing'
                self.idle_target_pos = None
            else:
                intended_dx = self.idle_behavior(now)
        elif self.state == 'chasing':
            if distance_to_player <= self.attack_radius:
                new_state = 'attacking'
                self.set_animation('slashing')
            elif distance_to_player > self.lose_aggro_radius:
                 new_state = 'idle'
            else:
                intended_dx = self.move_towards_player()
                self.set_animation('walking')
        elif self.state == 'attacking':
            if distance_to_player > self.attack_radius:
                new_state = 'chasing'
            else:
                self.attack_player(now)
                intended_dx = 0
                self.set_animation('slashing')

        if new_state != self.state:
             print(f"Враг {id(self)} перешел в состояние: {new_state}")
             self.state = new_state
             if self.state == 'idle':
                 self.set_animation('idle')
             elif self.state == 'chasing':
                 self.set_animation('walking')
             elif self.state == 'attacking':
                 self.set_animation('slashing')
        self.move(intended_dx, self.velocity_y)

        if self.state != 'attacking':
             if abs(intended_dx) > 0.1:
                 pass
             elif self.state == 'idle' and self.idle_target_pos is None:
                 self.set_animation('idle')

        self.animate()


    def move_towards_player(self):
        dx = 0
        if self.position != self.player.position:
            try:
                 direction_x = (self.player.position.x - self.position.x)
                 if abs(direction_x) > 1:
                    dx = math.copysign(self.speed, direction_x)
            except ValueError:
                 pass

        if dx > 0: self.facing_right = True
        elif dx < 0: self.facing_right = False

        return dx
    def attack_player(self, current_time):
        if current_time - self.last_attack_time > self.attack_cooldown_ms:
            print(f"Враг {id(self)} атакует игрока!")
            if hasattr(self.player, 'take_damage') and callable(getattr(self.player, 'take_damage')):
                 self.player.take_damage(self.attack_damage)
            else:
                 print(f"Ошибка: У объекта player нет метода take_damage!")

            self.last_attack_time = current_time

    def idle_behavior(self, current_time):
        dx = 0
        self.set_animation('idle')

        if current_time - self.idle_timer > self.idle_move_interval:
            self.idle_timer = current_time
            self.idle_move_interval = random.randint(3000, 7000)

            if random.random() < 0.5:
                wander_dist = 50
                angle = random.uniform(0, 2 * math.pi)
                offset = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * wander_dist
                self.idle_target_pos = self.position + offset
                print(f"Враг {id(self)} решил поблуждать к {self.idle_target_pos}")
            else:
                self.idle_target_pos = None

        if self.idle_target_pos:
            dist_to_target_x = self.idle_target_pos.x - self.position.x

            if abs(dist_to_target_x) > self.speed * 0.5:
                direction_x = math.copysign(1, dist_to_target_x)
                dx = direction_x * self.speed * 0.5

                if dx > 0:
                    self.facing_right = True
                elif dx < 0:
                    self.facing_right = False

                self.set_animation('walking')
            else:
                self.idle_target_pos = None
                self.set_animation('idle')
                dx = 0
        else:
            self.set_animation('idle')

        return dx
    def take_damage(self, amount):
         self.current_hp -= amount
         print(f"Враг {id(self)} получил {amount} урона. Осталось HP: {self.current_hp}")
         if self.current_hp <= 0:
             self.kill()
             print(f"Враг {id(self)} уничтожен.")
         else:
             self.set_animation('hurt')
             self.is_hurting = True
             self.hurt_start_time = pygame.time.get_ticks()