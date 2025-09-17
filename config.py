"""
Configuración del juego Tierra de las Manzanas - Nivel 1
"""

# Configuración de ventana
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
TITLE = "🍎 Nivel 1 - Tierra de las Manzanas - COMBATE"

# URLs de assets desde GitHub
JUAN_URLS = {
    "up": "https://github.com/user-attachments/assets/9310bb71-1229-4647-b208-b025cced50ec",
    "down": "https://github.com/user-attachments/assets/507e3015-5213-4134-9564-127d2d0641b7", 
    "left": "https://github.com/user-attachments/assets/acf6de12-85b7-41ea-868c-8bb9f227ddbb",
    "right": "https://github.com/user-attachments/assets/10059991-1a75-4a92-8e6c-7a8e6b7e7da0"
}

ADAN_URLS = {
    "up": "https://github.com/user-attachments/assets/a8b0cb2f-6b0a-460d-aa3e-40a404e02bae",
    "down": "https://github.com/user-attachments/assets/962334b6-0161-499a-b45d-9537cb82f0ee", 
    "left": "https://github.com/user-attachments/assets/6fd20d0d-0bce-46e5-ad48-909275503607",
    "right": "https://github.com/user-attachments/assets/83d3150d-67db-4071-9e46-1f47846f22d0"
}

BACKGROUND_URL = "https://github.com/user-attachments/assets/00593769-04d2-4083-a4dc-261e6a3fb3e6"

# Configuración de personajes
CHARACTER_SPEED = 5
CHARACTER_SIZE = 64
MAX_HEALTH = 100
ANIMATION_SPEED = 0.2

# Configuración de invulnerabilidad
INVULNERABLE_DURATION = 1000  # 1 segundo en milisegundos

# Configuración de cámara
CAMERA_SMOOTHING = 0.1

# Configuración de enemigos
MAX_WORMS = 3
VICTORY_CONDITION = 10  # Gusanos a derrotar para ganar

# Configuración de controles
SWITCH_COOLDOWN = 10  # frames

# Configuración de fondo
BACKGROUND_WIDTH = 1536
BACKGROUND_HEIGHT = 512