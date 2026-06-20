## Super short term
- Fix dying -> freeze
- Bug report /send_location not taking location groups (check if new PR does)
- compare memory of in game and menu to find difference → better menu detection
- World enemies
  - exists specific memory location
- Rescue toad on world map
  - exists specific memory location
- Run save on disconnect
- I think something with level completion is bugged
- Rework /save and /load to wait, print tab back, overwrite save file 7, can auto focus?
- Change logic for castle to match client
- 8-T_sc2 not sending
- Death link aren't received properly?
- Says in go mode with just 1 world 8 and other requirements
- Look at playthrough and see if that says something wrong
- Is something problematic with UT option overwrite, with types changing?: Might be with type bools
- Rework my region so each level is a separate region and connected to the next, where all are inside a larger world region
pyautogui.getWindowsWithT****itle("Dolphin")[0].activate()
- find way to auto focus window
- https://github.com/mhammond/pywin32
- Deathlink broken
- Run /load on connect
- Write some docs on how poptrackers work
- Add debug
- can't leve vine without climb
- climb sometimes softlocks you : solve this with /kill : docs 
- Add valid keys to option set
- Hur ser world castle ut i peach castle
- Save to another save state when running /save and /load
- https://github.com/randovania/py-dolphin-memory-engine/issues/10
  - create a gecko code that loads the instruction for me??
  - or just relly on people turning off keybinds require focus
- Rename world comp to castle beaten
- Message : only connect on the world map
- Ask to get added to index
- Change name off window
- Work on skipping intro cutsceen
- FAQ : why send all items
- Logic bug hint movie 12
- Only check for death when in between old states: double protection
- Send link to glossary in client: Maybe open as window?
- Add disclaimer about AI
- Rename to progressive world
- Remove worldN_tower
- Rename world_castle to worldN_completed
- Update window title with make_gui
- Add error if incompatible versions are used
- Double check defaults work for option sets : can set keys
- Set inventory powerups to last clear location on server on connect: update when new recived
- Add docs for settings
- Implement level completion  when ap location is checked (from collect or same slot co-op), make it a setting, except castles
- Implement light geck-code parsing
- Add component to slot data: "don't copy me"
- Test if send group works for other aps
- Try getting version control to work
- valid_file-extentions for settings
- AP: change how NSBMW import settings
- Ask if riivolution patch acceptable
- Look into StartGameInfo_s
- should just start using kamek, everything will be easier
- // Skip title screen movies kmWrite32(0x80781FB8, 0x60000000); kmWrite32(0x80781FBC, 0x38600000);
- Store traps when not in level
- Figure out how levels are stored in memory/ how its decisided which level to load
- Add contact me on discord if you want to work on this : want help from moder with experience
- Add disclaimer about kamek code base in dev docs
- Add a post in dc about ai
  - Disclosure: ai more clearly and newansed in credit
- Add image to client launcher
- Make collection a setting : Client command to change it
- --hook worlds.tracker.fuzzer_hook:Hook
- Fix logic??
- Find coin address for trap and filler
- Reverse control trap??
- How / where is the games level / enemy info loaded : look at mod tools, figure out if can replace
- decompile some level files, look at their structure, same with world map


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
- Jumping in wind softlooks you (2-4)
- DOLPHIN CONNECTION ISSUE
  - Re-add dolphin stats command
  - Look at other Wii games and see what they do to solve on connect
  - Lista ut hur can prints stack trace för dolphin nog connecting
  - Test what happens when try to connect when already connected
- Logic appears wrong: e.g. 4 shows in logic without swim, e.g. 1-1_sc1
  - Is it problem with tracker or game??
- Black screen like time rando with it disabled
- Climb softlocks jump in wind
- yea so loading my state from world 4-C and then trying to switch worlds just crashes : invalid read
- Closing game sends deathlink
- Bug? : if amount support received > 99 it'll send out inventory locations


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
- Allow setting AmountSupportReceived to -1 for random each time


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
