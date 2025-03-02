import numpy as np
from random import random

class SpinSystem:
    """
    Classe représentant un système de spins avec mise à jour en damier (checkerboard).
    Contient une methode induce_local_crash qui force un groupe d'agents à vendre (krach boursier)
    """

    def __init__(self, grid_height, grid_width, init_up=0.5):
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.init_up = init_up

        color_shape = (grid_height, grid_width // 2)
        self.black = np.ones(color_shape, dtype=np.byte)
        self.white = np.ones(color_shape, dtype=np.byte)
        self._init_spins()

    def _init_spins(self):
        for color_arr in (self.black, self.white):
            rows, cols = color_arr.shape
            for row in range(rows):
                for col in range(cols):
                    if random() < self.init_up:
                        color_arr[row, col] = -1
                    else:
                        color_arr[row, col] = +1

    def precompute_probabilities(self, reduced_neighbor_coupling, market_coupling):
        probabilities = np.empty((2, 5), dtype=float)
        for row in range(2):
            spin = +1 if row == 1 else -1
            for col in range(5):
                neighbour_sum = -4 + 2 * col
                field = reduced_neighbor_coupling * neighbour_sum - market_coupling * spin
                probabilities[row, col] = 1 / (1 + np.exp(field))
        return probabilities

    def _compute_neighbour_sum(self, is_black, source, row, col):
        grid_height, grid_width = source.shape
        lower_neighbor_row = row + 1 if (row + 1 < grid_height) else 0
        upper_neighbor_row = row - 1
        right_neighbor_col = col + 1 if (col + 1 < grid_width) else 0
        left_neighbor_col = col - 1

        if is_black:
            horizontal_neighbor_col = left_neighbor_col if (row % 2) else right_neighbor_col
        else:
            horizontal_neighbor_col = right_neighbor_col if (row % 2) else left_neighbor_col

        neighbour_sum = (
            source[upper_neighbor_row, col]
            + source[lower_neighbor_row, col]
            + source[row, col]
            + source[row, horizontal_neighbor_col]
        )
        return int(neighbour_sum)

    def _update_strategies(self, is_black, source, checkerboard_agents, probabilities):
        grid_height, grid_width = source.shape
        for row in range(grid_height):
            for col in range(grid_width):
                neighbour_sum = self._compute_neighbour_sum(is_black, checkerboard_agents, row, col)
                spin_idx = int((source[row, col] + 1) / 2)  # -1 -> 0, +1 -> 1
                sum_idx = int((neighbour_sum + 4) / 2)
                if random() < probabilities[spin_idx][sum_idx]:
                    source[row, col] = +1
                else:
                    source[row, col] = -1

    def update(self, reduced_neighbour_coupling, reduced_alpha):
        number_of_traders = 2 * self.black.shape[0] * self.black.shape[1]
        global_market = np.sum(self.black + self.white)

        market_coupling = reduced_alpha * abs(global_market) / number_of_traders
        probabilities = self.precompute_probabilities(reduced_neighbour_coupling, market_coupling)

        self._update_strategies(True,  self.black, self.white, probabilities)
        self._update_strategies(False, self.white, self.black, probabilities)

        return global_market / number_of_traders

    # -----------------------------
    # METHODE POUR INDUIRE UN CHOC
    # -----------------------------
    def induce_local_crash(self, fraction=0.05, region="random"):
        """
        Force une fraction d'agents à devenir vendeurs (-1) 
        dans une zone localisée (choc).
        
        :param fraction: Pourcentage d'agents dans la zone qui seront forcés à -1
        :param region: 
           - "random": choisit des positions aléatoires sur la grille complète
           - "top_left", "bottom_left", etc.
        """
        # black + white => on va manipuler le tableau complet
        # mais la portion est stockée en 2 sous-grilles
        rows_b, cols_b = self.black.shape
        nb_agents_black = rows_b * cols_b
        nb_change_black = int(nb_agents_black * fraction)

        rows_w, cols_w = self.white.shape
        nb_agents_white = rows_w * cols_w
        nb_change_white = int(nb_agents_white * fraction)

        if region == "random":
            # Choix aléatoire de nb_change_black positions dans black
            indices_b = np.random.choice(nb_agents_black, size=nb_change_black, replace=False)
            self.black.ravel()[indices_b] = -1
            # Idem pour white
            indices_w = np.random.choice(nb_agents_white, size=nb_change_white, replace=False)
            self.white.ravel()[indices_w] = -1

        elif region == "top_left":
            # on cible la moitié supérieure et la moitié gauche
            # pour black
            half_rows_b = rows_b // 2
            half_cols_b = cols_b // 2
            self.black[:half_rows_b, :half_cols_b] = -1
            # pour white
            half_rows_w = rows_w // 2
            half_cols_w = cols_w // 2
            self.white[:half_rows_w, :half_cols_w] = -1

        elif region == "top_right":
            # on cible la moitié supérieure et la moitié droite
            # pour black
            half_rows_b = rows_b // 2
            half_cols_b = cols_b // 2
            self.black[:half_rows_b, half_cols_b:] = -1
            # pour white
            half_rows_w = rows_w // 2
            half_cols_w = cols_w // 2
            self.white[:half_rows_w, half_cols_w:] = -1

        elif region == "bottom_left":
            # on cible la moitié inférieure et la moitié gauche
            # pour black
            half_rows_b = rows_b // 2
            half_cols_b = cols_b // 2
            self.black[half_rows_b:, :half_cols_b] = -1
            # pour white
            half_rows_w = rows_w // 2
            half_cols_w = cols_w // 2
            self.white[half_rows_w:, :half_cols_w] = -1

        elif region == "bottom_right":
            # on cible la moitié inférieure et la moitié droite
            # pour black
            half_rows_b = rows_b // 2
            half_cols_b = cols_b // 2
            self.black[half_rows_b:, half_cols_b:] = -1
            # pour white
            half_rows_w = rows_w // 2
            half_cols_w = cols_w // 2
            self.white[half_rows_w:, half_cols_w:] = -1

        else:
            raise ValueError("Error: param region must be 'random', 'top_left', 'top_right', 'bottom_left', or 'bottom_right'")