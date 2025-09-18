import pygame
import math
import random
from PIL import Image
import requests
from io import BytesIO

class WormEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_health = 40
        self.health = self.max_health
        self.speed = 2
        self.attack_damage = 15
        self.attack_range = 60
        self.attack_cooldown = 1500
        self.last_attack_time = 0
        
        # Estados de IA
        self.state = "patrol"  # patrol, chase, attack, hurt
        self.target = None
        self.patrol_points = []
        self.current_patrol = 0
        self.detection_range = 200
        self.give_up_range = 400
        
        # Animación con GIF
        self.current_direction = "down"
        self.animation_frame = 0
        self.animation_speed = 0.15
        self.moving = False
        
        # URL del GIF de movimiento del gusano desde GitHub Issues
        self.worm_gif_url = "https://github.com/user-attachments/assets/c275caea-e0a2-4a45-8eb2-a60485090789"
        
        # Diccionario para almacenar los frames de animación
        self.animations = {}
        self.load_worm_animation()
        
        # Movimiento
        self.vel_x = 0
        self.vel_y = 0
        self.friction = 0.8
        
        # Estado visual
        self.hurt_timer = 0
        self.hurt_duration = 200
        
        # Generar puntos de patrulla aleatorios
        self.generate_patrol_points()
        
        self.alive = True
    
    def load_worm_animation(self):
        """Carga el GIF del gusano y extrae sus frames"""
        print("Cargando animación del gusano desde GitHub...")
        
        try:
            print(f"📥 Descargando GIF del gusano desde GitHub...")
            
            # Descargar el GIF desde GitHub
            response = requests.get(self.worm_gif_url)
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
            
            # Usar los mismos frames para todas las direcciones
            self.animations = {
                "up": frames,
                "down": frames,
                "left": frames,
                "right": frames,
                "idle": [frames[0]] if frames else []  # Primer frame para estado idle
            }
            print(f"✅ Cargada animación del gusano: {len(frames)} frames")
            
        except Exception as e:
            print(f"❌ Error cargando animación del gusano: {e}")
            # Crear frame de respaldo en caso de error
            backup_surface = pygame.Surface((64, 64))
            backup_surface.fill((100, 50, 0))  # Marrón como placeholder
            self.animations = {
                "up": [backup_surface],
                "down": [backup_surface],
                "left": [backup_surface],
                "right": [backup_surface],
                "idle": [backup_surface]
            }
    
    def generate_patrol_points(self):
        """Genera puntos de patrulla aleatorios alrededor de la posición inicial"""
        base_x, base_y = self.x, self.y
        for _ in range(4):
            patrol_x = base_x + random.randint(-200, 200)
            patrol_y = base_y + random.randint(-200, 200)
            self.patrol_points.append((patrol_x, patrol_y))
    
    def find_nearest_player(self, players):
        """Encuentra el jugador más cercano"""
        nearest = None
        min_distance = float('inf')
        
        for player in players:
            distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
            if distance < min_distance:
                min_distance = distance
                nearest = player
        
        return nearest, min_distance
    
    def update_ai(self, players):
        """Actualiza la inteligencia artificial del gusano"""
        if not self.alive:
            return
        
        nearest_player, distance = self.find_nearest_player(players)
        
        # Máquina de estados de IA
        if self.state == "patrol":
            if distance < self.detection_range:
                self.state = "chase"
                self.target = nearest_player
                print(f"🐛 Gusano detectó jugador a {distance:.1f} unidades")
            else:
                self.patrol_behavior()
        
        elif self.state == "chase":
            if distance > self.give_up_range:
                self.state = "patrol"
                self.target = None
                print("🐛 Gusano perdió al jugador")
            elif distance < self.attack_range:
                self.state = "attack"
            else:
                self.chase_behavior(nearest_player)
        
        elif self.state == "attack":
            if distance > self.attack_range * 1.5:
                self.state = "chase"
            else:
                self.attack_behavior(nearest_player)
        
        elif self.state == "hurt":
            # Estado temporal cuando recibe daño
            self.hurt_timer -= 16  # Asumiendo 60 FPS
            if self.hurt_timer <= 0:
                self.state = "chase" if self.target else "patrol"
    
    def patrol_behavior(self):
        """Comportamiento de patrulla"""
        if not self.patrol_points:
            return
        
        target_x, target_y = self.patrol_points[self.current_patrol]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 30:  # Llegó al punto de patrulla
            self.current_patrol = (self.current_patrol + 1) % len(self.patrol_points)
            self.moving = False
        else:
            # Moverse hacia el punto de patrulla
            if distance > 0:
                self.vel_x += (dx / distance) * 0.5
                self.vel_y += (dy / distance) * 0.5
                self.moving = True
    
    def chase_behavior(self, target):
        """Comportamiento de persecución"""
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Moverse hacia el objetivo
            self.vel_x += (dx / distance) * self.speed * 0.8
            self.vel_y += (dy / distance) * self.speed * 0.8
            self.moving = True
            
            # Actualizar dirección de animación
            if abs(dx) > abs(dy):
                self.current_direction = "right" if dx > 0 else "left"
            else:
                self.current_direction = "down" if dy > 0 else "up"
    
    def attack_behavior(self, target):
        """Comportamiento de ataque"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.perform_attack(target)
            self.last_attack_time = current_time
    
    def perform_attack(self, target):
        """Realiza un ataque contra el objetivo"""
        # Verificar si el objetivo está en rango
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.attack_range:
            # Hacer daño al jugador
            if hasattr(target, 'take_damage'):
                target.take_damage(self.attack_damage)
            print(f"🐛 Gusano atacó al jugador! ({self.attack_damage} daño)")
            
            # Empujar al jugador
            if distance > 0:
                push_force = 3
                target.x += (dx / distance) * push_force
                target.y += (dy / distance) * push_force
    
    def take_damage(self, damage):
        """Recibe daño"""
        if not self.alive:
            return
            
        self.health -= damage
        self.hurt_timer = self.hurt_duration
        self.state = "hurt"
        
        # Efecto de empuje cuando recibe daño
        push_x = random.uniform(-2, 2)
        push_y = random.uniform(-2, 2)
        self.vel_x += push_x
        self.vel_y += push_y
        
        print(f"🐛 Gusano recibió {damage} daño (Vida: {self.health}/{self.max_health})")
        
        if self.health <= 0:
            self.alive = False
            print("💀 Gusano eliminado")
    
    def update(self, players):
        """Actualiza el gusano"""
        if not self.alive:
            return
        
        # Actualizar IA
        self.update_ai(players)
        
        # Detectar si se está moviendo
        prev_moving = self.moving
        self.moving = abs(self.vel_x) > 0.1 or abs(self.vel_y) > 0.1
        
        # Actualizar física
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Actualizar animación
        if self.moving:
            # Si se está moviendo, animar normalmente
            self.animation_frame += self.animation_speed
            current_animation = self.current_direction
            if current_animation in self.animations and len(self.animations[current_animation]) > 0:
                if self.animation_frame >= len(self.animations[current_animation]):
                    self.animation_frame = 0
        else:
            # Cuando está quieto, usar el primer frame como estado idle
            self.animation_frame = 0
            self.current_direction = "idle"
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja el gusano"""
        if not self.alive:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Dibujar animación del gusano si está disponible
        if self.current_direction in self.animations and len(self.animations[self.current_direction]) > 0:
            current_frames = self.animations[self.current_direction]
            frame_index = int(self.animation_frame) % len(current_frames)
            current_sprite = current_frames[frame_index]
            
            # Aplicar efecto de daño si está herido
            if self.hurt_timer > 0:
                # Crear superficie temporal para el efecto de daño
                hurt_surface = current_sprite.copy()
                hurt_surface.fill((255, 100, 100), special_flags=pygame.BLEND_ADD)
                screen.blit(hurt_surface, (screen_x, screen_y))
            else:
                screen.blit(current_sprite, (screen_x, screen_y))
        else:
            # Fallback: dibujar representación básica del gusano
            color = (100, 50, 0)  # Marrón
            
            # Efecto de daño
            if self.hurt_timer > 0:
                color = (255, 100, 100)  # Rojo cuando está herido
            
            # Dibujar cuerpo del gusano (varios segmentos)
            segments = 3
            segment_size = 20
            
            for i in range(segments):
                segment_x = screen_x + i * segment_size - 10
                segment_y = screen_y
                segment_color = tuple(max(0, c - i * 20) for c in color)
                
                pygame.draw.circle(screen, segment_color, 
                                 (segment_x, segment_y + segment_size), segment_size - i * 2)
        
        # Dibujar barra de vida
        if self.health < self.max_health:
            bar_width = 60
            bar_height = 6
            bar_x = screen_x - bar_width // 2 + 32
            bar_y = screen_y - 10
            
            # Fondo de la barra
            pygame.draw.rect(screen, (100, 0, 0), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Vida actual
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, (0, 255, 0), 
                           (bar_x, bar_y, health_width, bar_height))
        
        # Indicador de estado (debug)
        font = pygame.font.Font(None, 20)
        state_text = font.render(f"{self.state} ({'moving' if self.moving else 'idle'})", True, (255, 255, 255))
        screen.blit(state_text, (screen_x, screen_y - 30))
    
    def get_rect(self):
        """Obtiene rectángulo de colisión"""
        return pygame.Rect(self.x, self.y, 64, 64)

class WormSpawner:
    def __init__(self, max_worms=5):
        self.worms = []
        self.max_worms = max_worms
        self.spawn_cooldown = 10000  # 10 segundos
        self.last_spawn_time = 0
        self.spawn_areas = []  # Áreas donde pueden aparecer gusanos
    
    def add_spawn_area(self, x, y, width, height):
        """Añade un área donde pueden aparecer gusanos"""
        self.spawn_areas.append((x, y, width, height))
    
    def spawn_worm(self, players):
        """Intenta generar un nuevo gusano"""
        if len(self.worms) >= self.max_worms:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time < self.spawn_cooldown:
            return
        
        if not self.spawn_areas:
            return
        
        # Elegir área de spawn aleatoria
        spawn_area = random.choice(self.spawn_areas)
        spawn_x = random.randint(spawn_area[0], spawn_area[0] + spawn_area[2])
        spawn_y = random.randint(spawn_area[1], spawn_area[1] + spawn_area[3])
        
        # Verificar que no esté muy cerca de los jugadores
        too_close = False
        for player in players:
            distance = math.sqrt((spawn_x - player.x)**2 + (spawn_y - player.y)**2)
            if distance < 150:
                too_close = True
                break
        
        if not too_close:
            new_worm = WormEnemy(spawn_x, spawn_y)
            self.worms.append(new_worm)
            self.last_spawn_time = current_time
            print(f"🐛 Nuevo gusano apareció en ({spawn_x}, {spawn_y})")
    
    def update(self, players):
        """Actualiza todos los gusanos"""
        # Actualizar gusanos existentes
        for worm in self.worms[:]:
            if worm.alive:
                worm.update(players)
            else:
                self.worms.remove(worm)
        
        # Intentar generar nuevos gusanos
        self.spawn_worm(players)
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja todos los gusanos"""
        for worm in self.worms:
            worm.draw(screen, camera_x, camera_y)
    
    def get_worms(self):
        """Obtiene lista de gusanos vivos"""
        return [worm for worm in self.worms if worm.alive]