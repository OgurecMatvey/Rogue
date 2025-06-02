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
        self.animation_base_folder = os.path.abspath(
            os.path.join(script_dir, '..', '..', '..', 'rogue', 'assets', 'images', 'characters', 'Skeleton',
                         'Skeleton_Crusader_1', 'PNG', 'PNG_Sequences'))
        print(f"DEBUG: Ищем анимации в: {self.animation_base_folder}")

        self.jump_sound = None
        self.hit_sound = None
        self.walk_sound = None
        self.sprint_sound = None

        # Инициализация канала для звуков движения
        try:
            self.movement_sound_channel = pygame.mixer.Channel(0)  # Используем канал 0
        except pygame.error as e:
            print(f"Ошибка инициализации звукового канала: {e}")
            self.movement_sound_channel = None  # Обработка случая, если каналы не могут быть использованы

        self.current_playing_movement_sound_type = None  # 'walk', 'sprint' или None

        try:
            base_sound_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'rogue', 'assets', 'sounds'))
            print(f"МУЗЫКА - {base_sound_path}")

            jump_sound_file = os.path.join(base_sound_path, 'moss_knight_jump.wav')
            hit_sound_file = os.path.join(base_sound_path, 'PlayerHit.mp3')
            walk_sound_file = os.path.join(base_sound_path, 'grass_move_3.wav')
            sprint_sound_file = os.path.join(base_sound_path, 'hero_run_footsteps_grass.wav')

            if os.path.exists(hit_sound_file):
                self.hit_sound = pygame.mixer.Sound(hit_sound_file)
                print(f"Звук удара загружен: {hit_sound_file}")
                self.hit_sound.set_volume(0.4)  # Установка громкости напрямую на объекте Sound
            else:
                print(f"Файл звука не найден: {hit_sound_file}")

            if os.path.exists(jump_sound_file):
                self.jump_sound = pygame.mixer.Sound(jump_sound_file)
                print(f"Звук прыжка загружен: {jump_sound_file}")
                if self.jump_sound:
                    self.jump_sound.set_volume(0.2)
            else:
                print(f"Файл звука не найден: {jump_sound_file}")

            if os.path.exists(walk_sound_file):
                self.walk_sound = pygame.mixer.Sound(walk_sound_file)
                print(f"Звук ходьбы загружен: {walk_sound_file}")
                if self.walk_sound:
                    self.walk_sound.set_volume(0.3)  # Немного тише для ходьбы
            else:
                print(f"Файл звука не найден: {walk_sound_file}")

            if os.path.exists(sprint_sound_file):
                self.sprint_sound = pygame.mixer.Sound(sprint_sound_file)
                print(f"Звук бега загружен: {sprint_sound_file}")
                if self.sprint_sound:
                    self.sprint_sound.set_volume(0.4)  # Немного громче для бега
            else:
                print(f"Файл звука не найден: {sprint_sound_file}")

        except pygame.error as e:
            print(f"Ошибка загрузки звуков игрока в Pygame: {e}")
        except Exception as e:
            print(f"Произошла другая ошибка при загрузке звуков игрока: {e}")

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
            'slashing_in_the_air': load_animation_frames(
                os.path.join(self.animation_base_folder, 'Slashing_in_The_Air')),
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
            collision_width = self.rect.width * 0.5
            collision_height = self.rect.height * 0.7
            self.collision_rect = pygame.Rect(0, 0, collision_width, collision_height)
            self.collision_rect.center = self.rect.center

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
            if self.current_animation:
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
        elif self.current_animation_name == 'sliding':
            current_anim_speed = self.sliding_animation_speed_ms

        if now - self.last_frame_update > current_anim_speed:
            self.last_frame_update = now
            self.frame_index += 1

            if self.frame_index >= len(self.current_animation):
                if self.current_animation_name == 'slashing':
                    self.frame_index = len(self.current_animation) - 1
                    self.attack_animation_finished = True
                elif self.current_animation_name == 'sliding':
                    self.frame_index = 0
                else:
                    self.frame_index = 0

            if self.current_animation:
                new_frame_base_image = self.current_animation[self.frame_index]
                self.image = pygame.transform.flip(new_frame_base_image, not self.facing_right, False)

                if hasattr(self, 'rect') and self.rect is not None:
                    current_center = self.rect.center
                    self.rect = self.image.get_rect(center=current_center)
                    if hasattr(self, 'collision_rect'):
                        self.collision_rect.center = self.rect.center

    def update(self, dt, enemies_group):
        keys = pygame.key.get_pressed()
        dt_seconds = dt / 1000.0
        now = pygame.time.get_ticks()

        if self.is_attacking and not self.attack_animation_finished:
            self._animate()
            if self.on_ground:
                self.velocity.x *= 0.1

            if not self.on_ground:
                self.velocity.y += self.gravity_accel * dt_seconds

            self.position.x += self.velocity.x * dt_seconds
            self.collision_rect.centerx = round(self.position.x)
            self.check_collision('horizontal')
            self.position.x = self.collision_rect.centerx

            self.position.y += self.velocity.y * dt_seconds
            self.collision_rect.centery = round(self.position.y)
            self.check_collision('vertical')
            self.position.y = self.collision_rect.centery

            self.rect.center = self.collision_rect.center
            return

        if self.is_attacking and self.attack_animation_finished:
            self.is_attacking = False

        self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        current_move_speed = self.move_speed
        if self.is_running and not self.is_sliding:
            current_move_speed *= self.run_speed_multiplier

        if self.is_sliding:
            self.slide_timer -= dt
            if self.slide_timer <= 0:
                self.is_sliding = False
                self.velocity.x = 0
            else:
                slide_direction = 1 if self.facing_right else -1
                self.velocity.x = self.slide_speed * slide_direction
                if self.movement_sound_channel and self.movement_sound_channel.get_busy():
                    self.movement_sound_channel.stop()
                    self.current_playing_movement_sound_type = None

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

            self._set_animation('sliding')
            if hasattr(self, 'collision_rect'):
                self.collision_rect.center = self.rect.center
            self._animate()
            return

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

        if self.movement_sound_channel:
            target_sound_type = None
            if is_trying_to_move_horizontally and self.on_ground and not self.is_sliding and not self.is_attacking:
                if self.is_running:
                    target_sound_type = 'sprint'
                else:
                    target_sound_type = 'walk'

            if self.current_playing_movement_sound_type != target_sound_type:
                self.movement_sound_channel.stop()
                if target_sound_type == 'walk' and self.walk_sound:
                    self.movement_sound_channel.play(self.walk_sound, loops=-1)
                    self.current_playing_movement_sound_type = 'walk'
                elif target_sound_type == 'sprint' and self.sprint_sound:
                    self.movement_sound_channel.play(self.sprint_sound, loops=-1)
                    self.current_playing_movement_sound_type = 'sprint'
                else:
                    self.current_playing_movement_sound_type = None
            elif not target_sound_type and self.current_playing_movement_sound_type is not None:
                self.movement_sound_channel.stop()
                self.current_playing_movement_sound_type = None

        jump_initiated_this_frame = False
        if keys[pygame.K_SPACE] and self.on_ground and not self.is_sliding and not self.is_attacking:
            self.is_jumping = True
            self.on_ground = False
            self.velocity.y = self.jump_strength
            jump_initiated_this_frame = True
            if self.jump_sound:
                self.jump_sound.play()
            if self.movement_sound_channel and self.movement_sound_channel.get_busy():
                self.movement_sound_channel.stop()
                self.current_playing_movement_sound_type = None

        can_initiate_slide = self.on_ground and not self.is_sliding and not self.is_attacking and now - self.last_slide_time > self.slide_cooldown
        if keys[pygame.K_c] and can_initiate_slide:
            if is_trying_to_move_horizontally or self.is_running:
                self.is_sliding = True
                self.slide_timer = self.slide_duration
                self.last_slide_time = now
                if jump_initiated_this_frame:
                    self.is_jumping = False
                    self.velocity.y = 0
                    self.on_ground = True
                jump_initiated_this_frame = False

                if not self.is_jumping: self.velocity.y = 0

                if self.movement_sound_channel and self.movement_sound_channel.get_busy():
                    self.movement_sound_channel.stop()
                    self.current_playing_movement_sound_type = None

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

        if hasattr(self, 'collision_rect'):
            self.collision_rect.center = self.rect.center

        next_animation_name = self.current_animation_name

        if self.is_sliding:
            next_animation_name = 'sliding'
        elif self.is_attacking and not self.attack_animation_finished:
            next_animation_name = 'slashing'
        elif jump_initiated_this_frame:
            next_animation_name = 'jump_start'
        elif self.current_animation_name == 'jump_start':
            jump_start_anim = self.animations.get('jump_start')
            if jump_start_anim and self.frame_index >= len(jump_start_anim) - 1:
                if self.velocity.y < 0:
                    next_animation_name = 'jump_loop'
                else:
                    next_animation_name = 'falling'
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

        if self.current_animation_name != next_animation_name or \
                (
                        self.is_attacking and not self.attack_animation_finished and self.current_animation_name != 'slashing'):
            self._set_animation(next_animation_name)

        self._animate()

    def check_collision(self, direction):
        original_rect_center = self.rect.center

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

        if hasattr(self, 'collision_rect'):
            self.collision_rect.center = self.rect.center

        if direction == 'vertical' and not self.on_ground and self.velocity.y >= 0:
            feet_check_offset = 2
            feet_rect = pygame.Rect(self.rect.left, self.rect.bottom, self.rect.width, feet_check_offset)
            for wall_rect in self.walls:
                if feet_rect.colliderect(wall_rect):
                    self.rect.bottom = wall_rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.is_jumping = False
                    self.position.y = self.rect.centery
                    if hasattr(self, 'collision_rect'):
                        self.collision_rect.center = self.rect.center
                    break

    def take_damage(self, amount):
        if self.is_sliding:
            return
        self.current_hp -= amount
        self._set_animation('hurt')
        if self.current_hp < 0:
            self.current_hp = 0
        print(f"Игрок получил урон! Текущее ХП: {self.current_hp}/{self.max_hp}")
        if self.current_hp == 0:
            self.die()
    def respawn(self, spawn_point, current_walls):
        print(f"Игрок респавнится в: {spawn_point}")
        self.current_hp = self.max_hp
        self.position = pygame.math.Vector2(spawn_point)
        self.rect.center = self.position

        if hasattr(self, 'collision_rect'):
            self.collision_rect.center = self.rect.center

        self.velocity = pygame.math.Vector2(0, 0)
        self.is_jumping = False
        self.is_attacking = False
        self.attack_animation_finished = False
        self.is_sliding = False
        self.slide_timer = 0

        self._set_animation('idle')

        #self.walls = current_walls

        #self.check_collision('vertical')
        #self.position.x = self.rect.centerx
        #self.position.y = self.rect.centery
        #if hasattr(self, 'collision_rect'):
            #self.collision_rect.center = self.rect.center

        #if self.movement_sound_channel and self.movement_sound_channel.get_busy():
            #self.movement_sound_channel.stop()
            #self.current_playing_movement_sound_type = None

    def heal(self, amount):
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        print(f"Игрок исцелился! Текущее ХП: {self.current_hp}/{self.max_hp}")

    def attack(self, enemies_group):
        now = pygame.time.get_ticks()
        if not self.is_attacking and not self.is_sliding and now - self.last_attack_time > self.attack_cooldown:
            self.is_attacking = True
            self.attack_animation_finished = False
            self.last_attack_time = now
            self._set_animation('slashing')
            self.frame_index = 0

            if self.hit_sound:
                self.hit_sound.play()

            if self.movement_sound_channel and self.movement_sound_channel.get_busy():
                self.movement_sound_channel.stop()
                self.current_playing_movement_sound_type = None

            hitbox_height = self.rect.height * self.attack_hitbox_height_ratio
            hitbox_top = self.rect.centery - hitbox_height / 2

            if self.facing_right:
                attack_rect = pygame.Rect(self.rect.right, hitbox_top, self.attack_range, hitbox_height)
            else:
                attack_rect = pygame.Rect(self.rect.left - self.attack_range, hitbox_top, self.attack_range,
                                          hitbox_height)

            for enemy in enemies_group:
                if hasattr(enemy, 'collision_rect'):
                    if attack_rect.colliderect(enemy.collision_rect):
                        print(f"Игрок атаковал {enemy}!")
                        enemy.take_damage(self.attack_damage)
                elif attack_rect.colliderect(enemy.rect):
                    print(f"Игрок атаковал {enemy} (используя rect)!")
                    enemy.take_damage(self.attack_damage)
            return True
        return False

    def die(self):
        print("Игрок умер!")

    def dunger_zone(self, kill_zones):
        for zone in kill_zones:
            if hasattr(self, 'collision_rect') and self.collision_rect.colliderect(zone):
                self.take_damage(100)
                break
            elif self.rect.colliderect(zone):
                self.take_damage(100)
                break

    def in_portal(self, portal):
        for zone in portal:
            if hasattr(self, 'collision_rect') and self.collision_rect.colliderect(zone):
                return False
            elif self.rect.colliderect(zone):
                return False
            else:
                return True