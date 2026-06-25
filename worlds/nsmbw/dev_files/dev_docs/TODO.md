## Super short term
- do short playthrough, starting at world8, no bowser req
- fix carry shell? search where used in ghidra

## Playtest


## Bugs to fix
- Inventory item doesn't work on other versions


## Short term
- Multiplayer support
  - find other player pointers : for lives and powerups
  - Kill when in water
- Us pipe rando patches : always move next world → never
  - Look at pipe rando code for different patches : always move to next world seems useful
- fix UT-autotab
- Hint movies does not work on other save files?
- Inventory powerups only work savefile 2 : make a part of dSave pointer
- Derefrense player  pointer
- Add support for multiplayer and other savefile support
- Add enemy ambush and toad rescue
- Ask to get added to index: when doing next release
- PERSISTANTSTORAGE instead of local save file
- I have issue with fuzzing with hooks, UT and global_mutation
- Do playhtough, document completion times for time logic
- Fix so work with multiple dolphin instances (so players can have all games open at same time)



## Broken versions
# EU 1
- Movement
- Inventory

# EU 2
- Inventory

# US 1
- Inventory
- Star and water


## Mid term
- Implement graphics for Hint movie shop
  - Try to change hm menu to show which movies unlocks which items 
  - Need to include new messages.arc and some patch code
- Create functions that are called at start/end of level instead of continuously? (to optimize code)
  - Remove having to loop though all checks each frame?
- Bases on death messages create an ingame text message
- Change how world9 and peach function for better savestates : edit how worlds unlock, could try follow save address in dolphin
- make all levels unlock from start of world
- Riivolution patch that changes world map unlock order and which level required to leave
- Use persistent storage? for save file data instead of creating files?
- Implement light geck-code parsing?
- World enemies
  - exists specific memory location
- Rescue toad on world map
  - exists specific memory location
- Protocol
  - Damage-link
  - Filler link
    - Have a feature that on completion sends out filler/trap items to the MW when complete repeatable checks
- Improve level handling by actually changing the proper addresses
  - Figure out how levels are stored in memory/ how its decided which level to load
  - look into how level editors work : should play around with them
  - and search for info in dc
  - How/where is the games level / enemy info loaded : look at mod tools, figure out if can replace
  - decompile some level files, look at their structure, same with world map
- Improve JIT cache situation
  - Keyboard program causes issues with linux requiring root
  - https://github.com/randovania/py-dolphin-memory-engine/issues/10
  - create a gecko code that loads the instruction for me??
  - or just really on people turning off keybinds require focus
  - In theory I could write some PowerPC assembly that invalidates the cache internally but then I'd have to somehow make it detect external memory modifications and adapt to it. My problem with this method is to find a function to hook onto safely.
- Reenable part of climb that dissabled due to freezes
- Design icon for client : apstyle or mario head


## Difficult small bugs to fix
- Sometimes invisible on worldmap
  - Marios animation start from back of world
- Starts playing ending sequence when new file, or doesn't set start world
- Sneak freezes game
- Hint movies that requires all level completion don't work in game
- Maybe update how shell carry works
- yea so loading my state from world 4-C and then trying to switch worlds just crashes : invalid read
- DOLPHIN CONNECTION ISSUE
- game randomly freezes : inconsistent experience
- Sometimes game doesn't want to load, freezes on fade to black
- loading save state sends lots of inventory items

## Features
- Save toad / kill world enemy = hint/check
- CHEATS / Useful extra features
  - Double jump
  - Auto collect checkpoint
  - Start with powerup
  - Moon jump
- Finding toad in level gives hint
- TRAPS
  - Sandstorm
  - Darkness
  - Meteor
  - Stun / freez trap
- FILLER 
  - Gain this levels check point
- Features from gecko
  - Speed trap
  - fall damage trap


## Game patches
- Coin worlds single player
- Skipp intro cutscene
- Skipp playing hint movies when buying them
- Update world map - file
- AP-images for toad houses
- Not move forward to next world after completing previous
- allways leave level


## Long term
- Non ap rando (enemy, level, entrance)
  - One of set world level / level world changes ingame level: can be used for level rando
- Do something with coin battles?
  - Maybe have location for collecting at least % in levels, each level is an item
- Get rid of keyboard
  - Can do this by creating a instruction write wrapper that writes instruction to data and then have function in game load it instead: icbi followed by isync

## Features I (Miiroun) will not implement
- Native wii support
- Randomized ?-blocks
- Coin sanity
