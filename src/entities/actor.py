from .entity import Entity

class Actor(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        # Боевые характеристики
        self.attack_power = 10
        self.attack_speed = 1.0  # атак в секунду
        self.critical_chance = 0.05  # 5% шанс крита
        self.critical_multiplier = 1.5  # множитель крита
        
        # Характеристики движения
        self.movement_speed = 5
        self.can_move = True
        
        # Состояния
        self.is_attacking = False
        self.last_attack_time = 0
        
    def can_attack(self, current_time: int) -> bool:
        """Проверка возможности атаки по времени перезарядки"""
        return current_time - self.last_attack_time >= 1000 / self.attack_speed
        
    def get_damage_output(self) -> int:
        """Расчет наносимого урона с учетом крита"""
        import random
        damage = self.attack_power
        if random.random() < self.critical_chance:
            damage *= self.critical_multiplier
        return round(damage)

