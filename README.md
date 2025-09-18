# 🍎 Proyecto Tierra de las Manzanas

Un juego de aventuras 2D desarrollado en Python con Pygame, donde los personajes Adán y Juan luchan contra gusanos enemigos usando animaciones GIF descargadas desde GitHub.

## ✨ Características Principales

### 🎮 Personajes Jugables
- **Adán**: Personaje principal con ataques cuerpo a cuerpo y proyectiles
- **Juan**: Personaje secundario con sistema de combos

### 🎬 Sistema de Animaciones GIF
- **Movimiento**: Animaciones direccionales (arriba, abajo, izquierda, derecha)
- **Ataques**: Animaciones únicas para cada dirección de ataque
- **Descarga automática**: Las animaciones se cargan desde URLs de GitHub Issues
- **Transparencia**: Fondos transparentes para integración perfecta

### ⚔️ Sistema de Combate Mejorado
- **Adán**: 
  - Tecla `X` para ataques direccionales
  - Ataques cuerpo a cuerpo con alcance direccional
  - Proyectiles de largo alcance
- **Juan**:
  - Tecla `Z` para ataques combo direccionales
  - Sistema de combos (3 niveles)
  - Daño incremental por combo

### 🐛 Enemigos Inteligentes
- **Gusanos**: 
  - IA con estados (patrulla, persecución, ataque)
  - Animaciones de movimiento con GIF
  - Estado idle con primer frame cuando están quietos
  - Sistema de vida y daño

## 🎯 Controles

### Movimiento General
- `↑↓←→` o `WASD`: Mover personaje
- `ESC`: Salir del juego

### Ataques
- **Adán**: `X` - Ataque direccional con animación
- **Juan**: `Z` - Combo direccional con animación

## 🚀 Instalación y Ejecución

### Dependencias
```bash
pip install pygame pillow requests
```

### Estructura del Proyecto
```
Proyecto-tierra-de-las-manzanas/
├── src/
│   ├── characters/
│   │   ├── adan_character.py
│   │   └── juan_character.py
│   ├── attacks/
│   │   ├── adan_attacks.py
│   │   └── juan_attacks.py
│   ├── enemies/
│   │   └── worm_enemy.py
│   └── levels/
└── assets/
    └── gifs/
```

### Ejecución
```bash
python src/characters/adan_character.py  # Jugar con Adán
python src/characters/juan_character.py  # Jugar con Juan
```

## 🎨 URLs de Animaciones

### Adán - Ataques
- **Arriba**: https://github.com/user-attachments/assets/6544be63-1345-4a5a-b4e9-57ec4a18775a
- **Abajo**: https://github.com/user-attachments/assets/cbce589c-03c0-4bc0-a067-1b769b154fbd
- **Izquierda**: https://github.com/user-attachments/assets/1b2a5d84-7ef7-4598-ada0-68f21c785b06
- **Derecha**: https://github.com/user-attachments/assets/b1dcab29-5e9f-46aa-87f2-1690c0986e77

### Juan - Ataques
- **Arriba**: https://github.com/user-attachments/assets/dd75fe07-fdbc-44af-b96c-e02d24f1a541
- **Abajo**: https://github.com/user-attachments/assets/bcd29b68-808b-4840-a6bb-1691c94581b1
- **Izquierda**: https://github.com/user-attachments/assets/e1db84b2-d37d-4bc4-87f8-cce531c51300
- **Derecha**: https://github.com/user-attachments/assets/dd1ed297-05f1-468b-83fb-266d510595f3

### Gusano - Movimiento
- **Todas las direcciones**: https://github.com/user-attachments/assets/c275caea-e0a2-4a45-8eb2-a60485090789

## 🔧 Características Técnicas

### Sistema de Animaciones
- Carga automática de GIFs desde URLs
- Extracción de frames individuales con PIL
- Conversión a superficies Pygame con transparencia
- Manejo de errores con placeholders de respaldo

### Sistema de Combate
- Detección de colisiones direccional
- Áreas de ataque personalizadas por dirección
- Efectos visuales temporales
- Sistema de cooldown para ataques

### IA de Enemigos
- Máquina de estados (patrulla, persecución, ataque, herido)
- Detección de jugadores por proximidad
- Pathfinding básico hacia objetivos
- Generación automática de puntos de patrulla

## 🐛 Issues y Desarrollo

Las animaciones y assets están documentados en las issues del repositorio:
- Issue #5: Ataques de Adán
- Issue #6: Ataques de Juan  
- Issue #7: Movimiento de Gusanos

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🎮 Gameplay

El juego combina elementos de acción y aventura donde los jugadores controlan a Adán o Juan para luchar contra gusanos enemigos en un mundo 2D. Las animaciones fluidas y el sistema de combate direccional crean una experiencia de juego inmersiva y dinámica.

### Mecánicas Principales
- Exploración del mundo abierto
- Combate en tiempo real con animaciones
- Sistema de daño y vida para enemigos
- Respawn automático de enemigos
- Efectos visuales y de audio

¡Disfruta explorando la Tierra de las Manzanas! 🍎✨