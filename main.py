import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
from matplotlib.patches import Rectangle

from datetime import timedelta, datetime


class WFSim:
    def __init__(self, f=0.01, p=1e-4, bedrock=0.005, water=0.05, h=16, w=16):
        self.f = f
        self.p = p
        self.h = h
        self.w = w
        self.bedrock = bedrock
        self.water = water
        self.temp = self.temperature()

        self.landscape = np.random.randint(0, 2, (self.h, self.w))

        for i in range(self.landscape.shape[0]):
            for j in range(self.landscape.shape[1]):
                coef = 5 if self.surf_neighbors_check(i, j, "B") else 1
                if self.bedrock * coef > np.random.random():
                    self.landscape[i, j] = -2

                coef = 10 if self.surf_neighbors_check(i, j, "W") else 0.1
                if self.water * coef > np.random.random():
                    self.landscape[i, j] = -3

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

    def fire_neighbors_check(self, idx, jdx):
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for di, dj in offsets:
            ni, nj = idx + di, jdx + dj
            if 0 <= nj < self.w and 0 <= ni < self.h:
                if self.landscape[ni, nj] == 2:
                    return True
        return False

    def temperature(self, average_temp=20, amplitude=5, noise_level=2):
        hours = np.arange(24)
        temperatures = average_temp + amplitude * np.sin(2 * np.pi * hours / 24 - np.pi / 2)
        temperatures += np.random.normal(0, noise_level, 24)
        return temperatures

    def step(self, step):
        if step % 24 == 0 and step > 0:
            self.temp = self.temperature()

        new_landscape = self.landscape.copy()
        for i in range(self.landscape.shape[0]):
            for j in range(self.landscape.shape[1]):
                if self.landscape[i, j] == 2:
                    new_landscape[i, j] = -1
                if self.p > np.random.rand() and self.landscape[i, j] == 0:
                    new_landscape[i, j] = 1
                coef = 2 if self.temp[step % 24] > 25 else 1
                if (self.f * coef > np.random.rand() or self.fire_neighbors_check(i, j)) and self.landscape[i, j] == 1:
                    new_landscape[i, j] = 2
        self.landscape = new_landscape.copy()


def update(frame):
    im.set_data(Sim.landscape)
    ax.axis('off')
    Sim.step(frame)
    return [im]


color_list = ['steelblue', 'grey', 'black', 'olivedrab', 'forestgreen', 'orange']
cmap = colors.ListedColormap(color_list)
bounds = [-3, -2, -1, 0, 1, 2, 3]
norm = colors.BoundaryNorm(bounds, cmap.N)

Sim = WFSim(h=64, w=64)

fig, ax = plt.subplots(figsize=(16, 16))
im = ax.imshow(Sim.landscape, cmap=cmap, norm=norm)
plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

ani = animation.FuncAnimation(fig, update, frames=80, interval=20)
ani.save('temperature.gif', fps=1.5, savefig_kwargs={'pad_inches': 0})
plt.show()
