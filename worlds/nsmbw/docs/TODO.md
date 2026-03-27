## Super shortterm
- Send playtest message in dc after bugfix
- Turn SC into evenitems if dissabled
- World set is diffrent depending savefile


## Playtest
- Unlock powerups (what happens when have powerup and get new one)
  - doesn't work
  - If new powerupcode works ( progresion and big mario if not unlocked)
- Receive deathlink
- Playtest red switch


## Bugs to fix
- deathlink trigger when in pipe
- Sometimes invisible on worldmap
- Marios animation start from back of world
- Unlock new move/powerup requires restart client
  - Somthing problemtic, also with unlock_everything?
  - Think problem with how i run my commands: makes program crash
- World map locks/unlocks doesnt work on other savefiles
  - World unlock only works on savefile2
- Some in level code runs on start menu, needs better check if client connected
  - Send world 1-1 starcoins on load
  - problem self.status
- - fix so powerup correspond correctly against name of unlock
- Grabing powerup as small mario sets you small not big
- Powerup rando doesnt work on EU, what does?
- For death link in pipe: find player life counter: could probably check on_worldmap / worldmap_postion

## From playtest
- Hint movies doesn't send checks or show as unlocked
- Gamestate: in level
- Confused tower, castle and fortress??
- Change the flag that checks which world you are in for world 9, doesn't work
- Deathlink sends death when shouldn't: when entering or leaving level
- Add level requirements for hint movies
- Make progressive powerup be a yaml option
- Do ap-test for all options
- pack all of options in storge
-  create code that reads the version from the manifest


## Short term
- Make player start in their starter world
- Make level completion real checks but preplace them
  - probably shouldn't do or ok if not added to item pool?
    - Make client have a save file of completed levels (so can overwrite)
- Set swimspeed and yoshispeed = 0
- Ask discord for help finding which text to edit for custom names in starcoin field
- Fix so automaticaly add to host.yaml
- Kamek
- Add spin as check
- Fix other movement randos


## Tracker
- Set map page index to autoupdate depending on area
- Add images for power ups and moves
- Set up counter for # starcoins recived
- Make show list avalibe starcoins / level
- Make poptracker images into different files




## Mid term
- Implement graphics for Hintmovie shop
  - Try to change hm menu to show which movies unlocks which items 
  - Need to incluc new messages.arc and some patch code
- Create functions that are called at start/end of level instead of continuously? (to optimize code)
- Bases on death messages creat an ingame text message
- Do fuzzer test to see if options work
- Edit color of text client





## Features
- Disable unlock of final level until defeated x other worlds or have y starcoins
- Save toad / kill world enemy = hint
- Disable swim, Yoshi
- Setting for rom file path and if should auto open / close
- CHEATS
  - Double jump
  - Auto collect checkpoint
  - Start with powerup
- p-switch rando
- Randomize toadhouses
- Finding toad in level gives hint
- TRAPS
  - Add the goomba trap
- Disable 8-7 / make require 8-2
- Features from gecko
  - Speedtrap
  - fall damage

## Long term
- Add support for other roms
- Difficult logic
- Multiplayer suport
- Different savefiles
- Implement "cheats" in item pool to make easier
- Shrink Trap (revert to a no-powerup state) 
- Time Travel Trap (removes half of the level's time, or just runs it at double speed.)
- Non ap rando (enemy, level, entrance)
  - One of set world level / level world changes ingame level: can be used for level rando
- Expand and complete tracker
- Work on setting up patcher (do we need one?)
