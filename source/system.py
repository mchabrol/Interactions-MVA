import numpy as np
from random import random
from source.trader import Trader

class SpinSystem:
    """
    Système gérant l'ensemble des traders (spin + position) sur une grille divisée en damier (black/white).
    """

    def __init__(self, grid_height, grid_width, init_up=0.5):
        """
        Initialise la liste des traders black et white.
        :param grid_height: Nombre de lignes de la grille totale.
        :param grid_width: Nombre de colonnes de la grille totale.
        :param init_up: Pourcentage initial de spins -1 (i.e. 'down').
        """
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.init_up = init_up

        # on stocke les traders black et white
        # chacun a dimension (grid_height x grid_width/2)
        color_width = grid_width // 2

        self.traders_black = []
        self.traders_white = []

        # Créer et initialiser les traders
        self._init_traders(color_width)

    def _init_traders(self, color_width):
        """
        Initialise la liste des traders de manière aléatoire (spin +1 ou -1).
        """
        # Grille black
        for row in range(self.grid_height):
            for col in range(color_width):
                # spin par défaut = +1
                # on met -1 si random() < init_up
                spin_val = -1 if random() < self.init_up else +1
                trader = Trader(row=row, col=col, spin=spin_val, is_black=True)
                self.traders_black.append(trader)

        # Grille white
        for row in range(self.grid_height):
            for col in range(color_width):
                spin_val = -1 if random() < self.init_up else +1
                trader = Trader(row=row, col=col, spin=spin_val, is_black=False)
                self.traders_white.append(trader)

    def precompute_probabilities(self, reduced_neighbor_coupling, market_coupling):
        """
        Calcule les probabilités de flip pour toutes combinaisons de spin (-1 ou +1)
        et sommes de voisins (-4, -2, 0, +2, +4).
        Retourne une matrice 2x5 => [spin_idx][sum_idx].
        """
        probabilities = np.empty((2, 5), dtype=float)
        for row in range(2):
            spin = 1 if row == 1 else -1
            for col in range(5):
                neighbour_sum = -4 + 2*col  # -4, -2, 0, 2, 4
                field = reduced_neighbor_coupling * neighbour_sum - market_coupling * spin
                probabilities[row, col] = 1 / (1 + np.exp(field))
        return probabilities

    def _compute_neighbour_sum(self, trader, all_traders, is_black):
        """
        Calcule la somme des spins voisins (4 voisins: haut, bas, soi-même, horizontal).
        :param trader: l'objet Trader à mettre à jour
        :param all_traders: liste (black ou white) dans laquelle on cherche
                            la valeur du spin.
        :param is_black: bool indiquant si on est en train de mettre à jour black (True) ou white (False).
        """
        row, col = trader.row, trader.col
        grid_height = self.grid_height
        grid_width = len(all_traders) // grid_height  # color_width

        # bords périodiques
        lower_neighbor_row = row + 1 if (row + 1 < grid_height) else 0
        upper_neighbor_row = row - 1
        right_neighbor_col = col + 1 if (col + 1 < grid_width) else 0
        left_neighbor_col = col - 1

        # calcul de l'indice horizontal
        if is_black:
            # si row est pair => on prend right, sinon left
            horizontal_neighbor_col = left_neighbor_col if (row % 2) else right_neighbor_col
        else:
            # inverse
            horizontal_neighbor_col = right_neighbor_col if (row % 2) else left_neighbor_col

        # Récupération des spins : haut/bas/soi-même/horizontal
        # Comme on stocke all_traders dans un tableau 1D, on doit 
        # convertir (r, c) en index => index = r * color_width + c
        def idx(r, c):
            return r * grid_width + c

        spin_up    = all_traders[idx(upper_neighbor_row, col)].spin
        spin_down  = all_traders[idx(lower_neighbor_row, col)].spin
        spin_self  = all_traders[idx(row, col)].spin
        spin_horiz = all_traders[idx(row, horizontal_neighbor_col)].spin

        return spin_up + spin_down + spin_self + spin_horiz

    def _update_subgrid(self, subgrid, other_subgrid, probabilities, is_black):
        """
        Met à jour tous les traders de 'subgrid' en se basant sur les spins de 'other_subgrid'.
        :param subgrid: liste de Trader (black ou white)
        :param other_subgrid: l'autre liste
        :param probabilities: table 2x5 
        :param is_black: bool indiquant si subgrid == black
        """
        for trader in subgrid:
            neighbour_sum = self._compute_neighbour_sum(trader, other_subgrid, is_black)

            # spin_idx : 0 => -1, 1 => +1
            spin_idx = 1 if trader.spin == +1 else 0
            # sum_idx : (-4 => 0, -2 => 1, 0 => 2, 2 => 3, 4 => 4)
            sum_idx = int((neighbour_sum + 4) / 2)

            if random() < probabilities[spin_idx, sum_idx]:
                trader.spin = +1
            else:
                trader.spin = -1

    def update(self, reduced_neighbour_coupling, reduced_alpha):
        """
        Fait une mise à jour complète (black puis white) 
        et renvoie la magnétisation relative.
        """
        # 1) calcul market
        number_of_traders = len(self.traders_black) + len(self.traders_white)
        global_market = sum(t.spin for t in self.traders_black) \
                      + sum(t.spin for t in self.traders_white)
        # magnétisation = global_market / number_of_traders
        market_coupling = reduced_alpha * abs(global_market) / number_of_traders

        # 2) pré-calcul proba
        probabilities = self.precompute_probabilities(reduced_neighbour_coupling, market_coupling)

        # 3) update black (source=black, checkerboard=white)
        self._update_subgrid(self.traders_black, self.traders_white, probabilities, is_black=True)

        # 4) update white (source=white, checkerboard=black)
        self._update_subgrid(self.traders_white, self.traders_black, probabilities, is_black=False)

        return global_market / number_of_traders
