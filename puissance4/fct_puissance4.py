"""Contient les fonctions pour créer un puissance4.

Les fonctions on été testé individuelement.

Copyright mars 2019, PA Lambrecht.
Distribué sous licence publique WTFPL, version 2 (http://www.wtfpl.net/)
"""


def create_new_game():
    """Create a new matrice filled with None.

    return : list, matrice
    """
    set = []
    for i in range(6):
        set += [[]]
        for j in range(7):
            set[i] += [None]
    return set


def check_col(y, l):
    """Check if the column y is playable.

    param y : int, coord of the col.
    param l : list, matrix of the game.
    return : bool, True if playable else False.
    """
    for i in range(len(l)):
        if l[i][y]is None:
            return True
    return False


def clic_col(xy):
    """Return the column corresponding when the player clics.

    param xy : couple, coord in the matrix.
    return : int, column.
    """
    return xy[1]


def drop_coord(y, l):
    """Find the coord for the token to land.

    param y : int, column.
    param l : list, matrix of the game.
    return : couple, coord for the token to land.
    """
    for i in range(len(l)):
        if l[i][y] is not None:
            return (i - 1, y)
    return (i, y)


# condition de victoire
# diagonale1
def diag1(cell, joueur, l):
    """Loop search in diagonale for player's token.

    param cell: couple, coord token.
    param joueur: int, player.
    param l: list, matrix.
    return : int, nb of token aligned.
    """
    win = 1
    x, y = cell
    checkpoint = [cell]
    while l[x][y] == joueur:
        x -= 1
        y -= 1
        if 0 <= x <= 5 and 0 <= y <= 6 and l[x][y] == joueur:
            win += 1
        else:
            cell = checkpoint[0]
            x, y = cell
            while l[x][y] == joueur:
                x += 1
                y += 1
                if 0 <= x <= 5 and 0 <= y <= 6 and l[x][y] == joueur:
                    win += 1
                else:
                    return win
    return win


# diagonale2
def diag2(cell, joueur, l):
    """Loop search in diagonale for player's token.

    param cell: couple, coord token.
    param joueur: int, player.
    param l: list, matrix.
    return : int, nb of token aligned.
    """
    win = 1
    x, y = cell
    checkpoint = [cell]
    while l[x][y] == joueur:
        x -= 1
        y += 1
        if 0 <= x <= 5 and 0 <= y <= 6 and l[x][y] == joueur:
            win += 1
        else:
            cell = checkpoint[0]
            x, y = cell
            while l[x][y] == joueur:
                x += 1
                y -= 1
                if 0 <= x <= 5 and 0 <= y <= 6 and l[x][y] == joueur:
                    win += 1
                else:
                    return win
    return win


# horizontale
def hori(cell, joueur, l):
    """Loop search in horizontale for player's token.

    param cell: couple, coord token.
    param joueur: int, player.
    param l: list, matrix.
    return : int, nb of token aligned.
    """
    win = 1
    x, y = cell
    checkpoint = [cell]
    while l[x][y] == joueur:
        y -= 1
        if 0 <= x <= 5 and 0 <= y <= 6 and l[x][y] == joueur:
            win += 1
        else:
            cell = checkpoint[0]
            x, y = cell
            while l[x][y] == joueur:
                y += 1
                if 0 <= x <= 5 and 0 <= y <= 6 and l[x][y] == joueur:
                    win += 1
                else:
                    return win
    return win


# verticale
def vert(cell, joueur, l):
    """Loop search in verticale for player's token.

    param cell: couple, coord token.
    param joueur: int, player.
    param l: list, matrix.
    return : int, nb of token aligned.
    """
    win = 1
    x, y = cell
    checkpoint = [cell]
    while l[x][y] == joueur:
        x -= 1
        if 0 <= x <= 5 and 0 <= y <= 6 and l[x][y] == joueur:
            win += 1
        else:
            cell = checkpoint[0]
            x, y = cell
            while l[x][y] == joueur:
                x += 1
                if 0 <= x <= 5 and 0 <= y <= 6 and l[x][y] == joueur:
                    win += 1
                else:
                    return win
    return win
