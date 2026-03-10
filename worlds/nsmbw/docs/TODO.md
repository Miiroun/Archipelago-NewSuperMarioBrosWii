## Super shortterm
- fix deathlink
- Kill player if not in allowed world, skip deathlink
- Read location doc to find commands like for early / late items
  - placed_locked_item
- For killing ask ai again
- For death link in pipe: find player life counter: could probably check on_worldmap / worldmap_postion
  - For killing ask ai again
- Simplify item and location name

## Playtest
- Unlock powerups (what happens when have powerup and get new one)
  - doesn't work
- Test if savefile works
- Receive deathlink
- Playtest red switch



## Thoughts / decisions
- Maybe make items worth 3 starcoins and then fill up the rest with trash? Don't want too many useless checks
- Why do I get bounded packets like every 30 sec? probably nothing to worry about
- Could make most starcoins local



## Bugs to fix
- Send world 1-1 starcoins on load
  - problem self.status
- deathlink trigger when in pipe
- Sometimes invisible on worldmap
- World unlock only works on savefile2
- Code can't kill player
- Only groundpound as move is locked
- Mario's animation starts from back of world
- Unlock new move/powerup requires restart client
- Peach's castle doesn't set powerup



## Short term
- Compile and send out alpha version to playtest
- Set up gidha project (problem with jdk)
- Make player start in their starter world
- Make level completion real checks but preplace them
  - probably shouldn't do or ok if not added to item pool?
    - Make client have a save file of completed levels (so can overwrite)
- Set swimspeed and yoshispeed = 0
- Ask discord for help finding which text to edit for custom names in starcoin field
- Fix how levels are organized so that if levels parallel logic doesn't require earlier
- Add spin as check
- Fix other movement randos
- Update self.connectionstatus to be more accurate


Tracker
- Set map page index to autoupdate depending on area
- Add images for power ups and moves
- Set up counter for # starcoins recived
- Make show list avalibe starcoins / level






## Mid term
- When game in good state, do a continuous single player play through to get a feel for the game
- Implement graphics for Hintmovie shop
- Create documentation for how to install
- Randomize starting world
- Create functions that are called at start/end of level instead of continuously? (to optimize code)
- Implement so that option file does something
- Found where to add ctx.username = yaml\[playername\]
- Try to change hm menu to show which movies unlocks which items 
  - Look at source code, se if easy hm menu to modify (only 4 strings that are reused for each coin, not helpful)
- Get playtest data on what doesn't work on eu version

## Features
- Disable unlock of final level until defeated x other worlds or have y starcoins
- Save toad / kill world enemy = hint
- Disable swim, Yoshi
- Force Mushroom to generate early
- Secret exit location and logic (make so unlock send location but doesn't unlock canon)
- Prioritise Castle and Tower defeat to have high quality items
- Disable pipes and doors
- Read player info from player.yaml
- Setting for rom file path and if should auto open / close
- CHEATS
  - Double jump
  - Auto collect checkpoint
  - Start with powerup
- Option to make # of worlds / all worlds beaten to be able to access bowser
- p-switch rando
- Randomize toadhouses
- Finding toad in level gives hint
- TRAPS
  - Lose current powerup
  - Add the goomba trap
  - Lose powerup in inventory
- Disable 8-7 / make require 8-2

## Enging
- Write gecko code parser
- Write powerpc parser
- Features from gecko
  - Speedtrap
  - fall damage
- make it load from symbols in address map


## Long term
- Add support for other roms
- Difficult logic
- Multiplayer suport
- Different savefiles
- Implement "cheats" in item pool to make easier
- Shrink Trap (revert to a no-powerup state) 
- Time Travel Trap (removes half of the level's time, or just runs it at double speed.)
- Non ap rando (enemy, level, entrance)
- Expand and complete tracker
- Find GOOD memory address repository
- Work on setting up patcher (do we need one?)
