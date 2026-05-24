## Super short term
- Fix dying -> freeze
- Bug report /send_location not taking location groups (check if new PR does)
- compare memory of in game and menu to find difference -> better menu detection
- World enemies
  - exists specific memory location
- Rescue toad on world map
  - exists specific memory location


## Playtest
- Does fill inventory work on us rev2?
- Does 5-T show correct logic as asked by LugigiXRules
  - Powerup logic_o seams not working?
- SAVE REMOVED POWERUPS TO SLOTDATA
- test that deathlink groups and deathlink both works
- test options for world9
- Playtest star coin collect directly instead of after level completion


## Bugs to fix
- Camera is weired: might cause problems with 7-6
  - Dying in 7-6, 8-3 and 8-5 freezes game
  - might be issue with replacing save file : not correct magic number
  - watch memory if worldmap node is correct?
  - otherwise check savefile magic number
  - Seems to work kinda if clears level
  - test if still happens on minimal settings
  - Might be rough data writing: overwriting memory that I shouldn't
  - try with just world unlock
- Castle check is for airship not castle in client
- Inventory item doesn't work on other versions
- 8-t_sc2 not collected
- Something is broken with star coin generation logic
  - tracker ISSUE?


## Short term
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
- Hint movies does not work on other save files?
- Inventory powerups only work savefile 2 : make a part of dSave pointer
- Design icon for client : apstyle
- Derefrense player  pointer
- Add support for multiplayer and other savefile support
- Add enemy ambush and toad rescue
- Castles are gotten by airships since last level of world, rename them?

## Game patches
- Coin worlds single player
- Skipp intro cutscene
- Skipp playing hint movies when buying them
- Update world map - file
- AP-images for toad houses
- Not move forward to next world after completing previous
- allways leave level

## Filler link
- Have a feature that on completion sends out filler/trap items to the MW when complete repeatable checks


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
- Skipp cutscenes
- Create option presets
- Allow for filtered messages
- Change how world9 and peach function for better savestates
- make all levels unlock from start of world
- Add info to ap-wiki
- Riivolution patch that changes world map unlock order and which level required to leave
- Use data_storage for save file data instead of creating files?
- Should I check level completed in ap when connect : overwrite save file : better same slot co-op

## Difficult small bugs to fix
- Sometimes invisible on worldmap
  - Marios animation start from back of world
  - Might fix with : dMj2dGame_c
- Starts playing ending sequence when new file, or doesnt set start world
- Sneak freezes game
- 7-6 freezes when clear?, is temporarily removed
- Hint movies that requires all level completion don't work in game
- Maybe update how shell carry works

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
  - Gain this levels check point
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
