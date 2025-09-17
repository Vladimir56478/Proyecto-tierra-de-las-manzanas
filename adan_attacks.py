"""
Sistema de ataques para el personaje Adán
"""
import pygame
import math
from enum import Enum
from typing import List, Optional, Tuple, Any


class AttackType(Enum):
    """Tipos de ataque disponibles para Adán"""
    MELEE = "melee"
    RANGED = "ranged"


class AdanAttack:
    """Sistema de ataques para el personaje Adán"""
    
    def __init__(self, adan_character: Any):
        self.adan = adan_character
        self.attacks: List[Any] = []
        self.last_attack_time = 0
        self.attack_cooldown = 500  # 500ms entre ataques
        
        # Configuración de ataques
        self.melee_damage = 25
        self.melee_range = 80
        self.ranged_damage = 15
        self.ranged_speed = 8
        self.ranged_range = 300
        
    def can_attack(self) -> bool:
        """Verifica si puede atacar (cooldown)"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_attack_time >= self.attack_cooldown
    
    def melee_attack(self, targets: List[Any]) -> bool:
        """Ataque cuerpo a cuerpo de Adán"""
        if not self.can_attack():
            return False
            
        self.last_attack_time = pygame.time.get_ticks()
        
        # Calcular área de ataque basada en dirección
        attack_rect = self.get_attack_area()
        
        # Verificar colisiones con objetivos
        hits = []
        for target in targets:
            target_rect = pygame.Rect(target.x, target.y, 64, 64)
            if attack_rect.colliderect(target_rect):
                target.take_damage(self.melee_damage)
                hits.append(target)
        
        # Crear efecto visual
        self.create_melee_effect()
        
        print(f"🗡️ Adán ataque melee: {len(hits)} objetivos golpeados")
        return len(hits) > 0
    
    def ranged_attack(self, target_x, target_y):
        """Ataque a distancia de Adán"""
        if not self.can_attack():
            return False
            
        self.last_attack_time = pygame.time.get_ticks()
        
        # Calcular dirección hacia el objetivo
        dx = target_x - (self.adan.x + 32)
        dy = target_y - (self.adan.y + 32)
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.ranged_range:
            return False
        
        # Normalizar dirección
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Crear proyectil
        projectile = AdanProjectile(
            self.adan.x + 32, self.adan.y + 32,
            dx * self.ranged_speed, dy * self.ranged_speed,
            self.ranged_damage
        )
        
        self.attacks.append(projectile)
        print(f"🏹 Adán disparo proyectil hacia ({target_x}, {target_y})")
        return True
    
    def get_attack_area(self):
        """Obtiene el área de ataque melee basada en la dirección"""
        if self.adan.current_direction == "up":
            return pygame.Rect(self.adan.x, self.adan.y - self.melee_range, 64, self.melee_range)
        elif self.adan.current_direction == "down":
            return pygame.Rect(self.adan.x, self.adan.y + 64, 64, self.melee_range)
        elif self.adan.current_direction == "left":
            return pygame.Rect(self.adan.x - self.melee_range, self.adan.y, self.melee_range, 64)
        elif self.adan.current_direction == "right":
            return pygame.Rect(self.adan.x + 64, self.adan.y, self.melee_range, 64)
        return pygame.Rect(0, 0, 0, 0)
    
    def create_melee_effect(self):
        """Crea efecto visual para ataque melee"""
        effect = MeleeEffect(self.adan.x, self.adan.y, self.adan.current_direction)
        self.attacks.append(effect)
    
    def update(self, targets):
        """Actualiza proyectiles y efectos"""
        for attack in self.attacks[:]:
            attack.update()
            
            # Si es proyectil, verificar colisiones
            if isinstance(attack, AdanProjectile):
                for target in targets:
                    target_rect = pygame.Rect(target.x, target.y, 64, 64)
                    if attack.get_rect().colliderect(target_rect):
                        target.take_damage(attack.damage)
                        attack.active = False
                        print(f"💥 Proyectil de Adán impactó objetivo")
            
            # Eliminar ataques inactivos
            if not attack.active:
                self.attacks.remove(attack)
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja proyectiles y efectos"""
        for attack in self.attacks:
            attack.draw(screen, camera_x, camera_y)

class AdanProjectile:
    def __init__(self, x, y, vel_x, vel_y, damage):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.damage = damage
        self.active = True
        self.lifetime = 2000  # 2 segundos
        self.created_time = pygame.time.get_ticks()
        self.size = 8
    
    def update(self):
        """Actualiza posición del proyectil"""
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Verificar tiempo de vida
        if pygame.time.get_ticks() - self.created_time > self.lifetime:
            self.active = False
    
    def get_rect(self):
        """Obtiene rectángulo de colisión"""
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja el proyectil"""
        pygame.draw.circle(screen, (255, 255, 0), 
                         (int(self.x - camera_x), int(self.y - camera_y)), self.size)
        # Efecto de brillo
        pygame.draw.circle(screen, (255, 255, 255), 
                         (int(self.x - camera_x), int(self.y - camera_y)), self.size//2)

class MeleeEffect:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.active = True
        self.duration = 200  # 200ms
        self.created_time = pygame.time.get_ticks()
        self.alpha = 255
    
    def update(self):
        """Actualiza el efecto"""
        elapsed = pygame.time.get_ticks() - self.created_time
        if elapsed > self.duration:
            self.active = False
        else:
            # Fade out
            self.alpha = int(255 * (1 - elapsed / self.duration))
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja el efecto de ataque melee"""
        if not self.active:
            return
            
        # Crear superficie con transparencia
        effect_surface = pygame.Surface((80, 80))
        effect_surface.set_alpha(self.alpha)
        effect_surface.fill((255, 100, 100))
        
        # Posición del efecto
        effect_x = self.x - camera_x
        effect_y = self.y - camera_y
        
        # Ajustar posición según dirección
        if self.direction == "up":
            effect_y -= 60
        elif self.direction == "down":
            effect_y += 60
        elif self.direction == "left":
            effect_x -= 60
        elif self.direction == "right":
            effect_x += 60
        
        screen.blit(effect_surface, (effect_x, effect_y))