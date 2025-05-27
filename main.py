import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
from matplotlib.patches import Rectangle

from datetime import timedelta, datetime


class WFSim:
    def __init__(self, f=0.01, p=1e-4, h=16, w=16):
        self.f = f
        self.p = p
        self.h = h
        self.w = w

        self.landscape = np.random.randint(1, 2, (self.h, self.w))

    def fire_neighbors_check(self, idx, jdx):
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for di, dj in offsets:
            ni, nj = idx + di, jdx + dj
            if 0 <= nj < self.w and 0 <= ni < self.h:
                if self.landscape[ni, nj] == 2:
                    return True
        return False

    def step(self, step):
        new_landscape = self.landscape.copy()
        for i in range(self.landscape.shape[0]):
            for j in range(self.landscape.shape[1]):
                if self.landscape[i, j] == 2:
                    new_landscape[i, j] = 0
                if self.p > np.random.rand() and self.landscape[i, j] == 0:
                    new_landscape[i, j] = 1
                if (self.f > np.random.rand() or self.fire_neighbors_check(i, j)) and self.landscape[i, j] == 1:
                    new_landscape[i, j] = 2
        self.landscape = new_landscape.copy()


def update(frame):
    Sim.step(frame)
    im.set_data(Sim.landscape)
    ax.axis('off')
    return [im]


color_list = ['black', 'forestgreen', 'orange']
cmap = colors.ListedColormap(color_list)
bounds = [0, 1, 2, 3]
norm = colors.BoundaryNorm(bounds, cmap.N)

Sim = WFSim(h=64, w=64)

fig, ax = plt.subplots(figsize=(16, 16))
im = ax.imshow(Sim.landscape, cmap=cmap, norm=norm)
plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

ani = animation.FuncAnimation(fig, update, frames=80, interval=20)
ani.save('simple.gif', fps=1.5, savefig_kwargs={'pad_inches': 0})
plt.show()
