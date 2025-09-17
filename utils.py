"""
Utilidades comunes para el juego Tierra de las Manzanas
"""
import pygame
import requests
from PIL import Image
from io import BytesIO
from typing import List, Optional, Tuple, Dict, Any
import os
import json


class ResourceCache:
    """Cache para recursos descargados para evitar descargas repetidas"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, Any] = {}
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_path(self, url: str) -> str:
        """Genera una ruta de cache basada en la URL"""
        filename = url.split('/')[-1] or "asset"
        return os.path.join(self.cache_dir, f"{hash(url)}_{filename}")
    
    def is_cached(self, url: str) -> bool:
        """Verifica si un recurso está en cache"""
        return url in self.memory_cache or os.path.exists(self.get_cache_path(url))
    
    def save_to_cache(self, url: str, data: bytes) -> None:
        """Guarda datos en cache"""
        try:
            with open(self.get_cache_path(url), 'wb') as f:
                f.write(data)
        except IOError as e:
            print(f"⚠️ No se pudo guardar en cache {url}: {e}")
    
    def load_from_cache(self, url: str) -> Optional[bytes]:
        """Carga datos desde cache"""
        if url in self.memory_cache:
            return self.memory_cache[url]
        
        cache_path = self.get_cache_path(url)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = f.read()
                    self.memory_cache[url] = data
                    return data
            except IOError as e:
                print(f"⚠️ Error leyendo cache {cache_path}: {e}")
        return None


def download_with_cache(url: str, cache: Optional[ResourceCache] = None) -> Optional[bytes]:
    """
    Descarga un recurso con sistema de cache
    
    Args:
        url: URL del recurso a descargar
        cache: Sistema de cache opcional
    
    Returns:
        Bytes del recurso o None si hay error
    """
    if cache and cache.is_cached(url):
        data = cache.load_from_cache(url)
        if data:
            print(f"📦 Cargado desde cache: {url}")
            return data
    
    try:
        print(f"📥 Descargando desde GitHub: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.content
        if cache:
            cache.save_to_cache(url, data)
        
        return data
        
    except requests.RequestException as e:
        print(f"❌ Error descargando {url}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado descargando {url}: {e}")
        return None


def load_gif_frames(gif_data: bytes) -> List[pygame.Surface]:
    """
    Carga frames de un GIF y los convierte a superficies de pygame
    
    Args:
        gif_data: Datos binarios del GIF
    
    Returns:
        Lista de superficies de pygame
    """
    frames = []
    
    try:
        gif_stream = BytesIO(gif_data)
        gif = Image.open(gif_stream)
        
        for frame_num in range(gif.n_frames):
            gif.seek(frame_num)
            frame = gif.copy().convert("RGBA")
            
            # Convertir a superficie de pygame
            frame_data = frame.tobytes()
            pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
            pygame_surface = pygame_surface.convert_alpha()
            pygame_surface.set_colorkey((255, 255, 255))  # Fondo blanco transparente
            
            frames.append(pygame_surface)
        
        return frames
        
    except Exception as e:
        print(f"❌ Error procesando GIF: {e}")
        # Crear frame de respaldo
        backup_surface = pygame.Surface((64, 64))
        backup_surface.fill((255, 0, 255))  # Magenta para identificar errores
        return [backup_surface]


def create_backup_surface(width: int = 64, height: int = 64, color: Tuple[int, int, int] = (255, 0, 255)) -> pygame.Surface:
    """
    Crea una superficie de respaldo cuando fallan las cargas de recursos
    
    Args:
        width: Ancho de la superficie
        height: Alto de la superficie  
        color: Color RGB de la superficie
    
    Returns:
        Superficie de pygame
    """
    surface = pygame.Surface((width, height))
    surface.fill(color)
    return surface


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Limita un valor entre un mínimo y máximo
    
    Args:
        value: Valor a limitar
        min_value: Valor mínimo
        max_value: Valor máximo
    
    Returns:
        Valor limitado
    """
    return max(min_value, min(value, max_value))


def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """
    Calcula la distancia euclidiana entre dos puntos
    
    Args:
        pos1: Primera posición (x, y)
        pos2: Segunda posición (x, y)
    
    Returns:
        Distancia entre los puntos
    """
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return (dx * dx + dy * dy) ** 0.5


def lerp(start: float, end: float, factor: float) -> float:
    """
    Interpolación lineal entre dos valores
    
    Args:
        start: Valor inicial
        end: Valor final
        factor: Factor de interpolación (0.0 a 1.0)
    
    Returns:
        Valor interpolado
    """
    return start + (end - start) * factor


def validate_position(x: float, y: float, world_width: float = float('inf'), world_height: float = float('inf')) -> Tuple[float, float]:
    """
    Valida y ajusta una posición para que esté dentro de los límites del mundo
    
    Args:
        x: Coordenada X
        y: Coordenada Y
        world_width: Ancho máximo del mundo
        world_height: Alto máximo del mundo
    
    Returns:
        Posición validada (x, y)
    """
    x = clamp(x, 0, world_width)
    y = clamp(y, 0, world_height)
    return x, y


def save_game_config(config_data: Dict[str, Any], filename: str = "game_config.json") -> bool:
    """
    Guarda configuración del juego en un archivo JSON
    
    Args:
        config_data: Datos de configuración
        filename: Nombre del archivo
    
    Returns:
        True si se guardó exitosamente
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")
        return False


def load_game_config(filename: str = "game_config.json") -> Optional[Dict[str, Any]]:
    """
    Carga configuración del juego desde un archivo JSON
    
    Args:
        filename: Nombre del archivo
    
    Returns:
        Datos de configuración o None si hay error
    """
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
    return None