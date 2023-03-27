"""Interface graphique basée sur tkinter, événementielle mais non asynchrone.

Version 0.1b

On peut tester ce module en lançant directement l'interpréteur python avec ce
module en argument, le programme de test qui se trouve à la fin de ce fichier
sera appelé.

La classe principale fenetre et toutes ses méthodes sont décrites ci-dessous,
et une documentation en ligne est disponible sous python3 :
$ python3
>>> import graph
>>> help(graph)
ou
>>> help(graph.fenetre.<nom de fonction>)

Copyright décembre 2018, Vincent Loechner.
Distribué sous licence publique WTFPL, version 2 (http://www.wtfpl.net/)
"""

import tkinter as tk
import time
import queue

class fenetre(tk.Canvas):
    """Classe principale pour une fenêtre graphique.

    Arguments de création :
    - taille: un couple (hauteur, largeur) qui donne la taille du plateau
      (8, 8) par défaut
    - pixels: nombre de pixels de côté d'une case (80 par défaut)
    - axes: si True, affiche un cadre : des lignes verticales/horizontales qui
      séparent les cases (True par défaut)

    Hérite de la classe canvas, on peut directement appeler les méthodes sur
    les canvas sur une fenêtre (pour les experts !)
    Voir la documentation, chapitre "8. The Canvas widget" du document :
    http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html
    """

    def __init__(
        self, taille=(8, 8), pixels=80, axes=True
    ):
        """Initialisation de la classe fenêtre.

        Crée l'objet tkinter root, le canvas (dont hérite cette classe fenetre)
        et redirige les événements utilisés vers les fonctions adéquates.
        Les arguments sont décrits dans la documentation de la classe fenêtre.
        """
        # les quelques méthodes privées ci-dessous servent à réagir aux
        # événements de l'interface tkinter

        # privée: appelée si l'utilisateur clique sur une case
        def click(evenement):
            # min car on peut cliquer sur le dernier pixel qui déborde:
            i = min((evenement.y-1)//self.pixels, self.taille[0]-1)
            j = min((evenement.x-1)//self.pixels, self.taille[1]-1)
            # ajoute (ligne,colonne) à la queue
            self.eventq.put(("clic", (i, j)))
            # et sort de la mainloop d'attente
            self.root.quit()

        # privée: appelée si l'utilisateur tape une touche
        def key(evenement):
            # # min car on peut cliquer sur le dernier pixel qui déborde:
            # i = min((evenement.y-1)//self.pixels, self.taille[0]-1)
            # j = min((evenement.x-1)//self.pixels, self.taille[1]-1)
            # # ajoute (ligne,colonne) à la queue
            # self.eventq.put("clic", (i, j))
            self.eventq.put(("touche", evenement.keysym))

            # et sort de la mainloop d'attente
            self.root.quit()

        # privée: appelée si l'utilisateur ferme la fenêtre
        def async_end():
            # met "FIN" dans la queue et sort de mainloop
            # utilisation en appel asynchrone (provoqué par un événement)
            self.eventq.put(("FIN", None))
            self.ferme()

        # privée: vérifie régulièrement s'il n'y a pas des événements en
        # attente dans la queue, et réveille le thread d'attente si oui.
        def checke():
            self.after_id = self.root.after(1000, checke)
            # arrête mainloop
            self.root.quit()

        #################################
        # l'initialisation démarre ici
        self.taille = taille
        self.pixels = pixels
        self.root = None
        self.after_id = None

        self.eventq = queue.Queue()

        self.root = tk.Tk()
        self.root.grid()
        # on peut initialiser des boutons (dans un autre frame) ici
        # self.frame = tk.Frame(root)

        # crée LE canvas, pour un plateau de taille (h*l) cases, de pixels de
        # côté
        tk.Canvas.__init__(
                self,
                self.root,
                height=self.taille[0]*self.pixels,
                width=self.taille[1]*self.pixels,
                background="#ddd",
                takefocus=True)
        self.grid(row=0, column=0)
        self.focus_set()

        # appelle click (ci-dessus) si on clique dans le canvas
        self.bind("<Button-1>", click)
        # appelle key (ci-dessus) si on tape une touche
        self.bind("<Any-KeyPress>", key)

        # appelle checke au moins une fois par seconde
        self.after_id = self.root.after(1000, checke)
        # appelle async_end (ci-dessous) si on ferme la fenêtre
        self.root.protocol("WM_DELETE_WINDOW", async_end)

        # affiche la grille de départ
        self.affiche_matrice(axes=axes)

    def __enter__(self):
        """With -as: statement compatibility."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """With -as: statement compatibility."""
        self.ferme()

    def __del__(self):
        """Appelé quand l'objet est supprimé."""
        self.ferme()

    def ferme(self):
        """Ferme la fenêtre (définitivement)."""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.root is not None:
            self.root.destroy()
            self.root = None

    def message(self, message):
        """Affiche un message dans une espèce de boite/bouton.

        Renvoie True si l'utilisateur a bien cliqué sur le bouton.
        False s'il a fermé la fenêtre brutalement
        """
        # privée: fonction appelée si l'utilisateur clique sur le message
        def c(event):
            self.eventq.put("ok")
            self.root.quit()

        assert(self.root)
        m = tk.Message(
                self.root, text=message,
                padx=20, pady=20,
                relief=tk.RAISED, borderwidth=5,
                )
        # le clic sur le bouton le ferme.
        m.bind("<Button-1>", c)
        m.grid(row=0, column=0)
        while True:
            s = self.attend_clic()
            if s[0] == "FIN":
                # si j'ai reçu FIN, la fenêtre a été fermée
                # je remet le message dans la queue et je renvoie False
                self.eventq.put(s)
                return False
            # tous les autres événements ferment la boite à message.
            m.destroy()
            # et renvoient True
            return True

    ###########################################################################
    # interface de haut niveau :                                              #
    # fonctions d'affichage de matrices/plateaux hauteur*largeur pions        #
    # les matrices contiennent des entiers                                    #
    ###########################################################################

    # couleurs utilisées par défaut
    default_color = ["black", "white", "red", "green", "blue",
                     "yellow", "cyan", "purple", "orange", "darkgrey"]

    def affiche_matrice(
        self, matrice=None, axes=True
    ):
        """Affiche une matrice de jeu complète, avec les couleurs par défaut.

        Si matrice est égal à None (défaut), n'affiche que les axes
        Si axes=True (défaut) affiche les axes
        Renvoie la liste des objets graphiques créés sans les axes.
        """
        assert(self.root)
        # efface tout avant de commencer :
        self.efface()
        # axes
        if axes:
            for i in range(1, self.taille[0]):
                self.create_line(1, i*self.pixels+1,
                                 self.taille[1]*self.pixels+1, i*self.pixels+1,
                                 width=1)
            for i in range(1, self.taille[1]):
                self.create_line(i*self.pixels+1, 1,
                                 i*self.pixels+1, self.taille[0]*self.pixels+1,
                                 width=1)
        # pions
        o = []
        if matrice is not None:
            for i in range(self.taille[0]):
                for j in range(self.taille[1]):
                    if matrice[i][j] is not None:
                        o.append(self.affiche_pion((i, j), matrice[i][j],
                                                   refresh=False))
        # un seul update à la fin, pour la vitesse d'affichage
        self.update()
        return o

    def efface(
        self
    ):
        """Efface tout de la fenêtre.

        Tous les objets créés précédemment dans la fenêtre sont supprimés.
        """
        assert(self.root)
        self.delete(tk.ALL)

    ###########################################################################
    # interface de niveau intermédiaire :                                     #
    # fonctions d'affichage de pions/carrés sur un plateau de jeu             #
    ###########################################################################
    def affiche_pion(
        self, p, joueur=0,
        couleur=None,
        refresh=True
    ):
        """Affiche un pion en position p=(l,c), de la couleur du joueur.

        Paramètres :
        - p: position
        Paramètres optionnels :
        - joueur: numéro du joueur qui joue
          joueur n'est utilisé que si couleur n'est pas donné.
        ou
        - couleur: couleur de remplissage du pion (défaut: pris dans la liste
          default_color[joueur] 0:noir, 1:blanc, 2:rouge, etc.)
          si couleur est donné, joueur est ignoré.
        - refresh: faire le rafraichissement de la fenêtre (défaut: True)

        Retourne l'identifiant du pion
        """
        assert(self.root)
        if couleur is None:
            if isinstance(joueur, int):
                couleur = self.default_color[joueur % len(self.default_color)]
            else:
                couleur = self.default_color[0]

        bord = self.pixels//10+1
        i, j = p
        assert(0 <= i < self.taille[0] and 0 <= j < self.taille[1])
        o = self.create_oval(j*self.pixels+bord+1,
                             i*self.pixels+bord+1,
                             (j+1)*self.pixels-bord+1,
                             (i+1)*self.pixels-bord+1,
                             width=1, fill=couleur)
        if refresh:
            self.update()
        return o

    def deplace_pion(
        self, obj, pos, refresh=True
    ):
        """Déplace un pion en position pos.

        Paramètres :
        - obj: pion qui a été créé précédemment
        - pos: nouvelle position
        Paramètres optionnels :
        - refresh: faire le rafraichissement de la fenêtre (défaut: True)
        """
        assert(self.root)
        i, j = pos
        assert(0 <= i < self.taille[0] and 0 <= j < self.taille[1])
        bord = self.pixels//10+1
        self.coords(
            obj,
            j*self.pixels+bord+1,
            i*self.pixels+bord+1,
            (j+1)*self.pixels-bord+1,
            (i+1)*self.pixels-bord+1
            )
        if refresh:
            self.update()

    def remplit_carre(
        self, p,
        couleur="black",
        contour=0,
        refresh=True
    ):
        """Remplit la case en position p=(l,c), avec la couleur donnée.

        Paramètres :
        - p: position
        Paramètres optionnels :
        - couleur: couleur de remplissage du pion (défaut: noir)
        - contour: épaisseur de la bordure en pixels (défaut: 0)
        - refresh: faire le rafraichissement de la fenêtre (défaut: True)

        Retourne l'identifiant du carré
        """
        assert(self.root)
        i, j = p
        assert(0 <= i < self.taille[0] and 0 <= j < self.taille[1])
        o = self.create_rectangle(j*self.pixels+2,
                                  i*self.pixels+2,
                                  (j+1)*self.pixels+1,
                                  (i+1)*self.pixels+1,
                                  width=contour, fill=couleur)
        if refresh:
            self.update()
        return o

    def deplace_carre(
        self, obj, pos, refresh=True
    ):
        """Déplace un carré en position pos.

        Paramètres :
        - obj: carré qui a été créé précédemment
        - pos: nouvelle position
        Paramètres optionnels :
        - refresh: faire le rafraichissement de la fenêtre (défaut: True)
        """
        assert(self.root)
        i, j = pos
        assert(0 <= i < self.taille[0] and 0 <= j < self.taille[1])
        self.coords(
            obj,
            j*self.pixels+1,
            i*self.pixels+1,
            (j+1)*self.pixels+1,
            (i+1)*self.pixels+1
            )
        if refresh:
            self.update()

    ###########################################################################
    # interface de bas niveau :                                               #
    # fonctions d'affichage de droites/cercles/etc. en pixel                  #
    ###########################################################################
    def affiche_ligne(
        self, x1, x2, couleur="black", epaisseur=1, refresh=True
    ):
        """Affiche une ligne entre les pixels x1=(l1,c1) et x2=(l2,c2).

        - x1, x2: position (n° ligne, n° colonne) des deux points, en pixels
                  (0,0) = en haut à gauche.
        - couleur: couleur (défaut: noir)
        - epaisseur: épaisseur du trait (défaut: 1)
        - refresh: faire le rafraichissement de la fenêtre (défaut: True)

        Retourne l'identifiant de l'objet créé.
        """
        assert(self.root)
        o = self.create_line(x1[1]+1, x1[0]+1, x2[1]+1, x2[0]+1,
                             width=epaisseur, fill=couleur)
        if refresh:
            self.update()
        return o

    def affiche_cercle(
        self, x1, x2,
        couleur="black", contour=1, refresh=True
    ):
        """Affiche un disque entre les pixels de coordonnées x1 et x2.

        Paramètres :
        - x1, x2: position (ligne,colonne) des deux points extrêmes, en pixels
                  (0,0) = en haut à gauche.
        - couleur: couleur de remplissage (défaut: noir)
        - contour: épaisseur du trait de contour (défaut: 1)
        - refresh: faire le rafraichissement de la fenêtre (défaut: True)

        Retourne l'identifiant de l'objet créé.
        """
        assert(self.root)
        o = self.create_oval(x1[1]+1, x1[0]+1, x2[1]+1, x2[0]+1,
                             width=contour, fill=couleur)
        if refresh:
            self.update()
        return o

    def affiche_texte(
        self, position, texte,
        couleur="black", refresh=True
    ):
        """Affiche un texte centré à une certaine position (pixels).

        Paramètres :
        - position: position (ligne,colonne) en pixels
                    (0,0) = en haut à gauche.
        - texte : texte à afficher (chaîne de caractères)
        - couleur: couleur (défaut: noir)
        - refresh: faire le rafraichissement de la fenêtre (défaut: True)

        Retourne l'identifiant de l'objet créé.
        """
        assert(self.root)
        o = self.create_text(position[1]+1, position[0]+1,
                             font=("Georgia", 45, "bold"),
                             text=texte,
                             fill=couleur)
        if refresh:
            self.update()
        return o

    def arriere_plan(
        self, obj, derriere=1, refresh=True
    ):
        """Place l'objet graphique obj en arrière plan.

        - obj: identifiant de l'objet (retourné par une fonction de création)
        - derriere: l'objet derrière lequel se placer (par défaut : derrière
          tous les autres)
        - refresh: faire le rafraichissement de la fenêtre (défaut: True)
        """
        assert(self.root)
        # se met en fond, derrière l'objet 'derriere':
        self.tag_lower(obj, derriere)
        if refresh:
            self.update()

    def refresh(
        self
    ):
        """Raffraichit la fenêtre."""
        assert(self.root)
        self.update()

    def supprime(
        self, obj, refresh=True
    ):
        """Supprime l'objet graphique obj.

        - obj: identifiant de l'objet (retourné par une fonction de création)
        - refresh: faire le rafraichissement de la fenêtre (défaut: True)
        """
        assert(self.root)
        self.delete(obj)
        if refresh:
            self.update()

    ###########################################################################
    # fonction unique d'attente d'entrée/sortie                               #
    ###########################################################################
    def attend_clic(self, delai=None):
        """Attend que l'utilisateur interagisse avec la fenêtre.

        Paramètre :
        - delai : le délai d'attente (par défaut, attend indéfiniment) en
          millisecondes

        Renvoie :
        - si l'utilisateur clique sur une case du plateau, le couple
            ("clic", (ligne, colonne)), où (ligne, colonne) sont les
            coordonnées de la case cliquée
        - si l'utilisateur tape une touche du clavier, le couple
            ("touche", lettre) où lettre est la chaîne de caractères contenant
            la lettre qu'il a tapée, ou un code spécial (touches spéciales)
        - si l'utilisateur ferme la fenêtre, le couple
            ("FIN", None)
        - si le délai expire, la valeur
            None
        """
        # privée : fonction appelée si expiration du délai d'attente
        def delai_expire():
            self.eventq.put(None)
            self.idd = None
            self.root.quit()

        # identifiant du timer armé ici
        self.idd = None
        if delai is not None:
            assert(self.root)
            self.idd = self.root.after(delai, delai_expire)
        # ceci est la boucle d'attente principale de l'interface Tk().
        # elle checke les événements de la fenêtre et sort si un événement se
        # produit.
        while True:
            ####################
            try:
                # l'event queue est remplie par les événements graphiques
                r = self.eventq.get(False)
                # annule le timer lancé ci-dessus
                if self.idd is not None and self.root is not None:
                    self.root.after_cancel(self.idd)
                return r
            except queue.Empty:
                # aucun événement à traiter, on passe à mainloop
                pass
            ####################
            assert(self.root)
            # mainloop s'arrête si un événement se produit
            self.root.mainloop()
            ####################

    def position_souris(self):
        """Renvoie la position de la souris dans la fenêtre.

        retourne un couple de valeurs entières (pixels),
        (1,1) = en haut à gauche
        si une coordonnée est négative ou supérieure au max, la souris est
        sortie de la fenêtre.
        """
        def motion(event):
            self.souris = (event.y, event.x)

        assert(self.root)
        self.refresh()
        try:
            return self.souris
        except AttributeError:
            self.bind("<Motion>", motion)
            self.souris = (0, 0)
            return self.souris


###########################################################################
# programme de test : damier 8*8, clique pour placer/enlever des pions    #
###########################################################################
if __name__ == "__main__":
    # crée un plateau de taille COTE x COTE, chaque case fait LARGEUR pixels
    COTE = 8
    LARGEUR = 80
    g = fenetre((COTE, COTE), LARGEUR)

    # affiche un damier (colorie une case sur deux en jaune)
    for i in range(COTE):
        for j in range(i % 2, COTE, 2):
            g.remplit_carre((i, j), couleur="yellow", refresh=False)
    # il vaut mieux ne rafraichir qu'une fois à la fin de tous les affichages
    # (sinon c'est un peu lent)
    g.refresh()
    msg = g.affiche_texte((LARGEUR//2, LARGEUR+LARGEUR//2),
                          "Bonjour!")

    # boucle principale : attend les clics utilisateur et affiche des pions.
    # leurs identifiants sont stockés dans tab, et ils sont supprimés si
    # on reclique dessus.
    tab = [[None]*COTE for i in range(COTE)]
    joueur = 1
    while True:
        p = g.attend_clic()
        if p[0] != "clic":
            # si l'utilisateur ne clique pas sur une case je quitte
            break
        lig, col = p[1]
        if tab[lig][col] is None:
            tab[lig][col] = g.affiche_pion(p[1], joueur)
            # joueur : 1 -> -1 -> 1 -> ...
            joueur = -joueur
        else:
            g.supprime(tab[lig][col])
            tab[lig][col] = None

        g.supprime(msg)
        msg = g.affiche_texte((LARGEUR//2, LARGEUR+LARGEUR//2),
                              "Joueur "+[0, "blanc", "noir"][joueur])

    # ferme la fenêtre
    g.ferme()
