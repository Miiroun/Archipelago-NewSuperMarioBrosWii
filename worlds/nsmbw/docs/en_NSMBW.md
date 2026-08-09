# New Super Mario Bros Wii

## What is goal
- To beat bowsers castle at world 8
- Bowsers castle is looked behind having a number of star coin items and beaten the last level in a number of worlds. (Configurable in player yaml)


## Items
- Progression items
  - 17 World unlocks (are progressive, requires 2 to unlock whole world except world 9) e.g. World1 progressive, World2 progressive ...
  - 231 Star coins (so many star coins), used for buying hint movies, unlocking world 9 levels and bowser 
  - The amount of in game time you have to complete a level. You select in the option how many times you divide the 500 mario seconds in.
  - 6 Power-up unlocks (star counted as a move)
  - Move unlocks (needs to be unlocked before can be used) (some of these are experimental and currently locked)
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
    - !-switch
    - ?-switch
    - star
    - climb ( pole, ladders, ledge and vines)
    - door
    - pipe
    - Checkpoint
- Filler items
  - Inventory fill (one of every powerup)
  - 1ups 
  - Coin x01
  - Coin x10
  - Coin x50
  - Filler Power-up
- Traps
  - Loose powerup trap
  - Goomba speed trap
  - Death trap
  - Time trap 
  - Robbery trap
  - Shrink trap
  - Literature trap
  - Throw trap 
  - Reverse Control trap


## Locations
- Completing normal levels and collecting their star coins. (77 levels and 231 star coins) e.g. 1-1 Clear, 1-1 sc1, 2-C = 2-Castle, 3-G = 3-Ghosthouse, 4-A = 4-Airship
- Buying hint movies (exists 65) Check this [Gamespot article](https://gamefaqs.gamespot.com/wii/960544-new-super-mario-bros-wii/faqs/58584) if you need help with unlocking them. e.g. Hintmovie01
- Completing towers, castles and secret exits that unlock cannons ( 8 towers, 8 castles and 8 secret exits) World1 tower, 1-3 Secret exit
- Getting powerups to inventory (from toad-houses or enemy ambushes) e.g. Inventory_powerup_001


## Options
Options are specific to generation and are changed each multiworld, this is not a comprehensive list.
- Starting world is selectable in option
- Most locations and items can be turned on/off in options
- You can select your requirement for reaching bowser in your goal
- You can select normal or hard rules, with normal being trivial to figure out and hard REQUIRING skips and trix. 
  - Normal rules is highly recommended
- You can also select if you want brining powerups from outside the level to be considered in logic.


## Deathlink
Deathlink is supported by the client. You can either enable it from your yaml or with the client command /togle_death_link.
Deathlink groups and deathlink amnesty is also supported, you can set them in the same way.


## Settings
Settings can be found in host.yaml in the "nsmbw_settings" category and are playthrough agnostic.
They mostly include auto open, load, etc, lots of file and folder paths and others.
Among them are alternative to the keyboard library for Linux, and which slot to use for clearing cache.


## Known quirks / bugs / help with debug
- You will always start in world 1, and will have to manually move to a world that you have unlocked with the worldmap.
- Making savestates is currently difficult depending on location. Do not close game or make savestates when you are in peach's castle or world 9.
- For some features (death link and move rando) the game will overwrite savestate 8 in dolphin. (It does this to clear the JIT cache).
- If you have movement rando selected, you will be given some movement abilities to start out with to be able to grab your checks. You will always have button_right and either spin or big_jump.
- The client might ask you for a pop-tracker pack, you can ignore it for now as it is still in development.
- With movement rando on and not having the item climb will cause a soft lock if you encounter a ledge (like in 6-1). You are free from the softlock if you do /kill.
- Sometimes mario is invisible on the worldmap
- Only save file 2 will work to play on.
- Known Issues for other game versions
  - None US2: Inventory powerups
  - EU1: Movement (dont turn on)
  - US1: Star and swim movement (add these to don't rando moves if you have movement rando on)
- Don't go to the game menu with archipelago connected, this means don't use quick save in game: instead make save states.
- On Linux you will need to give the client root access for it to properly access save states
- Climb movement have issues, you can't leve vine without climb and through other ways can climb sometimes softlocks you. You solve this with the /kill command. 
- If you are connected to the game on the title screen then it will read of data in save slot 1 and might send all locations, be careful. Dont go to the main menu when you are connected to client.
- The clock might not display modified time correctly, but is accurate.
- Star item will somtimes display visually as active when not. This happens if it is not unlocked and you bring it from your inventory into a level.
- Deathlink problems:
  - If not received, try running /kill, if this does not work, make sure you have changed the dolphin settings in the set-up guide.
  - If not sending, try turing off your deathlink group and then toggle deathlink off and on again.
  - Run /deathlink_debug to get information about its current state.
- Dolphin doesn't autostart: make sure dolphin is your default program for opening iso / wbfs files
- If the client does not auto make savestates (This causes issues with deathlink, movement, etc): Make sure the dolphin settings are correct according to the set-up docs. If you use linux try switch the libraries used by changing the setting in host.yaml.


## FAQ
- What is not randomized currently?
  - Levels (order), enemies, powerups, pipes
- Deathlink?
  - Deathlink, deathlink groups and deathlink amnesty are implemented. Toggle them with command in client or with options in your yaml.
- What is different from vanilla
  - Can't unlock canons or secret exits
  - The unlocks from world 9 requires starcoin items
  - Peach's castle hint movie shop requires starcoin items
- Multiplayer?
  - You can play NSMBW multiplay 2 ways:
    1) Same-slot co-op: Both connect to the same archipelago slot separately. This entails you play seperate levels but a level completed for you get marked for your friend. Run /change_collection_level 2 for a better experience
    2) Local/Dolphin net-play: Not supported for powerups, deathlink movement rando.
-  Tracker?
  - A basic implementation of Universal tracker, see setup_en.md for instructions. A pop tracker pack is in development.
- Rivvolution patch?
  - Some settings require a riivolution patch, it should be auto generated and loaded when you first connect to the archipelago server
- Do you support item/location groups?
  - yes, e.g. Powerups, Movement, Hintmovies, Starcoins, Starcoins_World1, Starcoins_World1_Level1, Level_completion_world1, Level_completion
- Why are not cannons unlocked?
  - All cannons are locked and turned into locations, they can not be unlocked. Same with completing 7-6 and 8-7.
- Game versions
  - Game is developed on US rev2 of NSMBW. The client doesn't error out on other editions but some features will not work.
  - If you have another revision please report the problems you have in discord and mention your game revision.
- I want to help with this game, how do I start?
  - Help is appreciated, both coding, playtesting and logic. Begin by reading [dev_docs](../dev_files/dev_docs) and then ask in discord.
- Why is a level in logic?
  - Run /explain levelname and /explain_more levelname.
  - This will give you the rule for the location, you can run /movements to get a list of active movements. 
- Why does the client auto press hotkeys?
  - This is a solution to clear the JIT cache by making and loading a save state. If the specific keycombo causes issues you can change them in your game yaml and in host.yaml.
- Bugs?
  - Expect bugs, it is still in development.
  - Report a bug either at the [github](https://github.com/Miiroun/Archipelago-NewSuperMarioBrosWii/issues) or in the NSMBW thread in the [AP discord](https://discord.com/channels/731205301247803413/1327187652864380948), make sure to mention your game revision.

## Debug tips
- Restart launcher and computer after installing if the client doesn't show up in launcher or something doesn't work.
- Make sure you are on at least archipelago 0.6.7, lastest world and game version is US rev2 (and the file format is either .iso or .wbfs, .rvz will not work) and are playing on save file 2.
- If you have problem with the tracker, try updating it.
- Do not have another dolphin instance open when you start client.
- Connect to the server from the client after you are on the world map in game if you have problems on the title screen.
- Try running some client commands related to your issue.
  - If you have trouble with moves unlocking, death-link etc it probably issue with JIT_chache. The client automaticly makes savestate by pressing shirt+F8 and them F8. Make sure you have these button combos mapped to save-states in dolphoin.
- If you can not solve your problem, run the debug launcher (found inside your archipelago directory) and send a screenshot of the client in the nsmbw thread in the archipelago discord server.


## Other NSMBW modding projects
There exists two other nsmbw randomizers that I recomed looking into
- mkwcats pipe rando https://github.com/mkwcat/nsmbw-pipe-randomizer
- Hei's level rando https://hbrohei.github.io/NSMRWii/. Similar to ours but they have more features and config
- Newer Super Mario Bros Wii : the standard overhal mod https://newerteam.com/wii/. Greate recomendation if you want to try playing custom levels
- mkwcats 8 player mod https://github.com/mkwcat/nsmbw-project. For someone with friends plural and want CHAOS.
