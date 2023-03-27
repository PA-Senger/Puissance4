import fct_puissance4 as f
import graph
import time


set = f.create_new_game()       # nouvelle matrice de jeu
g = graph.fenetre((6, 7), 80)   # nouvelle fenêtre de jeu 6*7
msg = g.affiche_texte((240, 280), "PUISSANCE 4", couleur="purple")
tour = 1                        # initialisation du tour de jeu
over = False                    # game over ?
while over is False:
    joueur = None
    if tour % 2 == 0:           # attribution du joueur
        joueur = 2
    else:
        joueur = 1
    p = g.attend_clic()                   # attend un clic de l'utilisateur
    if p[0] == "FIN" or p[0] == "<esc>":  # condition de fermeture du jeu
        g.ferme()
        exit(0)
    col = f.clic_col(p[1])              # fct la plus inutile du game
    playable = f.check_col(col, set)    # verifie si la colonne est jouable
    if playable:                        # si jouable
        g.supprime(msg)
        cell = f.drop_coord(col, set)   # coord du pion a afficher
        x, y = cell
        for i in range(x):              # dropping du pion
            set[i][y] = g.affiche_pion((i, y), joueur)
            time.sleep(0.08)
            g.supprime(set[i][y])
            set[i][y] = None
        g.affiche_pion(cell, joueur)      # affichage du pion a destination
        set[x][y] = joueur                # place le nb du joueur ds la matrice
        if tour == 42:                    # conditon match nul
            g.affiche_texte((240, 280), "DRAW MATCH", couleur="purple")
            over = True                   # game over
        a = f.diag1((cell), joueur, set)  # check si un joueur a gagné
        b = f.diag2((cell), joueur, set)
        c = f.hori((cell), joueur, set)
        d = f.vert((cell), joueur, set)
        if joueur == 1:                 # condition victoire joueur 1
            if a == 4 or b == 4 or c == 4 or d == 4:
                g.affiche_texte((240, 280), "PLAYER 1 WINS", couleur="purple")
                over = True             # game over
        if joueur == 2:                 # condition victoire joueur 2
            if a == 4 or b == 4 or c == 4 or d == 4:
                g.affiche_texte((240, 280), "PLAYER 2 WINS", couleur="purple")
                over = True            # game over
        while over:                    # si game over, attend la fermeture
            p = g.attend_clic()
            if p[0] == "FIN" or p[0] == "<esc>":
                g.ferme()
                exit(0)
        tour += 1
