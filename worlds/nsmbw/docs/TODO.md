## Super shortterm
- Work on movement rando
  - tripple jump
  - climb : the grid from 3-c
  - hang  growing vines from 2- secret exit
  - swing vines : from 5-1
  - Sneak : 6-1
  - pow : hope discord answer
    - daLightBlock_c::powBlockActivate
    - daPowBlock_c::executeState_Shock
  - shell carry
  - titling platform as move : seaSwing ?
- Fix problem with reading external pack wrong
  - set up poptracker pack on my github
- Try flushing instruction cash from ap python -> no savestate
- Ask for playtest help: when have working moves
- Work on writing updated docs
- Remove item handled logger
- Debug why ap won't launch??
- Move tower and castle completion to correct when enters peach Castle
- Rename world item?
- Fixa have everything starcoin logic
- rework raw_rules and add new movement

## Movement rando
- Add spin as check
- best if make statechange if tries to climb/hang / siwing
- For carry should look at the gecko code mod
- tripple jump = find check and dissable
- spin = dissable button?
- p-switch
- p-switch and star should jave countdown timers
- running

## Future moves:
- pow
- run
- Maybe normal jump for super weird playthrough
- spin

## Playtest
- Playtest red switch
- test if bowser unlock does work now
  - Starcoin completion doesn't work with 0 SC 0 world comp
- Test so hintmovie 3 is unlocked
- World unlock only works on savefile2
- Deathlink receiving doesn't work
- Test so work with starcoins dissabled
- Check to see if completing castle completion still gives level completion
- Ap: playtest if hint movies unlockes correctly
- Water kills
- Test if world 9 can send items: problem with sending completion


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
- carry can carry coppa shell

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


## Important features (asked after a lot)
- World enemies
  - exists specific memory location
- Toad houses
  - could just make grafical changes and detect an increase of powerups in inventory which then is normaliced
  - or use specific pointer
- Rescue toad on world map
  - exists specific memory location
- Star power-up
- Movement
- Swim
  - set swimspeed 0




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


## Features
- Save toad / kill world enemy = hint/check
- CHEATS
  - Double jump
  - Auto collect checkpoint
  - Start with powerup
- p-switch rando
- Randomize toadhouses
- Finding toad in level gives hint
- TRAPS
  - Reverse control
  - Sandstrom
  - Shrink Trap (revert to a no-powerup state) 
  - Time Travel Trap (removes half of the level's time, or just runs it at double speed.)
  - litterature trap
  - P-switch
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
- Pipe, door, bosdor rando: Detect if player state=1 and not dead


## Long term
- Multiplayer support
- Non ap rando (enemy, level, entrance)
  - One of set world level / level world changes ingame level: can be used for level rando
- Button rando (disables buttons until unlocked)

## Features I (Miiroun) will not implement
- Consol support
- Randomized ?-blocks
