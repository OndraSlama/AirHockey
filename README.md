# AirHockey

Air hockey game and strategy simulation.

## Dependencies:

-   pygame (pip install pygame)

## Control:

-   Left mouse button - control right striker

-   Middle mouse button - puck will move to mouse position instantly

-   Right mouse button - puck will follow mouse (debug, strategy analysis etc.)

-   Mouse scroll - Change speed of the game

## Settings:

Basic settings can be set in main file. There, you can choose how many parrarel games will be evaluated at the same time (usefull for planned neuroevolution teaching) and whether you want to utilize multiprocessing algorithms - only usefull for many parrarel games and sped-up gameplay. Use MULTIPROCESS = False most of the times as it will run much faster in single game scenario.

For more advanced settings/tweaks, see Constants.py file. Many aspects of the simulation/game behaviour can be set there.

## Note:

Both strikers should now exhibit more advanced playstyle. Prediction and aiming are now implemented. 2 different strategies play againt each other. This should be almost final version of hardcoded strategies. Next step is to try teaching NN to play (NEAT, neuroevultion etc).
