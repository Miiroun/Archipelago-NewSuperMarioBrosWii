## Super short term
- test fussing on default yaml : 8 % generation failure alone 
  - problem with unittest completion
- PlayerGravity # gravity filler ?
- Just look in memory where store player data, follow intruc, find size -> multiplayer
  - dAcPy_c__data : length 0x2d08
  - daPlBase_c::GravityData
  - daPlBase_c__data
  - daPlBase_c__vt : hold func pointers
- multiplayer
  - Separate powerup unlocks?
- handle deathlink better
- Remove cost from hint movies???
  - PRO: no logic trouble, no impossible seeds
  - CON: star coins does less
  - Solution : make option so player consnets
- Search wiki for carry_block
- lose pow trap correct damage
- Add command for clearing inventory  : lower to at least 5
- I need to save modifiers so no issue when saving or loading save state
- Revise not implemented logic
- Rename movement to abilities?
- Consult with react, but spin should only be needed for 1-5 and 8-A and carry block
- Add better keyboard library support


## Playtest
- multiplayer
- deathlink amnesty
- death-trap no deathlink
- /kill no deathlink
- do complete playthrough, add spin jump and jump logic + time logic
- Deathlink group
- Playtest on linux so the root error is apparent
- test new read manifest works on frozen and linux
- Have someone with connection issues try running in administrator mode
- clear_inventory and clear_mod

## Bugs to fix
- still sends false deathlinks
- overwrite level comp ?
  - Heya! So I had an issue with save states. Everything worked fine during the first bit of an AP I did, Everything continued to work fine till this morning after about an hour of game time. For some reason my save states were automatically being loaded instead of saved, and while I did have back-up save states, I did have an issue of that messing with future aspects as all my levels I completed with star coins suddenly went uncleared. The only thing that was unlocked was secret exit paths in levels I cleared with a secret exit but couldn't get that fixed afterwards. I did use the recent version posted not long ago so i'm unsure if this was an issue on my end I could have fixed or not.
  - I had a back-up save state in Worlds 3 & 9, which were the two worlds I was focusing on and I believe the issues started after beating 9-8 or 9-3? The world 3 back-up state was only a few levels behind (like 2 or 3). However after beating like one or two levels, the game started loading a state it made itself in World 4. So whenever I tried loading the World 9 or World 3 state, things ended up breaking and even one of my back-up states got messed up as the game auto-stated the same moment I save stated. Luckily it was only one of them (I usually make two states just in case) but, yeah the issues started in world 9 but carried over even into world 3 where world 9 was never even touched on that particular state.
- Climb is locked even though it is excluded : 5 vines etc
- 1-C comp message shows when it shouldn't
- to carry anything over your head (i.e. propeller block (as pictured below), ice block (pictured mid-throw below), pow block (as pictured below), light block (as pictured below), barrel (as pictured below), or other player (as pictured below)), you need spin jump AND carry 
  - change logic
- Spin jump no logic, also no logic without normal jump
- Problem with desktop icon nsmbw? : Nsmbw desktop icon not work?
- Can't leave vine without spin jump
- Test and fix climb
- i wanted to make note of some issues i encountered while playing this apworld. i've been playing on save file 1, first on accident and later i've just been sticking to it, because the game didn't have any gamebreaking problems with that and i thought this would be good to report in case the future is to make it so you can play on the other save files. it may be hard to tell where save file 1 is causing problems though, so i'm sorry if you can't make use of all this regardless:
  - oh yea one more. on occasion there was some weird enemy AI going on. a fire bro threw its fireball to the right when it was facing the left, probably just when it was about to turn to face the other way, and a few boos were able to pursue me regardless of the direction mario was facing while climbing on a pole, enabling them to move vertically pretty fast. maybe these things were just caused by lag?
- Deathlink groups desync if reconnect to client
- Somehow accidentally sets deathlink group
- we finished our archipelago! there was one more issue i had, and this one made me cave and finally copy my save file 1 slot and switch to save file 2: inventory powerup slot checks 31-40 weren't being granted when i fulfilled their criteria. switching save file slots didn't fix it, so the host released those ten checks manually. i had 40 checks and checks 1-30 worked fine. also of note is that the issues i listed last time still occurred on save file 2. i saw all of them again except for anything about weird enemy ai. and one more: on rare occasion when playing a level, the star coin HUD element will show a star coin as collected when you haven't actually collected it yet. it tends to update itself to fix this error soon after you notice it, like when going into a pipe or beating the level


## Short term
- Multiplayer support
  - find other player pointers : for lives and powerups
  - Kill when in water
- Us pipe rando patches : always move next world → never
  - Look at pipe rando code for different patches : always move to next world seems useful
- fix UT-autotab : actually works? : needs to just update on switch and not death
- Hint movies does not work on other save files?
- Dereference player  pointer
- Add support for multiplayer and other savefile support
- Add enemy ambush and toad rescue
- PERSISTANTSTORAGE instead of local save file
- I have issue with fuzzing with hooks: UT 
- Do playthrough, document completion times for time logic
- Fix so work with multiple dolphin instances (so players can have all games open at same time)
- Inventory pow doesn't work on other save files
- toad resqu location
- toad house doesn't work to set, probably needs to update other location too
  - toad add1  80c807f0
  - toad add2  80c80f22


## Broken versions
# EU 1
- Movement

# EU 2
- Skipp intro
- Filler on other save files, in level check failing?

# US 1
- Movement broken
  - Star
  - Water
  - Spin
  - p-switch
  - Crouch
  - Walljump (slide)
  - ?-switch
- Movement works
  - Checkpoint


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
  - Trap link
  - Energy link?
  - Gifting?
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
- Fix a better way of doing hint movie logic
- Red coin sanity


## Difficult small bugs to fix
- Sometimes invisible on worldmap
  - Marios animation start from back of world
- Sneak freezes game
- Hint movies that requires all level completion don't work in game : vertify still problem
- DOLPHIN CONNECTION ISSUE
- game randomly freezes : inconsistent experience
- !switch doesnt block levels like 8-5 which are instant
- goomba patch errors when level doesn't goomba: rough write
- sometimes loading world crashes game
  - yea so loading my state from world 4-C and then trying to switch worlds just crashes : invalid read
  - ask for sead


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
  - Stun / freez trap : mario → ice block
  - Spawn enemies
  - Auto scroll
  - Speed up / slow down game clock
  - Ice physics
- FILLER 
  - Gain this levels check point
  - Get toad house (beginning of world) : toad house is in MJ..game.. files, should be easy tm
  - Insta kill all enemies
- Features from gecko
  - Speed trap
  - fall damage trap
- Make penguin progressive

## Game patches
- Coin worlds single player
- Skipp playing hint movies when buying them
- Update world map - file
- AP-images for toad houses


## Long term
- Non ap rando (enemy, level, entrance)
  - One of set world level / level world changes ingame level: can be used for level rando
- Do something with coin battles?
  - Maybe have location for collecting at least % in levels, each level is an item
- Get rid of keyboard
  - Can do this by creating a instruction write wrapper that writes instruction to data and then have function in game load it instead: icbi followed by isync
- Fix so work with multiple dolphin instances
- Add support for other mods: pipe rando, mkwcat 8player, newer (needs logic), etc
  - Needs to create new memory map (on the fly? or need to create it for all editions), would be helpful for using the memory patch with the randomizer


## Features I (Miiroun) will not implement
- Native wii support
- Randomized ?-blocks
- Coin sanity
