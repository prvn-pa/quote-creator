import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from datetime import datetime

# Fixed pastel color palette (converted to 0–1 scale)
PASTEL_COLORS = [
    (62/255, 33/255, 97/255), (137/255, 79/255, 166/255),
    (203/255, 78/255, 145/255), (245/255, 121/255, 148/255),
    (246/255, 132/255, 178/255), (244/255, 98/255, 108/255),
    (182/255, 97/255, 184/255), (71/255, 88/255, 153/255),
    (110/255, 98/255, 157/255)
]

def choose_color():
    return random.choice(PASTEL_COLORS)

def draw_layered_hills(ax, num_layers=6, height_variation=0.1):
    base_y = 0.3
    for i in range(num_layers):
        color = choose_color()
        y_offset = base_y + i * 0.05
        x = np.linspace(0, 1, 500)
        y = np.sin(x * 5 + i) * height_variation + y_offset
        y = np.clip(y, 0, 1)
        ax.fill_between(x, y, y2=0, color=color, zorder=5 + i)

def draw_sky_gradient(ax):
    top = choose_color()
    bottom = choose_color()
    for i in range(100):
        r = i / 100
        color = r * np.array(top) + (1 - r) * np.array(bottom)
        ax.fill_between([0, 1], 1 - r * 0.5, 1 - r * 0.5 + 0.01, color=color, zorder=0)

def draw_sun(ax):
    sun_color = choose_color()
    sun = patches.Circle((0.75, 0.72), 0.12, color=sun_color, zorder=3)
    ax.add_patch(sun)

def draw_path(ax):
    path_color = choose_color()
    t = np.linspace(0, 1, 500)
    x = t
    y = 0.15 + 0.05 * np.sin(t * 6)
    ax.plot(x, y, color=path_color, linewidth=10, zorder=10)

def draw_scene(save_path='generated_pastel_landscape'):
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=200)  # 2560x1440
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')  # Ensure circles are perfect
    ax.axis('off')

    draw_sky_gradient(ax)
    draw_sun(ax)  # Draw sun first so hills can overlap it
    draw_layered_hills(ax)
    draw_path(ax)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{save_path}_{timestamp}.png"
    plt.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"Image saved as {filename}")

draw_scene()

