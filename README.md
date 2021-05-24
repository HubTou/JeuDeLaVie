# About JeuDeLaVie

Yet another (Python+PyGame) implementation of John Horton Conway's [Game of Life](https://fr.wikipedia.org/wiki/Jeu_de_la_vie).

With goals of readability (it was intended as an example for my son - no sophisticated algorithms such as HashLife here), providing a [PyGame](https://www.pygame.org/) example, in a program (project) with rather complete functionalities (configuration file, saves, multi modes, etc.) BUT with a minimalist GUI only using the window title (a challenge!), the idea being to later use a PyGame GUI framework, for example such as [Simple Game Code](https://program.sambull.org/sgc/)

# Installation / Configuration / Usage

Install Python 3 and PyGame, then launch vie.py from your file explorer or use "python vie.py" on the command line.

After first launch, a vie.cfg configuration file will be created that you'll be able to tweak to your taste (including setting the game in English).

Windows users: you can download Python and PyGame from the following locations:
- https://www.python.org/downloads/windows/ (I used python-3.7.7-amd64.exe)
- https://pypi.org/project/pygame/#files (I used pygame-1.9.6-cp37-cp37m-win_amd64.whl)

On first launch, it'll automatically download and install LifeWiki's [1500+ pattern files collection](http://www.conwaylife.com/patterns/all.zip).


# Versions and changelog

1.1 2020-05-16

    - CORRECTION: Corrected a bug when using File mode before the creation of the backup directory or the first file inside
    - CORRECTION: Corrected a bug with PlainText files loading (empty lines instead of dot filled lines)
    - CORRECTION: Correction a bug with RunLengthEncoded files loading (multiplicator before the "$" character)
    - NEW FEATURE: Automatic download and install of LifeWiki's pattern collection
    - NEW FEATURE: Measuring evolution cycle duration and displaying it on the console in DEBUG mode
    - OPTIMIZATION: Use integers when comparing the number of cell neighbours with the birth/survival rule
    - OPTIMIZATION: Evolve or crop only the useful part of the game grid
    - PRESENTATION: Improve PEP8 compliance

1.0 2020-05-08

    Initial public release.

# Caveats

The source code comments and names are written in French (my primary audience is my son).
However the game is released with both a French or English translation (set this in the configuration file).

# Limits & Known bugs

 - Best displayed on Full HD (1920*1080) screens, else the text strings are shortened till SVGA resolution (800x600) then truncated
 - The examples' name in the internal library of patterns are only in French

# Further development plans

All the main functionalities are implemented.

There's a list of possible unimplemented functionalities at the end of the vie.py file.

# License

This open source software is distributed under a BSD license (see the "License" file for details).

# Credits

 - In memory of [John Horton Conway](https://en.wikipedia.org/wiki/John_Horton_Conway), 1937-2020.
 - The article [La vie, seul où à deux](http://download.abandonware.org/magazines/Jeux%20et%20Strategie/jeuxetstrategie_numero009/Jeux_et_Strategie%20009%20-%20p018%20%281981-06-07%29.jpg) in [Jeux & Stratégie n°9](https://www.abandonware-magazines.org/affiche_mag.php?mag=185&num=4151&album=oui), which made me discover this game in June 1981 
 - The book "Récréations informatiques", bibliothèque Pour la Science, diffusion Belin, which made me (re)discover this game in 1987 and want to program it
 - Wikipedia which made me (re)discover the remarkable patterns provided in the included internal library
 - WikiLife for its pattern collection and its description of the [usual file formats](https://conwaylife.com/wiki/Category:File_formats)

# Author

Hubert Tournier

May 16, 2020
