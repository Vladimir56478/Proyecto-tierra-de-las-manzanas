import pygame
import sys
from PIL import Image
import requests
from io import BytesIO

class Character:
    def __init__(self, name, gif_urls, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.speed = 5
        self.current_direction = "down"
        self.moving = False
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.gif_urls = gif_urls
        self.animations = {}
        self.load_animations()
        
    def load_animations(self):
        """Carga todos los GIFs y extrae sus frames"""
        print(f"Cargando animaciones de {self.name}...")
        
        for direction, url in self.gif_urls.items():
            try:
                print(f"📥 Descargando {self.name} {direction} desde GitHub...")
                
                response = requests.get(url)
                response.raise_for_status()
                gif_data = BytesIO(response.content)
                
                gif = Image.open(gif_data)
                frames = []
                
                for frame_num in range(gif.n_frames):
                    gif.seek(frame_num)
                    frame = gif.copy().convert("RGBA")
                    
                    frame_data = frame.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
                    
                    pygame_surface = pygame_surface.convert_alpha()
                    pygame_surface.set_colorkey((255, 255, 255))
                    
                    frames.append(pygame_surface)
                
                self.animations[direction] = frames
                print(f"✅ Cargada animación {self.name} '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando {self.name} {direction}: {e}")
                backup_surface = pygame.Surface((64, 64))
                backup_surface.fill((255, 0, 255))
                self.animations[direction] = [backup_surface]
    
    def update(self, keys_pressed):
        """Actualiza el movimiento y animación del personaje"""
        self.moving = False
        
        # Detectar movimiento y dirección
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.y -= self.speed
            self.current_direction = "up" if self.name == "Adán" else "down"  # Juan tiene direcciones invertidas
            self.moving = True
            
        elif keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.y += self.speed
            self.current_direction = "down" if self.name == "Adán" else "up"
            self.moving = True
            
        elif keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.x -= self.speed
            self.current_direction = "left" if self.name == "Adán" else "right"
            self.moving = True
            
        elif keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.x += self.speed
            self.current_direction = "right" if self.name == "Adán" else "left"
            self.moving = True
        
        # Actualizar frame de animación
        if self.moving:
            self.animation_frame += self.animation_speed
            if self.current_direction in self.animations and len(self.animations[self.current_direction]) > 0:
                if self.animation_frame >= len(self.animations[self.current_direction]):
                    self.animation_frame = 0
        else:
            self.animation_frame = 0
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja al personaje en la pantalla con offset de cámara"""
        if self.current_direction in self.animations and len(self.animations[self.current_direction]) > 0:
            current_frames = self.animations[self.current_direction]
            frame_index = int(self.animation_frame) % len(current_frames)
            current_sprite = current_frames[frame_index]
            
            # Dibujar el sprite con offset de cámara
            screen.blit(current_sprite, (self.x - camera_x, self.y - camera_y))
        else:
            # Placeholder si no hay animación
            placeholder_rect = pygame.Rect(self.x - camera_x, self.y - camera_y, 64, 64)
            color = (255, 165, 0) if self.name == "Adán" else (0, 255, 0)
            pygame.draw.rect(screen, color, placeholder_rect)

class Background:
    def __init__(self, image_url, width, height):
        self.width = width
        self.height = height
        self.image = None
        self.load_background(image_url)
        
    def load_background(self, url):
        """Carga la imagen de fondo desde GitHub"""
        try:
            print("📥 Descargando escenario nivel 1...")
            response = requests.get(url)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            
            # Convertir a superficie de pygame
            image_data = pil_image.tobytes()
            self.image = pygame.image.fromstring(image_data, pil_image.size, pil_image.mode)
            
            print(f"✅ Escenario cargado: {pil_image.size}")
            
        except Exception as e:
            print(f"❌ Error cargando escenario: {e}")
            # Crear fondo de respaldo
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((34, 139, 34))  # Verde bosque
    
    def draw(self, screen, camera_x, camera_y, screen_width, screen_height):
        """Dibuja el fondo con desplazamiento de cámara"""
        if self.image:
            # Calcular posición del fondo
            bg_x = -camera_x % self.width
            bg_y = -camera_y % self.height
            
            # Dibujar múltiples copias del fondo para crear efecto infinito
            for x in range(-self.width, screen_width + self.width, self.width):
                for y in range(-self.height, screen_height + self.height, self.height):
                    screen.blit(self.image, (x + bg_x, y + bg_y))

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 1000
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🍎 Nivel 1 - Tierra de las Manzanas")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # URLs de los personajes desde GitHub
        juan_urls = {
            "up": "https://github.com/user-attachments/assets/9310bb71-1229-4647-b208-b025cced50ec",
            "down": "https://github.com/user-attachments/assets/507e3015-5213-4134-9564-127d2d0641b7", 
            "left": "https://github.com/user-attachments/assets/acf6de12-85b7-41ea-868c-8bb9f227ddbb",
            "right": "https://github.com/user-attachments/assets/10059991-1a75-4a92-8e6c-7a8e6b7e7da0"
        }
        
        adan_urls = {
            "up": "https://github.com/user-attachments/assets/a8b0cb2f-6b0a-460d-aa3e-40a404e02bae",
            "down": "https://github.com/user-attachments/assets/962334b6-0161-499a-b45d-9537cb82f0ee", 
            "left": "https://github.com/user-attachments/assets/6fd20d0d-0bce-46e5-ad48-909275503607",
            "right": "https://github.com/user-attachments/assets/83d3150d-67db-4071-9e46-1f47846f22d0"
        }
        
        # Crear personajes
        self.juan = Character("Juan", juan_urls, 400, 300)
        self.adan = Character("Adán", adan_urls, 500, 300)
        
        # Sistema de alternancia
        self.current_character = self.juan
        self.other_character = self.adan
        
        # Cámara
        self.camera_x = 0
        self.camera_y = 0
        
        # Escenario
        escenario_url = "https://github.com/user-attachments/assets/00593769-04d2-4083-a4dc-261e6a3fb3e6"
        self.background = Background(escenario_url, 1536, 512)
        
        # Control de alternancia
        self.switch_cooldown = 0
        
    def handle_events(self):
        """Maneja todos los eventos del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_TAB and self.switch_cooldown <= 0:
                    # Alternar entre personajes
                    self.switch_character()
                    self.switch_cooldown = 10  # Evitar cambios accidentales
        return True
    
    def switch_character(self):
        """Alterna entre Juan y Adán"""
        if self.current_character == self.juan:
            self.current_character = self.adan
            self.other_character = self.juan
        else:
            self.current_character = self.juan
            self.other_character = self.adan
        
        print(f"🔄 Cambiado a: {self.current_character.name}")
    
    def update(self):
        """Actualiza la lógica del juego"""
        keys_pressed = pygame.key.get_pressed()
        
        # Actualizar personaje activo
        self.current_character.update(keys_pressed)
        
        # Actualizar cámara para seguir al personaje activo
        target_camera_x = self.current_character.x - self.screen_width // 2
        target_camera_y = self.current_character.y - self.screen_height // 2
        
        # Suavizar movimiento de cámara
        self.camera_x += (target_camera_x - self.camera_x) * 0.1
        self.camera_y += (target_camera_y - self.camera_y) * 0.1
        
        # Mantener personajes dentro de límites (opcional)
        # self.current_character.x = max(32, min(self.current_character.x, 2000))
        # self.current_character.y = max(32, min(self.current_character.y, 1000))
        
        # Reducir cooldown de cambio
        if self.switch_cooldown > 0:
            self.switch_cooldown -= 1
    
    def draw(self):
        """Dibuja todo en la pantalla"""
        # Limpiar pantalla
        self.screen.fill((50, 100, 50))
        
        # Dibujar fondo con scroll
        self.background.draw(self.screen, self.camera_x, self.camera_y, self.screen_width, self.screen_height)
        
        # Dibujar personaje inactivo (más transparente)
        other_surface = pygame.Surface((64, 64))
        other_surface.set_alpha(128)  # 50% transparente
        if self.other_character.current_direction in self.other_character.animations:
            frames = self.other_character.animations[self.other_character.current_direction]
            if frames:
                frame = frames[0]  # Primer frame estático
                other_surface.blit(frame, (0, 0))
                self.screen.blit(other_surface, (self.other_character.x - self.camera_x, self.other_character.y - self.camera_y))
        
        # Dibujar personaje activo
        self.current_character.draw(self.screen, self.camera_x, self.camera_y)
        
        # UI e información
        font = pygame.font.Font(None, 36)
        
        # Personaje activo
        active_text = font.render(f"🎮 Jugando: {self.current_character.name}", True, (255, 255, 255))
        self.screen.blit(active_text, (10, 10))
        
        # Instrucciones
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "🎮 Controles:",
            "WASD/Flechas - Mover",
            "TAB - Cambiar personaje",
            "ESC - Salir"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = font_small.render(instruction, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, self.screen_height - 100 + i * 20))
        
        # Información de debug
        debug_text = f"Cámara: ({int(self.camera_x)}, {int(self.camera_y)}) | {self.current_character.name}: ({int(self.current_character.x)}, {int(self.current_character.y)})"
        debug_surface = font_small.render(debug_text, True, (200, 200, 200))
        self.screen.blit(debug_surface, (10, 50))
        
        pygame.display.flip()
    
    def run(self):
        """Bucle principal del juego"""
        print("🚀 Iniciando Nivel 1 - Tierra de las Manzanas...")
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