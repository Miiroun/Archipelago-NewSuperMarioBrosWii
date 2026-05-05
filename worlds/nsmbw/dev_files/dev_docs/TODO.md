## Super short term
- Pin docs in dc
- Wait on logic getting made
- Playtest
- -> make release
- Add info to ap-wiki
- Change starting world into a choice instead of range


## Playtest
- Playtest red switch
- test if bowser unlock does work now
- Test so hint movie 3 is unlocked
- Check to see if completing castle completion still gives level completion
- Ap: playtest if hint movies unlocks correctly
- Test if world 9 can send items: problem with sending completion
- test so completing castle sends its check
- Test world 9 sends level completion
- Playtest so hint movies work correctly
- Double check so bowser unlock works correctly
- Test that generation time is reasonable
- test if rocket pipe is disabled
- Playtest so powerups from toad houses are checks
- Test hint movies unlock correctly from castles / towers
- Death link
- Does direction-lock impact world map?


## Bugs to fix
- Sometimes invisible on worldmap
  - Marios animation start from back of world
- Starts playing ending sequence when new file
- World unlock only works on savefile2, same with goal completion
- sends death link on connect
- Sneak freezes game
- 7-6 freezes when clear?


## Important features (asked after a lot)
- World enemies
  - exists specific memory location
- Rescue toad on world map
  - exists specific memory location

  
## Short term
- World map locks/unlocks doesn't work on other savefiles
- Add more options to how world 9 levels are unlocked
- Turn traps into individual options : set that starts filled out
- Option for #amount filler
- add some cashing for received checks, so doesn't double count already accounted for items when relogs
- Try to get EU conversion to work
- Add unit test
- UT
  - Auto tabbing
- Protocol
  - Grouped death-link
  - Damage-link
  - Filler link


## Filler link
- Have a feature that on completion sends out filler/trap items to the MW when complete repeatable checks


## Broken versions
# EU 2
- World unlocks
- is in level check
- star coin and level completed checks
- hint movies
# US 1
- Somthing doesnt work


## Mid term
- Implement graphics for Hint movie shop
  - Try to change hm menu to show which movies unlocks which items 
  - Need to include new messages.arc and some patch code
- Create functions that are called at start/end of level instead of continuously? (to optimize code)
- Bases on death messages creat an ingame text message
- Support different savefiles
- Skipp cutscenes
- Create option presets
- Remove having to loop  though all checks each frame?
- Allow for filtered messages
- Change how world9 and peach function for better savestates
- make all levels unlock from start of world
- create unit test for logic

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
  - Death trap
- FILLER 
  - 1 normal coin
  - random powerup : gain
  - short amount star power
- Features from gecko
  - Speed trap
  - fall damage


## Long term
- Multiplayer support
- Non ap rando (enemy, level, entrance)
  - One of set world level / level world changes ingame level: can be used for level rando
- Do something with coin battles?

## Features I (Miiroun) will not implement
- Consol support
- Randomized ?-blocks
- Coin sanity
