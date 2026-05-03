# New Super Mario Bros Wii

## Where is the options page?

The [player options page for this game](../player-options) contains all the options you need to configure and export a
config file.


## What is goal
- To beat bowsers castle at world 8
- Bowsers castle is looked behind having a number of star coin items and beaten the last level in a number of worlds. (Configurable in player yaml)
- To do this you need 2x world 8 unlock and ground pound (for 8-airship)


## Items
- Progression items
  - 17 World unlocks (are progressive, requires 2 to unlock whole world except world 9) e.g. World1, World2
  - 231 Star coins (so many star coins), used for buying hint movies, unlocking world 9 levels and bowser 
  - 6 Power-up unlocks
  - Move unlocks (needs to be unlocked before can be used)
    - button up/down/right/left
    - run
    - spin jump
    - jump
    - ground pound
    - wall jump
    - crouch
    - yoshi
    - carry
    - swim
    - p-switch
    - red-switch
    - ?-switch
    - star
    - climb ( pole, ladders, ledge and vines)
    - door
    - pipe
- Filler items
  - Inventory fill (one of every powerup)
  - 1ups
- Traps
  - Loose powerup
  - Goomba speed trap
  - Death trap


## Locations
- Completing normal levels and collecting their star coins. (77 levels and 231 star coins) e.g. 1-1_clear, 1-1_sc1
- Buying hint movies (exists 65) Check this [Gamespot article](https://gamefaqs.gamespot.com/wii/960544-new-super-mario-bros-wii/faqs/58584) if you need help with unlocking them. Hintmovie1
- Completing towers, castles and secret exits that unlock cannons ( 8 towers, 8 castles and 8 secret exits) World1_tower, Secret_exit1-3
- Getting powerups to inventory

## Options
- Starting world is selectable in option


## Known quirks
- Starting a new save plays then ending animation instead of the starting one. This is just a visual glitch, if you enter the created savefile agin it should work.
- Making savestates is currently difficult depending on location. Do not close game or make savestates when you are in peach's castle or world 9.
- For some features (death link and move rando) the game will overwrite savestate 8 in dolphin. (It does this to clear the JIT cache).
- If you have movement rando selected, you will be given some movement abilities to start out with to be able to grab your checks. You will always have button_right and either spin or big_jump.
- The client will ask for a pop-tracker pack, you can ignore it for now as it is still in development.


## Client commands
- /toogle_deathlink
  - Adds or removes the death link tag.
- /reapply_checks
  - Run this if you have not sent a level location that you have completed.
- /dev
  - A developer cheat command that is helpful for debugging features.
- /save
  - Saves some of the client memory to a file. Can be helpful to run if the client craches.
- /starcoin_count
  - Returns the amount of star coin items received.
- /completed_worlds
  - Returns the number of worlds that the game count as completed for unlocking bowsers castle.
- /kill
  - Kills mario, run this if you get softlocked.
- /refresh
  - Clears the JIT cache, run if you don't recive a move or get stuck in death loop.

## FAQ
- What is not randomized currently?
  - Levels (order), enemies, powerups, pipes
- Deathlink?
  - Deathlink is implemented. Toggel it with command in client or with setting in yaml.
- What is diffrent from vannila
  - Can't unlock canons
  - The unlocks from world 9 requies 10 starcoin items / world number  to unlock
- Multiplayer?
  - Multiplayer is currently not supported
  - You can play but only mario will be restricted to some of the unlocks
-  Tracker?
  - A basic implementation of Universal tracker, see setup_en.md for instructions. A pop tracker pack is in development.
- Where is Rivvolution patch?
  - In its current state the client does not modify the game file in any way (just editing the games live memory). This means that you do not need a mod patch.
- Why aren't star coins sent?
  - You need to complete the level
- Do you support item/location groups?
  - yes, e.g. Powerups, Movement, Hintmovies, Starcoins, Starcoins_World1, Starcoins_World1_Level1, Level_completion_world1, Level_completion
- Why are not cannons unlocked?
  - All cannons are locked and turned into locations, they can not be unlocked. Same with completing 7-6 and 8-7.
- Bugs?
  - Expect bugs, it is still in development.
  - Report a bug either at the [github](https://github.com/Miiroun/Archipelago-NewSuperMarioBrosWii/issues) or in the NSMBW thread in the [AP discord](https://discord.com/channels/731205301247803413/1327187652864380948).

## Debug tips
- Restart launcher and computer after installing if the client doesn't show up in launcher or something doesn't work.
- Make sure you are on at least archipelago 0.6.7, lastest world and game version is US rev2.
- Do not have another client open when you start client.
- Connect to the server from the client after you are on the world map in game if you have problems on the title screen.
- Try running the client commands the clear caches.
- If you can not solve your problem, run the debug launcher (found inside your archipelago directory) and send a screenshot in the nsmbw thread in the archipelago discord server.