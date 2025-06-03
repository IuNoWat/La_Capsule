# 22/04/2025
J'ai récupéré un module appelé "picod" du projet Muséomix CNAM, c'est exactement ce dont on a besoin pour utiliser une PICO comme lecteur analogique.

J'ai réussi à l'installer sur la pi et à faire blinker une led à l'aide de :
import picod
pico=picod.pico()
pico.gpio_write(25,1)

Maintenant, il faut essayer de lire un positif

Ha j'ai oublié de push aussi

# 23/04

J'ai push

ça fonctionne pour détection de positif, attention les GPIO commencent par zéro et pas par 1

Pour l'analogique en revanche c'est toujours compliqué... Il y a écrit 10k sur les potard linéaires, je pense que c'est très faible, car la valeur detectée passe de 4095 fixe à 4095 très légerement flucutant.
Mais surtout, je ne comprends pas les changement qu'introduisent les resistances et/ou les condensateurs.

# 01/05

C'est bon, le detecteur analogique fonctionne
Les potards sont branchés de la façon suivante :

Vue de dessous :
```
DATA  +
  |___|
  |   |
  |   |
  |   |
  |   |
  |   |
  |   |
  |   |
  |   |
  |   |
  |___|
    |
   GND
```

Les potards du joystick PS2 fonctionnent aussi

Je vais essayer de faire une v0 avec tous les branchements de fait :

Pico :
	-Potard linéaire 1
	-Potard linéaire 2
	-Joystick 1
	-Joystick 2

Problèmes :
- Il n'y a qu'au grand maximum 4 entrées analogiques sur une pico. Il va falloir faire des choix
  - Pour le Zoom, je peux remplacer le potard rotatif par un interrupteur à deux côtés que j'ai déjà, qui fonctionnera très bien
	
# 10/05

J'ai réussi à faire fonctionner le principe LED+°Boutton sur un seul GPIO. Le montage est le suivant :
```
 +3.3V
-------
      |
      |
   resistor (270..330E)
      |
      |
     LED
      |
      |
GPIO--o
      |
      |
      o
       /  switch
      o
      |
      |
------
 GND
```

J'ai également essayé d'installer un condensateur ( 470uf, 10V) sur la connection 3V/GND, ça a fait redémarrer la pi. Je ne sais pas trop pourquoi, peut-être que cela a crée une chute de tension trop importante ?

De ce que je peux voir, il n'y a aucune fluctuation ou faux positif dans les valeurs du boutton.
