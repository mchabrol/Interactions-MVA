import numpy as np
import matplotlib.pyplot as plt
import math
import matplotlib.colors as colors

def read_config_file(filename):
    config = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split("=")
            config[key.strip()] = value.strip()
    return config

def reconstruct_grid(black, white):
    """
    Rebuild complet grid from sub-matrices black and white.

    :param black: black spin array 
    :param white: white spin array
    :return: full grid
    """
    # dimensions
    rows, cols_half = black.shape
    cols = cols_half * 2  
    
    full_grid = np.zeros((rows, cols), dtype=np.byte)
    
    full_grid[:, ::2] = black 
    full_grid[:, 1::2] = white

    return full_grid


def visualize_grid(grid, title='Grid visualization'):
    """
    Plot a grid with spins in {-1, 0, +1}.
    """
    cmap = colors.ListedColormap(['black', 'gray', 'white'])
    bounds = [-1.5, -0.5, 0.5, 1.5]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    plt.figure(figsize=(6,6))
    im = plt.imshow(grid, cmap=cmap, norm=norm)

    cbar = plt.colorbar(im, ticks=[-1, 0, 1])
    cbar.set_label("Spin Value")

    plt.title(title)
    plt.show()


def plot_array_list(arr_list, max_cols=3, timesteps=None):
    """
    Plot each grid of arr_list in a subplot, using a colormap.
    """
    from math import ceil
    
    n_plots = len(arr_list)
    n_cols = min(n_plots, max_cols)
    n_rows = ceil(n_plots / n_cols)
    if not timesteps:
        timesteps = np.arange(len(arr_list))

    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(4*n_cols, 4*n_rows))
    axes = axes.flatten() if n_rows*n_cols > 1 else [axes]

    cmap = colors.ListedColormap(['black', 'gray', 'white'])
    bounds = [-1.5, -0.5, 0.5, 1.5]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    for i, arr in enumerate(arr_list):
        ax = axes[i]
        im = ax.imshow(arr, cmap=cmap, norm=norm)
        ax.set_title(f"Time {timesteps[i]}", fontsize=12)
        ax.axis('off')


    for j in range(i+1, n_rows*n_cols):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    plt.suptitle("Evolution of the system", fontsize=16)
    plt.show()

