import numpy as np
from random import random

class SpinSystem:
    """
    Classe représentant un système de spins avec mise à jour en damier (checkerboard).
    Inclut un sous-groupe d'agents privilégiés réagissant différemment.
    """

    def __init__(
        self,
        grid_height: int,
        grid_width: int,
        init_up: float = 0.5,
        privileged_fraction: float = 0.1,
        privileged_flip_factor: float = 1.5
    ):
        """
        :param grid_height: Nombre de lignes de la grille (height).
        :param grid_width: Nombre de colonnes de la grille (width).
        :param init_up: Pourcentage de spins initiaux orientés "down" (-1).
                        (ex. init_up = 0.3 => 30% de -1, 70% de +1)
        :param privileged_fraction: Fraction d'agents privilégiés (0 <= f <= 1).
        :param privileged_flip_factor: Facteur de multiplication de la proba
                                       de flip pour les agents privilégiés.
        """
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.init_up = init_up
        self.privileged_fraction = privileged_fraction
        self.privileged_flip_factor = privileged_flip_factor

        # Taille des sous-grilles "black" et "white"
        color_shape = (grid_height, grid_width // 2)

        # Grilles de spins
        self.black = np.ones(color_shape, dtype=np.byte)
        self.white = np.ones(color_shape, dtype=np.byte)

        # Masques booléens pour identifier les agents privilégiés
        self.black_privileged = np.zeros(color_shape, dtype=bool)
        self.white_privileged = np.zeros(color_shape, dtype=bool)

        # Initialisation aléatoire des spins
        self._init_spins()

        # Sélection aléatoire des agents privilégiés
        self._init_privileged_agents()

    def _init_spins(self):
        """
        Initialise aléatoirement les spins dans black et white :
        +1 = spin "up", -1 = spin "down".
        """
        for color_arr in (self.black, self.white):
            rows, cols = color_arr.shape
            for row in range(rows):
                for col in range(cols):
                    if random() < self.init_up:
                        color_arr[row, col] = -1  # "down"
                    else:
                        color_arr[row, col] = +1  # "up"

    def _init_privileged_agents(self):
        """
        Marque une fraction privileged_fraction de spins comme "privilégiés" 
        dans black et white. On choisit au hasard.
        """
        # black
        rows_b, cols_b = self.black_privileged.shape
        nb_agents_black = rows_b * cols_b
        nb_priv_black = int(nb_agents_black * self.privileged_fraction)
        indices_black = np.random.choice(nb_agents_black, size=nb_priv_black, replace=False)
        self.black_privileged.ravel()[indices_black] = True

        # white
        rows_w, cols_w = self.white_privileged.shape
        nb_agents_white = rows_w * cols_w
        nb_priv_white = int(nb_agents_white * self.privileged_fraction)
        indices_white = np.random.choice(nb_agents_white, size=nb_priv_white, replace=False)
        self.white_privileged.ravel()[indices_white] = True

    def precompute_probabilities(self, reduced_neighbor_coupling: float, market_coupling: float) -> np.ndarray:
        """
        Calcule les probabilités de flip pour toutes les combinaisons :
        - 2 états initiaux du spin : +1 ou -1 (row=0 => spin=-1, row=1 => spin=+1)
        - 5 sommes de voisins possibles : -4, -2, 0, +2, +4 (col=0..4)
        
        :param reduced_neighbor_coupling: (-2 * beta * j)
        :param market_coupling: (reduced_alpha * abs(M) / number_of_traders)
        :return: un tableau (2,5) de probabilités
        """
        probabilities = np.empty((2, 5), dtype=float)
        for row in range(2):
            spin = 1 if row == 1 else -1
            for col in range(5):
                neighbour_sum = -4 + 2 * col  # -4, -2, 0, +2, +4
                field = (reduced_neighbor_coupling * neighbour_sum) - (market_coupling * spin)
                # Règle de Heatbath : P(flip) = 1 / (1 + exp(field))
                prob_flip = 1 / (1 + np.exp(field))
                probabilities[row, col] = prob_flip

        return probabilities

    def _compute_neighbour_sum(self, is_black: bool, source: np.ndarray, row: int, col: int) -> int:
        """
        Calcule la somme des spins voisins en mode damier (4 voisins):
        - haut, bas, soi-même, horizontal
        :param is_black: indique si on traite la sous-grille black ou white
        :param source: l'autre sous-grille servant de voisins
        :param row, col: position dans la sous-grille
        :return: somme entière des spins
        """
        grid_height, grid_width = source.shape

        # bords périodiques (haut/bas)
        lower_neighbor_row = (row + 1) if ((row + 1) < grid_height) else 0
        upper_neighbor_row = (row - 1)

        # bords périodiques (gauche/droite)
        right_neighbor_col = (col + 1) if ((col + 1) < grid_width) else 0
        left_neighbor_col = (col - 1)

        if is_black:
            # si row est pair => droite, sinon gauche
            horizontal_neighbor_col = left_neighbor_col if (row % 2) else right_neighbor_col
        else:
            # inverse
            horizontal_neighbor_col = right_neighbor_col if (row % 2) else left_neighbor_col

        neighbour_sum = (
            source[upper_neighbor_row, col]
            + source[lower_neighbor_row, col]
            + source[row, col]
            + source[row, horizontal_neighbor_col]
        )
        return int(neighbour_sum)

    def _update_subgrid(
        self,
        is_black: bool,
        source: np.ndarray,
        checkerboard_agents: np.ndarray,
        probabilities: np.ndarray,
        global_market: int
    ):
        """
        Met à jour tous les spins de 'source' (black ou white).
        :param is_black: True si on met à jour black, False si on met à jour white
        :param source: la sous-grille en cours de mise à jour (self.black ou self.white)
        :param checkerboard_agents: l'autre sous-grille (white ou black)
        :param probabilities: matrice 2x5 de proba calculée par precompute_probabilities
        :param global_market: somme totale des spins (black + white)
        """
        grid_height, grid_width = source.shape

        # masque booléen des agents privilégiés (black ou white)
        privileged_mask = self.black_privileged if is_black else self.white_privileged

        for row in range(grid_height):
            for col in range(grid_width):
                neighbour_sum = self._compute_neighbour_sum(is_black, checkerboard_agents, row, col)
                # spin_idx: 0 => -1, 1 => +1
                current_spin = source[row, col]
                spin_idx = 1 if current_spin == +1 else 0

                sum_idx = int((neighbour_sum + 4) / 2)

                base_prob = probabilities[spin_idx, sum_idx]

                # Si l'agent est privilégié, on multiplie la prob de flip par privileged_flip_factor
                if privileged_mask[row, col]:
                    prob = base_prob * self.privileged_flip_factor
                    prob = min(prob, 1.0)  # cap à 1
                else:
                    prob = base_prob

                # Décision de flip
                if random() < prob:
                    source[row, col] = +1
                else:
                    source[row, col] = -1

    def update(self, reduced_neighbour_coupling: float, reduced_alpha: float) -> float:
        """
        Fait une mise à jour complète (black puis white),
        et renvoie la magnétisation relative (global_market / number_of_traders).
        :param reduced_neighbour_coupling: -2 * beta * j
        :param reduced_alpha: -2 * beta * alpha
        :return: magnétisation (valeur dans [-1, +1])
        """
        # 1) Calcul du nombre total de spins
        number_of_traders = 2 * self.black.shape[0] * self.black.shape[1]

        # 2) Calcul de la magnétisation globale
        global_market = np.sum(self.black + self.white)

        # 3) Calcul de l'effet du marché (market_coupling)
        market_coupling = reduced_alpha * np.abs(global_market) / number_of_traders

        # 4) Pré-calcul des probabilités de flip
        probabilities = self.precompute_probabilities(reduced_neighbour_coupling, market_coupling)

        # 5) Mise à jour de la sous-grille black
        self._update_subgrid(True, self.black, self.white, probabilities, global_market)
        # 6) Mise à jour de la sous-grille white
        self._update_subgrid(False, self.white, self.black, probabilities, global_market)

        # 7) Retourne la magnétisation relative
        return global_market / number_of_traders
