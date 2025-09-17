import pygame
import sys
from PIL import Image
import requests
from io import BytesIO

class JuanCharacter:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.current_direction = "down"  # Cambiar de "idle" a "down" para que aparezca visible
        self.moving = False
        self.animation_frame = 0
        self.animation_speed = 0.2
        
        # URLs de los GIFs de Juan desde GitHub
        self.gif_urls = {
            "up": "https://github.com/user-attachments/assets/9310bb71-1229-4647-b208-b025cced50ec",
            "down": "https://github.com/user-attachments/assets/507e3015-5213-4134-9564-127d2d0641b7", 
            "left": "https://github.com/user-attachments/assets/acf6de12-85b7-41ea-868c-8bb9f227ddbb",
            "right": "https://github.com/user-attachments/assets/10059991-1a75-4a92-8e6c-7a8e6b7e7da0"
        }
        
        # Diccionario para almacenar los frames de cada dirección
        self.animations = {}
        
        # Sistema de salud (será configurado por el juego principal)
        self.max_health = 100
        self.health = self.max_health
        
        # Sistema de invulnerabilidad
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 1000  # 1 segundo
        
        # Nombre para compatibilidad
        self.name = "Juan"
        
        self.load_animations()
        
    def load_animations(self):
        """Carga todos los GIFs y extrae sus frames sin alteraciones"""
        print("Cargando animaciones de Juan...")
        
        for direction, url in self.gif_urls.items():
            try:
                # Descargar el GIF desde GitHub
                response = requests.get(url)
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
                    # Establecer el color blanco como transparente
                    pygame_surface.set_colorkey((255, 255, 255))
                    
                    frames.append(pygame_surface)
                
                self.animations[direction] = frames
                print(f"✅ Cargada animación '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando {direction}: {e}")
                # Crear frame de respaldo con gráficos simples
                self.animations[direction] = self.create_fallback_animation(direction)
        
        # Si no se cargó ninguna animación, crear todas las de respaldo
        if not any(self.animations.values()):
            print("🎨 Creando animaciones de respaldo para Juan...")
            for direction in ["up", "down", "left", "right"]:
                self.animations[direction] = self.create_fallback_animation(direction)
    
    def create_fallback_animation(self, direction):
        """Crea una animación simple como respaldo usando formas geométricas"""
        frames = []
        
        # Crear 4 frames para una animación simple
        for frame_idx in range(4):
            surface = pygame.Surface((64, 64), pygame.SRCALPHA)
            surface.fill((0, 0, 0, 0))  # Transparente
            
            # Cuerpo principal (azul para Juan)
            body_color = (50, 100, 200)  # Azul
            pygame.draw.ellipse(surface, body_color, (16, 20, 32, 40))
            
            # Cabeza
            head_color = (255, 220, 177)  # Color piel
            pygame.draw.circle(surface, head_color, (32, 16), 12)
            
            # Brazos (simple líneas)
            arm_color = (255, 220, 177)
            arm_offset = (frame_idx % 2) * 2 - 1  # Movimiento de brazos
            pygame.draw.line(surface, arm_color, (20, 30), (15 + arm_offset, 35), 3)
            pygame.draw.line(surface, arm_color, (44, 30), (49 - arm_offset, 35), 3)
            
            # Piernas (simple líneas)
            leg_color = (100, 50, 25)  # Marrón
            leg_offset = (frame_idx % 2) * 3 - 1  # Movimiento de piernas
            pygame.draw.line(surface, leg_color, (24, 55), (22 + leg_offset, 62), 4)
            pygame.draw.line(surface, leg_color, (40, 55), (42 - leg_offset, 62), 4)
            
            # Dirección específica - cambiar orientación del personaje
            if direction == "left":
                # Voltear horizontalmente
                surface = pygame.transform.flip(surface, True, False)
            elif direction == "up":
                # Hacer más pequeño (perspectiva)
                surface = pygame.transform.scale(surface, (60, 60))
                new_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
                new_surface.blit(surface, (2, 2))
                surface = new_surface
            
            frames.append(surface)
        
        print(f"✅ Creada animación de respaldo para Juan '{direction}': {len(frames)} frames")
        return frames
    
    def take_damage(self, damage):
        """Recibe daño"""
        if self.invulnerable:
            return False
        
        self.health -= damage
        self.health = max(0, self.health)
        
        # Activar invulnerabilidad temporal
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()
        
        print(f"💔 {self.name} recibió {damage} daño (Vida: {self.health}/{self.max_health})")
        
        if self.health <= 0:
            print(f"💀 {self.name} ha sido derrotado")
            return True  # Indica que el personaje murió
        
        return False
    
    def update(self, keys_pressed):
        """Actualiza el movimiento y animación de Juan"""
        self.moving = False
        old_x, old_y = self.x, self.y
        
        # Actualizar invulnerabilidad
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_time >= self.invulnerable_duration:
                self.invulnerable = False
        
        # Detectar movimiento y dirección
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.y -= self.speed
            self.current_direction = "down"  # Corregido: up muestra down
            self.moving = True
            
        elif keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.y += self.speed
            self.current_direction = "up"  # Corregido: down muestra up
            self.moving = True
            
        elif keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.x -= self.speed
            self.current_direction = "right"  # Corregido: left muestra right
            self.moving = True
            
        elif keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.x += self.speed
            self.current_direction = "left"  # Corregido: right muestra left
            self.moving = True
        
        # Actualizar frame de animación
        if self.moving:
            # Si se está moviendo, animar normalmente
            self.animation_frame += self.animation_speed
            if self.animation_frame >= len(self.animations[self.current_direction]):
                self.animation_frame = 0
        else:
            # Cuando no se mueve, mantener el primer frame pero asegurar que sea visible
            self.animation_frame = 0
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dibuja a Juan en la pantalla con soporte para cámara"""
        if self.current_direction in self.animations and len(self.animations[self.current_direction]) > 0:
            current_frames = self.animations[self.current_direction]
            frame_index = int(self.animation_frame) % len(current_frames)
            current_sprite = current_frames[frame_index]
            
            # Efecto de parpadeo cuando es invulnerable
            if self.invulnerable:
                current_time = pygame.time.get_ticks()
                if (current_time // 100) % 2:  # Parpadear cada 100ms
                    current_sprite = current_sprite.copy()
                    current_sprite.set_alpha(128)  # Semi-transparente
            
            # Dibujar el sprite en la posición actual con offset de cámara
            screen.blit(current_sprite, (self.x - camera_x, self.y - camera_y))
        else:
            # Si no hay animación disponible, dibujar un rectángulo de placeholder
            placeholder_rect = pygame.Rect(self.x - camera_x, self.y - camera_y, 64, 64)
            pygame.draw.rect(screen, (0, 255, 0), placeholder_rect)  # Verde para debug
        
        # Mostrar información de debug
        font = pygame.font.Font(None, 24)
        debug_text = f"Juan - Dir: {self.current_direction} | Frame: {int(self.animation_frame)} | Moving: {self.moving}"
        text_surface = font.render(debug_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

    def draw_health_bar(self, screen, camera_x, camera_y):
        """Dibuja la barra de vida del personaje"""
        if self.health < self.max_health:
            bar_width = 60
            bar_height = 8
            bar_x = self.x - camera_x + 2
            bar_y = self.y - camera_y - 15
            
            # Fondo de la barra
            pygame.draw.rect(screen, (100, 0, 0), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Vida actual
            health_width = int((self.health / self.max_health) * bar_width)
            health_color = (0, 255, 0) if self.health > 30 else (255, 255, 0) if self.health > 15 else (255, 0, 0)
            pygame.draw.rect(screen, health_color, 
                           (bar_x, bar_y, health_width, bar_height))

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 1000
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🎮 Aventuras de Juan - Animaciones GIF")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Crear el personaje Juan en el centro de la pantalla
        start_x = self.screen_width // 2 - 32
        start_y = self.screen_height // 2 - 32
        self.juan = JuanCharacter(start_x, start_y)
        
        # Colores
        self.bg_color = (30, 30, 50)  # Azul oscuro
        
    def handle_events(self):
        """Maneja todos los eventos del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def update(self):
        """Actualiza la lógica del juego"""
        keys_pressed = pygame.key.get_pressed()
        self.juan.update(keys_pressed)
        
        # Mantener a Juan dentro de los límites de la pantalla
        self.juan.x = max(0, min(self.juan.x, self.screen_width - 64))
        self.juan.y = max(0, min(self.juan.y, self.screen_height - 64))
    
    def draw(self):
        """Dibuja todo en la pantalla"""
        # Limpiar pantalla con color de fondo
        self.screen.fill(self.bg_color)
        
        # Dibujar una cuadrícula para referencia visual
        grid_size = 50
        grid_color = (50, 50, 70)
        for x in range(0, self.screen_width, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.screen_height))
        for y in range(0, self.screen_height, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.screen_width, y))
        
        # Dibujar a Juan
        self.juan.draw(self.screen)
        
        # Instrucciones
        font = pygame.font.Font(None, 28)
        instructions = [
            "🎮 Controles:",
            "↑↓←→ o WASD - Mover a Juan",
            "ESC - Salir del juego"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = font.render(instruction, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, self.screen_height - 100 + i * 25))
        
        # Actualizar pantalla
        pygame.display.flip()
    
    def run(self):
        """Bucle principal del juego"""
        print("🚀 Iniciando juego de Juan...")
        print("⏳ Cargando recursos...")
        
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        print("👋 ¡Gracias por jugar!")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import pygame
        import PIL
        import requests
        print("✅ Todas las dependencias están instaladas")
    except ImportError as e:
        print(f"❌ Falta instalar: {e}")
        print("Instala con: pip install pygame pillow requests")
        sys.exit(1)
    
    # Crear y ejecutar el juego
    game = Game()
    game.run()