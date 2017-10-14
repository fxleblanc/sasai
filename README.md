# Sword and Soul Artificial Intelligence #
Simple Artificial Intelligence to beat the Sword and Soul flash minigame

## Attack minigame ##
The attack minigame consists of one enemy shooting apples in three directions. The goal of the player is to press either Up, Down or Right on his keyboard at the right time to cut the apples.

![](https://media.giphy.com/media/xT9IgGCFO4k82TmzoA/giphy.gif)

# Usage #
First, setup your virtualenv with python 2
```
virtualenv -p python2 env
source env/bin/activate
```

Then, install the python dependencies
```
pip install -r requirements
```

Launch the program
```
python attack-minigame.py
```

Click on the top left corner of the Flash game screen, then the bottom right. Then, click inside the Flash game screen to put the focus in it. The program should output coordinates with delays in the terminal screen.
