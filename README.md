# 🍎 Tierra de las Manzanas - Videojuego

Un videojuego de aventuras desarrollado en Python con pygame, protagonizado por Juan y Adán en la mágica tierra de las manzanas.

## 🎮 Descripción del Proyecto

"Tierra de las Manzanas" es un juego de aventuras 2D donde los jugadores pueden controlar a dos personajes principales: Juan y Adán. El juego presenta un mundo dinámico con animaciones fluidas y mecánicas de juego innovadoras.

## 🚀 Características

### Personajes Jugables
- **Juan**: Personaje principal con animaciones completas de movimiento
- **Adán**: Segundo personaje jugable con mecánicas únicas
- **Sistema de alternancia**: Cambia entre personajes con la tecla TAB

### Mecánicas de Juego
- ✅ Animaciones GIF cargadas desde GitHub
- ✅ Cámara dinámica que sigue al personaje
- ✅ Escenario con scroll infinito
- ✅ Sistema de niveles progresivos
- ✅ Controles intuitivos (WASD/Flechas)

## 📁 Estructura del Proyecto

```
Proyecto-tierra-de-las-manzanas/
├── src/
│   ├── characters/          # Código de personajes
│   │   ├── juan_character.py    # Lógica y animaciones de Juan
│   │   └── adan_character.py    # Lógica y animaciones de Adán
│   ├── levels/              # Niveles del juego
│   │   └── nivel1.py           # Primer nivel del juego
│   └── utils/               # Utilidades y helpers
├── assets/                  # Recursos del juego
│   └── gifs/               # Animaciones GIF
└── README.md               # Este archivo
```

## 🛠️ Tecnologías Utilizadas

- **Python 3.13+**
- **Pygame 2.6+** - Motor de juego
- **Pillow (PIL)** - Procesamiento de imágenes
- **Requests** - Descarga de assets desde GitHub

## 📦 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Vladimir56478/Proyecto-tierra-de-las-manzanas.git
   cd Proyecto-tierra-de-las-manzanas
   ```

2. **Instalar dependencias:**
   ```bash
   pip install pygame pillow requests
   ```

3. **Ejecutar el juego:**
   ```bash
   # Jugar con Juan
   python src/characters/juan_character.py
   
   # Jugar con Adán
   python src/characters/adan_character.py
   
   # Jugar el Nivel 1 (ambos personajes)
   python src/levels/nivel1.py
   ```

## 🎮 Controles

### Movimiento
- **↑ / W** - Mover hacia arriba
- **↓ / S** - Mover hacia abajo
- **← / A** - Mover hacia la izquierda
- **→ / D** - Mover hacia la derecha

### Sistema de Juego (Nivel 1)
- **TAB** - Alternar entre Juan y Adán
- **ESC** - Salir del juego

## 🎯 Roadmap

### ✅ Completado
- [x] Sistema básico de personajes
- [x] Animaciones con GIFs desde GitHub
- [x] Nivel 1 funcional
- [x] Sistema de alternancia de personajes
- [x] Cámara dinámica
- [x] Escenario con scroll

### 🔄 En Desarrollo
- [ ] Más niveles
- [ ] Sistema de colisiones
- [ ] Objetos interactivos
- [ ] Sistema de puntuación
- [ ] Efectos de sonido
- [ ] Menú principal

---

¡Disfruta explorando la Tierra de las Manzanas! 🍎🎮
