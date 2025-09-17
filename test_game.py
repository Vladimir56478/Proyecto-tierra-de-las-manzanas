"""
Tests básicos para el juego Tierra de las Manzanas
"""
import unittest
import pygame
import sys
import os

# Agregar el directorio actual al path para importar módulos del juego
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import ResourceCache, clamp, distance, lerp, validate_position
import config


class TestUtils(unittest.TestCase):
    """Tests para las funciones utilitarias"""
    
    def test_clamp(self):
        """Test de la función clamp"""
        self.assertEqual(clamp(5, 0, 10), 5)
        self.assertEqual(clamp(-5, 0, 10), 0)
        self.assertEqual(clamp(15, 0, 10), 10)
        self.assertEqual(clamp(5.5, 0.0, 10.0), 5.5)
    
    def test_distance(self):
        """Test de la función distance"""
        self.assertEqual(distance((0, 0), (3, 4)), 5.0)
        self.assertEqual(distance((0, 0), (0, 0)), 0.0)
        self.assertAlmostEqual(distance((1, 1), (2, 2)), 1.414, places=3)
    
    def test_lerp(self):
        """Test de la función lerp"""
        self.assertEqual(lerp(0, 10, 0.5), 5.0)
        self.assertEqual(lerp(0, 10, 0.0), 0.0)
        self.assertEqual(lerp(0, 10, 1.0), 10.0)
        self.assertEqual(lerp(10, 20, 0.3), 13.0)
    
    def test_validate_position(self):
        """Test de la función validate_position"""
        x, y = validate_position(5, 10, 100, 100)
        self.assertEqual((x, y), (5, 10))
        
        x, y = validate_position(-5, 10, 100, 100)
        self.assertEqual((x, y), (0, 10))
        
        x, y = validate_position(150, 10, 100, 100)
        self.assertEqual((x, y), (100, 10))


class TestResourceCache(unittest.TestCase):
    """Tests para el sistema de cache de recursos"""
    
    def setUp(self):
        """Configuración para cada test"""
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.cache = ResourceCache(self.temp_dir)
    
    def tearDown(self):
        """Limpieza después de cada test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_path_generation(self):
        """Test de generación de rutas de cache"""
        url = "https://example.com/test.png"
        path = self.cache.get_cache_path(url)
        self.assertTrue(path.startswith(self.temp_dir))
        self.assertTrue("test.png" in path)
    
    def test_cache_operations(self):
        """Test de operaciones básicas de cache"""
        url = "https://example.com/test.png"
        test_data = b"test image data"
        
        # Verificar que inicialmente no está en cache
        self.assertFalse(self.cache.is_cached(url))
        
        # Guardar en cache
        self.cache.save_to_cache(url, test_data)
        
        # Verificar que ahora está en cache
        self.assertTrue(self.cache.is_cached(url))
        
        # Cargar desde cache
        loaded_data = self.cache.load_from_cache(url)
        self.assertEqual(loaded_data, test_data)


class TestConfig(unittest.TestCase):
    """Tests para la configuración del juego"""
    
    def test_config_values(self):
        """Test de que los valores de configuración sean válidos"""
        self.assertIsInstance(config.SCREEN_WIDTH, int)
        self.assertIsInstance(config.SCREEN_HEIGHT, int)
        self.assertIsInstance(config.FPS, int)
        self.assertIsInstance(config.CHARACTER_SPEED, int)
        self.assertIsInstance(config.MAX_HEALTH, int)
        
        self.assertGreater(config.SCREEN_WIDTH, 0)
        self.assertGreater(config.SCREEN_HEIGHT, 0)
        self.assertGreater(config.FPS, 0)
        self.assertGreater(config.CHARACTER_SPEED, 0)
        self.assertGreater(config.MAX_HEALTH, 0)
    
    def test_character_urls(self):
        """Test de que las URLs de personajes estén definidas"""
        required_directions = ["up", "down", "left", "right"]
        
        for direction in required_directions:
            self.assertIn(direction, config.JUAN_URLS)
            self.assertIn(direction, config.ADAN_URLS)
            self.assertTrue(config.JUAN_URLS[direction].startswith("https://"))
            self.assertTrue(config.ADAN_URLS[direction].startswith("https://"))


class TestGameIntegration(unittest.TestCase):
    """Tests de integración básicos"""
    
    def setUp(self):
        """Configuración para tests de integración"""
        # Configurar pygame en modo sin pantalla para tests
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
    
    def test_character_creation(self):
        """Test de creación de personajes"""
        from nivel1_juego_completo import Character
        from utils import ResourceCache
        
        cache = ResourceCache()
        character = Character("Test", config.JUAN_URLS, 100, 200, cache)
        
        self.assertEqual(character.name, "Test")
        self.assertEqual(character.x, 100)
        self.assertEqual(character.y, 200)
        self.assertEqual(character.health, config.MAX_HEALTH)
        self.assertEqual(character.max_health, config.MAX_HEALTH)
        self.assertFalse(character.invulnerable)
        self.assertFalse(character.moving)
    
    def test_character_damage(self):
        """Test del sistema de daño de personajes"""
        from nivel1_juego_completo import Character
        from utils import ResourceCache
        
        cache = ResourceCache()
        character = Character("Test", config.JUAN_URLS, 100, 200, cache)
        
        # Test daño normal
        initial_health = character.health
        died = character.take_damage(20)
        self.assertEqual(character.health, initial_health - 20)
        self.assertTrue(character.invulnerable)
        self.assertFalse(died)
        
        # Test daño mientras es invulnerable
        invulnerable_health = character.health
        died = character.take_damage(10)
        self.assertEqual(character.health, invulnerable_health)  # No debe cambiar
        self.assertFalse(died)
        
        # Test daño mortal
        character.invulnerable = False
        died = character.take_damage(character.health)
        self.assertEqual(character.health, 0)
        self.assertTrue(died)


def run_tests():
    """Ejecuta todos los tests"""
    # Crear suite de tests
    test_suite = unittest.TestSuite()
    
    # Agregar tests
    test_classes = [TestUtils, TestResourceCache, TestConfig, TestGameIntegration]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Ejecutando tests del juego Tierra de las Manzanas...")
    success = run_tests()
    
    if success:
        print("✅ Todos los tests pasaron exitosamente")
        sys.exit(0)
    else:
        print("❌ Algunos tests fallaron")
        sys.exit(1)