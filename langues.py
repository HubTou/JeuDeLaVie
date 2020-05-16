#!/usr/bin/python3
""" Constantes linguistiques
Titre : Le jeu de la Vie
Auteur : Hubert Tournier
Création : 29/04/2020
Version : 1.1 (16/05/2020)
Version 1.1 :
- PRESENTATION : Amélioration conformité PEP8
"""

# Chaînes avec version normale uniquement
texte1 = \
{
    "fr" : # Français
    {
        "TITRE" : "Le jeu de la Vie",

        "TELECHARGEMENT"  : "Téléchargement de la base de formes du site LifeWiki (une fois, < 30 s)",
        "DECOMPRESSION"   : "Installation de la base de formes du site LifeWiki (une fois, < 30 s)",
        "TERMINE"         : "Terminé en ",
        "CYCLE_EVOLUTION" : "Cycle d'évolution terminé en ",
        "SECONDES"        : " secondes",

        "POP_MINIMUM" : "min",
        "POP_MAXIMUM" : "max",

        "AVERTISSEMENT" : "AVERTISSEMENT ",
        "ERREUR"        : "ERREUR ",
        "FICHIER"       : "fichier",
        "NOLIGNE"       : "n° ligne",
        "LIGNE"         : "ligne",

        "TOUCHE_BIBLIOTHEQUE" : "b",
        "TOUCHE_FICHIER"      : "f",
        "TOUCHE_SAUVEGARDER"  : "s",
        "TOUCHE_RESTAURER"    : "r",
        "TOUCHE_VIDER"        : "v",
        "TOUCHE_QUITTER"      : "q",
        "TOUCHE_CONFIRMATION" : "o",

        "DERNIERE_PARTIE" : "_DernierePartie"
    },

    "en" : # English
    {
        "TITRE" : "The game of Life",

        "TELECHARGEMENT" : "Downloading the pattern collection from LifeWiki website (only once, < 30 s)",
        "DECOMPRESSION"  : "Installing the pattern collection from LifeWiki website (only once, < 30 s)",
        "TERMINE"        : "Done in ",
        "CYCLE_EVOLUTION" : "Evolution cycle completed in ",
        "SECONDES"       : " seconds",

        "POP_MINIMUM"   : "min",
        "POP_MAXIMUM"   : "max",

        "AVERTISSEMENT" : "WARNING",
        "ERREUR"        : "ERROR",
        "FICHIER"       : "file",
        "NOLIGNE"       : "line #",
        "LIGNE"         : "line",

        "TOUCHE_BIBLIOTHEQUE" : "l",
        "TOUCHE_FICHIER"      : "f",
        "TOUCHE_SAUVEGARDER"  : "s",
        "TOUCHE_RESTAURER"    : "r",
        "TOUCHE_VIDER"        : "e",
        "TOUCHE_QUITTER"      : "q",
        "TOUCHE_CONFIRMATION" : "y",

        "DERNIERE_PARTIE" : "_LastGame"
    }
}

# Chaînes avec version normale ou abrégée
texte2 = \
{
    "fr" : # Français
    {
        "long" :
        {
            "MODE_EDITION"      : " [mode édition : ESC=mode évolution, B=bibliothèque interne, F=sélecteur de fichier, clic=poser, S=sauvegarder, R=restaurer, V=vider, Q=quitter]",
            "MODE_BIBLIOTHEQUE" : " [mode bibliothèque interne : ESC=mode édition, flèches=sélectionner, souris=positionner, Entrée=poser] => ",
            "MODE_EVOLUTION"    : " [mode évolution : ESC=mode édition, +/-=accélérer/décélérer, Espace=pause]",
            "MODE_SAISIE"       : " [mode saisie : ESC=mode édition, Entrée=valider] Nom du fichier ? => ",
            "MODE_CONFIRMATION" : " [mode confirmation : O/o=confirmer, autre=annuler] Ecraser le fichier ? => ",
            "MODE_FICHIER"      : " [mode sélecteur de fichier : ESC=mode édition, flèches=sélectionner, souris=positionner, Entrée=poser] => ",
            "MODE_PAUSE"        : " [mode évolution en pause : ESC=mode édition, Espace=reprendre] ",

            "VITESSE"    : "vitesse",
            "GENERATION" : "génération",
            "POPULATION" : "population",
            "NAISSANCES" : "naissances",
            "SURVIE"     : "survies",
            "DECES"      : "décès"
        },
        "court" :
        {
            "MODE_EDITION"      : " [édition: ESC/B/F/clic/S/R/V/Q]",
            "MODE_BIBLIOTHEQUE" : " [bibliothèque: ESC/flèches/souris/Entrée] => ",
            "MODE_EVOLUTION"    : " [évolution: ESC/+/-/Espace]",
            "MODE_SAISIE"       : " [saisie: ESC/Entrée] Nom ? => ",
            "MODE_CONFIRMATION" : " [confirmation: O/o/autre] Ecraser ? => ",
            "MODE_FICHIER"      : " [sélecteur de fichier: ESC/flèches/souris/Entrée] => ",
            "MODE_PAUSE"        : " [évolution en pause: ESC/Espace] ",

            "VITESSE"    : "v",
            "GENERATION" : "gen",
            "POPULATION" : "pop",
            "NAISSANCES" : "n",
            "SURVIE"     : "s",
            "DECES"      : "d"
        }
    },

    "en" : # English
    {
        "long" :
        {
            "MODE_EDITION"      : " [edit mode: ESC=evolution mode, L=internal library, F=file selector, click=paste, S=save, R=restore, E=empty, Q=quit]",
            "MODE_BIBLIOTHEQUE" : " [internal library mode: ESC=edit mode, arrows=select, mouse=position, Return=paste] => ",
            "MODE_EVOLUTION"    : " [evolution mode: ESC=edit mode, +/-=faster/slower, Space=pause] ",
            "MODE_SAISIE"       : " [typing mode: ESC=edit mode, Return=validate] File name? => ",
            "MODE_CONFIRMATION" : " [confirmation mode: Y/y=confirm, other=cancel] Overwrite file? => ",
            "MODE_FICHIER"      : " [file selection mode: ESC=edit mode, arrows=select, mouse=position, Return=paste] => ",
            "MODE_PAUSE"        : " [evolution mode stalled: ESC=edit mode, Space=unpause] ",

            "VITESSE"      : "speed",
            "GENERATION"   : "generation",
            "POPULATION"   : "population",
            "NAISSANCES"   : "births",
            "SURVIE"       : "survivals",
            "DECES"        : "deaths"
        },
        "court" :
        {
            "MODE_EDITION"      : " [edit: ESC/L/F/click/S/R/E/Q]",
            "MODE_BIBLIOTHEQUE" : " [library: ESC/arrows/mouse/Return] => ",
            "MODE_EVOLUTION"    : " [evolution: ESC/+/-/Space] ",
            "MODE_SAISIE"       : " [typing: ESC/Return] Name? => ",
            "MODE_CONFIRMATION" : " [confirmation: Y/y/other] Overwrite? => ",
            "MODE_FICHIER"      : " [file selection: ESC/arrows/mouse/Return] => ",
            "MODE_PAUSE"        : " [evolution stalled: ESC/Space] ",

            "VITESSE"    : "s",
            "GENERATION" : "gen",
            "POPULATION" : "pop",
            "NAISSANCES" : "b",
            "SURVIE"     : "s",
            "DECES"      : "d"
        }
    }
}
