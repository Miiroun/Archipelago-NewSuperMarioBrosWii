## Super short term
- Wait on logic getting made
- -> make release
- Pin docs in dc
  - make new GitHub branch


## Playtest
- Verify bowser unlock logic wise


## Bugs to fix


## Important features (asked after a lot)
- World enemies
  - exists specific memory location
- Rescue toad on world map
  - exists specific memory location


## Short term
- Add more options to how world 9 levels are unlocked
- add some cashing for received checks, so doesn't double count already accounted for items when relogs
- Protocol
  - Grouped death-link
  - Damage-link
  - Filler link
- change to option of collects star coin on level completion or when you get them
- Multiplayer support
  - find other player pointers : for lives and powerups
  - Kill when in water
- Have a vote in discord about if riivolution patch
- Try debuging about intro cutscene : look at patch in ghidra
- Us pipe rando patches : always move next world → never
  - Look at pipe rando code for different patches : always move to next world seems useful
- fix UT-autotab
- Work on multiplayer support
- Hint movies doe not work on other save files?
- Inventory powerups only work savefile 2 : make a part of dSave pointer

## Filler link
- Have a feature that on completion sends out filler/trap items to the MW when complete repeatable checks


## Broken versions
# EU 1
- Movement


# EU 2
- 

# US 1
- 


## Mid term
- Implement graphics for Hint movie shop
  - Try to change hm menu to show which movies unlocks which items 
  - Need to include new messages.arc and some patch code
- Create functions that are called at start/end of level instead of continuously? (to optimize code)
  - Remove having to loop though all checks each frame?
- Bases on death messages create an ingame text message
- Skipp cutscenes
- Create option presets
- Allow for filtered messages
- Change how world9 and peach function for better savestates
- make all levels unlock from start of world
- Add info to ap-wiki
- Riivolution patch that changes world map unlock order and which level required to leave
- Use data_storage for save file data instead of creating files?

## Difficult small bugs to fix
- Sometimes invisible on worldmap
  - Marios animation start from back of world
  - Might fix with : dMj2dGame_c
- Starts playing ending sequence when new file, or doesnt set start world
- Sneak freezes game
- 7-6 freezes when clear?, is temporarily removed
- Hint movies that requires all level completion don't work in game


## Features
- Save toad / kill world enemy = hint/check
- CHEATS
  - Double jump
  - Auto collect checkpoint
  - Start with powerup
  - Moon jump
- Finding toad in level gives hint
- TRAPS
  - Reverse control
  - Sandstorm
  - Shrink Trap (revert to a no-powerup state) 
  - Time Travel Trap (removes half of the level's time, or just runs it at double speed.)
  - literature trap
- FILLER 
  - 1 normal coin
  - random powerup : gain
- Features from gecko
  - Speed trap
  - fall damage


## Long term
- Non ap rando (enemy, level, entrance)
  - One of set world level / level world changes ingame level: can be used for level rando
- Do something with coin battles?
  - Maybe have location for collecting at least % in levels, each level is an item

## Features I (Miiroun) will not implement
- Native wii support
- Randomized ?-blocks
- Coin sanity
