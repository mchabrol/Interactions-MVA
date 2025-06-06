import numpy as np
from random import random

class SpinSystem:
    """
    Classe représentant un système de spins avec mise à jour en damier (checkerboard).
    Possibilité d'ajouter une zone d'agents neutres localisés.
    """

    def __init__(self, grid_height, grid_width, init_up=0.5, fraction_neutral=0.2, region_neutral="random"):
        """
        Initialise le système de spins avec des agents pouvant être neutres.
        
        :param grid_height: Hauteur de la grille
        :param grid_width: Largeur de la grille
        :param init_up: Pourcentage d'agents initialement à +1
        :param fraction_neutral: Fraction d'agents qui seront toujours neutres (S = 0)
        :param region_neutral: Zone où placer les agents neutres ("random", "top_left", "top_right", "bottom_left", "bottom_right")
        """
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.init_up = init_up
        self.fraction_neutral = fraction_neutral
        self.region_neutral = region_neutral

        color_shape = (grid_height, grid_width // 2)
        self.black = np.ones(color_shape, dtype=np.int8)
        self.white = np.ones(color_shape, dtype=np.int8)

        self._init_spins()


    def _init_spins(self):
        """
        Initialise les spins : +1 ("up"), -1 ("down"), 0 (neutre).
        On peut choisir entre une répartition aléatoire des neutres ou une zone localisée.
        """

        total_agents = self.grid_height * self.grid_width
        num_neutral = int(self.fraction_neutral * total_agents)

        full_grid = np.ones((self.grid_height, self.grid_width), dtype=np.int8)

        if self.region_neutral == "random":
            # selection aleatoire de num_neutral agents dans toute la grille
            indices = np.random.choice(total_agents, num_neutral, replace=False)
            full_grid.ravel()[indices] = 0  # mettre les indices selectionnes à 0

        else:
            half_h, half_w = self.grid_height // 2, self.grid_width // 2

            if self.region_neutral == "top_left":
                region_x, region_y = np.meshgrid(np.arange(0, half_h), np.arange(0, half_w), indexing='ij')
            elif self.region_neutral == "top_right":
                region_x, region_y = np.meshgrid(np.arange(0, half_h), np.arange(half_w, self.grid_width), indexing='ij')
            elif self.region_neutral == "bottom_left":
                region_x, region_y = np.meshgrid(np.arange(half_h, self.grid_height), np.arange(0, half_w), indexing='ij')
            elif self.region_neutral == "bottom_right":
                region_x, region_y = np.meshgrid(np.arange(half_h, self.grid_height), np.arange(half_w, self.grid_width), indexing='ij')
            else:
                raise ValueError("Erreur: région neutre invalide ! Choisir 'random', 'top_left', 'top_right', 'bottom_left' ou 'bottom_right'.")

            region_indices = np.ravel_multi_index((region_x.ravel(), region_y.ravel()), full_grid.shape)

            num_neutral_in_zone = min(int(self.fraction_neutral * len(region_indices)), len(region_indices))
            selected_indices = np.random.choice(region_indices, num_neutral_in_zone, replace=False)

            full_grid.ravel()[selected_indices] = 0

        # affectation des valeurs restantes à +1 ou -1
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if full_grid[i, j] == 0:
                    continue  # deja neutre
                full_grid[i, j] = 1 if random() < self.init_up else -1

        self.black[:, :] = full_grid[:, ::2] 
        self.white[:, :] = full_grid[:, 1::2] 


    def precompute_probabilities(self, reduced_neighbor_coupling, market_coupling):
        """
        Calcule les probabilités de flip pour toutes les combinaisons :
        - 2 états initiaux du spin : (+1 ou -1 ou 0)  
        - 9 sommes de voisins possibles : (-4, -3, -2, -1, 0, +1, +2, +3, +4)
        """
        probabilities = np.empty((3, 9), dtype=float)
        # spin_idx: 0 => spin = -1, 1 => spin = +1
        for spin_idx in [0, 1, 2]:
            spin_val = -1 if spin_idx == 2 else spin_idx
            for col in range(9):
                neighbour_sum = -4 + col  # -4, -3, -2, -1, 0, +1, +2, +3, +4
                field = reduced_neighbor_coupling * neighbour_sum \
                        - market_coupling * spin_val 
                probabilities[spin_idx, col] = 1.0 / (1.0 + np.exp(field))
        return probabilities

    def _compute_neighbour_sum(self, is_black, source, row, col):
        """
        Calcule la somme des spins voisins. 
        Les spins neutres (0) sont pris tels quels => s'ajoutent à la somme.
        """
        grid_height, grid_width = source.shape

        # voisin du bas
        lower_neighbor_row = (row + 1) if (row + 1 < grid_height) else 0
        # voisin du haut 
        upper_neighbor_row = (row - 1) if (row - 1 >= 0) else (grid_height - 1)

        # voisins gauche/droite 
        right_neighbor_col = (col + 1) if (col + 1 < grid_width) else 0
        left_neighbor_col  = (col - 1) if (col - 1 >= 0) else (grid_width - 1)

        if is_black:
            horizontal_neighbor_col = left_neighbor_col if (row % 2) else right_neighbor_col
        else:
            horizontal_neighbor_col = right_neighbor_col if (row % 2) else left_neighbor_col

        neighbour_sum = (
            source[upper_neighbor_row, col] +
            source[lower_neighbor_row, col] +
            source[row, col] +
            source[row, horizontal_neighbor_col]
        )
        return int(neighbour_sum)

    def _update_strategies(self, is_black, source, checkerboard_agents, probabilities):
        """
        Met à jour chaque spin (-1/+1) en se référant à checkerboard_agents.
        Les spins neutres (0) ne changent jamais.
        """
        grid_height, grid_width = source.shape
        for row in range(grid_height):
            for col in range(grid_width):
                current_spin = source[row, col]
                if current_spin == 0:
                    continue

                neighbour_sum = self._compute_neighbour_sum(is_black, checkerboard_agents, row, col)
                spin_idx = 2 if current_spin == -1 else current_spin
                # sum_idx = index pour (-4, -3, -2, -1, 0, +1, +2, +3, +4)
                sum_idx = int((neighbour_sum + 4)) 

                # flip
                if random() < probabilities[spin_idx][sum_idx]:
                    source[row, col] = +1
                else:
                    source[row, col] = -1

    def update(self, reduced_neighbour_coupling, reduced_alpha, excluding_neutrals=False):
        """
        Met à jour les spins en excluant les neutres.
        """
        number_of_traders = 2 * self.black.shape[0] * self.black.shape[1] #
        global_market = np.sum(self.black + self.white)

        market_coupling = reduced_alpha * abs(global_market) / number_of_traders
        probabilities = self.precompute_probabilities(reduced_neighbour_coupling, market_coupling)

        self._update_strategies(True,  self.black, self.white, probabilities)
        self._update_strategies(False, self.white, self.black, probabilities)

        if not excluding_neutrals:
            return global_market / number_of_traders
        if excluding_neutrals: 
            if self.region_neutral == "random":
                number_of_neutrals = int(self.fraction_neutral * self.grid_height * self.grid_width)
            else : 
                number_of_neutrals = int(self.fraction_neutral * (self.grid_height * self.grid_width)/4)
            return (global_market) / (number_of_traders - number_of_neutrals)
    
   


