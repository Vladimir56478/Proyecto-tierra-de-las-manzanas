import pygame
import math
import random

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
        
        # Animación
        self.current_direction = "down"
        self.animation_frame = 0
        self.animation_speed = 0.15
        
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
        else:
            # Moverse hacia el punto de patrulla
            if distance > 0:
                self.vel_x += (dx / distance) * 0.5
                self.vel_y += (dy / distance) * 0.5
    
    def chase_behavior(self, target):
        """Comportamiento de persecución"""
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Moverse hacia el objetivo
            self.vel_x += (dx / distance) * self.speed * 0.8
            self.vel_y += (dy / distance) * self.speed * 0.8
            
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
            # Hacer daño al jugador (esto debería ser manejado por el sistema de juego)
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
        
        # Actualizar física
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Actualizar animación
        if abs(self.vel_x) > 0.1 or abs(self.vel_y) > 0.1:
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 4:  # Asumiendo 4 frames de animación
                self.animation_frame = 0
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja el gusano"""
        if not self.alive:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Color base del gusano
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
        state_text = font.render(self.state, True, (255, 255, 255))
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