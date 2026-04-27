## Super short term
- Work on movement rando
  - work on fence : search chain ghidra
  - update ?-switch
    - use memory watch to find whitch function sets it
    - try searching for pointer with correct memory address 0x811B452A, on US rev2
  - update sneak
    - set speeds to 0
  - search dAcPy_c & Snake
  - Hang action
- Fix problem with reading external pack wrong
  - set up poptracker pack on my github
- Try flushing instruction cash from ap python -> no savestate
- Ask for playtest help: when have working moves
- Work on writing updated docs
- Remove item handled logger
- Move tower and castle completion to correct when enters peach Castle
- Rename world item?
- Fix have everything starcoin logic : or make it at least deprioritesed 
- Implement code feedback
- Double check star coins logic works correctly
- UT yamless
- Clarify tacker= UT : in docs
- make levels unlock from start of world
- Add warring if playing on other savefile
- add items for geting powerups to inventory
- fix so levels are completed in peach castle
- Maybe add manual movement
- Inform manager of bad manifest


## Playtest
- Playtest red switch
- test if bowser unlock does work now
  - Starcoin completion doesn't work with 0 SC 0 world comp
- Test so hintmovie 3 is unlocked
- Deathlink receiving doesn't work
- Test so work with starcoins dissabled
- Check to see if completing castle completion still gives level completion
- Ap: playtest if hint movies unlockes correctly
- Test if world 9 can send items: problem with sending completion
- test so completing castle sends its check
- Test world 9 sends level completion
- Playtest so hint movies work correctly
- Doublecheck so bowser unlock works correctly
- Test that generation time is reasonable
- Does it work to connect to a EU version?
- test if rocket pipe is disabled
- Check p-switch works all levels
- CHeck so all movments are dissabled


## Bugs to fix
- Sometimes invisible on worldmap
  - Marios animation start from back of world
- Saving to file doesnt work
- Sometimes (1/1000) random fill error
  - fuzzer fails ca 0.5% of times
- Problem with dolphi cashing instructions (move dissable)
  - Wall jump isn't reunlocked
- Freez on worldmap
- Somehow messes with mini and penguin amount when not received star coins
- Making castle and tower checks priority causes fill errors ca 2 out of 1000 times
- Starts playing ending sequence when new file
- loading secret exist from 1-3 freezes game
- World unlock only works on savefile2
- bug that requires me to beat tower/castle levels twice for level progression?
- Debug why ap won't launch??
- ?-dissable donsnt work on 8-4 or 2-2, proberbly only works on 6-3, vill proberbly have to manuly check all levels
- Something doesnt work with creating a new file
- sends death link on connect
- Somehow starting world doesnt work correctly?
- First yellow pipe in world7 doesnt work

## Docs update
- Documentation: better setup instructions, be extra clear around when press conect and backup save file
  - tell them to start on cleared save
- clearify that star coins are not collected until level completed
- Explain new setup and supported options
- inclued ~ location amount
- trubelshooting tips
  - Name debug launcher in pins and GitHub
  - restart launcher, computer
  - savefile 2, us rev2
  - dont have dolphin open
- refer to optioncreator from setup guide
- link to UT
- Add location amount to options and docs
- Call out 1-7 1-8 in docs
- Add to docs: don't savestate in peach Castle or world 9
- Docs: add list item& location names


## Important features (asked after a lot)
- World enemies
  - exists specific memory location
- Toad houses
  - could just make grafical changes and detect an increase of powerups in inventory which then is normaliced
  - or use specific pointer
- Rescue toad on world map
  - exists specific memory location



## Short term
- World map locks/unlocks doesnt work on other savefiles
- Fix so traps work
- Add more options to how world 9 levels are unlocked
- Turn traps into individual options
- Option for #amount filler
- add some cashing for recived checks, so doesnt double count allready acounted for items when relogs
- Lock star as powerup
- Have yoshi and star as separate options?
- Update item and location names: ask in discord to get recommendation for names
- For hint-movie reasons proberbly need to mark that castle levels are completed in game
- Try to get EU conversion to work

## Filler link
- Have a feture that on compleation sends out filler/trap items to the MW when complete repeatable checks

## Broken versions
# EU 2
- World unlocks
- is in level check
- star coin and level completed checks
- hint movies
# US 1
- Somthing doesnt work


## Tracker
- Add auto-tabbing



## Mid term
- Implement graphics for Hintmovie shop
  - Try to change hm menu to show which movies unlocks which items 
  - Need to incluc new messages.arc and some patch code
- Create functions that are called at start/end of level instead of continuously? (to optimize code)
- Bases on death messages creat an ingame text message
- Support different savefiles
- Skipp cutscenes
- Create option presets
- Remove having to loop  though all checks each frame?
- Convert memory patches to riivolution
- Support none windows
- Allow for filtered messages
- Change how world9 and peach function for better savestates


## Features
- Save toad / kill world enemy = hint/check
- CHEATS
  - Double jump
  - Auto collect checkpoint
  - Start with powerup
  - Moon jump
- Randomize toadhouses
- Finding toad in level gives hint
- TRAPS
  - Reverse control
  - Sandstrom
  - Shrink Trap (revert to a no-powerup state) 
  - Time Travel Trap (removes half of the level's time, or just runs it at double speed.)
  - litterature trap
  - P-switch
  - Death trap
- FILLER 
  - 1 normal coin
  - star timer 
  - yoshi : appears
  - random powerup : gain
  - short amount star power
- Disable 8-7 / make require 8-2
- Features from gecko
  - Speedtrap
  - fall damage
- Pipe rando : pipes as unlockable item
- Movement
  - Se items for unimplemented changes

## Long term
- Multiplayer support
- Non ap rando (enemy, level, entrance)
  - One of set world level / level world changes ingame level: can be used for level rando
- Button rando (disables buttons until unlocked)
- Do something with coin battles?

## Features I (Miiroun) will not implement
- Consol support
- Randomized ?-blocks
- Coin sanity
