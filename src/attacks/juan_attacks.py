import pygame
import math
from PIL import Image
import requests
from io import BytesIO

class JuanAttack:
    def __init__(self, character):
        self.character = character
        self.combo_hits = []
        self.special_effects = []
        self.last_attack_time = 0
        self.attack_cooldown = 300
        self.combo_count = 0
        self.max_combo = 3
        
        # Variables para animaciones de ataque
        self.is_attacking = False
        self.attack_animation_frame = 0
        self.attack_animation_speed = 0.3
        self.attack_direction = "down"
        
        # URLs de los GIFs de ataque de Juan desde GitHub Issues
        self.attack_gif_urls = {
            "up": "https://github.com/user-attachments/assets/dd75fe07-fdbc-44af-b96c-e02d24f1a541",
            "down": "https://github.com/user-attachments/assets/bcd29b68-808b-4840-a6bb-1691c94581b1", 
            "left": "https://github.com/user-attachments/assets/e1db84b2-d37d-4bc4-87f8-cce531c51300",
            "right": "https://github.com/user-attachments/assets/dd1ed297-05f1-468b-83fb-266d510595f3"
        }
        
        # Diccionario para almacenar los frames de cada dirección de ataque
        self.attack_animations = {}
        self.load_attack_animations()
        
    def load_attack_animations(self):
        """Carga todos los GIFs de ataque y extrae sus frames"""
        print("Cargando animaciones de ataque de Juan desde GitHub...")
        
        for direction, url in self.attack_gif_urls.items():
            try:
                print(f"📥 Descargando ataque {direction} desde GitHub...")
                
                # Descargar el GIF desde GitHub
                response = requests.get(url)
                response.raise_for_status()
                gif_data = BytesIO(response.content)
                
                # Abrir el GIF con PIL
                gif = Image.open(gif_data)
                frames = []
                
                # Extraer todos los frames del GIF
                for frame_num in range(gif.n_frames):
                    gif.seek(frame_num)
                    frame = gif.copy().convert("RGBA")
                    
                    # Convertir PIL image a superficie de Pygame
                    frame_data = frame.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
                    
                    # Hacer transparente el fondo blanco
                    pygame_surface = pygame_surface.convert_alpha()
                    pygame_surface.set_colorkey((255, 255, 255))
                    
                    frames.append(pygame_surface)
                
                self.attack_animations[direction] = frames
                print(f"✅ Cargada animación de ataque '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando ataque {direction}: {e}")
                # Crear frame de respaldo en caso de error
                backup_surface = pygame.Surface((64, 64))
                backup_surface.fill((0, 255, 0))  # Verde como placeholder
                self.attack_animations[direction] = [backup_surface]
    
    def start_attack_animation(self, direction):
        """Inicia la animación de ataque en la dirección especificada"""
        self.is_attacking = True
        self.attack_direction = direction
        self.attack_animation_frame = 0
        
    def update_attack_animation(self):
        """Actualiza la animación de ataque"""
        if self.is_attacking:
            self.attack_animation_frame += self.attack_animation_speed
            
            # Si terminó la animación, resetear
            if (self.attack_direction in self.attack_animations and 
                self.attack_animation_frame >= len(self.attack_animations[self.attack_direction])):
                self.is_attacking = False
                self.attack_animation_frame = 0
    
    def handle_attack_input(self, keys_pressed, enemies):
        """Maneja la entrada de ataque (tecla Z)"""
        if keys_pressed[pygame.K_z]:
            # Determinar dirección de ataque basada en la dirección actual del personaje
            direction = getattr(self.character, 'current_direction', 'down')
            
            # Iniciar animación de ataque
            self.start_attack_animation(direction)
            
            # Realizar ataque combo
            return self.combo_attack(enemies)
        
        return False
        
    def combo_attack(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        self.combo_count = (self.combo_count + 1) % self.max_combo
        
        base_damage = 15 + (self.combo_count * 5)
        range_multiplier = 1 + (self.combo_count * 0.5)
        
        # Crear área de ataque direccional
        attack_range = int(70 * range_multiplier)
        if self.attack_direction == "up":
            attack_rect = pygame.Rect(self.character.x - 20, self.character.y - attack_range, 104, attack_range + 32)
        elif self.attack_direction == "down":
            attack_rect = pygame.Rect(self.character.x - 20, self.character.y + 32, 104, attack_range)
        elif self.attack_direction == "left":
            attack_rect = pygame.Rect(self.character.x - attack_range, self.character.y - 20, attack_range + 32, 104)
        elif self.attack_direction == "right":
            attack_rect = pygame.Rect(self.character.x + 32, self.character.y - 20, attack_range, 104)
        else:
            # Ataque circular por defecto
            attack_rect = pygame.Rect(
                self.character.x - attack_range//2, 
                self.character.y - attack_range//2, 
                attack_range + 64, 
                attack_range + 64
            )
        
        combo_effect = {
            'rect': attack_rect,
            'start_time': current_time,
            'duration': 150,
            'combo_level': self.combo_count,
            'direction': self.attack_direction
        }
        self.combo_hits.append(combo_effect)
        
        hit_enemy = False
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 64, 64)
            if attack_rect.colliderect(enemy_rect):
                enemy.take_damage(base_damage)
                hit_enemy = True
                print(f"👊 Juan combo x{self.combo_count + 1} hacia {self.attack_direction} ({base_damage} daño)")
        
        return hit_enemy
    
    def special_attack(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown * 2:
            return False
        
        self.last_attack_time = current_time
        
        special_range = 150
        attack_rect = pygame.Rect(
            self.character.x - special_range//2, 
            self.character.y - special_range//2, 
            special_range + 64, 
            special_range + 64
        )
        
        special_effect = {
            'rect': attack_rect,
            'start_time': current_time,
            'duration': 300,
            'type': 'special'
        }
        self.special_effects.append(special_effect)
        
        special_damage = 35
        hit_enemy = False
        
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 64, 64)
            if attack_rect.colliderect(enemy_rect):
                enemy.take_damage(special_damage)
                hit_enemy = True
                print(f"💥 Juan ataque especial ({special_damage} daño)")
        
        self.combo_count = 0
        
        return hit_enemy
    
    def update(self, enemies):
        current_time = pygame.time.get_ticks()
        
        # Actualizar animación de ataque
        self.update_attack_animation()
        
        self.combo_hits = [hit for hit in self.combo_hits 
                          if current_time - hit['start_time'] < hit['duration']]
        
        self.special_effects = [effect for effect in self.special_effects 
                              if current_time - effect['start_time'] < effect['duration']]
    
    def draw(self, screen, camera_x, camera_y):
        current_time = pygame.time.get_ticks()
        
        # Dibujar animación de ataque si está activa
        if self.is_attacking and self.attack_direction in self.attack_animations:
            current_frames = self.attack_animations[self.attack_direction]
            if len(current_frames) > 0:
                frame_index = int(self.attack_animation_frame) % len(current_frames)
                current_sprite = current_frames[frame_index]
                
                # Dibujar la animación de ataque en la posición del personaje
                attack_x = int(self.character.x - camera_x)
                attack_y = int(self.character.y - camera_y)
                screen.blit(current_sprite, (attack_x, attack_y))
        
        for hit in self.combo_hits:
            progress = (current_time - hit['start_time']) / hit['duration']
            alpha = int(255 * (1 - progress))
            
            colors = [(100, 255, 100), (150, 255, 150), (200, 255, 200)]
            color = colors[hit['combo_level']]
            
            effect_surface = pygame.Surface((hit['rect'].width, hit['rect'].height))
            effect_surface.set_alpha(alpha)
            effect_surface.fill(color)
            
            screen.blit(effect_surface, (hit['rect'].x - camera_x, hit['rect'].y - camera_y))
        
        for effect in self.special_effects:
            progress = (current_time - effect['start_time']) / effect['duration']
            alpha = int(255 * (1 - progress))
            
            effect_surface = pygame.Surface((effect['rect'].width, effect['rect'].height))
            effect_surface.set_alpha(alpha)
            effect_surface.fill((255, 255, 100))
            
            screen.blit(effect_surface, (effect['rect'].x - camera_x, effect['rect'].y - camera_y))
    
    def draw_ui(self, screen):
        font = pygame.font.Font(None, 24)
        
        combo_text = f"Combo: {self.combo_count + 1}/{self.max_combo}"
        combo_surface = font.render(combo_text, True, (100, 255, 100))
        screen.blit(combo_surface, (300, 10))
        
        current_time = pygame.time.get_ticks()
        cooldown_remaining = max(0, self.attack_cooldown - (current_time - self.last_attack_time))
        if cooldown_remaining > 0:
            cooldown_text = f"Cooldown: {cooldown_remaining}ms"
            cooldown_surface = font.render(cooldown_text, True, (255, 255, 100))
            screen.blit(cooldown_surface, (300, 35))