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
    Reconstruit la grille complète à partir des sous-matrices black et white.
    
    :param black: Tableau des spins noirs.
    :param white: Tableau des spins blancs.
    :return: Grille complète fusionnée.
    """
    # Dimensions
    rows, cols_half = black.shape
    cols = cols_half * 2  # La vraie grille a le double de colonnes
    
    # Créer une grille vide
    full_grid = np.zeros((rows, cols), dtype=np.byte)
    
    # Remplissage de la grille en damier
    full_grid[:, ::2] = black  # `black` dans les colonnes paires
    full_grid[:, 1::2] = white  # `white` dans les colonnes impaires

    return full_grid


def visualize_grid(grid, title='Grid visualization'):
    """
    Affiche une grille dont les spins sont dans {-1, 0, +1} 
    en utilisant un colormap discret : noir, gris, blanc.
    """
    # 1) Définir les couleurs et les bornes
    cmap = colors.ListedColormap(['black', 'gray', 'white'])
    # Les bornes délimitent les intervalles pour chaque couleur
    bounds = [-1.5, -0.5, 0.5, 1.5]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    plt.figure(figsize=(6,6))
    # 2) Afficher l'image avec la cmap et le norm adéquat
    im = plt.imshow(grid, cmap=cmap, norm=norm)

    # 3) Ajouter la barre de couleur avec des ticks discrets
    cbar = plt.colorbar(im, ticks=[-1, 0, 1])
    cbar.set_label("Spin Value")

    plt.title(title)
    plt.show()


def plot_array_list(arr_list, max_cols=3, timesteps=None):
    """
    Trace chaque grille de arr_list dans un subplot, en utilisant un colormap discret.
    """
    from math import ceil
    
    n_plots = len(arr_list)
    n_cols = min(n_plots, max_cols)
    n_rows = ceil(n_plots / n_cols)
    if not timesteps:
        timesteps = np.arange(len(arr_list))

    # Préparer la figure
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(4*n_cols, 4*n_rows))
    axes = axes.flatten() if n_rows*n_cols > 1 else [axes]

    # Définir le colormap discret
    cmap = colors.ListedColormap(['black', 'gray', 'white'])
    bounds = [-1.5, -0.5, 0.5, 1.5]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    for i, arr in enumerate(arr_list):
        ax = axes[i]
        im = ax.imshow(arr, cmap=cmap, norm=norm)
        ax.set_title(f"Time {timesteps[i]}", fontsize=12)
        ax.axis('off')

    # Masquer les axes inutilisés
    for j in range(i+1, n_rows*n_cols):
        axes[j].set_visible(False)

    # Ajouter une colorbar pour l'ensemble
    #cbar = fig.colorbar(im, ax=axes, ticks=[-1, 0, 1], orientation='horizontal', fraction=0.05, pad=0.05)
    #cbar.set_label("Spin Value")

    plt.tight_layout()
    plt.show()

