import numpy as np


class WFSim:
    # Ініціалізація параметрів симуляції
    def __init__(self, f=0.01, p=1e-4, wind='NE', bedrock=0.005, water=0.05, grass=0.1, cloud=0.1, h=16, w=16):
        self.f = f
        self.p = p
        self.h = h
        self.w = w
        self.bedrock = bedrock
        self.water = water
        self.wind = wind
        self.cloud = np.random.random(1)[0]
        self.temp = self.temperature()
        self.offsets = {'calm': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
                        'N': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1)],
                        'S': [(0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
                        'E': [(-1, 0), (-1, 1), (0, 1), (1, 0), (1, 1)],
                        'W': [(-1, -1), (-1, 0), (0, -1), (1, -1), (1, 0)],
                        'NE': [(-1, 0), (-1, 1), (0, 1)],
                        'NW': [(-1, -1), (-1, 0), (0, -1)],
                        'SE': [(0, 1), (1, 0), (1, 1)],
                        'SW': [(0, -1), (1, -1), (1, 0)]}
        self.cloud_offsets = {'calm': [],
                              'N': [(1, 0)],
                              'S': [(-1, 0)],
                              'E': [(0, -1)],
                              'W': [(0, 1)],
                              'NE': [(1, -1)],
                              'NW': [(1, 1)],
                              'SE': [(-1, -1)],
                              'SW': [(-1, 1)]}

        self.landscape = np.random.randint(0, 2, (self.h, self.w))
        self.old_landscape = self.landscape.copy()

        self.burned_ratio = round((self.landscape == -1).sum() / (self.h * self.w) * 100, 2)
        self.tree_cover = round((self.landscape == -1).sum() / (self.h * self.w) * 100, 2)

        for i in range(self.landscape.shape[0]):
            for j in range(self.landscape.shape[1]):
                coef = 5 if self.surf_neighbors_check(i, j, "B") else 1
                if self.bedrock * coef > np.random.random():
                    self.landscape[i, j] = -2

                coef = 10 if self.surf_neighbors_check(i, j, "W") else 0.1
                if self.water * coef > np.random.random():
                    self.landscape[i, j] = -3

    # Перевіряє, чи є поруч заданий тип поверхні (води або скелі)
    def surf_neighbors_check(self, idx, jdx, kind='W'):
        if kind == 'W':
            value = -2
        elif kind == 'B':
            value = -1
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for di, dj in offsets:
            ni, nj = idx + di, jdx + dj
            if 0 <= nj < self.w and 0 <= ni < self.h:
                if self.landscape[ni, nj] == value:
                    return True
        return False

    # Визначає, и може пожежа поширитися на певну клітинку, враховуючи напрямок вітру
    def fire_neighbors_check(self, idx, jdx):
        offsets = self.offsets[self.wind]
        for di, dj in offsets:
            ni, nj = idx + di, jdx + dj
            if 0 <= nj < self.w and 0 <= ni < self.h:
                if self.landscape[ni, nj] == 2 and self.landscape[idx, jdx] == 1:
                    return True
        return False

    # Генерує добову зміну температури з випадковим шумом
    def temperature(self, average_temp=20, amplitude=5, noise_level=2):
        hours = np.arange(24)
        temperatures = average_temp + amplitude * np.sin(2 * np.pi * hours / 24 - np.pi / 2)
        temperatures += np.random.normal(0, noise_level, 24)
        return temperatures

    # Створює маску хмар випадковим способом на ландшафті
    def generate_cloud(self):
        size = 16
        mask = np.zeros((self.h, self.w))
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        idx_prev, jdx_prev = np.random.randint(0, self.h), np.random.randint(0, self.w)
        for _ in range(size):
            for di, dj in [offsets[np.random.randint(len(offsets))]]:
                ni, nj = idx_prev + di, jdx_prev + dj
                if 0 <= nj < self.w and 0 <= ni < self.h:
                    cell = (np.random.randint(min(0, idx_prev - 1), min(self.h, idx_prev + 1)),
                            np.random.randint(min(0, jdx_prev - 1), min(self.w, jdx_prev + 1)))
                    mask[ni, nj] = 1
                idx_prev, jdx_prev = ni, nj
        return mask.astype(bool)

    # Переміщує хмари відповідно до напрямку вітру
    def cloud_move(self):
        offsets = self.cloud_offsets[self.wind]
        mask = np.zeros((self.h, self.w))
        for idx in range(self.landscape.shape[0]):
            for jdx in range(self.landscape.shape[1]):
                for di, dj in offsets:
                    ni, nj = idx + di, jdx + dj
                    if 0 <= nj < self.w and 0 <= ni < self.h and self.landscape[idx, jdx] == 3:
                        mask[ni, nj] = 1
        return mask.astype(bool)

    # Оновлює стан ландшафту на кожному кроці симуляції, змінюючи температуру, поширюючи вогонь, додаючи нові дерева та переміщуючи хмари
    def step(self, step):
        if step % 24 == 0 and step > 0:
            self.temp = self.temperature()

        new_landscape = self.landscape.copy()
        for i in range(self.landscape.shape[0]):
            for j in range(self.landscape.shape[1]):
                if new_landscape[i, j] == 3:
                    if self.old_landscape[i, j] == -1 or self.old_landscape[i, j] == 2:
                        new_landscape[i, j] = 0
                    else:
                        new_landscape[i, j] = self.old_landscape[i, j]
                if new_landscape[i, j] == 2:
                    new_landscape[i, j] = -1
                if self.p > np.random.rand() and self.landscape[i, j] == 0:
                    new_landscape[i, j] = 1
                coef = 2 if self.temp[step % 24] > 25 else 1
                if (self.f * coef > np.random.rand() or self.fire_neighbors_check(i, j)) and self.landscape[i, j] == 1:
                    new_landscape[i, j] = 2
        self.old_landscape = new_landscape.copy()
        if 3 in self.landscape and self.wind != 'calm':
            new_landscape[self.cloud_move()] = 3
        if self.cloud > np.random.rand():
            new_landscape[self.generate_cloud()] = 3
        self.landscape = new_landscape.copy()
        self.burned_ratio = round((self.landscape == -1).sum() / (self.h * self.w) * 100, 2)
        self.tree_cover = round((self.landscape == 1).sum() / (self.h * self.w) * 100, 2)
