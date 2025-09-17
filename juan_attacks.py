import pygame
import math
from enum import Enum

class JuanAttackType(Enum):
    COMBO = "combo"
    SPECIAL = "special"

class JuanAttack:
    def __init__(self, juan_character):
        self.juan = juan_character
        self.attacks = []
        self.last_attack_time = 0
        self.attack_cooldown = 400  # 400ms entre ataques
        
        # Sistema de combo
        self.combo_count = 0
        self.combo_timeout = 1500  # 1.5s para mantener combo
        self.last_combo_time = 0
        
        # Configuración de ataques
        self.combo_damage = [20, 25, 35]  # Daño progresivo del combo
        self.combo_range = 90
        self.special_damage = 50
        self.special_range = 150
        self.special_cooldown = 3000  # 3s para ataque especial
        self.last_special_time = 0
        
    def can_attack(self):
        """Verifica si puede atacar (cooldown)"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_attack_time >= self.attack_cooldown
    
    def can_special_attack(self):
        """Verifica si puede usar ataque especial"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_special_time >= self.special_cooldown
    
    def combo_attack(self, targets):
        """Sistema de combo de Juan"""
        if not self.can_attack():
            return False
        
        current_time = pygame.time.get_ticks()
        self.last_attack_time = current_time
        
        # Verificar si el combo continúa
        if current_time - self.last_combo_time > self.combo_timeout:
            self.combo_count = 0
        
        self.last_combo_time = current_time
        
        # Incrementar combo
        self.combo_count = min(self.combo_count + 1, len(self.combo_damage))
        damage = self.combo_damage[self.combo_count - 1]
        
        # Calcular área de ataque
        attack_rect = self.get_combo_area()
        
        # Verificar colisiones
        hits = []
        for target in targets:
            target_rect = pygame.Rect(target.x, target.y, 64, 64)
            if attack_rect.colliderect(target_rect):
                target.take_damage(damage)
                hits.append(target)
        
        # Crear efecto visual
        self.create_combo_effect()
        
        print(f"👊 Juan combo x{self.combo_count}: {len(hits)} objetivos golpeados ({damage} daño)")
        return len(hits) > 0
    
    def special_attack(self, targets):
        """Ataque especial de Juan (área amplia)"""
        if not self.can_attack() or not self.can_special_attack():
            return False
        
        current_time = pygame.time.get_ticks()
        self.last_attack_time = current_time
        self.last_special_time = current_time
        
        # Reset combo
        self.combo_count = 0
        
        # Ataque en área amplia
        center_x = self.juan.x + 32
        center_y = self.juan.y + 32
        
        hits = []
        for target in targets:
            target_center_x = target.x + 32
            target_center_y = target.y + 32
            
            distance = math.sqrt((center_x - target_center_x)**2 + (center_y - target_center_y)**2)
            if distance <= self.special_range:
                target.take_damage(self.special_damage)
                hits.append(target)
        
        # Crear efecto especial
        self.create_special_effect()
        
        print(f"⚡ Juan ataque especial: {len(hits)} objetivos golpeados")
        return len(hits) > 0
    
    def get_combo_area(self):
        """Obtiene área de ataque combo"""
        range_size = self.combo_range + (self.combo_count * 10)  # Rango aumenta con combo
        
        if self.juan.current_direction == "down":  # Juan tiene direcciones invertidas
            return pygame.Rect(self.juan.x, self.juan.y - range_size, 64, range_size)
        elif self.juan.current_direction == "up":
            return pygame.Rect(self.juan.x, self.juan.y + 64, 64, range_size)
        elif self.juan.current_direction == "right":
            return pygame.Rect(self.juan.x - range_size, self.juan.y, range_size, 64)
        elif self.juan.current_direction == "left":
            return pygame.Rect(self.juan.x + 64, self.juan.y, range_size, 64)
        return pygame.Rect(0, 0, 0, 0)
    
    def create_combo_effect(self):
        """Crea efecto visual para combo"""
        effect = ComboEffect(self.juan.x, self.juan.y, self.juan.current_direction, self.combo_count)
        self.attacks.append(effect)
    
    def create_special_effect(self):
        """Crea efecto visual para ataque especial"""
        effect = SpecialEffect(self.juan.x + 32, self.juan.y + 32, self.special_range)
        self.attacks.append(effect)
    
    def update(self, targets):
        """Actualiza efectos de ataque"""
        for attack in self.attacks[:]:
            attack.update()
            if not attack.active:
                self.attacks.remove(attack)
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja efectos de ataque"""
        for attack in self.attacks:
            attack.draw(screen, camera_x, camera_y)
    
    def draw_ui(self, screen):
        """Dibuja UI de combo y cooldowns"""
        font = pygame.font.Font(None, 24)
        
        # Mostrar combo
        if self.combo_count > 0:
            combo_text = f"COMBO x{self.combo_count}"
            color = (255, 255 - self.combo_count * 50, 0)  # Más rojo con mayor combo
            text_surface = font.render(combo_text, True, color)
            screen.blit(text_surface, (10, 80))
        
        # Mostrar cooldown especial
        current_time = pygame.time.get_ticks()
        special_remaining = max(0, self.special_cooldown - (current_time - self.last_special_time))
        if special_remaining > 0:
            special_text = f"Especial: {special_remaining/1000:.1f}s"
            text_surface = font.render(special_text, True, (100, 100, 255))
            screen.blit(text_surface, (10, 110))
        else:
            text_surface = font.render("Especial: LISTO", True, (0, 255, 0))
            screen.blit(text_surface, (10, 110))

class ComboEffect:
    def __init__(self, x, y, direction, combo_level):
        self.x = x
        self.y = y
        self.direction = direction
        self.combo_level = combo_level
        self.active = True
        self.duration = 300
        self.created_time = pygame.time.get_ticks()
        self.alpha = 255
    
    def update(self):
        elapsed = pygame.time.get_ticks() - self.created_time
        if elapsed > self.duration:
            self.active = False
        else:
            self.alpha = int(255 * (1 - elapsed / self.duration))
    
    def draw(self, screen, camera_x, camera_y):
        if not self.active:
            return
        
        # Color más intenso con mayor combo
        intensity = min(255, 100 + self.combo_level * 50)
        color = (intensity, intensity // 2, 0)
        
        effect_surface = pygame.Surface((100, 100))
        effect_surface.set_alpha(self.alpha)
        effect_surface.fill(color)
        
        effect_x = self.x - camera_x - 18
        effect_y = self.y - camera_y - 18
        
        screen.blit(effect_surface, (effect_x, effect_y))

class SpecialEffect:
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.active = True
        self.duration = 500
        self.created_time = pygame.time.get_ticks()
        self.current_radius = 0
    
    def update(self):
        elapsed = pygame.time.get_ticks() - self.created_time
        if elapsed > self.duration:
            self.active = False
        else:
            # Expandir el efecto
            progress = elapsed / self.duration
            self.current_radius = self.radius * progress
    
    def draw(self, screen, camera_x, camera_y):
        if not self.active:
            return
        
        center_screen_x = int(self.center_x - camera_x)
        center_screen_y = int(self.center_y - camera_y)
        
        # Dibujar múltiples círculos para efecto
        for i in range(3):
            alpha = 100 - i * 30
            radius = max(1, int(self.current_radius) - i * 20)
            if radius > 0:
                pygame.draw.circle(screen, (255, 255, 0), 
                                 (center_screen_x, center_screen_y), radius, 3)