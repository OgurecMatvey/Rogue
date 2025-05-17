import pygame
import os


def load_animation_frames(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Ошибка: Папка с анимацией не найдена: {folder_path}")
        return []
    frames = []
    try:
        filenames = sorted(os.listdir(folder_path))
        for filename in filenames:
            if filename.endswith('.png'):
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
    return frames

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, walls_list):
         super().__init__()
         script_dir = os.path.dirname(os.path.abspath(__file__))
         # Убедись, что этот путь корректен для твоей структуры проекта
         self.animation_base_folder = os.path.abspath(os.path.join(script_dir, '..', '..', '..', 'rogue', 'assets', 'images', 'characters', 'Skeleton', 'Skeleton_Crusader_1', 'PNG', 'PNG_Sequences')) # Ваш путь
         print(f"DEBUG: Ищем анимации в: {self.animation_base_folder}")

         self.animations = {
             'idle': load_animation_frames(os.path.join(self.animation_base_folder, 'Idle')),
             'walking': load_animation_frames(os.path.join(self.animation_base_folder, 'Walking')),
             'running': load_animation_frames(os.path.join(self.animation_base_folder, 'Running')),
             'slashing': load_animation_frames(os.path.join(self.animation_base_folder, 'Slashing')),
             'falling': load_animation_frames(os.path.join(self.animation_base_folder, 'Falling_Down')),
             'jump_loop': load_animation_frames(os.path.join(self.animation_base_folder, 'Jump_Loop')),
             'jump_start': load_animation_frames(os.path.join(self.animation_base_folder, 'Jump_Start')),
             'hurt': load_animation_frames(os.path.join(self.animation_base_folder, 'Hurt')),
             'run_slashing': load_animation_frames(os.path.join(self.animation_base_folder, 'Run_Slashing')),
             'slashing_in_the_air': load_animation_frames(os.path.join(self.animation_base_folder, 'Slashing_in_The_Air')),
             'sliding': load_animation_frames(os.path.join(self.animation_base_folder, 'Sliding')),
         }
         self.current_animation_name = 'idle'
         self.current_animation = self.animations.get(self.current_animation_name, [])
         self.frame_index = 0
         self.animation_speed_ms = 30
         self.running_animation_speed_ms = 25
         self.slashing_animation_speed_ms = 30

         self.sliding_animation_speed_ms = 50
         self.last_frame_update = pygame.time.get_ticks()

         self.facing_right = True

         if self.current_animation:
             base_image = self.current_animation[self.frame_index]
             self.image = pygame.transform.flip(base_image, not self.facing_right, False)
             self.rect = self.image.get_rect(center=(x, y))
         else:
             print(f"ОШИБКА: Начальная анимация '{self.current_animation_name}' не найдена или пуста!")
             self.image = pygame.Surface([50, 50])
             self.image.fill((255, 0, 0))
             self.rect = self.image.get_rect(center=(x, y))
             self.current_animation = []

         self.max_hp = 100
         self.current_hp = self.max_hp
         self.position = pygame.math.Vector2(self.rect.center)
         self.velocity = pygame.math.Vector2(0, 0)
         self.move_speed = 200
         self.run_speed_multiplier = 1.5
         self.jump_strength = -450
         self.gravity_accel = 1000

         self.walls = walls_list
         self.is_jumping = False
         self.on_ground = False
         self.is_running = False

         self.is_attacking = False
         self.attack_animation_finished = False
         self.attack_cooldown = 500
         self.last_attack_time = 0
         self.attack_damage = 25
         self.attack_range = 50
         self.attack_hitbox_height_ratio = 0.8

         self.is_sliding = False
         self.slide_duration = 500
         self.slide_timer = 0
         self.slide_speed = 500
         self.slide_cooldown = 1000
         self.last_slide_time = 0

    def _set_animation(self, animation_name):
        if animation_name not in self.animations:
            print(f"Предупреждение: Попытка переключиться на несуществующую анимацию '{animation_name}'")
            return

        new_anim_frames = self.animations[animation_name]
        if not new_anim_frames:
            print(
                f"Предупреждение: Анимация '{animation_name}' пуста. Сохранение текущей '{self.current_animation_name}'.")
            return

        if self.current_animation_name != animation_name:
            self.current_animation_name = animation_name
            self.current_animation = new_anim_frames
            self.frame_index = 0
            base_image = self.current_animation[self.frame_index]
            self.image = pygame.transform.flip(base_image, not self.facing_right, False)

            if hasattr(self, 'rect') and self.rect is not None:
                current_center = self.rect.center
                self.rect = self.image.get_rect(center=current_center)

    def _animate(self):
        if not self.current_animation:
            return

        now = pygame.time.get_ticks()
        current_anim_speed = self.animation_speed_ms
        if self.is_running and self.current_animation_name == 'running':
            current_anim_speed = self.running_animation_speed_ms
        elif self.current_animation_name == 'slashing':
            current_anim_speed = self.slashing_animation_speed_ms


        if now - self.last_frame_update > current_anim_speed:
            self.last_frame_update = now
            self.frame_index += 1

            if self.frame_index >= len(self.current_animation):
                if self.current_animation_name == 'slashing':
                    self.frame_index = len(self.current_animation) - 1
                    self.attack_animation_finished = True
                    self.is_attacking = False
                elif self.current_animation_name == 'sliding':
                    self.frame_index = 0
                else:
                    self.frame_index = 0

            new_frame_base_image = self.current_animation[self.frame_index]
            self.image = pygame.transform.flip(new_frame_base_image, not self.facing_right, False)

            if hasattr(self, 'rect') and self.rect is not None:
                current_center = self.rect.center
                self.rect = self.image.get_rect(center=current_center)


    def update(self, dt, enemies_group):
        keys = pygame.key.get_pressed()
        dt_seconds = dt / 1000.0
        now = pygame.time.get_ticks()

        if self.is_attacking and not self.attack_animation_finished:
            self._animate()
            # Если во время атаки, не обрабатываем движение и другие действия
            # Но гравитация должна действовать, если атака в воздухе (это уже сложнее)
            # Для простоты пока оставим так, атака на земле блокирует движение
            if self.on_ground: # Простое допущение: атака на земле останавливает
                 self.velocity.x = 0
            # Применение гравитации и вертикального движения даже во время атаки
            if not self.on_ground:
                self.velocity.y += self.gravity_accel * dt_seconds
            self.position.x += self.velocity.x * dt_seconds # Горизонтальное движение может быть 0
            self.rect.centerx = round(self.position.x)
            self.check_collision('horizontal')
            self.position.x = self.rect.centerx
            self.position.y += self.velocity.y * dt_seconds
            self.rect.centery = round(self.position.y)
            self.check_collision('vertical')
            self.position.y = self.rect.centery
            return
        if self.is_attacking and not self.attack_animation_finished:
            self._animate()
            return


        self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        current_move_speed = self.move_speed
        if self.is_running:
            current_move_speed *= self.run_speed_multiplier

        if self.is_sliding:
            self.slide_timer -= dt
            if self.slide_timer <= 0:
                self.is_sliding = False
                self.velocity.x = 0 # Остановить после подката, или оставить инерцию? Пока останавливаем.
            else:
                # Движение во время подката
                slide_direction = 1 if self.facing_right else -1
                self.velocity.x = self.slide_speed * slide_direction
                # Можно добавить замедление к концу подката, если хотите

            # Гравитация во время подката
            if not self.on_ground:
                self.velocity.y += self.gravity_accel * dt_seconds

            # Применяем движение и коллизии
            self.position.x += self.velocity.x * dt_seconds
            self.rect.centerx = round(self.position.x)
            self.check_collision('horizontal')
            self.position.x = self.rect.centerx

            self.position.y += self.velocity.y * dt_seconds
            self.rect.centery = round(self.position.y)
            self.check_collision('vertical')
            self.position.y = self.rect.centery

            # Устанавливаем анимацию подката
            self._set_animation('sliding')
            self._animate()
            return # Выходим из update, так как подкат обрабатывается

        is_trying_to_move_horizontally = False
        pressed_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        pressed_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        current_horizontal_speed = 0
        if pressed_left and not pressed_right:
            current_horizontal_speed = -current_move_speed
            self.facing_right = False
            is_trying_to_move_horizontally = True
        elif pressed_right and not pressed_left:
            current_horizontal_speed = current_move_speed
            self.facing_right = True
            is_trying_to_move_horizontally = True

        self.velocity.x = current_horizontal_speed

        jump_initiated_this_frame = False

        if keys[pygame.K_SPACE] and self.on_ground:
            self.is_jumping = True
            self.on_ground = False
            self.velocity.y = self.jump_strength
            jump_initiated_this_frame = True

        if keys[pygame.K_c] and self.on_ground and not self.is_sliding and now - self.last_slide_time > self.slide_cooldown:
            if is_trying_to_move_horizontally or self.is_running: # Подкат во время движения или бега
                self.is_sliding = True
                self.slide_timer = self.slide_duration
                self.last_slide_time = now
                # Направление подката уже установлено self.facing_right
                # Можно отменить прыжок, если он был инициирован в тот же кадр
                if jump_initiated_this_frame:
                    self.is_jumping = False
                    self.velocity.y = 0 # Отменяем начальный импульс прыжка
                    self.on_ground = True # Возвращаем на землю для подката
                jump_initiated_this_frame = False # Подкат имеет приоритет
                # Останавливаем вертикальное движение если не прыжок
                if not self.is_jumping: self.velocity.y = 0
        if not self.on_ground:
            self.velocity.y += self.gravity_accel * dt_seconds

        self.position.x += self.velocity.x * dt_seconds
        self.rect.centerx = round(self.position.x)
        self.check_collision('horizontal')
        self.position.x = self.rect.centerx

        self.position.y += self.velocity.y * dt_seconds
        self.rect.centery = round(self.position.y)
        self.check_collision('vertical')
        self.position.y = self.rect.centery

        next_animation_name = self.current_animation_name

        if self.is_sliding:  # Анимация подката имеет приоритет
            next_animation_name = 'sliding'
        elif self.is_attacking and not self.attack_animation_finished:
            next_animation_name = 'slashing'
        elif jump_initiated_this_frame:  # Используем jump_start если прыжок только начался
            next_animation_name = 'jump_start'
            # Логика для jump_start -> jump_loop / falling
        elif self.current_animation_name == 'jump_start':
            if self.animations.get('jump_start') and len(self.animations['jump_start']) > 0 and \
               self.frame_index >= len(self.animations['jump_start']) - 1:
                if self.velocity.y < 0:
                    next_animation_name = 'jump_loop'
                else:
                    next_animation_name = 'falling'
            else:
                next_animation_name = 'jump_start'
        elif not self.on_ground:
            self.is_jumping = True
            if self.velocity.y < 0:
                next_animation_name = 'jump_loop'
            elif self.velocity.y >= 0:
                next_animation_name = 'falling'
        else:
            self.is_jumping = False
            if self.velocity.x != 0:
                if self.is_running:
                    next_animation_name = 'running'
                else:
                    next_animation_name = 'walking'
            else:
                next_animation_name = 'idle'

        if self.current_animation_name == 'slashing' and self.attack_animation_finished:
             pass
        else:
            self._set_animation(next_animation_name)
        self._set_animation(next_animation_name)
        self._animate()


    def check_collision(self, direction):
        if direction == 'vertical':
            self.on_ground = False

        for wall_rect in self.walls:
            if self.rect.colliderect(wall_rect):
                if direction == 'horizontal':
                    if self.velocity.x > 0:
                        self.rect.right = wall_rect.left
                    elif self.velocity.x < 0:
                        self.rect.left = wall_rect.right
                    self.velocity.x = 0
                    self.position.x = self.rect.centerx
                elif direction == 'vertical':
                    if self.velocity.y > 0:
                        self.rect.bottom = wall_rect.top
                        self.velocity.y = 0
                        self.on_ground = True
                        self.is_jumping = False
                    elif self.velocity.y < 0:
                        self.rect.top = wall_rect.bottom
                        self.velocity.y = 0
                    self.position.y = self.rect.centery
        if direction == 'vertical' and not self.on_ground:
            feet_check_offset = 1
            feet_rect = pygame.Rect(self.rect.left, self.rect.bottom, self.rect.width, feet_check_offset)
            for wall_rect in self.walls:
                if feet_rect.colliderect(wall_rect):
                    if self.velocity.y >= 0 :
                        self.rect.bottom = wall_rect.top
                        self.velocity.y = 0
                        self.on_ground = True
                        self.is_jumping = False
                        self.position.y = self.rect.centery
                        break
    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0
        print(f"Игрок получил урон! Текущее ХП: {self.current_hp}/{self.max_hp}")
        if self.current_hp == 0:
            self.die()

    def heal(self, amount):
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        print(f"Игрок исцелился! Текущее ХП: {self.current_hp}/{self.max_hp}")

    def attack(self, enemies_group):
        now = pygame.time.get_ticks()
        # Нельзя атаковать во время подката
        if not self.is_attacking and not self.is_sliding and now - self.last_attack_time > self.attack_cooldown:
            # ... (остальная часть метода attack без изменений) ...
            self.is_attacking = True
            self.attack_animation_finished = False  # Сброс флага перед новой атакой
            self.last_attack_time = now
            self._set_animation('slashing')  # Устанавливаем анимацию атаки
            self.frame_index = 0  # Начинаем анимацию с первого кадра

            # Логика определения hitbox атаки
            hitbox_height = self.rect.height * self.attack_hitbox_height_ratio
            hitbox_top = self.rect.centery - hitbox_height / 2

            if self.facing_right:
                attack_rect = pygame.Rect(self.rect.right, hitbox_top, self.attack_range, hitbox_height)
            else:  # facing left
                attack_rect = pygame.Rect(self.rect.left - self.attack_range, hitbox_top, self.attack_range,
                                          hitbox_height)

            for enemy in enemies_group:
                if attack_rect.colliderect(enemy.rect):
                    print(f"Игрок атаковал {enemy}!")
                    enemy.take_damage(self.attack_damage)
            return True
        return False
    def die(self):
        print("Игрок умер!")

    def dunger_zone(self, kill_zones):
        for zone in kill_zones:
            if self.rect.colliderect(zone):
                self.take_damage(20)
