==============================================================================================================================
Fire Burdened © 2023 by erebys-2 is licensed under CC BY-NC 4.0 

"This license requires that reusers give credit to the creator. 
It allows reusers to distribute, remix, adapt, and build upon the material in any medium or format,*
for noncommercial purposes only."

*This applies to the code.
DO NOT reuse the assets- anything non-code in this repository- without explicit permission.
Contact @kc2854 on Discord for permission.
==============================================================================================================================

Description:
Fire Burdened is a combat platformer with gameplay emphasis on very short range melee and high maneuverability
built in Python using the Pygame Library.

I have set up infrastructure to build a metroidvania, namely the ability to transition into levels of 
various sizes non-linearly and having multiple transitions per level, however it is unlikely that this game will be 
fully realized into one since my vision for it doesn't require such a large world.

Currently there are 2 conjoined debugging levels that loop back to one another.

Disclaimer:
This is my first major coding project outside of school assignments so there will be some bad code.
Now and then I go back and try to clean up older code as I learn better coding.


------------------------------------------------------------------------------------------------
SET UP: (This is for Windows, GG Mac bros)
------------------------------------------------------------------------------------------------

    Download the following:
    1. Python, 
    2. Pygame CE, 

        To install Pygame CE on Windows:
        Win + R, type "cmd", enter, then paste: "pip install pygame-ce"

    3. (OPTIONAL) Visual Studio Code or some other IDE, 

        Download the microsoft python extension, then go into settings and search "Execute in File Dir", set it as enable.

        The second part is important or else the next time you open VS code you will get file not found errors.

	If you want to try modding the code, I would highly reccommend Kevin Rose's python indent extension since vanilla VS code has issues
	with indent oversensitivity for python.

This zip file has all the directories in right places.


------------------------------------------------------------------------------------------------
RUNNING GAME:
------------------------------------------------------------------------------------------------

Open game_window.py in your IDE and run it. 
Or 
Open command prompt and cd to the fire_burdened folder; type "python game_window.py".

------------------------------------------------------------------------------------------------
HOW TO PLAY:
------------------------------------------------------------------------------------------------

*Note: The controls can be reconfigured and saved, but the paragraph below still explains
the base mechanics. I recommend trying the default settings. The philosophy was to have one
hand deal with purely movement, and the other hand deal with attacks and special moves.

The controls are:
-WAD to move
-I to melee
-O to shoot
-S to roll
-ALT to sprint
-Enter and Escape for textboxes, pausing game, and some UI
-Y to open inventory
-U to use the current item in your selected inventory slot

Jumping:
    Jumping is variable height. Hold the key for longer and you'll jump higher and farther.

Rolling:
    Pressing S will iniate a roll. 
    Stamina will be consumed the longer you roll.
    Rolling can be canceled by:
        -Hitting a wall
        -Jumping
        -Pressing the opposite direction key A or D
    You do not take damage while in roll animation.

Melee:
    The direction of the melee attack depends on vertical velocity.
    Pressing I while falling will do a downstrike; pressing I while rising will do an upstrike.
    Pressing I while rolling will do a crit.
    Pressing I while holding down the same direction key A or D will increase horizontal distance traveled.
    Melee animation can be canceled 1 frame early by:
        -Jumping (hold jump after pressing I until you jump)
        -Pressing the opposite direction key A or D (hold either keys after pressing I)
        -Rolling
    You can deflect bullets by hitting them back.

Sprint:
    Holding right ALT increases your movement AND animation speed (all your actions will be faster too), 
    but your stamina regeneration rate is significantly lowered.

Shoot: 
    Holding O will deplete some initial stamina then continuously charge up how
    many projectiles you shoot. You shoot when you lift the key.
    (Nerfed because all my test players are cowards)

Escape/Backspace and Enter can be used in the main menu or pause menu for quick navigation.

Taking Damage:
    There is NO contact damage. 
    The current enemies are so simple that there might seem like contact damage since they're coded to deploy
    their attack hitboxes when close to the player. When damaged, their attack hitboxes are removed.

Inventory:
    The game is not paused while your inventory is open, so keep it open at your own peril!

Use Item:
    If you select an inventory slot it will still be selected when your inventory is closed. 
    You can quickly use the item in that slot using this key.

**Note 2: Toggle screen will change your resolution while the game is running; it does not work on Mac.


========================================================================================
Insiprations:
-Momodora: Reverie Under the Moonlight
-Undertale
-Hollowknight
-Dark Souls

Acknowledgments:
-Coding with Russ for a good base/ tutorial to jump off from
-r/Pygame for inspiration

Note: This file also contains a level editor, it is user hostile.
Keep an eye on the terminal when you run it.
The tiles with numbers are essentially pointers to background art and will
not display if on the main layer. X to show grid, WS to change levels,
AD to move around, L to increment layers.




