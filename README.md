# Proyecto-tierra-de-las-manzanas

El back-end y front-end del videojuego "Tierra de las Manzanas"

## 🎮 Descripción del Juego

Un juego 2D de combate desarrollado con pygame donde controlas a dos personajes (Juan y Adán) para luchar contra enemigos gusano en un mundo de manzanas.

## 🛠️ Instalación y Dependencias

### Requisitos
- Python 3.8+
- pygame 2.0+
- Pillow (PIL)
- requests

### Instalación
```bash
pip install pygame pillow requests
```

## 🚀 Cómo Ejecutar

```bash
python nivel1_juego_completo.py
```

## 🎯 Controles

- **WASD / Flechas**: Mover personaje
- **ESPACIO**: Ataque básico
- **X**: Ataque especial
- **TAB**: Cambiar entre Juan y Adán
- **R**: Reiniciar juego (cuando termina)
- **ESC**: Salir del juego

## 🏗️ Estructura del Código

```
├── nivel1_juego_completo.py  # Archivo principal del juego
├── config.py                 # Configuración centralizada
├── utils.py                  # Utilidades y sistema de cache
├── adan_attacks.py           # Sistema de ataques de Adán
├── juan_attacks.py           # Sistema de ataques de Juan
├── worm_enemy.py             # Sistema de enemigos
├── test_game.py              # Tests unitarios
└── cache/                    # Cache de recursos descargados
```

## ✨ Características

### 🎨 Sistema de Personajes
- **Juan**: Especialista en combos y ataques especiales
- **Adán**: Combate cuerpo a cuerpo y ataques a distancia
- Sistema de salud con invulnerabilidad temporal
- Animaciones fluidas para cada dirección

### 🤖 Sistema de Enemigos
- Gusanos con IA básica (patrulla, persecución, ataque)
- Sistema de spawn dinámico
- Diferentes comportamientos según la situación

### 🎯 Sistema de Combate
- Ataques básicos y especiales únicos por personaje
- Sistema de cooldowns para equilibrio
- Efectos visuales para retroalimentación

### 🎮 Características Técnicas
- **Cache de recursos**: Evita descargas repetidas
- **Manejo robusto de errores**: Continúa funcionando aunque fallen algunos recursos
- **Configuración centralizada**: Fácil ajuste de parámetros
- **Type hints**: Código más mantenible y legible
- **Tests unitarios**: Validación automática de funcionalidad

## 🧪 Tests

Ejecutar tests unitarios:
```bash
python test_game.py
```

Los tests verifican:
- Funciones utilitarias (clamp, distance, lerp)
- Sistema de cache de recursos
- Configuración del juego
- Creación y mecánicas de personajes

## 🔧 Configuración

Edita `config.py` para personalizar:
- Resolución de pantalla
- Velocidad de personajes
- URLs de recursos
- Parámetros de combate
- Condiciones de victoria

## 🛡️ Manejo de Errores

El juego incluye:
- Fallbacks visuales cuando fallan las descargas
- Cache automático para mejorar rendimiento
- Validación de estados del juego
- Manejo graceful de errores de red

## 🎯 Objetivo del Juego

Derrotar **10 gusanos enemigos** para ganar. Los gusanos aparecen gradualmente y atacan a los personajes. Usa los ataques únicos de cada personaje estratégicamente.

## 🔄 Mejoras Realizadas

- ✅ Refactorización completa del código
- ✅ Sistema de cache para recursos
- ✅ Manejo robusto de errores
- ✅ Type hints y documentación
- ✅ Tests unitarios
- ✅ Configuración centralizada
- ✅ Mejor organización del código

---

*Desarrollado con ❤️ usando Python y pygame*
