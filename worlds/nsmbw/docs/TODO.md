## Super shortterm
- Work on movement rando
- IS_world_unlocked check is broken
- Implement item and location groups
- test wii code tools localy if they are wrong or ive implemented wrong
- fix dolphin cashing issue with existing movement (or write instructuion to say restart)


## Movement rando
- Shipp with riivolution patch??
- Add spin as check
- Set swimspeed and yoshispeed = 0
- Disable swim, Yoshi
- could also kill if touch water
- best if make statechange if tries to climb/hang / siwing
- For carry should look at the gecko code mod
- tripple jump = find check and dissable
- spin = dissable button?


## Playtest
- Playtest red switch
- test if bowser unlock does work now
  - Starcoin completion doesn't work with 0 SC 0 world comp
- Test so hintmovie 3 is unlocked
- World unlock only works on savefile2
- Deathlink receiving doesn't work
- Test so work with starcoins dissabled
- Check to see if completing castle completion still gives level completion


## Bugs to fix
- Sometimes invisible on worldmap
  - Marios animation start from back of world
- Saving to file doesnt work
- Sometimes (1/1000) random fill error
- Add fix for death on title screen
- STARCOIN LOGIC BROKEN (something wrong with new system)
- Problem with dolphi cashing instructions (move dissable)
  - Wall jump isn't reunlocked
- Freez on worldmap
- STARCOIN LOGIC BROKEN (something wrong with new system)
  - esp 6-3sc3
- Somehow messes with mini and penguin amount when not received star coins
- - World final Castle are in logic when shouldn't
- World unlock seems to be of by 1?
  - needs to fix so doesn't spot out errors
- Doesn't send castle completion check (for world 9)??
- Making castle and tower checks priority causes fill errors ca 2 out of 1000 times

## Docs update
- Documentation: better setup instructions, be extra clear around when press conect and backup save file
  - tell them to start on cleared save
- clearify that star coins are not collected until level completed
- Explain new setup and supported options
- inclued ~ location amount

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
- Yoshi
  - set yoshispeed 0
- Swim
  - set swimspeed 0




## Short term
- World map locks/unlocks doesnt work on other savefiles
- implenet starcoin setting in client
  - maybe just precollect in world
  - Pre_fil : place items: starcoins (if they are dissabled)
- Fix so traps work
- Add more options to how world 9 levels are unlocked
- Turn traps into individual options
- Option for #amount filler
- add some cashing for recived checks, so doesnt double count allready acounted for items when relogs
- Lock star as powerup
- Have yoshi and star as separate options?
- Update item and location names: ask in discord to get recommendation for names
- Change which checks are logic wise put in region 2, castle needs to be in 1
- Remove having too loop  though all checks each frame?
- For hint-movie reasons proberbly need to mark that castle levels are completed in game


## Filler link
- Have a feture that on compleation sends out filler/trap items to the MW when complete repeatable checks
- 

## Broken versions
# EU 2
- World unlocks
- is in level check
- star coin and level completed checks
- hint movies
# US 1
- Somthing doesnt work

## Tracker
- Fix ability to load external packs.
- Add auto-tabbing



## Mid term
- Implement graphics for Hintmovie shop
  - Try to change hm menu to show which movies unlocks which items 
  - Need to incluc new messages.arc and some patch code
- Create functions that are called at start/end of level instead of continuously? (to optimize code)
- Bases on death messages creat an ingame text message
- Edit color of text client
- Support different savefiles
- Skipp cutscreens
- Create option presets


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
- Disable 8-7 / make require 8-2
- Features from gecko
  - Speedtrap
  - fall damage


## Long term
- Difficult logic
- Multiplayer suport
- Non ap rando (enemy, level, entrance)
  - One of set world level / level world changes ingame level: can be used for level rando

