import numpy as np
import matplotlib.pyplot as plt
import math

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


def visualize_grid(grid):
    """
    Affiche une grille de spins sous forme d’une image en noir et blanc.
    
    :param grid: La grille complète de spins (-1 et 1).
    """
    plt.figure(figsize=(6,6))
    plt.imshow(grid, cmap='gray', vmin=-1, vmax=1)
    plt.colorbar(label="Spin Value")
    plt.title('Grid visualization')
    plt.show()


def plot_array_list(arr_list, max_cols=3, timesteps=None):
    """
    Trace la liste de tableaux arr_list dans des subplots.
    max_cols indique le nb maximum de colonnes.
    """
    n_plots = len(arr_list)
    # Déterminer le nombre de colonnes (pas plus que max_cols)
    n_cols = min(n_plots, max_cols)
    # Calculer le nombre de lignes
    n_rows = math.ceil(n_plots / n_cols)
    if not timesteps:
        timesteps = np.arange(len(arr_list))

    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(4*n_cols, 4*n_rows))

    # Au cas où n_rows==1 ou n_cols==1, on transforme axes en liste
    axes = axes.flatten() if n_rows*n_cols > 1 else [axes]

    for i, arr in enumerate(arr_list):
        ax = axes[i]
        # Exemple : on affiche le tableau arr sous forme d’image
        ax.imshow(arr, cmap='gray', interpolation='none')
        ax.set_title(f"Time {timesteps[i]}", fontsize=20)
        ax.axis('off')

    # Si jamais il reste des cases vides dans la grille, on les masque
    for j in range(i+1, n_rows*n_cols):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.show()

