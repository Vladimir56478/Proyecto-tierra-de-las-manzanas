"""
Tierra de las Manzanas - Nivel 1 (Combate)
Juego 2D desarrollado con pygame
"""
import pygame
import sys
from typing import Dict, List, Optional, Tuple, Any
import random

# Importar módulos del juego
from adan_attacks import AdanAttack
from juan_attacks import JuanAttack
from worm_enemy import WormEnemy, WormSpawner
from utils import (
    ResourceCache, download_with_cache, load_gif_frames, 
    create_backup_surface, clamp, distance, lerp
)
import config

class Character:
    """Representa un personaje jugable en el juego"""
    
    def __init__(self, name: str, gif_urls: Dict[str, str], x: float, y: float, cache: Optional[ResourceCache] = None):
        self.name = name
        self.x = x
        self.y = y
        self.speed = config.CHARACTER_SPEED
        self.current_direction = "down"
        self.moving = False
        self.animation_frame = 0.0
        self.animation_speed = config.ANIMATION_SPEED
        self.gif_urls = gif_urls
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.cache = cache or ResourceCache()
        
        # Sistema de salud
        self.max_health = config.MAX_HEALTH
        self.health = self.max_health
        
        # Invulnerabilidad temporal tras recibir daño
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = config.INVULNERABLE_DURATION
        
        # Estado de carga
        self.animations_loaded = False
        
        self.load_animations()
        
    def load_animations(self) -> None:
        """Carga todos los GIFs y extrae sus frames con sistema de cache"""
        print(f"Cargando animaciones de {self.name}...")
        
        for direction, url in self.gif_urls.items():
            try:
                print(f"📥 Procesando {self.name} {direction}...")
                
                # Descargar con cache
                gif_data = download_with_cache(url, self.cache)
                if not gif_data:
                    print(f"❌ No se pudo descargar {self.name} {direction}")
                    self.animations[direction] = [create_backup_surface()]
                    continue
                
                # Procesar frames
                frames = load_gif_frames(gif_data)
                self.animations[direction] = frames
                
                print(f"✅ Cargada animación {self.name} '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando {self.name} {direction}: {e}")
                self.animations[direction] = [create_backup_surface()]
        
        self.animations_loaded = True
        print(f"✅ Animaciones de {self.name} cargadas completamente")
    
    def take_damage(self, damage: int) -> bool:
        """
        Aplica daño al personaje
        
        Args:
            damage: Cantidad de daño a aplicar
        
        Returns:
            True si el personaje murió, False en caso contrario
        """
        if self.invulnerable:
            return False
        
        self.health = max(0, self.health - damage)
        
        # Activar invulnerabilidad temporal
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()
        
        print(f"💔 {self.name} recibió {damage} daño (Vida: {self.health}/{self.max_health})")
        
        if self.health <= 0:
            print(f"💀 {self.name} ha sido derrotado")
            return True
        
        return False
    
    def update(self, keys_pressed: pygame.key.ScancodeWrapper) -> None:
        """
        Actualiza el movimiento y animación del personaje
        
        Args:
            keys_pressed: Estado actual de las teclas presionadas
        """
        self.moving = False
        
        # Actualizar invulnerabilidad
        self._update_invulnerability()
        
        # Procesar movimiento
        self._process_movement(keys_pressed)
        
        # Actualizar animación
        self._update_animation()
    
    def _update_invulnerability(self) -> None:
        """Actualiza el estado de invulnerabilidad"""
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_time >= self.invulnerable_duration:
                self.invulnerable = False
    
    def _process_movement(self, keys_pressed: pygame.key.ScancodeWrapper) -> None:
        """Procesa el movimiento del personaje"""
        # Detectar movimiento y dirección
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.y -= self.speed
            self.current_direction = "up" if self.name == "Adán" else "down"
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
    
    def _update_animation(self) -> None:
        """Actualiza el frame de animación"""
        if self.moving:
            self.animation_frame += self.animation_speed
            if (self.current_direction in self.animations and 
                len(self.animations[self.current_direction]) > 0):
                if self.animation_frame >= len(self.animations[self.current_direction]):
                    self.animation_frame = 0
        else:
            self.animation_frame = 0
    
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """
        Dibuja al personaje en la pantalla con offset de cámara
        
        Args:
            screen: Superficie donde dibujar
            camera_x: Offset X de la cámara
            camera_y: Offset Y de la cámara
        """
        if not self.animations_loaded:
            # Dibujar placeholder mientras cargan las animaciones
            placeholder_rect = pygame.Rect(
                self.x - camera_x, self.y - camera_y, 
                config.CHARACTER_SIZE, config.CHARACTER_SIZE
            )
            color = (255, 165, 0) if self.name == "Adán" else (0, 255, 0)
            pygame.draw.rect(screen, color, placeholder_rect)
            return
        
        if (self.current_direction in self.animations and 
            len(self.animations[self.current_direction]) > 0):
            
            current_frames = self.animations[self.current_direction]
            frame_index = int(self.animation_frame) % len(current_frames)
            current_sprite = current_frames[frame_index]
            
            # Efecto de parpadeo cuando es invulnerable
            if self.invulnerable:
                current_time = pygame.time.get_ticks()
                if (current_time // 100) % 2:  # Parpadear cada 100ms
                    current_sprite = current_sprite.copy()
                    current_sprite.set_alpha(128)  # Semi-transparente
            
            # Dibujar el sprite con offset de cámara
            screen.blit(current_sprite, (self.x - camera_x, self.y - camera_y))
        else:
            # Placeholder si no hay animación
            placeholder_rect = pygame.Rect(
                self.x - camera_x, self.y - camera_y, 
                config.CHARACTER_SIZE, config.CHARACTER_SIZE
            )
            color = (255, 165, 0) if self.name == "Adán" else (0, 255, 0)
            pygame.draw.rect(screen, color, placeholder_rect)
    
    def draw_health_bar(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """
        Dibuja la barra de vida del personaje
        
        Args:
            screen: Superficie donde dibujar
            camera_x: Offset X de la cámara
            camera_y: Offset Y de la cámara
        """
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
            health_color = self._get_health_color()
            pygame.draw.rect(screen, health_color, 
                           (bar_x, bar_y, health_width, bar_height))
    
    def _get_health_color(self) -> Tuple[int, int, int]:
        """Retorna el color de la barra de vida basado en la salud actual"""
        health_percentage = self.health / self.max_health
        if health_percentage > 0.6:
            return (0, 255, 0)  # Verde
        elif health_percentage > 0.3:
            return (255, 255, 0)  # Amarillo
        else:
            return (255, 0, 0)  # Rojo

class Background:
    """Maneja el fondo del juego con scroll infinito"""
    
    def __init__(self, image_url: str, width: int, height: int, cache: Optional[ResourceCache] = None):
        self.width = width
        self.height = height
        self.image: Optional[pygame.Surface] = None
        self.cache = cache or ResourceCache()
        self.load_background(image_url)
        
    def load_background(self, url: str) -> None:
        """
        Carga la imagen de fondo desde GitHub con sistema de cache
        
        Args:
            url: URL de la imagen de fondo
        """
        try:
            print("📥 Descargando escenario nivel 1...")
            
            # Descargar con cache
            image_data = download_with_cache(url, self.cache)
            if not image_data:
                print("❌ No se pudo descargar el escenario")
                self._create_fallback_background()
                return
            
            # Convertir imagen
            from PIL import Image
            from io import BytesIO
            
            image_stream = BytesIO(image_data)
            pil_image = Image.open(image_stream)
            
            # Convertir a superficie de pygame
            image_data = pil_image.tobytes()
            self.image = pygame.image.fromstring(image_data, pil_image.size, pil_image.mode)
            
            print(f"✅ Escenario cargado: {pil_image.size}")
            
        except Exception as e:
            print(f"❌ Error cargando escenario: {e}")
            self._create_fallback_background()
    
    def _create_fallback_background(self) -> None:
        """Crea un fondo de respaldo"""
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((34, 139, 34))  # Verde bosque
    
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float, 
             screen_width: int, screen_height: int) -> None:
        """
        Dibuja el fondo con desplazamiento de cámara y efecto infinito
        
        Args:
            screen: Superficie donde dibujar
            camera_x: Offset X de la cámara
            camera_y: Offset Y de la cámara
            screen_width: Ancho de la pantalla
            screen_height: Alto de la pantalla
        """
        if not self.image:
            return
            
        # Calcular posición del fondo
        bg_x = -camera_x % self.width
        bg_y = -camera_y % self.height
        
        # Dibujar múltiples copias del fondo para crear efecto infinito
        for x in range(-self.width, screen_width + self.width, self.width):
            for y in range(-self.height, screen_height + self.height, self.height):
                screen.blit(self.image, (x + bg_x, y + bg_y))

class Game:
    """Clase principal del juego"""
    
    def __init__(self):
        pygame.init()
        
        # Configuración básica
        self.screen_width = config.SCREEN_WIDTH
        self.screen_height = config.SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(config.TITLE)
        
        self.clock = pygame.time.Clock()
        self.fps = config.FPS
        
        # Sistema de cache para recursos
        self.cache = ResourceCache()
        
        # Inicializar componentes del juego
        self._initialize_characters()
        self._initialize_combat_systems()
        self._initialize_camera()
        self._initialize_background()
        self._initialize_enemies()
        self._initialize_game_state()
        
    def _initialize_characters(self) -> None:
        """Inicializa los personajes del juego"""
        self.juan = Character("Juan", config.JUAN_URLS, 400, 300, self.cache)
        self.adan = Character("Adán", config.ADAN_URLS, 500, 300, self.cache)
        
        # Sistema de alternancia de personajes
        self.current_character = self.juan
        self.other_character = self.adan
        
    def _initialize_combat_systems(self) -> None:
        """Inicializa los sistemas de combate"""
        self.juan_attack = JuanAttack(self.juan)
        self.adan_attack = AdanAttack(self.adan)
        
    def _initialize_camera(self) -> None:
        """Inicializa el sistema de cámara"""
        self.camera_x = 0.0
        self.camera_y = 0.0
        
    def _initialize_background(self) -> None:
        """Inicializa el fondo del juego"""
        self.background = Background(
            config.BACKGROUND_URL, 
            config.BACKGROUND_WIDTH, 
            config.BACKGROUND_HEIGHT, 
            self.cache
        )
        
    def _initialize_enemies(self) -> None:
        """Inicializa el sistema de enemigos"""
        self.worm_spawner = WormSpawner(max_worms=config.MAX_WORMS)
        self._setup_enemy_spawns()
        
    def _initialize_game_state(self) -> None:
        """Inicializa el estado del juego"""
        self.switch_cooldown = 0
        self.game_over = False
        self.victory = False
        self.enemies_defeated = 0
        self.victory_condition = config.VICTORY_CONDITION
        
    def _setup_enemy_spawns(self) -> None:
        """Configura las áreas donde pueden aparecer enemigos"""
        spawn_areas = [
            (100, 100, 200, 200),
            (800, 200, 200, 200),
            (300, 600, 200, 200),
            (700, 700, 200, 200)
        ]
        
        for x, y, width, height in spawn_areas:
            self.worm_spawner.add_spawn_area(x, y, width, height)
        
    def handle_events(self) -> bool:
        """
        Maneja todos los eventos del juego
        
        Returns:
            True si el juego debe continuar, False si debe terminar
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if not self._handle_keydown_event(event.key):
                    return False
        return True
    
    def _handle_keydown_event(self, key: int) -> bool:
        """
        Maneja eventos de teclas presionadas
        
        Args:
            key: Código de la tecla presionada
            
        Returns:
            True si el juego debe continuar, False si debe terminar
        """
        if key == pygame.K_ESCAPE:
            return False
        elif key == pygame.K_TAB and self.switch_cooldown <= 0:
            self.switch_character()
            self.switch_cooldown = config.SWITCH_COOLDOWN
        elif key == pygame.K_SPACE:
            self.perform_basic_attack()
        elif key == pygame.K_x:
            self.perform_special_attack()
        elif key == pygame.K_r and (self.game_over or self.victory):
            self.restart_game()
        
        return True
    
    def switch_character(self) -> None:
        """Alterna entre Juan y Adán"""
        if self.current_character == self.juan:
            self.current_character = self.adan
            self.other_character = self.juan
        else:
            self.current_character = self.juan
            self.other_character = self.adan
        
        print(f"🔄 Cambiado a: {self.current_character.name}")
    
    def perform_basic_attack(self) -> None:
        """Realiza ataque básico del personaje actual"""
        if self.game_over or self.victory:
            return
            
        worms = self.worm_spawner.get_worms()
        
        hit = False
        if self.current_character == self.juan:
            hit = self.juan_attack.combo_attack(worms)
        else:  # Adán
            hit = self.adan_attack.melee_attack(worms)
        
        if hit:
            self._check_defeated_enemies(worms)
    
    def perform_special_attack(self) -> None:
        """Realiza ataque especial del personaje actual"""
        if self.game_over or self.victory:
            return
            
        worms = self.worm_spawner.get_worms()
        
        hit = False
        if self.current_character == self.juan:
            hit = self.juan_attack.special_attack(worms)
        else:  # Adán - Ataque a distancia hacia el gusano más cercano
            if worms:
                nearest_worm = self._find_nearest_worm(worms)
                hit = self.adan_attack.ranged_attack(
                    nearest_worm.x + config.CHARACTER_SIZE // 2, 
                    nearest_worm.y + config.CHARACTER_SIZE // 2
                )
        
        if hit:
            self._check_defeated_enemies(worms)
    
    def _find_nearest_worm(self, worms: List[WormEnemy]) -> WormEnemy:
        """Encuentra el gusano más cercano al personaje actual"""
        return min(worms, key=lambda w: 
            distance((w.x, w.y), (self.current_character.x, self.current_character.y)))
    
    def _check_defeated_enemies(self, worms: List[WormEnemy]) -> None:
        """Verifica y cuenta los enemigos derrotados"""
        for worm in worms:
            if not worm.alive:
                self.enemies_defeated += 1
    
    def update(self) -> None:
        """Actualiza la lógica del juego"""
        if self.game_over or self.victory:
            return
            
        keys_pressed = pygame.key.get_pressed()
        
        # Actualizar componentes del juego
        self._update_characters(keys_pressed)
        self._check_game_conditions()
        self._update_camera()
        self._update_combat_systems()
        self._update_enemies()
        self._update_cooldowns()
    
    def _update_characters(self, keys_pressed: pygame.key.ScancodeWrapper) -> None:
        """Actualiza los personajes"""
        self.current_character.update(keys_pressed)
    
    def _check_game_conditions(self) -> None:
        """Verifica las condiciones de game over y victoria"""
        # Verificar si los personajes murieron
        if self.juan.health <= 0 and self.adan.health <= 0:
            self.game_over = True
            print("💀 GAME OVER - Ambos personajes han muerto")
        
        # Verificar condición de victoria
        if self.enemies_defeated >= self.victory_condition:
            self.victory = True
            print("🏆 ¡VICTORIA! Has derrotado a todos los gusanos")
    
    def _update_camera(self) -> None:
        """Actualiza la posición de la cámara para seguir al personaje activo"""
        target_camera_x = self.current_character.x - self.screen_width // 2
        target_camera_y = self.current_character.y - self.screen_height // 2
        
        # Suavizar movimiento de cámara
        self.camera_x = lerp(self.camera_x, target_camera_x, config.CAMERA_SMOOTHING)
        self.camera_y = lerp(self.camera_y, target_camera_y, config.CAMERA_SMOOTHING)
    
    def _update_combat_systems(self) -> None:
        """Actualiza los sistemas de combate"""
        worms = self.worm_spawner.get_worms()
        self.juan_attack.update(worms)
        self.adan_attack.update(worms)
    
    def _update_enemies(self) -> None:
        """Actualiza el sistema de enemigos"""
        players = [self.juan, self.adan]
        self.worm_spawner.update(players)
    
    def _update_cooldowns(self) -> None:
        """Actualiza los cooldowns del juego"""
        if self.switch_cooldown > 0:
            self.switch_cooldown -= 1
    
    def restart_game(self) -> None:
        """Reinicia el juego al estado inicial"""
        # Reiniciar personajes
        self.juan.health = self.juan.max_health
        self.adan.health = self.adan.max_health
        self.juan.x, self.juan.y = 400, 300
        self.adan.x, self.adan.y = 500, 300
        self.juan.invulnerable = False
        self.adan.invulnerable = False
        
        # Reiniciar enemigos
        self.worm_spawner.worms.clear()
        
        # Reiniciar estado del juego
        self.game_over = False
        self.victory = False
        self.enemies_defeated = 0
        self.switch_cooldown = 0
        
        # Reiniciar cámara
        self.camera_x = 0.0
        self.camera_y = 0.0
        
        print("🔄 Juego reiniciado")
    
    def draw(self):
        """Dibuja todo en la pantalla"""
        # Limpiar pantalla
        self.screen.fill((50, 100, 50))
        
        # Dibujar fondo con scroll
        self.background.draw(self.screen, self.camera_x, self.camera_y, self.screen_width, self.screen_height)
        
        # Dibujar personaje inactivo (más transparente)
        other_surface = pygame.Surface((64, 64))
        other_surface.set_alpha(128)
        if self.other_character.current_direction in self.other_character.animations:
            frames = self.other_character.animations[self.other_character.current_direction]
            if frames:
                frame = frames[0]
                other_surface.blit(frame, (0, 0))
                self.screen.blit(other_surface, (self.other_character.x - self.camera_x, self.other_character.y - self.camera_y))
        
        # Dibujar personaje activo
        self.current_character.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar barras de vida
        self.juan.draw_health_bar(self.screen, self.camera_x, self.camera_y)
        self.adan.draw_health_bar(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar enemigos
        self.worm_spawner.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar efectos de ataque
        self.juan_attack.draw(self.screen, self.camera_x, self.camera_y)
        self.adan_attack.draw(self.screen, self.camera_x, self.camera_y)
        
        # UI e información
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        font = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        
        # Personaje activo
        active_text = font.render(f"🎮 Jugando: {self.current_character.name}", True, (255, 255, 255))
        self.screen.blit(active_text, (10, 10))
        
        # Vidas de los personajes
        juan_health_text = font_small.render(f"Juan: {self.juan.health}/100 HP", True, (0, 255, 0) if self.juan.health > 30 else (255, 0, 0))
        self.screen.blit(juan_health_text, (10, 50))
        
        adan_health_text = font_small.render(f"Adán: {self.adan.health}/100 HP", True, (0, 255, 0) if self.adan.health > 30 else (255, 0, 0))
        self.screen.blit(adan_health_text, (150, 50))
        
        # Progreso
        progress_text = font_small.render(f"Gusanos derrotados: {self.enemies_defeated}/{self.victory_condition}", True, (255, 255, 255))
        self.screen.blit(progress_text, (10, 75))
        
        # UI específica del personaje
        if self.current_character == self.juan:
            self.juan_attack.draw_ui(self.screen)
        
        # Controles
        instructions = [
            "🎮 Controles:",
            "WASD/Flechas - Mover",
            "ESPACIO - Ataque básico",
            "X - Ataque especial",
            "TAB - Cambiar personaje",
            "ESC - Salir"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = font_small.render(instruction, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, self.screen_height - 140 + i * 20))
        
        # Estados especiales
        if self.game_over:
            game_over_text = font.render("💀 GAME OVER - Presiona R para reiniciar", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(game_over_text, text_rect)
        
        elif self.victory:
            victory_text = font.render("🏆 ¡VICTORIA! - Presiona R para reiniciar", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(victory_text, text_rect)
        
        # Información de debug
        debug_text = f"Gusanos activos: {len(self.worm_spawner.get_worms())} | Cámara: ({int(self.camera_x)}, {int(self.camera_y)})"
        debug_surface = font_small.render(debug_text, True, (200, 200, 200))
        self.screen.blit(debug_surface, (300, 50))
    
    def run(self):
        """Bucle principal del juego"""
        print("🚀 Iniciando Nivel 1 - Tierra de las Manzanas (COMBATE)...")
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