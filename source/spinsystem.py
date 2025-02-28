import numpy as np
from random import random

class SpinSystem:
    """
    Classe représentant un système de spins avec mise à jour en damier (checkerboard).
    """

    def __init__(self, grid_height, grid_width, init_up=0.5):
        """
        Initialise la grille (black, white) avec un pourcentage init_up de spins "down" (-1).
        """
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.init_up = init_up  # Pourcentage de spins initiaux orientés "down"

        # Initialisation des deux sous-matrices black et white
        # On conserve l'idée de color_shape pour stocker la moitié du nombre de colonnes
        color_shape = (grid_height, grid_width // 2)
        self.black = np.ones(color_shape, dtype=np.byte)
        self.white = np.ones(color_shape, dtype=np.byte)

        self._init_spins()

    def _init_spins(self):
        """
        Initialise aléatoirement les spins dans black et white :
        +1 = spin "up", -1 = spin "down".
        """
        for color_arr in (self.black, self.white):
            rows, cols = color_arr.shape
            for row in range(rows):
                for col in range(cols):
                    # Si random() < init_up, on met le spin à -1 ("down"),
                    # sinon il reste +1 ("up").
                    if random() < self.init_up:
                        color_arr[row, col] = -1

    def precompute_probabilities(self, reduced_neighbor_coupling, market_coupling):
        """
        Calcule les probabilités de flip pour toutes les combinaisons :
        - 2 états initiaux du spin : (+1 ou -1)
        - 5 sommes de voisins possibles : (-4, -2, 0, +2, +4)
        """
        probabilities = np.empty((2, 5), dtype=float)
        for row in range(2):
            # row=0 => spin=-1, row=1 => spin=+1
            spin = 1 if row else -1
            for col in range(5):
                neighbour_sum = -4 + 2*col  # -4, -2, 0, +2, +4
                field = reduced_neighbor_coupling * neighbour_sum \
                        - market_coupling * spin
                # Règle de Heatbath : P(flip) = 1 / (1 + exp(field))
                probabilities[row, col] = 1 / (1 + np.exp(field))
        return probabilities

    def _compute_neighbour_sum(self, is_black, source, row, col):
        """
        Calcule la somme des spins voisins selon la mise à jour en damier.
        - is_black indique si on met à jour la grille "black".
        - source est l'autre grille (voisins).
        """
        grid_height, grid_width = source.shape

        # Voisins haut/bas (avec bords périodiques)
        lower_neighbor_row = row + 1 if (row + 1 < grid_height) else 0
        upper_neighbor_row = row - 1

        # Voisins gauche/droite (avec bords périodiques)
        right_neighbor_col = col + 1 if (col + 1 < grid_width) else 0
        left_neighbor_col = col - 1

        # Détermine le voisin horizontal en fonction de la parité de row
        if is_black:
            horizontal_neighbor_col = left_neighbor_col if (row % 2) else right_neighbor_col
        else:
            horizontal_neighbor_col = right_neighbor_col if (row % 2) else left_neighbor_col

        # Somme des spins : haut + bas + lui-même + voisin horizontal
        neighbour_sum = (
            source[upper_neighbor_row, col]
            + source[lower_neighbor_row, col]
            + source[row, col]
            + source[row, horizontal_neighbor_col]
        )
        return int(neighbour_sum)

    def _update_strategies(self, is_black, source, checkerboard_agents, probabilities):
        """
        Met à jour tous les spins de 'source' (black ou white) en se basant sur la grille 'checkerboard_agents'.
        """
        grid_height, grid_width = source.shape

        for row in range(grid_height):
            for col in range(grid_width):
                neighbour_sum = self._compute_neighbour_sum(is_black, checkerboard_agents, row, col)

                # Convertit le spin (-1 ou +1) en index (0 ou 1)
                spin_idx = int((source[row, col] + 1) / 2)  # -1 -> 0, +1 -> 1
                # Convertit la somme des voisins (-4,-2,0,2,4) en index (0..4)
                sum_idx = int((neighbour_sum + 4) / 2)

                # Tire un nombre aléatoire pour décider si le spin bascule
                if random() < probabilities[spin_idx][sum_idx]:
                    source[row, col] = 1
                else:
                    source[row, col] = -1

    def update(self, reduced_neighbour_coupling, reduced_alpha):
        """
        Met à jour l'ensemble du système (black puis white),
        calcule la magnétisation relative et la renvoie.
        """
        # Nombre total de spins
        number_of_traders = 2 * self.black.shape[0] * self.black.shape[1]

        # Calcul de la magnétisation globale
        global_market = np.sum(self.black + self.white)

        # Calcul de l'effet du marché
        market_coupling = reduced_alpha * np.abs(global_market) / number_of_traders

        # Précalcul des probabilités de flip
        probabilities = self.precompute_probabilities(reduced_neighbour_coupling, market_coupling)

        # Mise à jour d'abord des spins "black" (en se référant à "white"),
        # puis des spins "white" (en se référant à "black").
        self._update_strategies(True,  self.black, self.white, probabilities)
        self._update_strategies(False, self.white, self.black, probabilities)

        # Retourne la magnétisation relative
        return global_market / number_of_traders
