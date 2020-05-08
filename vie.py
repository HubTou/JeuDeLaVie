#!/usr/bin/python3
"""
Titre : Le jeu de la Vie
Auteur : Hubert Tournier
Création : 29/04/2020
Version : 1.0 (08/05/2020)
Module : Principal
Description : 
- Une implémentation du jeu de la Vie (https://fr.wikipedia.org/wiki/Jeu_de_la_vie)
- Ayant pour objectifs la lisibilité (vocation pédagogique - pas d'algorithme sophistiqué type HashLife),
  donner un exemple d'utilisation de PyGame(https://www.pygame.org/)
  dans un programme (projet) fonctionnellement assez complet (fichier de configuration, sauvegardes, multi-modes, etc.)
  mais avec une interface homme-machine minimaliste uniquement dans le bandeau de fenêtre (challenge !)
  l'idée étant d'utiliser ultérieurement un framework GUI PyGame tel que Simple Game Code (https://program.sambull.org/sgc/)
Crédits :
- En mémoire de John Horton Conway, 1937-2020 (https://fr.wikipedia.org/wiki/John_Horton_Conway)
- Le livre "Récréations informatiques", bibliothèque Pour la Science, diffusion Belin, qui m'a fait découvrir ce jeu en 1987
- Wikipedia qui m'a (re)fait découvrir les structures remarquables programmées dans la bibliothèque ci-jointe
- WikiLife pour sa collection de patterns et sa description des formats de fichiers usuels (https://conwaylife.com/wiki/Category:File_formats)
Limites :
- Affichage optimal sur écran Full HD (1920*1080) sinon libellés réduits jusqu'à SVGA (800x600) ensuite affichages tronqués
- Le nom des exemples de la bibliothèque interne n'est qu'en français
"""

import ctypes
import os
import platform
import pygame
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import pygame.time as GAME_TIME
import re
#import requests # Nécessite une installation séparée
#import shutil
import sys
#import zipfile
    
from langues import *
from bibliotheque import *

### Constantes #################################################################
MODE_EDITION      = 0
MODE_BIBLIOTHEQUE = 1
MODE_EVOLUTION    = 2
MODE_SAISIE       = 3
MODE_CONFIRMATION = 4
MODE_FICHIER      = 5
MODE_PAUSE        = 6

RESOLUTION_FULL_HD      = 1920 # pixels de largeur
HAUTEUR_BANDEAU_FENETRE = 37 # pixels
HAUTEUR_MENU_WINDOWS    = 54 # pixels
HAUTEUR_RESERVEE        = HAUTEUR_BANDEAU_FENETRE + HAUTEUR_MENU_WINDOWS # pixels
EPAISSEUR_LIGNE         = 1 # pixels

NOIR  = (0, 0, 0)
ROUGE = (255, 0, 0)
VERT  = (0, 255, 0)
BLEU  = (0, 0, 255)
BLANC = (255, 255, 255)

# Valeurs des cases
CELLULE_MORTE     = 0
CELLULE_NAISSANTE = 1
# et n = âge de la cellule

FICHIER_CONFIGURATION = "vie.cfg"
REPERTOIRE_SAUVEGARDE = "bibli"
TAILLE_NOM_FICHIER    = 64 # caractères

### Bibliothèque de fonctions ##################################################

################################################################################
def chargerOuCreerFichierDeConfiguration() :
    """ Retourne un dictionnaire contenant les paramètres de configuration définis par l'utilisateur dans un fichier """
    parametres = \
    {
        "LANGUE"       : "fr",
        "LARGEUR_CASE" : 9,       # pixels
        "CYCLE_DE_VIE" : 250,     # ticks d'horloge
        "REGLE"        : "B3/S23" # en notation B/S (https://www.conwaylife.com/wiki/Rulestring)
    }

    if os.path.isfile(FICHIER_CONFIGURATION) :
        fichier = open(FICHIER_CONFIGURATION, "r")
        for ligneFichier in fichier :
            expression = re.match(r'^\s*(?P<cle>\w*)\s*=\s*(?P<valeur>[^\s#]*)', ligneFichier)
            if expression is not None:
                tuple = expression.groupdict()
                if tuple["cle"] is None or tuple["valeur"] is None:
                    continue
                elif tuple["cle"] == "LANGUE" :
                    parametres["LANGUE"] = tuple["valeur"]
                elif tuple["cle"] == "LARGEUR_CASE" :
                    parametres["LARGEUR_CASE"] = int(tuple["valeur"])
                elif tuple["cle"] == "CYCLE_DE_VIE" :
                    parametres["CYCLE_DE_VIE"] = int(tuple["valeur"])
                elif tuple["cle"] == "REGLE" :
                    parametres["REGLE"] = tuple["valeur"]
    else :
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
    fichier.close()
    return parametres

################################################################################
def dessinerGrille() :
    """ Dessine la grille de jeu sans l'afficher """
    fenetre.fill(BLANC)
    
    # Dessin des barres verticales
    for i in range(nbColonnes + 1) :
        x = (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE) * i
        pygame.draw.line(fenetre, NOIR, (x, 0), (x, hauteurFenetre - 1), EPAISSEUR_LIGNE)
    
    # Dessin des barres horizontales
    for j in range(nbLignes + 1) :
        y = (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE) * j
        pygame.draw.line(fenetre, NOIR, (0, y), (largeurFenetre - 1, y), EPAISSEUR_LIGNE)

################################################################################
def dessinerCellule(colonne, ligne) :
    """ Dessine une cellule dans la grille de jeu sans l'afficher """
    if plateau[ligne][colonne] == CELLULE_MORTE :
        couleur = BLANC
    elif plateau[ligne][colonne] == CELLULE_NAISSANTE :
        couleur = VERT
    else :
        couleur = BLEU
    xCentre = (colonne * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)) + parametres["LARGEUR_CASE"] // 2
    yCentre = (ligne * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)) + parametres["LARGEUR_CASE"] // 2
    rayon = parametres["LARGEUR_CASE"] // 2
    if parametres["LARGEUR_CASE"] % 2 != 0 :
        xCentre += 1
        yCentre += 1
    else :
        rayon -= 1
    epaisseur = 0 # Cercle plein
    pygame.draw.circle(fenetre, couleur, (xCentre, yCentre), rayon, epaisseur)

################################################################################
def afficherEcran() :
    """ Affiche l'écran préparé """
    pygame.display.update()

################################################################################
def afficherPlateau() :
    """ Affiche la grille de jeu avec ses cellules """
    dessinerGrille()
    for ligne in range(nbLignes) :
        for colonne in range (nbColonnes) :
            dessinerCellule(colonne, ligne)
    afficherEcran()

################################################################################
def deplacerEncadre(encadre) :
    """ Déplace le cadre indiquant la zone de collage d'une structure et retourne un objet rect encadrant la nouvelle structure """
    # Effacer l'encadré précédent
    pygame.draw.rect(fenetre, NOIR, encadre, 1)
    
    # Tracer le nouvel encadre
    encadre = pygame.draw.rect(
        fenetre,
        VERT,
        (
            EPAISSEUR_LIGNE - 1 + (positionSouris[0] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)) * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE),
            EPAISSEUR_LIGNE - 1 + (positionSouris[1] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)) * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE),
            EPAISSEUR_LIGNE + largeurStructure * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE),
            EPAISSEUR_LIGNE + hauteurStructure * (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE)
        ),
        1
    )
    
    afficherEcran()
    return encadre

################################################################################
def afficherBandeau(texte) :
    """ Affiche le bandeau de la fenêtre de jeu """
    pygame.display.set_caption(texte1[parametres["LANGUE"]]["TITRE"] + texte)

################################################################################
def afficherBandeauEvolution() :
    """ Affiche le bandeau de la fenêtre de jeu en mode évolution ou pause """
    if mode == MODE_EVOLUTION :
        commandes =  texte2[parametres["LANGUE"]][format]["MODE_EVOLUTION"]
    else : # if mode == MODE_PAUSE :
        commandes = texte2[parametres["LANGUE"]][format]["MODE_PAUSE"]

    if format == "long" :
        afficherBandeau(commandes + "  "
            + texte2[parametres["LANGUE"]][format]["VITESSE"] + "=" + str(parametres["CYCLE_DE_VIE"]) + "  "
            + texte2[parametres["LANGUE"]][format]["GENERATION"] + "=" + str(generation) + "  "
            + texte2[parametres["LANGUE"]][format]["POPULATION"] + "=" + str(statut[0]) + " ("
            + texte1[parametres["LANGUE"]]["POP_MINIMUM"] + "=" + str(populationMin) + "  "
            + texte1[parametres["LANGUE"]]["POP_MAXIMUM"] + "=" + str(populationMax) + ")  "
            + texte2[parametres["LANGUE"]][format]["NAISSANCES"] + "=" + str(statut[1]) + "  "
            + texte2[parametres["LANGUE"]][format]["SURVIE"] + "=" + str(statut[2]) + "  "
            + texte2[parametres["LANGUE"]][format]["DECES"] + "=" + str(statut[3]))
    else :
        afficherBandeau(commandes + " "
            + texte2[parametres["LANGUE"]][format]["COURT_VITESSE"] + "=" + str(parametres["CYCLE_DE_VIE"]) + " "
            + texte2[parametres["LANGUE"]][format]["COURT_GENERATION"] + "=" + str(generation) + " "
            + texte2[parametres["LANGUE"]][format]["COURT_POPULATION"] + "=" + str(statut[0]) + " ["
            + str(populationMin) + "-"
            + str(populationMax) + "] "
            + texte2[parametres["LANGUE"]][format]["COURT_NAISSANCES"] + "=" + str(statut[1]) + " "
            + texte2[parametres["LANGUE"]][format]["COURT_SURVIE"] + "=" + str(statut[2]) + " "
            + texte2[parametres["LANGUE"]][format]["COURT_DECES"] + "=" + str(statut[3]))

################################################################################
def compterCellules() :
    """ Retourne le nombre de cellules dans la grille de jeu """
    nbCellules = 0
    for ligne in range(nbLignes) :
        for colonne in range (nbColonnes) :
            if not plateau[ligne][colonne] == CELLULE_MORTE :
                nbCellules += 1
    return nbCellules

################################################################################
def viderPlateau() :
    """ Affiche la grille de jeu après en avoir retiré toutes les cellules """
    for ligne in range(nbLignes) :
        for colonne in range (nbColonnes) :
            plateau[ligne][colonne] = CELLULE_MORTE
    afficherPlateau()

################################################################################
def evolution() :
    """ Applique la règle d'évolution configurée à la grille de jeu et retourne les recensements associés """
    population = 0
    naissances = 0
    survie = 0
    deces = 0
    
    # Créer un tableau comptant les cellules voisines
    voisines = []
    for i in range(nbLignes) :
        ligne = []
        for j in range(nbColonnes) :
            ligne.append(0)
        voisines.append(ligne.copy())
    
    # Le peupler en une seule passe, sans réexaminer plusieurs fois une même cellule :
    for ligne in range(nbLignes) :
        for colonne in range (nbColonnes) :
            if plateau[ligne][colonne] != CELLULE_MORTE :
                if ligne > 0 :
                    if colonne > 0 : voisines[ligne - 1][colonne - 1] += 1
                    voisines[ligne - 1][colonne] += 1
                    if colonne < nbColonnes - 1 : voisines[ligne - 1][colonne + 1] += 1
                if colonne > 0 : voisines[ligne][colonne - 1] += 1
                if colonne < nbColonnes - 1 : voisines[ligne][colonne + 1] += 1
                if ligne < nbLignes - 1 :
                    if colonne > 0 : voisines[ligne + 1][colonne - 1] += 1
                    voisines[ligne + 1][colonne] += 1
                    if colonne < nbColonnes - 1 : voisines[ligne + 1][colonne + 1] += 1
    
    # La règle du jeu de la vie    
    for ligne in range(nbLignes) :
        for colonne in range (nbColonnes) :
            if plateau[ligne][colonne] == CELLULE_MORTE :
                if str(voisines[ligne][colonne]) in regle["naissance"] :
                    plateau[ligne][colonne] = CELLULE_NAISSANTE
                    population += 1
                    naissances += 1
            else :
                if str(voisines[ligne][colonne]) in regle["survie"] :
                    plateau[ligne][colonne] += 1
                    population += 1
                    survie += 1
                else :
                    plateau[ligne][colonne] = CELLULE_MORTE
                    deces += 1
    afficherPlateau()
    return (population, naissances, survie, deces)

################################################################################
def ligneVivante(ligne) :
    """ Retourne un booléen indiquant si la ligne spécifiée contient au moins une cellule vivante """
    for colonne in range (nbColonnes) :
        if plateau[ligne][colonne] != CELLULE_MORTE :
            return True
    return False

################################################################################
def colonneVivante(colonne) :
    """ Retourne un booléen indiquant si la colonne spécifiée contient au moins une cellule vivante """
    for ligne in range (nbLignes) :
        if plateau[ligne][colonne] != CELLULE_MORTE :
            return True
    return False

################################################################################
def detourerPlateau() :
    """ Retourne les coordonnées des coins supérieur gauche et inférieur droit de la grille de jeu contenant l'ensemble des cellules vivantes """
    zoneUtile = { "PREMIERE_LIGNE" : -1, "PREMIERE_COLONNE" : -1, "DERNIERE_LIGNE" : nbLignes, "DERNIERE_COLONNE" : nbColonnes }
    for colonne in range(nbColonnes) :
        if colonneVivante(colonne) :
            zoneUtile["PREMIERE_COLONNE"] = colonne
            break
    if zoneUtile["PREMIERE_COLONNE"] == -1 :
        # Rien à sauvegarder !
        return zoneUtile
    for colonne in range(nbColonnes - 1, -1, -1) :
        if colonneVivante(colonne) :
            zoneUtile["DERNIERE_COLONNE"] = colonne
            break
    for ligne in range(nbLignes) :
        if ligneVivante(ligne) :
            zoneUtile["PREMIERE_LIGNE"] = ligne
            break
    for ligne in range(nbLignes -1, -1, -1) :
        if ligneVivante(ligne) :
            zoneUtile["DERNIERE_LIGNE"] = ligne
            break
    return zoneUtile

################################################################################
def sauvegarderFichier(cheminFichier) :
    """ Sauvegarde la zone utile de la grille de jeu dans un fichier au format Plain Text """
    if not os.path.exists(REPERTOIRE_SAUVEGARDE):
        os.makedirs(REPERTOIRE_SAUVEGARDE)
    fichier = open(cheminFichier, "w")
    fichier.write("!Name: " + nomFichier + "\n")
    fichier.write("!Position: " + str(zoneUtile["PREMIERE_COLONNE"]) + "," + str(zoneUtile["PREMIERE_LIGNE"]) + "\n")
    fichier.write("!\n")
    for ligne in range(zoneUtile["PREMIERE_LIGNE"], zoneUtile["DERNIERE_LIGNE"] + 1) :
        for colonne in range(zoneUtile["PREMIERE_COLONNE"], zoneUtile["DERNIERE_COLONNE"] + 1) :
            if plateau[ligne][colonne] == CELLULE_MORTE :
                fichier.write(".")
            else :
                fichier.write("O")
        fichier.write("\n")
    fichier.close()

################################################################################
def chargerFichierPlaintext(cheminFichier) :
    """ Retourne la structure contenue dans un fichier au format Plain Text (.cells) """
    structure = []
    noLigne = 0
    maxColonnes = 0
    fichier = open(cheminFichier, "r")
    for ligneFichier in fichier :
        noLigne += 1
        ligneFichier = ligneFichier.strip()
        if not (ligneFichier == "" or ligneFichier.startswith("!")) :
            if len(ligneFichier) > maxColonnes :
                maxColonnes = len(ligneFichier)
            ligne = []
            for caractere in ligneFichier :
                if caractere == '.' :
                    ligne.append(CELLULE_MORTE)
                elif caractere == "O" :
                    ligne.append(CELLULE_NAISSANTE)
                elif caractere == "*" :
                    ligne.append(CELLULE_NAISSANTE)
                    print(texte1[parametres["LANGUE"]]["AVERTISSEMENT"] + ": " + texte1[parametres["LANGUE"]]["FICHIER"] + "=" + cheminFichier + " " + texte1[parametres["LANGUE"]]["NOLIGNE"] + "=" + str(noLigne) + " " + texte1[parametres["LANGUE"]]["LIGNE"] + "=" + ligneFichier)
                else :
                    print(texte1[parametres["LANGUE"]]["ERREUR"] + ": " + texte1[parametres["LANGUE"]]["FICHIER"] + "=" + cheminFichier + " " + texte1[parametres["LANGUE"]]["NOLIGNE"] + "=" + str(noLigne) + " " + texte1[parametres["LANGUE"]]["LIGNE"] + "=" + ligneFichier)
                    break
            structure.append(ligne.copy())
    fichier.close()
    
    # Certains fichiers du LifeWiki ne respectent pas la spécification sur https://www.conwaylife.com/wiki/Plaintext
    # et ne mentionnent pas les cellules mortes en fin de ligne
    # Maintenant que l'on connaît la largeur maximale de la structure on les rajoute
    for ligne in range(len(structure)) :
        cellulesManquantes = maxColonnes - len(structure[ligne])
        if cellulesManquantes > 0 :
            for i in range(cellulesManquantes) :
                structure[ligne].append(CELLULE_MORTE)
    
    return structure

################################################################################
def chargerPositionDansFichierPlaintext(cheminFichier) :
    """ Retourne la position indiquée dans un fichier au format Plain Text """
    position = (0, 0)
    fichier = open(cheminFichier, "r")
    for ligneFichier in fichier :
        ligneFichier = ligneFichier.strip()
        if ligneFichier.startswith("!Position: ") :
            resultat = ligneFichier.split(" ")[1].split(",")
            position = ( int(resultat[0]), int(resultat[1]) )
    fichier.close()
    return position

################################################################################
def chargerFichierRunLengthEncoded(cheminFichier) :
    """ Retourne la structure contenue dans un fichier au format Run Length Encoded (.rle) """
    structure = []
    ligne = []
    nbCellules = 0
    nbLignes = 0
    nombre = 0
    fin = False
    noLigne = 0
    fichier = open(cheminFichier, "r")
    for ligneFichier in fichier :
        noLigne += 1
        ligneFichier = ligneFichier.strip()
        if ligneFichier == "" or ligneFichier.startswith("#") :
            continue
        elif ligneFichier.startswith("x") :
            expression = re.match(r'^\s*x\s*=\s*(?P<x>\d*)\s*,\s*y\s*=\s*(?P<y>\d*)(\s*,\s*rule\s*=\s*(?P<rule>[bB]\d*/[sS]\d*))?', ligneFichier)
            if expression is not None :
                enTete = expression.groupdict()
                largeurStructure = int(enTete["x"])
                hauteurStructure = int(enTete["y"])
            else :
                print(texte1[parametres["LANGUE"]]["ERREUR"] + ": " + texte1[parametres["LANGUE"]]["FICHIER"] + "=" + cheminFichier + " " + texte1[parametres["LANGUE"]]["NOLIGNE"] + "=" + str(noLigne) + " " + texte1[parametres["LANGUE"]]["LIGNE"] + "=" + ligneFichier)
        else :    
            for caractere in ligneFichier :
                if caractere == ' ' or caractere == '\t' :
                    continue
                elif caractere >= "0" and caractere <= "9" :
                    nombre = (nombre * 10) + int(caractere)
                elif caractere == 'b' or caractere == 'B' :
                    if nombre == 0 :
                        nombre = 1
                    for i in range(nombre) :
                        ligne.append(CELLULE_MORTE)
                        nbCellules += 1
                    nombre = 0
                elif caractere == 'o' or caractere == 'O' :
                    if nombre == 0 :
                        nombre = 1
                    for i in range(nombre) :
                        ligne.append(CELLULE_NAISSANTE)
                        nbCellules += 1
                    nombre = 0
                elif caractere == '$' or caractere == '!' :
                    for i in range(nbCellules, largeurStructure) :
                        ligne.append(CELLULE_MORTE) 
                    nbCellules = 0
                    structure.append(ligne.copy())
                    ligne = []
                    nbLignes = nbLignes + 1
                    if caractere == '!' :
                        for j in range (nbLignes, hauteurStructure) :
                            for i in range(largeurStructure) :
                                ligne.append(CELLULE_MORTE)
                            structure.append(ligne.copy())
                            ligne = []
                        fin = True
                        break
                else :
                    print(texte1[parametres["LANGUE"]]["AVERTISSEMENT"] + ": " + texte1[parametres["LANGUE"]]["FICHIER"] + "=" + cheminFichier + " " + texte1[parametres["LANGUE"]]["NOLIGNE"] + "=" + str(noLigne) + " " + texte1[parametres["LANGUE"]]["LIGNE"] + "=" + ligneFichier)
                    break
        if fin == True :
            break
    fichier.close()
    return structure

################################################################################
def chargerFichier(cheminFichier) :
    """ Retourne la structure contenue dans un fichier """
    if cheminFichier.lower().endswith(".cells") :
        return chargerFichierPlaintext(cheminFichier)
    elif cheminFichier.lower().endswith(".rle") :
        return chargerFichierRunLengthEncoded(cheminFichier)

################################################################################
"""
def telechargerEtInstallerPatternCollection() :
    # Téléchargement de la pattern collection depuis le site LifeWiki
    if not os.path.exists(REPERTOIRE_SAUVEGARDE):
        os.makedirs(REPERTOIRE_SAUVEGARDE)
    if not os.path.isfile(REPERTOIRE_SAUVEGARDE + "/_README_.txt") :
        t1 = time.time()
        url = 'http://www.conwaylife.com/patterns/all.zip'
        cheminFichier = REPERTOIRE_SAUVEGARDE + "/" + url.split('/')[-1]
        requeteHTTP = requests.get(url, stream = True)
        with open(cheminFichier, 'wb') as fichier :
            shutil.copyfileobj(requeteHTTP.raw, fichier)
        t2 = time.time()
        print("Temps de téléchargement = " + str(t2 - t1) + " secondes")
        
    # Installation
    with zipfile.ZipFile(cheminFichier) as fichierZip :
        fichierZip.extractall(REPERTOIRE_SAUVEGARDE)
    os.remove(cheminFichier)
    
    # Elimination des doublons entre fichiers .cells et .rle
    listeFichiers = [f for f in os.listdir(REPERTOIRE_SAUVEGARDE) if os.path.isfile(os.path.join(REPERTOIRE_SAUVEGARDE, f)) and f.lower().endswith(".cells")]
    for fichier in range(len(listeFichiers)) :
        nomSansExtension = fichier.split('.')[:-1])
        cheminFichier = REPERTOIRE_SAUVEGARDE + "/" + nomSansExtension + ".rle"
        if os.path.isfile(cheminFichier) :
            os.remove(cheminFichier)
"""

### Programme principal ########################################################

parametres = chargerOuCreerFichierDeConfiguration()

# Fenêtre positionnée en haut à gauche de l'écran (à faire avant l'initialisation de PyGame)
# décalée du bandeau de fenêtre Windows
os.environ['SDL_VIDEO_WINDOW_POS'] = "0," + str(HAUTEUR_BANDEAU_FENETRE)

pygame.init()

# Initialisation de l'écran et de la fenêtre de jeu
if platform.system() == "Windows" :
    # La fonction suivante évite que Windows ne mette la fenêtre à l'échelle ce qui fausse les calculs de pixels
    ctypes.windll.user32.SetProcessDPIAware()
    largeurEcran = ctypes.windll.user32.GetSystemMetrics(0)
    hauteurEcran = ctypes.windll.user32.GetSystemMetrics(1)
    ecran = (largeurEcran, hauteurEcran)
else :
    ecran = pygame.display.Info()
    largeurEcran = ecran.current_w
    hauteurEcran = ecran.current_h
largeurFenetre = largeurEcran
hauteurFenetre = hauteurEcran - HAUTEUR_RESERVEE
if largeurEcran >= RESOLUTION_FULL_HD :
    format = "long"
else :
    format = "court"

# Initialisation du plateau de jeu
nbColonnes = ((largeurFenetre + EPAISSEUR_LIGNE) // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
nbLignes = ((hauteurFenetre + EPAISSEUR_LIGNE) // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
plateau = []
for i in range(nbLignes) :
    ligne = []
    for j in range(nbColonnes) :
        ligne.append(0)
    plateau.append(ligne.copy())

# Initialisation de l'interface graphique
# et redimensionnement de la fenêtre au nombre de cases affichables
mode = MODE_EDITION
largeurFenetre = EPAISSEUR_LIGNE + (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE) * nbColonnes
hauteurFenetre = EPAISSEUR_LIGNE + (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE) * nbLignes
fenetre = pygame.display.set_mode((largeurFenetre, hauteurFenetre))
afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_EDITION"])
afficherPlateau()

# Initialisation de la règle du jeu
expression = re.match(r'^B(?P<naissance>\d*)/S(?P<survie>\d*)$', parametres["REGLE"])
regle = expression.groupdict()

# Boucle principale du programme
programmeTermine = False
derniereEvolution = GAME_TIME.get_ticks()
encadre = (0, 0, 1, 1)
zoneUtile = { "PREMIERE_LIGNE" : -1, "PREMIERE_COLONNE" : -1, "DERNIERE_LIGNE" : nbLignes, "DERNIERE_COLONNE" : nbColonnes }
while programmeTermine == False :
    
    horloge = GAME_TIME.get_ticks()
    # Evolution si le moment est venu, qu'il reste une cellule en vie et qu'on ne soit pas arrivé en stase
    if mode == MODE_EVOLUTION and horloge - derniereEvolution > parametres["CYCLE_DE_VIE"] and populationMin > 0 and not (statut[1] == 0 and statut[3] == 0) :
        derniereEvolution =  horloge
        generation += 1
        statut = evolution()
        if statut[0] < populationMin :
            populationMin = statut[0]
        elif statut[0] > populationMax :
            populationMax = statut[0]
        afficherBandeauEvolution()
    
    for event in GAME_EVENTS.get() :
        if event.type == pygame.MOUSEMOTION :
            positionSouris = event.pos
            if mode == MODE_BIBLIOTHEQUE or mode == MODE_FICHIER :
                encadre = deplacerEncadre(encadre)

        if event.type == pygame.MOUSEBUTTONUP :
            colonne = (positionSouris[0] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
            ligne = (positionSouris[1] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
            if mode == MODE_EDITION :
                if plateau[ligne][colonne] == CELLULE_MORTE :
                    plateau[ligne][colonne] = CELLULE_NAISSANTE
                else :
                    plateau[ligne][colonne] = CELLULE_MORTE
                dessinerCellule(colonne, ligne)
                afficherEcran()
        
        if event.type == pygame.KEYDOWN :
            
            if event.type == GAME_GLOBALS.QUIT : # Quitter
                programmeTermine = True
            
            if event.key == pygame.K_ESCAPE : # Changer de mode
                if mode == MODE_EDITION :
                    mode = MODE_EVOLUTION
                    generation = 1
                    nbCellules = compterCellules()
                    statut = (nbCellules, nbCellules, 0, 0)
                    populationMin = nbCellules
                    populationMax = nbCellules
                    afficherBandeauEvolution()
                    
                    # Si la configuration de départ n'est pas vide, on la note au cas où elle serait intéressante
                    zoneUtile = detourerPlateau()
                    if zoneUtile["PREMIERE_COLONNE"] != -1 :
                        nomFichier = texte1[parametres["LANGUE"]]["DERNIERE_PARTIE"]
                        sauvegarderFichier(REPERTOIRE_SAUVEGARDE + "/" + texte1[parametres["LANGUE"]]["DERNIERE_PARTIE"] + ".cells")
                else :
                    mode = MODE_EDITION
                    afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_EDITION"])
                    pygame.draw.rect(fenetre, NOIR, encadre, 1)
                    afficherEcran()
            
            if mode == MODE_EDITION :
                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_BIBLIOTHEQUE"] : # Sélectionner un motif dans la bibliothèque interne
                    mode = MODE_BIBLIOTHEQUE
                    indice = 0
                    cle = list(bibliotheque)[indice]
                    afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_BIBLIOTHEQUE"] + cle)
                    hauteurStructure = len(bibliotheque[cle])
                    largeurStructure = len(bibliotheque[cle][0])
                    encadre = deplacerEncadre((0, 0, 1, 1))
                
                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_FICHIER"] : # Sélectionner un fichier
                    mode = MODE_FICHIER
                    listeFichiers = [f for f in os.listdir(REPERTOIRE_SAUVEGARDE) if os.path.isfile(os.path.join(REPERTOIRE_SAUVEGARDE, f)) and (f.lower().endswith(".cells") or f.lower().endswith(".rle"))]
                    indice = 0
                    afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_FICHIER"] + listeFichiers[indice])
                    structure = chargerFichier(REPERTOIRE_SAUVEGARDE + "/" + listeFichiers[indice])
                    hauteurStructure = len(structure)
                    largeurStructure = len(structure[0])
                    encadre = deplacerEncadre((0, 0, 1, 1))
                
                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_QUITTER"] : # Quitter
                    programmeTermine = True
                
                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_SAUVEGARDER"] : # Sauvegarder le plateau au format PlainText (https://conwaylife.com/wiki/Plaintext)
                    zoneUtile = detourerPlateau()
                    mode = MODE_SAISIE
                    nomFichier = ""
                    afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_SAISIE"])
                
                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_RESTAURER"] : # Restaurer le plateau de la dernière partie s'il existe
                    cheminFichier = REPERTOIRE_SAUVEGARDE + "/" + texte1[parametres["LANGUE"]]["DERNIERE_PARTIE"] + ".cells"
                    if os.path.isfile(cheminFichier) :
                        structure = chargerFichierPlaintext(cheminFichier)
                        position = chargerPositionDansFichierPlaintext(cheminFichier)
                        viderPlateau()
                        for ligne in range(len(structure)) :
                            for colonne in range(len(structure[ligne])) :
                                if ligne + position[1] < nbLignes and colonne + position[0] < nbColonnes :
                                    plateau[ligne + position[1]][colonne + position[0]] = structure[ligne][colonne]
                        afficherPlateau()
                
                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_VIDER"] : # Vider le plateau
                    viderPlateau()
            
            elif mode == MODE_SAISIE :
                if (event.unicode >= "A" and event.unicode <= "Z") \
                or (event.unicode >= "a" and event.unicode <= "z") \
                or (event.unicode >= "0" and event.unicode <= "9") \
                or event.unicode == ' ' \
                or event.unicode == '-' \
                or event.unicode == '_' :
                    if len(nomFichier) < TAILLE_NOM_FICHIER :
                        nomFichier += event.unicode
                        afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_SAISIE"] + nomFichier)
                
                if event.key == pygame.K_BACKSPACE :
                    if len(nomFichier) > 1 :
                        nomFichier = nomFichier[:-1]
                        afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_SAISIE"] + nomFichier)
                
                if event.key == pygame.K_RETURN :
                    # Sauvegarde avec demande de confirmation en cas d'écrasement
                    cheminFichier = REPERTOIRE_SAUVEGARDE + "/" + nomFichier + ".cells"
                    if not os.path.isfile(cheminFichier) :
                        sauvegarderFichier(cheminFichier)
                        mode = MODE_EDITION
                        afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_EDITION"])
                    else :
                        mode = MODE_CONFIRMATION
                        afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_CONFIRMATION"])
            
            elif mode == MODE_CONFIRMATION :
                if event.unicode.lower() == texte1[parametres["LANGUE"]]["TOUCHE_CONFIRMATION"] : # confirmer
                    sauvegarderFichier(cheminFichier)
                mode = MODE_EDITION
                afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_EDITION"])
            
            elif mode == MODE_BIBLIOTHEQUE :
                if event.key == pygame.K_UP or event.key == pygame.K_LEFT \
                or event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT :
                    if event.key == pygame.K_UP or event.key == pygame.K_LEFT :
                        indice -= 1
                    if event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT :
                        indice += 1
                    if indice < 0 :
                        indice = len(list(bibliotheque)) - 1
                    elif indice == len(list(bibliotheque)) :
                        indice = 0
                    
                    cle = list(bibliotheque)[indice]
                    afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_BIBLIOTHEQUE"] + cle)
                    hauteurStructure = len(bibliotheque[cle])
                    largeurStructure = len(bibliotheque[cle][0])
                    encadre = deplacerEncadre(encadre)
                
                if event.key == pygame.K_RETURN :
                    # Collage de la structure à la position de la souris
                    colonnePlateau = (positionSouris[0] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
                    lignePlateau = (positionSouris[1] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
                    cle = list(bibliotheque)[indice]
                    for ligne in range(len(bibliotheque[cle])) :
                        for colonne in range(len(bibliotheque[cle][ligne])) :
                            if ligne + lignePlateau < nbLignes and colonne + colonnePlateau < nbColonnes :
                                plateau[ligne + lignePlateau][colonne + colonnePlateau] = bibliotheque[cle][ligne][colonne]
                    afficherPlateau()
            
            elif mode == MODE_FICHIER :
                if event.key == pygame.K_UP or event.key == pygame.K_LEFT \
                or event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT \
                or event.key == pygame.K_PAGEUP or event.key == pygame.K_PAGEDOWN \
                or event.key == pygame.K_HOME or event.key == pygame.K_END :
                    page = len(listeFichiers) // 20 # 5% de la liste
                    if event.key == pygame.K_UP or event.key == pygame.K_LEFT :
                        indice -= 1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT :
                        indice += 1
                    elif event.key == pygame.K_PAGEUP :
                        if indice > page :
                            indice -= page
                        else :
                            indice = 0
                    elif event.key == pygame.K_PAGEDOWN :
                        if indice < len(listeFichiers) - page :
                            indice += page
                        else :
                            indice = len(listeFichiers) - 1
                    elif event.key == pygame.K_HOME :
                        indice = 0
                    elif event.key == pygame.K_END :
                        indice = len(listeFichiers) - 1
                    if indice < 0 :
                        indice = len(listeFichiers) - 1
                    elif indice == len(listeFichiers) :
                        indice = 0
                    
                    afficherBandeau(texte2[parametres["LANGUE"]][format]["MODE_FICHIER"] + listeFichiers[indice])
                    structure = chargerFichier(REPERTOIRE_SAUVEGARDE + "/" + listeFichiers[indice])
                    hauteurStructure = len(structure)
                    largeurStructure = len(structure[0])
                    encadre = deplacerEncadre(encadre)
                
                if event.key == pygame.K_RETURN :
                    # Collage de la structure à la position de la souris
                    colonnePlateau = (positionSouris[0] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
                    lignePlateau = (positionSouris[1] // (parametres["LARGEUR_CASE"] + EPAISSEUR_LIGNE))
                    for ligne in range(len(structure)) :
                        for colonne in range(len(structure[ligne])) :
                            if ligne + lignePlateau < nbLignes and colonne + colonnePlateau < nbColonnes :
                                plateau[ligne + lignePlateau][colonne + colonnePlateau] = structure[ligne][colonne]
                    afficherPlateau()

            elif mode == MODE_PAUSE :
                if event.key == pygame.K_SPACE : # Remettre l'évolution en marche
                    mode = MODE_EVOLUTION
                    afficherBandeauEvolution()
            
            else : # if mode == MODE_EVOLUTION
                if event.unicode == "+" : # Accélérer l'évolution
                    parametres["CYCLE_DE_VIE"] //= 2
                    if parametres["CYCLE_DE_VIE"] == 0 : # Jusqu'à un tick d'horloge maximum
                        parametres["CYCLE_DE_VIE"] = 1
                    else :
                        afficherBandeauEvolution()
                
                if event.unicode == "-" : # Ralentir l'évolution
                    parametres["CYCLE_DE_VIE"] *= 2
                    afficherBandeauEvolution()

                if event.key == pygame.K_SPACE : # Mettre l'évolution en pause
                    mode = MODE_PAUSE
                    afficherBandeauEvolution()
        
        if event.type == pygame.QUIT :
            programmeTermine = True    

pygame.quit()
sys.exit()
"""
### Idées d'améliorations ######################################################
- stockage matriciel actuel avec conservation de l'information sur les bordures et calculs uniquement dans cet espace (optimisation)
- interface homme-machine avec Simple Game Code (https://program.sambull.org/sgc/)
    - écran de démarrage = mode configuration
        - crédits
        - explication
        - liens
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
                    - par exemple : matrice à partir du coin supérieur gauche sur un plateau infini et troué
- plus d'options d'édition
    - mode sélection de zone
        - couper, coller
        - rotation à 90°
        - symétrie verticale/horizontales
        - vidage
    - mode édition: bouton 1 peindre, bouton 2 effacer
    - mode écriture de texte
- détecteur de configurations intéressantes :
    - oscillateurs (calculer hash configuration initiale et courante et indiquer période si égalité)
    - vaisseaux (idem si position de départ et d'arrivée différente)
- générateur de structures pour recherche systématique avec le détecteur précédent
- version compilée
"""