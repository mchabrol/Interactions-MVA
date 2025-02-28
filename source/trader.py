class Trader:
    """
    Représente un agent (trader) individuel dans le système de spins.
    """

    def __init__(self, row, col, spin=1, is_black=True):
        """
        :param row: Indice de ligne dans la grille.
        :param col: Indice de colonne dans la grille.
        :param spin: État du trader : +1 (acheteur) ou -1 (vendeur).
        :param is_black: Booléen indiquant si ce trader appartient 
                         à la grille 'black' (True) ou 'white' (False).
        """
        self.row = row
        self.col = col
        self.spin = spin
        self.is_black = is_black

    def flip(self):
        """
        Inverse le spin du trader.
        """
        self.spin = -self.spin

    def __repr__(self):
        return f"Trader(row={self.row}, col={self.col}, spin={self.spin}, is_black={self.is_black})"
