## Super shortterm
- Implement world 9 and tower logic (change amount starcoins have based on if want to open or not)
- Red block
- Fix get/set levelstats
  - works for all world 3 and world 1&2 except castle and tower # might overwright castle and tower myself

\
## Playtest
- Try unlock new world
- Unlock powerups ( what happens when have powerup and get new one)
- Generate new world for testing, with 2 games
- Test new level get/set
- Experiment with hoocking up 2 game as multiworld(maybe with APquest)
- - Test deathlink (set up ap with another game)

\
## Thoguhts / decisions
- Maybe make items worth 3 starcoins and then fill upp the rest with trash? Don't want to many useless checks
- Maybe still add spin to rando
- Look at pipe rando code


\
## Bugs to fix
- Freez during startup
- crashes when shut down
- Fix launcher Gui doesnt open new
- - Add launcher ICON?
- Fix memory address of set world?
- Fix bugs when have all items
- - porberbly because doesnt properly reset jumping stuff
- Sometimes doesnt open file when tabed out

\
## Before alpha release
- Atleast RC for AP 6.7.0
- Remember to delete iso files


\
## Short term
- Understand worldnode path better (so can disable after castle / tower and secret exit)
- Find way to lock / unlock nodes on map (only works my checking/uncheking level since continus uppdate?)
- Compile and send out alpha version to playtest
- Try change hm menu
- - Look at source code, se if easy hm menu to modify (only 4 strings that are reused for each coin, not helpful)
- set upp gidha project (problem with jdk)
- Make player start in their starter world
- Make level completion real checks but preplace them
- - Make client have a save file of completed levels (so can overwrite)
- Set swimspeed and yoshispeed = 0
- Try make riivolution patch
- How do i disable walk to next world from tower and start game at world 1?
- Disable canon secret exists but make them checks
- Ask discord for help finding witch text to edit for custom names in starcoin field
- Try reading player info from player.yaml





\
## Mid term
- When game in good state, do a continuous single player play through to get a feel for the game
- Create a local savefile for client (what do need it for?)
- Implement graphics for Hintmovie shop
- colorswitch, p-switch (client and apworld)
- Create documentation for how to install
- Randomiz starting world
- Create functions that called at start/end of level instead of continuously? (to optimize code)
- Implement so that option file does something


\
## Features
- Loose powerup trap
- Add the gomba trap
- Disable unlock of final level until defeated x other worlds or have y starcoins
- Save toad / kill world enemy= hint
- Disable swim, Yoshi
- Force Mushroom generate early
- Secret exit location and logic (make so unlock send location but doesnt unlock canon)
- Make world 8 unlock generate late
- Prioritice Castle and Tower defeath to have high quality items
- Disable pipes and door


\
## Long term
- Add support for other roms
- Difficult logic
- multiplayer suport
- Diffrent savefiles
- Implement "cheats" in item pool to make easier
- Shrink Trap (revert to a no-powerup state) 
- Time Travel Trap (removes half of the levels time, or just runs it at double speed.)
- non ap rando (enemy, level, enterence)
- Expand and complete trackern
- Find GOOD memory address repository
- Work on setting up patcher (do we need one?)




