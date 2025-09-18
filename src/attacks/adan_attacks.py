import pygame
import math
from PIL import Image
import requests
from io import BytesIO

class AdanAttack:
    def __init__(self, character):
        self.character = character
        self.projectiles = []
        self.melee_attacks = []
        self.last_attack_time = 0
        self.attack_cooldown = 500
        
        # Variables para animaciones de ataque
        self.is_attacking = False
        self.attack_animation_frame = 0
        self.attack_animation_speed = 0.3
        self.attack_direction = "down"
        
        # URLs de los GIFs de ataque de Adán desde GitHub Issues
        self.attack_gif_urls = {
            "up": "https://github.com/user-attachments/assets/6544be63-1345-4a5a-b4e9-57ec4a18775a",
            "down": "https://github.com/user-attachments/assets/cbce589c-03c0-4bc0-a067-1b769b154fbd", 
            "left": "https://github.com/user-attachments/assets/1b2a5d84-7ef7-4598-ada0-68f21c785b06",
            "right": "https://github.com/user-attachments/assets/b1dcab29-5e9f-46aa-87f2-1690c0986e77"
        }
        
        # Diccionario para almacenar los frames de cada dirección de ataque
        self.attack_animations = {}
        self.load_attack_animations()
        
    def load_attack_animations(self):
        """Carga todos los GIFs de ataque y extrae sus frames"""
        print("Cargando animaciones de ataque de Adán desde GitHub...")
        
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
                backup_surface.fill((255, 0, 0))  # Rojo como placeholder
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
        """Maneja la entrada de ataque (tecla X)"""
        if keys_pressed[pygame.K_x]:
            # Determinar dirección de ataque basada en la dirección actual del personaje
            direction = getattr(self.character, 'current_direction', 'down')
            
            # Iniciar animación de ataque
            self.start_attack_animation(direction)
            
            # Realizar ataque cuerpo a cuerpo
            return self.melee_attack(enemies)
        
        return False
    
    def melee_attack(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        
        # Crear área de ataque más grande y direccional
        attack_range = 80
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
            attack_rect = pygame.Rect(self.character.x - 30, self.character.y - 30, 120, 120)
        
        melee_effect = {
            'rect': attack_rect,
            'start_time': current_time,
            'duration': 200,
            'direction': self.attack_direction
        }
        self.melee_attacks.append(melee_effect)
        
        hit_enemy = False
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 64, 64)
            if attack_rect.colliderect(enemy_rect):
                enemy.take_damage(40)
                hit_enemy = True
                print(f"⚔️ Adán golpeó con ataque cuerpo a cuerpo hacia {self.attack_direction} (40 daño)")
        
        return hit_enemy
    
    def ranged_attack(self, target_x, target_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        
        dx = target_x - (self.character.x + 32)
        dy = target_y - (self.character.y + 32)
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
        
        projectile = {
            'x': self.character.x + 32,
            'y': self.character.y + 32,
            'dx': dx,
            'dy': dy,
            'speed': 400,
            'damage': 25,
            'active': True,
            'start_time': current_time
        }
        self.projectiles.append(projectile)
        print(f"🏹 Adán lanzó proyectil")
        return True
    
    def update(self, enemies):
        current_time = pygame.time.get_ticks()
        dt = 1/60
        
        # Actualizar animación de ataque
        self.update_attack_animation()
        
        for projectile in self.projectiles[:]:
            if not projectile['active']:
                continue
                
            projectile['x'] += projectile['dx'] * projectile['speed'] * dt
            projectile['y'] += projectile['dy'] * projectile['speed'] * dt
            
            projectile_rect = pygame.Rect(projectile['x'] - 5, projectile['y'] - 5, 10, 10)
            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, 64, 64)
                if projectile_rect.colliderect(enemy_rect) and projectile['active']:
                    enemy.take_damage(projectile['damage'])
                    projectile['active'] = False
                    print(f"🎯 Proyectil de Adán impactó ({projectile['damage']} daño)")
                    break
            
            if (projectile['x'] < -100 or projectile['x'] > 1100 or 
                projectile['y'] < -100 or projectile['y'] > 800 or
                current_time - projectile['start_time'] > 3000):
                projectile['active'] = False
        
        self.projectiles = [p for p in self.projectiles if p['active']]
        
        self.melee_attacks = [attack for attack in self.melee_attacks 
                            if current_time - attack['start_time'] < attack['duration']]
    
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
        
        for projectile in self.projectiles:
            if projectile['active']:
                x = int(projectile['x'] - camera_x)
                y = int(projectile['y'] - camera_y)
                pygame.draw.circle(screen, (255, 100, 100), (x, y), 5)
                pygame.draw.circle(screen, (255, 200, 200), (x, y), 3)
        
        for attack in self.melee_attacks:
            progress = (current_time - attack['start_time']) / attack['duration']
            alpha = int(255 * (1 - progress))
            
            effect_surface = pygame.Surface((attack['rect'].width, attack['rect'].height))
            effect_surface.set_alpha(alpha)
            effect_surface.fill((255, 255, 100))
            
            screen.blit(effect_surface, (attack['rect'].x - camera_x, attack['rect'].y - camera_y))