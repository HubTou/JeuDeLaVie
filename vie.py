#!/usr/bin/python3
""" Module principal
Titre: Le jeu de la Vie
Auteur: Hubert Tournier
Création: 29/04/2020
Version: 1.1 (16/05/2020)
Description:
- Une implémentation du jeu de la Vie (https://fr.wikipedia.org/wiki/Jeu_de_la_vie)
- Ayant pour objectifs la lisibilité (vocation pédagogique - pas d'algorithme sophistiqué type
  HashLife), donner un exemple d'utilisation de PyGame(https://www.pygame.org/) dans un programme
  (projet) fonctionnellement assez complet (fichier de configuration, sauvegardes, multi-modes,
  etc.) mais avec une interface homme-machine minimaliste uniquement dans le bandeau de fenêtre
  (challenge !), l'idée étant d'utiliser ultérieurement un framework GUI PyGame tel que Simple Game
  Code (https://program.sambull.org/sgc/)
Crédits:
- En mémoire de John Horton Conway, 1937-2020 (https://fr.wikipedia.org/wiki/John_Horton_Conway)
- Le livre "Récréations informatiques", bibliothèque Pour la Science, diffusion Belin, qui m'a fait
  découvrir ce jeu en 1987
- Wikipedia qui m'a (re)fait découvrir les structures remarquables programmées dans la bibliothèque
  ci-jointe
- WikiLife pour sa collection de patterns et sa description des formats de fichiers usuels
  (https://conwaylife.com/wiki/Category:File_formats)
Limites:
- Affichage optimal sur écran Full HD (1920*1080) sinon libellés réduits jusqu'à SVGA (800x600)
  ensuite affichages tronqués
- Le nom des exemples de la bibliothèque interne n'est qu'en français
Version 1.1:
- CORRECTION: Correction d'un bug en cas d'utilisation du mode Fichier avant la création du
  répertoire de sauvegarde avec un premier fichier
- CORRECTION: Correction d'un bug avec le chargement de fichiers PlainText (existence de lignes
  vides au lieu d'être remplies de ".")
- CORRECTION: Correction d'un bug avec le chargement de fichiers RLE (existence de multiplicateurs
  devant le caractère "$")
- FONCTIONNALITE : Téléchargement et installation automatique de la base de formes du site LifeWiki
- FONCTIONNALITE: Calcul du temps d'évolution et affichage sur la console en mode DEBUG
- OPTIMISATION: Rester en mode numérique pour la comparaison des voisines d'une cellule avec la
  règle des naissances et survies
- OPTIMISATION: Ne faire évoluer ou détourer que la zone utile de la grille de jeu
- PRESENTATION: Amélioration conformité PEP8
"""

import ctypes
import os
import platform
import re
import shutil
import sys
import time
import zipfile

# les imports suivants nécessitent l'installation de composants
# supplémentaires
# pip install --trusted-host pypi.org --trusted-host pypi.python.org
#             --trusted-host files.pythonhosted.org requests
import requests
import pygame
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import pygame.time as GAME_TIME

from langues import *
from bibliotheque import *

### Constantes #########################################################
MODE_EDITION = 0
MODE_BIBLIOTHEQUE = 1
MODE_EVOLUTION = 2
MODE_SAISIE = 3
MODE_CONFIRMATION = 4
MODE_FICHIER = 5
MODE_PAUSE = 6

RESOLUTION_FULL_HD = 1920 # pixels de largeur
HAUTEUR_BANDEAU_FENETRE = 37 # pixels
HAUTEUR_MENU_WINDOWS = 54 # pixels
HAUTEUR_RESERVEE = HAUTEUR_BANDEAU_FENETRE + HAUTEUR_MENU_WINDOWS # pixels
EPAISSEUR_LIGNE = 1 # pixels

NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
BLANC = (255, 255, 255)

# Valeurs des cases
CELLULE_MORTE = 0
CELLULE_NAISSANTE = 1
# et n = âge de la cellule

FICHIER_CONFIGURATION = "vie.cfg"
REPERTOIRE_SAUVEGARDE = "bibli"
TAILLE_NOM_FICHIER = 64 # caractères

### Bibliothèque de fonctions ##########################################

########################################################################
def charger_ou_creer_fichier_de_configuration():
    """ Retourne les paramètres de configuration définis par l'utilisateur dans un fichier """
    parametres = \
    {
        "LANGUE" : "fr",
        "LARGEUR_CASE" : 9, # pixels
        "CYCLE_DE_VIE" : 250, # ticks d'horloge
        "REGLE" : "B3/S23", # en notation B/S (https://www.conwaylife.com/wiki/Rulestring)
        "DEBUG" : False
    }

    if os.path.isfile(FICHIER_CONFIGURATION):
        fichier = open(FICHIER_CONFIGURATION, "r")
        for ligne_fichier in fichier:
            expression = re.match(r'^\s*(?P<cle>\w*)\s*=\s*(?P<valeur>[^\s#]*)', ligne_fichier)
            if expression is not None:
                cle_valeur = expression.groupdict()
                if cle_valeur["cle"] is not None and cle_valeur["valeur"] is not None:
                    if cle_valeur["cle"] == "LANGUE":
                        parametres["LANGUE"] = cle_valeur["valeur"]
                    elif cle_valeur["cle"] == "LARGEUR_CASE":
                        parametres["LARGEUR_CASE"] = int(cle_valeur["valeur"])
                    elif cle_valeur["cle"] == "CYCLE_DE_VIE":
                        parametres["CYCLE_DE_VIE"] = int(cle_valeur["valeur"])
                    elif cle_valeur["cle"] == "REGLE":
                        parametres["REGLE"] = cle_valeur["valeur"]
                    elif cle_valeur["cle"] == "DEBUG":
                        if cle_valeur["valeur"] == "1":
                            parametres["DEBUG"] = True
                        else:
                            parametres["DEBUG"] = False
    else:
        fichier = open(FICHIER_CONFIGURATION, "w")
        fichier.write("# Code de langue parmi 'fr' ou 'en'\n")
        fichier.write("# Language code between 'fr' or 'en'\n")
        fichier.write("LANGUE = fr\n")
        fichier.write("#LANGUE = en\n")
        fichier.write("\n")
        fichier.write("# Largeur de cellule en pixels (les valeurs impaires sont préférables)\n")
        fichier.write("# Cell width in pixels (odd values are better)\n")
        fichier.write("LARGEUR_CASE = 9\n")
        fichier.write("#LARGEUR_CASE = 15\n")
        fichier.write("#LARGEUR_CASE = 19\n")
        fichier.write("\n")
        fichier.write("# Cycle de vie en ticks d'horloge (plus petit = plus rapide)\n")
        fichier.write("# Life cycle in clock ticks (smaller = faster)\n")
        fichier.write("#CYCLE_DE_VIE = 125\n")
        fichier.write("CYCLE_DE_VIE = 250\n")
        fichier.write("#CYCLE_DE_VIE = 500\n")
        fichier.write("\n")
        fichier.write("# Règle du jeu en notation B/S (nombre de cellules voisines pour B=naissance/S=survie)\n")
        fichier.write("# Game's rule in B/S notation (number of neighbouring cells for B=birth/S=survival)\n")
        fichier.write("REGLE = B3/S23 # John Horton Conway's game of Life\n")
        fichier.write("#REGLE = B36/S23 # Nathan Thompson's HighLife\n")
        fichier.write("#REGLE = B3678/S34678 # Nathan Thompson's day & night\n")
        fichier.write("\n")
        fichier.write("# Mode de débogage\n")
        fichier.write("# Debug mode\n")
        fichier.write("DEBUG = 0 # off\n")
        fichier.write("#DEBUG = 1 # on\n")
    fichier.close()
    return parametres

########################################################################
def initialiser_bibliotheque():
    """ Crée et peuple le répertoire bibliothèque """
    if not os.path.exists(REPERTOIRE_SAUVEGARDE):
        os.makedirs(REPERTOIRE_SAUVEGARDE)

    # Création d'un fichier pour permettre au menu Fichier de fonctionner dès le départ
    nom_fichier = texte1[parametres["LANGUE"]]["DERNIERE_PARTIE"]
    chemin_fichier = REPERTOIRE_SAUVEGARDE + "/" + nom_fichier + ".cells"
    if not os.path.exists(chemin_fichier):
        fichier = open(chemin_fichier, "w")
        fichier.write("!Name: " + nom_fichier + "\n")
        fichier.write("!Position: 1,1\n")
        fichier.write("!\n")
        fichier.write(".O.\n")
        fichier.write("..O\n")
        fichier.write("OOO\n")
        fichier.close()

    # Téléchargement de la pattern collection depuis le site LifeWiki
    if not os.path.isfile(REPERTOIRE_SAUVEGARDE + "/_README_.txt"):
        print("\n" + texte1[parametres["LANGUE"]]["TELECHARGEMENT"])
        print("...")
        chrono_1 = time.time()
        url = 'http://www.conwaylife.com/patterns/all.zip'
        chemin_fichier = REPERTOIRE_SAUVEGARDE + "/" + url.split('/')[-1]
        requete_http = requests.get(url, stream=True)
        with open(chemin_fichier, 'wb') as fichier:
            shutil.copyfileobj(requete_http.raw, fichier)
        chrono_2 = time.time()
        print(texte1[parametres["LANGUE"]]["TERMINE"] + str(chrono_2 - chrono_1) + texte1[parametres["LANGUE"]]["SECONDES"])

        # Décompression
        print("\n" + texte1[parametres["LANGUE"]]["DECOMPRESSION"])
        print("...")
        chrono_1 = time.time()
        with zipfile.ZipFile(chemin_fichier) as fichier_zip:
            fichier_zip.extractall(REPERTOIRE_SAUVEGARDE)
        os.remove(chemin_fichier)

        # élimination des doublons entre fichiers .cells et .rle
        liste_fichiers = [f for f in os.listdir(REPERTOIRE_SAUVEGARDE) if os.path.isfile(os.path.join(REPERTOIRE_SAUVEGARDE, f)) and f.lower().endswith(".cells")]
        for nom_fichier in liste_fichiers:
            nom_sans_extension = nom_fichier[:-6]
            chemin_fichier = REPERTOIRE_SAUVEGARDE + "/" + nom_sans_extension + ".rle"
            if os.path.isfile(chemin_fichier):
                os.remove(chemin_fichier)
        chrono_2 = time.time()
        print(texte1[parametres["LANGUE"]]["TERMINE"] + str(chrono_2 - chrono_1) + texte1[parametres["LANGUE"]]["SECONDES"] + "\n")

########################################################################
def dessiner_grille():
    """ Dessine la grille de jeu sans l'afficher """
    fenetre.fill(BLANC)

    # Dessin des barres verticales
    for i in range(nb_colonnes + 1):
        x = (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE) * i
        pygame.draw.line(fenetre, NOIR, (x, 0), (x, hauteur_fenetre - 1), EPAISSEUR_LIGNE)

    # Dessin des barres horizontales
    for j in range(nb_lignes + 1):
        y = (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE) * j
        pygame.draw.line(fenetre, NOIR, (0, y), (largeur_fenetre - 1, y), EPAISSEUR_LIGNE)

########################################################################
def dessiner_cellule(colonne, ligne):
    """ Dessine une cellule dans la grille de jeu sans l'afficher """
    if plateau[ligne][colonne] == CELLULE_MORTE:
        couleur = BLANC
    elif plateau[ligne][colonne] == CELLULE_NAISSANTE:
        couleur = VERT
    else:
        couleur = BLEU
    x_centre = (colonne * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)) + parametres["LARGEUR_CASE"] // 2
    y_centre = (ligne * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)) + parametres["LARGEUR_CASE"] // 2
    rayon = parametres["LARGEUR_CASE"] // 2
    if parametres["LARGEUR_CASE"] % 2 != 0:
        x_centre += 1
        y_centre += 1
    else:
        rayon -= 1
    epaisseur = 0 # Cercle plein
    pygame.draw.circle(fenetre, couleur, (x_centre, y_centre), rayon, epaisseur)

########################################################################
def afficher_ecran():
    """ Affiche l'écran préparé """
    pygame.display.update()

########################################################################
def afficher_plateau():
    """ Affiche la grille de jeu avec ses cellules """
    dessiner_grille()
    for ligne in range(nb_lignes):
        for colonne in range(nb_colonnes):
            dessiner_cellule(colonne, ligne)
    afficher_ecran()

########################################################################
def deplacer_encadre(encadre):
    """ Retourne un objet rect encadrant la nouvelle structure """
    # Effacer l'encadré précédent
    pygame.draw.rect(fenetre, NOIR, encadre, 1)

    # Tracer le nouvel encadre
    encadre = pygame.draw.rect(
        fenetre,
        VERT,
        (
            EPAISSEUR_LIGNE - 1 + (position_souris[0] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)) * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE),
            EPAISSEUR_LIGNE - 1 + (position_souris[1] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)) * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE),
            EPAISSEUR_LIGNE + largeur_structure * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE),
            EPAISSEUR_LIGNE + hauteur_structure * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)
        ),
        1
    )

    afficher_ecran()
    return encadre

########################################################################
def afficher_bandeau(texte):
    """ Affiche le bandeau de la fenêtre de jeu """
    pygame.display.set_caption(texte1[parametres["LANGUE"]]["TITRE"] + texte)

########################################################################
def afficher_bandeau_evolution():
    """ Affiche le bandeau de la fenêtre de jeu en mode évolution ou pause """
    if mode == MODE_EVOLUTION:
        commandes = texte2[parametres["LANGUE"]][libelles]["MODE_EVOLUTION"]
    else: # if mode == MODE_PAUSE:
        commandes = texte2[parametres["LANGUE"]][libelles]["MODE_PAUSE"]

    if libelles == "long":
        afficher_bandeau(commandes + "  "
                         + texte2[parametres["LANGUE"]][libelles]["VITESSE"] + "=" + str(parametres["CYCLE_DE_VIE"]) + "  "
                         + texte2[parametres["LANGUE"]][libelles]["GENERATION"] + "=" + str(generation) + "  "
                         + texte2[parametres["LANGUE"]][libelles]["POPULATION"] + "=" + str(statut["population"]) + " ("
                         + texte1[parametres["LANGUE"]]["POP_MINIMUM"] + "=" + str(population_min) + "  "
                         + texte1[parametres["LANGUE"]]["POP_MAXIMUM"] + "=" + str(population_max) + ")  "
                         + texte2[parametres["LANGUE"]][libelles]["NAISSANCES"] + "=" + str(statut["naissances"]) + "  "
                         + texte2[parametres["LANGUE"]][libelles]["SURVIE"] + "=" + str(statut["survie"]) + "  "
                         + texte2[parametres["LANGUE"]][libelles]["DECES"] + "=" + str(statut["deces"]))
    else:
        afficher_bandeau(commandes + " "
                         + texte2[parametres["LANGUE"]][libelles]["COURT_VITESSE"] + "=" + str(parametres["CYCLE_DE_VIE"]) + " "
                         + texte2[parametres["LANGUE"]][libelles]["COURT_GENERATION"] + "=" + str(generation) + " "
                         + texte2[parametres["LANGUE"]][libelles]["COURT_POPULATION"] + "=" + str(statut["population"]) + " ["
                         + str(population_min) + "-"
                         + str(population_max) + "] "
                         + texte2[parametres["LANGUE"]][libelles]["COURT_NAISSANCES"] + "=" + str(statut["naissances"]) + " "
                         + texte2[parametres["LANGUE"]][libelles]["COURT_SURVIE"] + "=" + str(statut["survie"]) + " "
                         + texte2[parametres["LANGUE"]][libelles]["COURT_DECES"] + "=" + str(statut["deces"]))

########################################################################
def compter_cellules():
    """ Retourne le nombre de cellules dans la grille de jeu """
    nb_cellules = 0
    for ligne in range(nb_lignes):
        for colonne in range(nb_colonnes):
            if not plateau[ligne][colonne] == CELLULE_MORTE:
                nb_cellules += 1
    return nb_cellules

########################################################################
def vider_plateau():
    """ Affiche la grille de jeu après en avoir retiré toutes les cellules """
    for ligne in range(nb_lignes):
        for colonne in range(nb_colonnes):
            plateau[ligne][colonne] = CELLULE_MORTE
    afficher_plateau()

########################################################################
def ligne_vivante(ligne, x_1, x_2):
    """ Retourne un booléen indiquant si la ligne spécifiée contient au moins une cellule vivante """
    for colonne in range(x_1, x_2 + 1):
        if plateau[ligne][colonne] != CELLULE_MORTE:
            return True
    return False

########################################################################
def colonne_vivante(colonne, y_1, y_2):
    """ Retourne un booléen indiquant si la colonne spécifiée contient au moins une cellule vivante """
    for ligne in range(y_1, y_2 + 1):
        if plateau[ligne][colonne] != CELLULE_MORTE:
            return True
    return False

########################################################################
def detourer_plateau(x_1, y_1, x_2, y_2):
    """ Retourne la zone utile de la grille de jeu """
    zone_utile = {"X_1": -1, "Y_1": -1, "X_2": nb_colonnes, "Y_2": nb_lignes}
    for colonne in range(x_1, x_2 + 1):
        if colonne_vivante(colonne, y_1, y_2):
            zone_utile["X_1"] = colonne
            break
    if zone_utile["X_1"] == -1:
        # Rien à sauvegarder !
        return zone_utile
    for colonne in range(x_2, x_1 - 1, -1):
        if colonne_vivante(colonne, y_1, y_2):
            zone_utile["X_2"] = colonne
            break
    for ligne in range(y_1, y_2 + 1):
        if ligne_vivante(ligne, x_1, x_2):
            zone_utile["Y_1"] = ligne
            break
    for ligne in range(y_2, y_1 - 1, -1):
        if ligne_vivante(ligne, x_1, x_2):
            zone_utile["Y_2"] = ligne
            break
    return zone_utile

########################################################################
def evolution(zone_utile):
    """ Applique la règle d'évolution configurée à la grille de jeu """
    chrono_1 = time.time()

    population = 0
    naissances = 0
    survie = 0
    deces = 0

    # Créer un tableau pour compter les cellules voisines
    voisines = []
    for i in range(nb_lignes):
        ligne = []
        for j in range(nb_colonnes):
            ligne.append(0)
        voisines.append(ligne.copy())

    # Le peupler en une seule passe, sans réexaminer plusieurs fois une
    # même cellule et en ne parcourant que la zone utile
    for ligne in range(zone_utile["Y_1"], zone_utile["Y_2"] + 1):
        for colonne in range(zone_utile["X_1"], zone_utile["X_2"] + 1):
            if plateau[ligne][colonne] != CELLULE_MORTE:
                if ligne > 0:
                    if colonne > 0:
                        voisines[ligne - 1][colonne - 1] += 1
                    voisines[ligne - 1][colonne] += 1
                    if colonne < nb_colonnes - 1:
                        voisines[ligne - 1][colonne + 1] += 1
                if colonne > 0:
                    voisines[ligne][colonne - 1] += 1
                if colonne < nb_colonnes - 1:
                    voisines[ligne][colonne + 1] += 1
                if ligne < nb_lignes - 1:
                    if colonne > 0:
                        voisines[ligne + 1][colonne - 1] += 1
                    voisines[ligne + 1][colonne] += 1
                    if colonne < nb_colonnes - 1:
                        voisines[ligne + 1][colonne + 1] += 1

    # Implémentation de la règle du jeu indiquée dans la zone utile
    # avec une marge supplémentaire d'une colonne/ligne
    ligne_depart = zone_utile["Y_1"] - 1
    if ligne_depart < 0:
        ligne_depart = 0
    ligne_arrivee = zone_utile["Y_2"] + 1
    if ligne_arrivee >= nb_lignes:
        ligne_arrivee = nb_lignes - 1
    colonne_depart = zone_utile["X_1"] - 1
    if colonne_depart < 0:
        colonne_depart = 0
    colonne_arrivee = zone_utile["X_2"] + 1
    if colonne_arrivee >= nb_colonnes:
        colonne_arrivee = nb_colonnes - 1
    for ligne in range(ligne_depart, ligne_arrivee + 1):
        for colonne in range(colonne_depart, colonne_arrivee + 1):
            if plateau[ligne][colonne] == CELLULE_MORTE:
                if voisines[ligne][colonne] in regle_naissance:
                    plateau[ligne][colonne] = CELLULE_NAISSANTE
                    population += 1
                    naissances += 1
            else:
                if voisines[ligne][colonne] in regle_survie:
                    plateau[ligne][colonne] += 1
                    population += 1
                    survie += 1
                else:
                    plateau[ligne][colonne] = CELLULE_MORTE
                    deces += 1
    afficher_plateau()

    # Redéfinition de la zone utile
    zone_utile = detourer_plateau(colonne_depart, ligne_depart, colonne_arrivee, ligne_arrivee)

    chrono_2 = time.time()
    if parametres["DEBUG"]:
        print(texte1[parametres["LANGUE"]]["CYCLE_EVOLUTION"] + str(chrono_2 - chrono_1) + texte1[parametres["LANGUE"]]["SECONDES"])

    return {
        "statut": {"population": population, "naissances": naissances, "survie": survie, "deces": deces},
        "zone_utile": zone_utile
        }

########################################################################
def sauvegarder_fichier(chemin_fichier):
    """ Sauvegarde la zone utile de la grille de jeu dans un fichier au format Plain Text """
    if not os.path.exists(REPERTOIRE_SAUVEGARDE):
        os.makedirs(REPERTOIRE_SAUVEGARDE)
    fichier = open(chemin_fichier, "w")
    fichier.write("!Name: " + nom_fichier + "\n")
    fichier.write("!Position: " + str(zone_utile["X_1"]) + "," + str(zone_utile["Y_1"]) + "\n")
    fichier.write("!\n")
    for ligne in range(zone_utile["Y_1"], zone_utile["Y_2"] + 1):
        for colonne in range(zone_utile["X_1"], zone_utile["X_2"] + 1):
            if plateau[ligne][colonne] == CELLULE_MORTE:
                fichier.write(".")
            else:
                fichier.write("O")
        fichier.write("\n")
    fichier.close()

########################################################################
def charger_fichier_plaintext(chemin_fichier):
    """ Retourne la structure contenue dans un fichier au format Plain Text (.cells) """
    structure = []
    no_ligne = 0
    max_colonnes = 0
    fichier = open(chemin_fichier, "r")
    for ligne_fichier in fichier:
        no_ligne += 1
        ligne_fichier = ligne_fichier.strip()
        if not ligne_fichier.startswith("!"):
            if len(ligne_fichier) > max_colonnes:
                max_colonnes = len(ligne_fichier)
            ligne = []
            for caractere in ligne_fichier:
                if caractere == '.':
                    ligne.append(CELLULE_MORTE)
                elif caractere == "O":
                    ligne.append(CELLULE_NAISSANTE)
                elif caractere == "*":
                    ligne.append(CELLULE_NAISSANTE)
                    print(texte1[parametres["LANGUE"]]["AVERTISSEMENT"] + ": " + texte1[parametres["LANGUE"]]["FICHIER"] + "=" + chemin_fichier + " " + texte1[parametres["LANGUE"]]["no_ligne"] + "=" + str(no_ligne) + " " + texte1[parametres["LANGUE"]]["LIGNE"] + "=" + ligne_fichier)
                else:
                    print(texte1[parametres["LANGUE"]]["ERREUR"] + ": " + texte1[parametres["LANGUE"]]["FICHIER"] + "=" + chemin_fichier + " " + texte1[parametres["LANGUE"]]["no_ligne"] + "=" + str(no_ligne) + " " + texte1[parametres["LANGUE"]]["LIGNE"] + "=" + ligne_fichier)
                    break
            structure.append(ligne.copy())
    fichier.close()

    # Certains fichiers du LifeWiki ne respectent pas la spécification sur
    # https://www.conwaylife.com/wiki/Plaintext et ne mentionnent pas les cellules mortes en fin de
    # ligne, ni les lignes composées uniquement de cellules mortes
    # Maintenant que l'on connaît la largeur maximale de la structure on les rajoute
    for ligne in range(len(structure)):
        cellules_manquantes = max_colonnes - len(structure[ligne])
        if cellules_manquantes > 0:
            for i in range(cellules_manquantes):
                structure[ligne].append(CELLULE_MORTE)

    return structure

########################################################################
def charger_position_dans_fichier_plaintext(chemin_fichier):
    """ Retourne la position indiquée dans un fichier au format Plain Text """
    position = (0, 0)
    fichier = open(chemin_fichier, "r")
    for ligne_fichier in fichier:
        ligne_fichier = ligne_fichier.strip()
        if ligne_fichier.startswith("!Position: "):
            resultat = ligne_fichier.split(" ")[1].split(",")
            position = (int(resultat[0]), int(resultat[1]))
    fichier.close()
    return position

########################################################################
def charger_fichier_run_length_encoded(chemin_fichier):
    """ Retourne la structure contenue dans un fichier au format Run Length Encoded (.rle) """
    structure = []
    ligne = []
    nb_cellules = 0
    nb_lignes = 0
    nombre = 0
    fin = False
    no_ligne = 0
    fichier = open(chemin_fichier, "r")
    for ligne_fichier in fichier:
        no_ligne += 1
        ligne_fichier = ligne_fichier.strip()
        if ligne_fichier == "" or ligne_fichier.startswith("#"):
            continue
        elif ligne_fichier.startswith("x"):
            expression = re.match(r'^\s*x\s*=\s*(?P<x>\d*)\s*,\s*y\s*=\s*(?P<y>\d*)(\s*,\s*rule\s*=\s*(?P<rule>[bB]\d*/[sS]\d*))?', ligne_fichier)
            if expression is not None:
                en_tete = expression.groupdict()
                largeur_structure = int(en_tete["x"])
                hauteur_structure = int(en_tete["y"])
            else:
                print(texte1[parametres["LANGUE"]]["ERREUR"] + ": " + texte1[parametres["LANGUE"]]["FICHIER"] + "=" + chemin_fichier + " " + texte1[parametres["LANGUE"]]["no_ligne"] + "=" + str(no_ligne) + " " + texte1[parametres["LANGUE"]]["LIGNE"] + "=" + ligne_fichier)
        else:
            for caractere in ligne_fichier:
                if caractere in (' ', '\\t'):
                    continue
                elif caractere >= "0" and caractere <= "9":
                    nombre = (nombre * 10) + int(caractere)
                elif caractere in ('b', 'B'):
                    if nombre == 0:
                        nombre = 1
                    for i in range(nombre):
                        ligne.append(CELLULE_MORTE)
                        nb_cellules += 1
                    nombre = 0
                elif caractere in ('o', 'O'):
                    if nombre == 0:
                        nombre = 1
                    for i in range(nombre):
                        ligne.append(CELLULE_NAISSANTE)
                        nb_cellules += 1
                    nombre = 0
                elif caractere == '$':
                    if nombre == 0:
                        nombre = 1
                    for j in range(nombre):
                        for i in range(nb_cellules, largeur_structure):
                            ligne.append(CELLULE_MORTE)
                        nb_cellules = 0
                        structure.append(ligne.copy())
                        ligne = []
                        nb_lignes = nb_lignes + 1
                    nombre = 0
                elif caractere == '!':
                    for i in range(nb_cellules, largeur_structure):
                        ligne.append(CELLULE_MORTE)
                    nb_cellules = 0
                    structure.append(ligne.copy())
                    ligne = []
                    nb_lignes = nb_lignes + 1
                    for j in range(nb_lignes, hauteur_structure):
                        for i in range(largeur_structure):
                            ligne.append(CELLULE_MORTE)
                        structure.append(ligne.copy())
                        ligne = []
                    fin = True
                    break
                else:
                    print(texte1[parametres["LANGUE"]]["AVERTISSEMENT"] + ": " + texte1[parametres["LANGUE"]]["FICHIER"] + "=" + chemin_fichier + " " + texte1[parametres["LANGUE"]]["no_ligne"] + "=" + str(no_ligne) + " " + texte1[parametres["LANGUE"]]["LIGNE"] + "=" + ligne_fichier)
                    break
        if fin:
            break
    fichier.close()
    return structure

########################################################################
def charger_fichier(chemin_fichier):
    """ Retourne la structure contenue dans un fichier """
    if chemin_fichier.lower().endswith(".cells"):
        return charger_fichier_plaintext(chemin_fichier)
    elif chemin_fichier.lower().endswith(".rle"):
        return charger_fichier_run_length_encoded(chemin_fichier)

### Programme principal ################################################

# Création du fichier de configuration et du répertoire de sauvegarde
parametres = charger_ou_creer_fichier_de_configuration()
initialiser_bibliotheque()

# Fenêtre positionnée en haut à gauche de l'écran (à faire avant l'initialisation de PyGame)
# décalée du bandeau de fenêtre
os.environ['SDL_VIDEO_WINDOW_POS'] = "0," + str(HAUTEUR_BANDEAU_FENETRE)

pygame.init()

# Initialisation de l'écran et de la fenêtre de jeu
if platform.system() == "Windows":
    # La fonction suivante évite que Windows ne mette la fenêtre à l'échelle ce qui fausse les calculs de pixels
    ctypes.windll.user32.SetProcessDPIAware()
    largeur_ecran = ctypes.windll.user32.GetSystemMetrics(0)
    hauteur_ecran = ctypes.windll.user32.GetSystemMetrics(1)
    ecran = (largeur_ecran, hauteur_ecran)
else:
    ecran = pygame.display.Info()
    largeur_ecran = ecran.current_w
    hauteur_ecran = ecran.current_h
largeur_fenetre = largeur_ecran
hauteur_fenetre = hauteur_ecran - HAUTEUR_RESERVEE
if largeur_ecran >= RESOLUTION_FULL_HD:
    libelles = "long"
else:
    libelles = "court"

# Initialisation du plateau de jeu
nb_colonnes = ((largeur_fenetre + EPAISSEUR_LIGNE) // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
nb_lignes = ((hauteur_fenetre + EPAISSEUR_LIGNE) // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
plateau = []
for i in range(nb_lignes):
    ligne = []
    for j in range(nb_colonnes):
        ligne.append(0)
    plateau.append(ligne.copy())

# Initialisation de l'interface graphique
# et redimensionnement de la fenêtre au nombre de cases affichables
mode = MODE_EDITION
largeur_fenetre = EPAISSEUR_LIGNE + (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE) * nb_colonnes
hauteur_fenetre = EPAISSEUR_LIGNE + (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE) * nb_lignes
fenetre = pygame.display.set_mode((largeur_fenetre, hauteur_fenetre))
afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_EDITION"])
afficher_plateau()

# Initialisation de la règle du jeu
expression = re.match(r'^B(?P<naissance>\d*)/S(?P<survie>\d*)$', parametres["REGLE"])
regle = expression.groupdict()
regle_naissance = []
for caractere in regle["naissance"]:
    regle_naissance.append(int(caractere))
regle_survie = []
for caractere in regle["survie"]:
    regle_survie.append(int(caractere))

# Boucle principale du programme
programme_termine = False
derniere_evolution = GAME_TIME.get_ticks()
encadre = (0, 0, 1, 1)
zone_utile = {"X_1": -1, "Y_1": -1, "X_2": nb_colonnes, "Y_2": nb_lignes}
while not programme_termine:

    horloge = GAME_TIME.get_ticks()
    # Evolution si le moment est venu, qu'il reste une cellule en vie et qu'on ne soit pas arrivé en stase
    if mode == MODE_EVOLUTION and horloge - derniere_evolution > parametres["CYCLE_DE_VIE"] and population_min > 0 and not (statut["naissances"] == 0 and statut["deces"] == 0):
        derniere_evolution = horloge
        generation += 1
        resultat = evolution(zone_utile)
        statut = resultat["statut"]
        zone_utile = resultat["zone_utile"]
        if statut["population"] < population_min:
            population_min = statut["population"]
        elif statut["population"] > population_max:
            population_max = statut["population"]
        afficher_bandeau_evolution()

    for event in GAME_EVENTS.get():
        if event.type == pygame.MOUSEMOTION:
            position_souris = event.pos
            if mode == MODE_BIBLIOTHEQUE or mode == MODE_FICHIER:
                encadre = deplacer_encadre(encadre)

        if event.type == pygame.MOUSEBUTTONUP:
            colonne = (position_souris[0] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
            ligne = (position_souris[1] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
            if mode == MODE_EDITION:
                if plateau[ligne][colonne] == CELLULE_MORTE:
                    plateau[ligne][colonne] = CELLULE_NAISSANTE
                else:
                    plateau[ligne][colonne] = CELLULE_MORTE
                dessiner_cellule(colonne, ligne)
                afficher_ecran()

        if event.type == pygame.KEYDOWN:

            if event.type == GAME_GLOBALS.QUIT: # Quitter
                programme_termine = True

            if event.key == pygame.K_ESCAPE: # Changer de mode
                if mode == MODE_EDITION:
                    mode = MODE_EVOLUTION
                    generation = 1
                    nb_cellules = compter_cellules()
                    statut = {"population": nb_cellules, "naissances": nb_cellules, "survie": 0, "deces": 0}
                    population_min = nb_cellules
                    population_max = nb_cellules
                    afficher_bandeau_evolution()

                    # Si la configuration de départ n'est pas vide, on la note au cas où elle serait intéressante
                    zone_utile = detourer_plateau(0, 0, nb_colonnes - 1, nb_lignes - 1)
                    if zone_utile["X_1"] != -1:
                        nom_fichier = texte1[parametres["LANGUE"]]["DERNIERE_PARTIE"]
                        sauvegarder_fichier(REPERTOIRE_SAUVEGARDE + "/" + texte1[parametres["LANGUE"]]["DERNIERE_PARTIE"] + ".cells")
                else:
                    mode = MODE_EDITION
                    afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_EDITION"])
                    pygame.draw.rect(fenetre, NOIR, encadre, 1)
                    afficher_ecran()

            if mode == MODE_EDITION:
                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_BIBLIOTHEQUE"]: # Sélectionner un motif dans la bibliothèque interne
                    mode = MODE_BIBLIOTHEQUE
                    indice = 0
                    cle = list(bibliotheque)[indice]
                    afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_BIBLIOTHEQUE"] + cle)
                    hauteur_structure = len(bibliotheque[cle])
                    largeur_structure = len(bibliotheque[cle][0])
                    encadre = deplacer_encadre((0, 0, 1, 1))

                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_FICHIER"]: # Sélectionner un fichier
                    mode = MODE_FICHIER
                    listeFichiers = [f for f in os.listdir(REPERTOIRE_SAUVEGARDE) if os.path.isfile(os.path.join(REPERTOIRE_SAUVEGARDE, f)) and (f.lower().endswith(".cells") or f.lower().endswith(".rle"))]
                    indice = 0
                    afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_FICHIER"] + listeFichiers[indice])
                    structure = charger_fichier(REPERTOIRE_SAUVEGARDE + "/" + listeFichiers[indice])
                    hauteur_structure = len(structure)
                    largeur_structure = len(structure[0])
                    encadre = deplacer_encadre((0, 0, 1, 1))

                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_QUITTER"]: # Quitter
                    programme_termine = True

                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_SAUVEGARDER"]: # Sauvegarder le plateau au format PlainText (https://conwaylife.com/wiki/Plaintext)
                    zone_utile = detourer_plateau(0, 0, nb_colonnes - 1, nb_lignes - 1)
                    mode = MODE_SAISIE
                    nom_fichier = ""
                    afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_SAISIE"])

                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_RESTAURER"]: # Restaurer le plateau de la dernière partie s'il existe
                    chemin_fichier = REPERTOIRE_SAUVEGARDE + "/" + texte1[parametres["LANGUE"]]["DERNIERE_PARTIE"] + ".cells"
                    if os.path.isfile(chemin_fichier):
                        structure = charger_fichier_plaintext(chemin_fichier)
                        position = charger_position_dans_fichier_plaintext(chemin_fichier)
                        vider_plateau()
                        for ligne in range(len(structure)):
                            for colonne in range(len(structure[ligne])):
                                if ligne + position[1] < nb_lignes and colonne + position[0] < nb_colonnes:
                                    plateau[ligne + position[1]][colonne + position[0]] = structure[ligne][colonne]
                        afficher_plateau()

                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_VIDER"]: # Vider le plateau
                    vider_plateau()

            elif mode == MODE_SAISIE:
                if (event.unicode >= "A" and event.unicode <= "Z") \
                or (event.unicode >= "a" and event.unicode <= "z") \
                or (event.unicode >= "0" and event.unicode <= "9") \
                or event.unicode == ' ' \
                or event.unicode == '-' \
                or event.unicode == '_':
                    if len(nom_fichier) < TAILLE_NOM_FICHIER:
                        nom_fichier += event.unicode
                        afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_SAISIE"] + nom_fichier)

                if event.key == pygame.K_BACKSPACE:
                    if len(nom_fichier) > 1:
                        nom_fichier = nom_fichier[:-1]
                        afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_SAISIE"] + nom_fichier)

                if event.key == pygame.K_RETURN:
                    # Sauvegarde avec demande de confirmation en cas d'écrasement
                    chemin_fichier = REPERTOIRE_SAUVEGARDE + "/" + nom_fichier + ".cells"
                    if not os.path.isfile(chemin_fichier):
                        sauvegarder_fichier(chemin_fichier)
                        mode = MODE_EDITION
                        afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_EDITION"])
                    else:
                        mode = MODE_CONFIRMATION
                        afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_CONFIRMATION"])

            elif mode == MODE_CONFIRMATION:
                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_CONFIRMATION"]: # confirmer
                    sauvegarder_fichier(chemin_fichier)
                mode = MODE_EDITION
                afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_EDITION"])

            elif mode == MODE_BIBLIOTHEQUE:
                if event.key == pygame.K_UP or event.key == pygame.K_LEFT \
                or event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
                    if event.key == pygame.K_UP or event.key == pygame.K_LEFT:
                        indice -= 1
                    if event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
                        indice += 1
                    if indice < 0:
                        indice = len(list(bibliotheque)) - 1
                    elif indice == len(list(bibliotheque)):
                        indice = 0

                    cle = list(bibliotheque)[indice]
                    afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_BIBLIOTHEQUE"] + cle)
                    hauteur_structure = len(bibliotheque[cle])
                    largeur_structure = len(bibliotheque[cle][0])
                    encadre = deplacer_encadre(encadre)

                if event.key == pygame.K_RETURN:
                    # Collage de la structure à la position de la souris
                    colonne_plateau = (position_souris[0] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
                    ligne_plateau = (position_souris[1] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
                    cle = list(bibliotheque)[indice]
                    for ligne in range(len(bibliotheque[cle])):
                        for colonne in range(len(bibliotheque[cle][ligne])):
                            if ligne + ligne_plateau < nb_lignes and colonne + colonne_plateau < nb_colonnes:
                                plateau[ligne + ligne_plateau][colonne + colonne_plateau] = bibliotheque[cle][ligne][colonne]
                    afficher_plateau()

            elif mode == MODE_FICHIER:
                if event.key == pygame.K_UP or event.key == pygame.K_LEFT \
                or event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT \
                or event.key == pygame.K_PAGEUP or event.key == pygame.K_PAGEDOWN \
                or event.key == pygame.K_HOME or event.key == pygame.K_END:
                    page = len(listeFichiers) // 20 # 5% de la liste
                    if event.key == pygame.K_UP or event.key == pygame.K_LEFT:
                        indice -= 1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
                        indice += 1
                    elif event.key == pygame.K_PAGEUP:
                        if indice > page:
                            indice -= page
                        else:
                            indice = 0
                    elif event.key == pygame.K_PAGEDOWN:
                        if indice < len(listeFichiers) - page:
                            indice += page
                        else:
                            indice = len(listeFichiers) - 1
                    elif event.key == pygame.K_HOME:
                        indice = 0
                    elif event.key == pygame.K_END:
                        indice = len(listeFichiers) - 1
                    if indice < 0:
                        indice = len(listeFichiers) - 1
                    elif indice == len(listeFichiers):
                        indice = 0

                    afficher_bandeau(texte2[parametres["LANGUE"]][libelles]["MODE_FICHIER"] + listeFichiers[indice])
                    structure = charger_fichier(REPERTOIRE_SAUVEGARDE + "/" + listeFichiers[indice])
                    hauteur_structure = len(structure)
                    largeur_structure = len(structure[0])
                    encadre = deplacer_encadre(encadre)

                if event.key == pygame.K_RETURN:
                    # Collage de la structure à la position de la souris
                    colonne_plateau = (position_souris[0] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
                    ligne_plateau = (position_souris[1] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
                    for ligne in range(len(structure)):
                        for colonne in range(len(structure[ligne])):
                            if ligne + ligne_plateau < nb_lignes and colonne + colonne_plateau < nb_colonnes:
                                plateau[ligne + ligne_plateau][colonne + colonne_plateau] = structure[ligne][colonne]
                    afficher_plateau()

            elif mode == MODE_PAUSE:
                if event.key == pygame.K_SPACE: # Remettre l'évolution en marche
                    mode = MODE_EVOLUTION
                    afficher_bandeau_evolution()

            else: # if mode == MODE_EVOLUTION
                if event.unicode == "+": # Accélérer l'évolution
                    parametres["CYCLE_DE_VIE"] //= 2
                    if parametres["CYCLE_DE_VIE"] == 0: # Jusqu'à un tick d'horloge maximum
                        parametres["CYCLE_DE_VIE"] = 1
                    else:
                        afficher_bandeau_evolution()

                if event.unicode == "-": # Ralentir l'évolution
                    parametres["CYCLE_DE_VIE"] *= 2
                    afficher_bandeau_evolution()

                if event.key == pygame.K_SPACE: # Mettre l'évolution en pause
                    mode = MODE_PAUSE
                    afficher_bandeau_evolution()

        if event.type == pygame.QUIT:
            programme_termine = True

pygame.quit()
sys.exit()
"""
### Idées d'améliorations ##############################################
- cycle de vie en centièmes de secondes plutôt qu'en ticks d'horloge pour ceux qui veulent aller
  encore plus vite
- couleur de l'encadré paramétrable dans le fichier de configuration
- commande infos dans mode Fichier pour afficher les commentaires contenus dans le fichier
- interface homme-machine avec Simple Game Code
  (https://program.sambull.org/sgc/)
    - écran de démarrage
        - crédits
        - explication
        - liens
    - écran de configuration
        - choix règle
        - choix langue
        - choix taille cases
        - choix vitesse
    - écran d'aide pour détailler les commandes simplifiées
    - ascenseurs horizontaux et verticaux
        - nouvelles options de configuration pour bordures
            - fermé (comme actuellement)
            - fermé électrique (tue toutes les cellules qui touche le bord)
            - ouvert
                - passer à un stockage relatif plutôt que matriciel
                    - par exemple: matrice à partir du coin supérieur gauche sur un plateau infini
                      et troué
- plus d'options d'édition
    - mode sélection de zone
        - couper, coller
        - rotation à 90°
        - symétrie verticale/horizontales
        - vidage
    - mode édition: bouton 1 peindre, bouton 2 effacer
    - mode écriture de texte
- Version "tout en un" exécutable avec py2exe

### Dans un autre logiciel associé #####################################
- générateur systématique de structures de taille incrémentale
    - avec calcul de hachage de la structure originelle
    - et détecteur de configurations intéressantes:
        - oscillateurs (calculer hash configuration initiale et courante et indiquer période si
          égalité)
        - vaisseaux (idem si position de départ et d'arrivée différente)
    => objectifs:
        - identifier une liste de valeurs de hachage
          de "natures mortes" et "d'oscillateurs" ne nécessitant pas de recalcul
        - sera utile lors d'une bascule sur un stockage par zones utiles et avec un calcul
          d'évolution uniquement sur les zones n'appartenant pas aux 2 catégories précédentes
"""
