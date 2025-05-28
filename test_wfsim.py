import unittest
from wfsim import WFSim


class TestWFSim(unittest.TestCase):
    # Ініціалізація симуляції
    def setUp(self):
        self.sim = WFSim(h=10, w=10, wind='N', bedrock=0, water=0)

    # Перевірка коректності ініціалізації (розмір ландшафту та довжина масиву температури)
    def test_initialization(self):
        self.assertEqual(self.sim.landscape.shape, (10, 10))
        self.assertEqual(len(self.sim.temp), 24)

    # Тестування методу отримання температури, перевіряє кількість значень та їхній тип
    def test_temperature_variation(self):
        temps = self.sim.temperature()
        self.assertEqual(len(temps), 24)
        self.assertTrue(all(isinstance(t, float) for t in temps))

    # Імітує розповсюдження вогню
    def test_fire_spread(self):
        self.sim.landscape[5, 5] = 1  # Дерево
        self.sim.landscape[4, 5] = 2  # Вогонь
        self.assertTrue(self.sim.fire_neighbors_check(5, 5))

    # Виконує 1 крок симуляції та перевіряє, чи розмір ландшафту залишився незмінним
    def test_step_function(self):
        old_landscape = self.sim.landscape.copy()
        self.sim.step(1)
        self.assertEqual(self.sim.landscape.shape, old_landscape.shape)

    # Генерує карту хмар і перевіряє, чи вона має коректний розмір та хоча б одну хмарну клітинку
    def test_cloud_generation(self):
        cloud_mask = self.sim.generate_cloud()
        self.assertEqual(cloud_mask.shape, (10, 10))
        self.assertTrue(cloud_mask.any())  # Має містити хоча б одну істинну

    # Перевіряє переміщення хмар у ландшафті
    def test_cloud_move(self):
        self.sim.landscape[5, 5] = 3  # Хмара
        cloud_mask = self.sim.cloud_move()
        self.assertEqual(cloud_mask.shape, (10, 10))
        self.assertTrue(cloud_mask.any())

    # Перевіряє сусідні клітинки на відповідність певному типу поверхні
    def test_surf_neighbors_check(self):
        self.sim.landscape[4, 4] = -2
        result = self.sim.surf_neighbors_check(5, 5, kind='W')
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
