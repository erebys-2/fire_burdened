===============================================================
NO FILES MAY BE REDISTRIBUTED WITHOUT EXPLICIT PERMISSION.
ASSETS MAY NOT BE REUSED.
CODE MAY BE REFERENCED AND REPURPOSED.
===============================================================

Description:
Fire Burdened is a combat platformer with gameplay emphasis on very short range melee and high maneuverability
built in Python using the Pygame Library.

I have set up infrastructure to build a metroidvania, namely the ability to transition into levels of 
various sizes non-linearly and having multiple transitions per level, however it is unlikely that this game will be 
fully realized into one since my vision for it doesn't require such a large world.

Currently there are 2 conjoined debugging levels that loop back to one another.

Disclaimer:
This is my first major coding project outside of school assignments so there will be some jank and spaghetti (bad code).
Now and then I go back and try to clean up older code as I learn better coding.

Live Dev Log: 
https://docs.google.com/document/d/1DKHFFTGyHRi6FeIa0QXCALuBxQLR8XExPAktH98XHok/edit?usp=sharing


SET UP:

    Download the following if you haven't already:
    1. Python, 
    2. Pygame, 

        To install Pygame I think it was 
        Win + R, type "cmd", enter, then paste: "python3 -m pip install -U pygame"

    3. Visual Studio Code or some other IDE, 

        Download the microsoft python extension, then go into settings and 
	search "Execute in File Dir", set it as enable.

        The second part is important or else the next time 
	you open VS code you will be hit with file not found errors...
        why this is not a default setting eludes me.

	Personally I use VS code with Kevin Rose's python indent extension, 
	VS code for python is unuseable without it.


This zip file has the directories in right places.

To run, open game_window.py and hit the run button in the upper right corner.

The controls are WAD to move, I to melee, O to shoot, S to roll, and ALT to sprint.
The direction of the melee attack depends on if you're falling or rising.
I while falling will do a downstrike, I while rising will do an upstrike.
I while rolling will do a crit.
You can jump and roll in mid air too.

Holding ALT increases your speed, but your stamina regeneration rate is lowered.
Holding O will deplete some initial stamina then continuously charge up how
many projectiles you shoot. You shoot when you lift the key.

========================================================================================
Insiprations:
-Momodora: Reverie Under the Moonlight
-Undertale
-Hollowknight
-Dark Souls

Special Thanks:
-Coding with Russ for a good base/ tutorial to jump off from
-r/Pygame for inspiration

Note: This file also contains a level editor, it is user hostile.
Keep an eye on the terminal when you run it.
The tiles with numbers are essentially pointers to background art and will
not display if on the main layer. X to show grid, WS to change levels,
AD to move around, L to increment layers.




