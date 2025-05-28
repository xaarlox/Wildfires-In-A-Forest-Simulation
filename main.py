import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors

from datetime import timedelta, datetime
from wfsim import WFSim


def update(frame):
    im.set_data(Sim.landscape)
    info_text = (
        f"Date: {initial_date + timedelta(hours=frame)}\n"
        f"Wind: {Sim.wind}\n"
        f"Temperature: {round(Sim.temp[frame % 24], 1)}°C\n"
        f"Burned area: {Sim.burned_ratio} %\n"
        f"Tree cover: {Sim.tree_cover} %"
    )
    text.set_text(info_text)
    ax.axis('off')
    Sim.step(frame)
    return [im]


color_list = ['steelblue', 'grey', 'black', 'olivedrab', 'forestgreen', 'orange', 'white']
cmap = colors.ListedColormap(color_list)
bounds = [-3, -2, -1, 0, 1, 2, 3, 4]
norm = colors.BoundaryNorm(bounds, cmap.N)

Sim = WFSim(h=64, w=64)
initial_date = datetime.now().replace(microsecond=0)

fig, ax = plt.subplots(figsize=(6, 6))
im = ax.imshow(Sim.landscape, cmap=cmap, norm=norm)
text = ax.text(2, 10, "", ha='left', fontsize=10, color='white',
               bbox=dict(facecolor='black', alpha=0.8, edgecolor='black', boxstyle='round,pad=0.5'))
plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

ani = animation.FuncAnimation(fig, update, frames=80, interval=20)
ani.save('animation.gif', fps=1.5, savefig_kwargs={'pad_inches': 0})
plt.show()
