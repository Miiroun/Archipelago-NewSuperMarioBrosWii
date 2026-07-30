# TODO 
Mention riivolution, keybindings and dolphin default program

## Super short term
- PlayerGravity # gravity filler ?
- Just look in memory where store player data, follow intruc, find size -> multiplayer
  - dAcPy_c__data : length 0x2d08
  - daPlBase_c::GravityData
  - daPlBase_c__data
  - daPlBase_c__vt : hold func pointers
- multiplayer
  - Separate powerup unlocks?
- Rename:
  - movement to abilities?
  - dontrandomoves to default moves?
  - include option to sanity?
- update docs
- button_down and button_up and pipe logic
- request channel
- Secret exit items
  - client
    - read from data
    - reunlock when got
  - update docs
  - fix option validation
  - add thing if they aren't enabled
  - run visulaize to verify regions are correct
- Command to repromt game file?
- Can create riivolution patch and auto extract using dolphin tools
- create an function to  and bytes
- Run checks to not auto save in peach castle or world9
- Ask AP-world dev for x% of filler should be local option
- Rando game tile sheet, enemy sheet, music etc. Easiest done through riivolution
- Deathlink Amnesty incorrect, not ressetting
- Suggestion: make local_items take an amount
- Try redumping my copy of nsmbw : test which guide / method best to link to
- 2-2sc1 & sc2
- 1-C sc3
- Why is deathlink group displayed as wrong??
- Hintmovie sanity?
- Add command to repromt for a new game file: Check if file exists etc : otherwise repromt
- Ask for help in dc for names
- technically can do without riivolution path, but is nice if anyone want to launch it themselvs
- Starcoin multiplier for hint movies
  - backcomp
- Work on preventing sending of locations on title screen
- 8-2 secret exit requires more logic
- Hm are broken 6, 9, 55 ...
- Ask for help in dc for names
- Secret exit items in client !!!
- Setting to allow gen with > 100 inv pow 
- Hm option: cumulative but order is sorted after hm unlock order
- Run language test world thing
- Work more on map pack: download images from wiki
- do I need to split up doolphin tool and dolphin for linux users?
- Current issue seems to be
- look into hint movies
  - look up hint movie prossessing in ghidra
- Other shuffles?
  - enterence
  - enemy
  - background
  - text
  - object
  - characters?
- Add riivolution info to docs
- Add logic to level rando
- test if loading code actually fails the client
- Don't run gen when not connected
- run /dev x2 and then see which hm aren't showing up
- need to hardcode bowser logic to rules instead of in raw, because dont want it to move
- Dolphin wsl
- Separate dolphin tools setting for Linux
- Turn on dolphin close confirmation
- Beat some levels on vanilla save file 1 to verify no wrong sends are happening
- Doolphintool -h
- Reword timer modifier option
- on_progressive should req that powerup and super mushrom are both received while on should depend on outside powerups
- Make Clear cache f key be setting
- Put disclaimer that collect SC immediately doesn't impact logic
- NSMBW version in window title
- Hm 5 probably not a problem
- Try sending !-switch
- Remove comment above check sc in level
- Deleate main branch (again)
- Deathlink: if in level ()
- Add setting to which save file to continuously save/load from
- Docs mention no changes dolphin setting or keybind
- If unlocked set red switch to on
- Hm in peach castle is not correct amount on free, should remove req of having sc
- Remove req for cost of having X HM on other settings
- need rules for when not to unlock inventory pow: either beat 1-3 (toad), have access to world enemys, or door + climb + toadhouse
- Add key binds to docs
- Location scout hm: give as hint, as an option
  - Could maybe change name of hm based on if priority / useful / filler
- Create bash script for: generate, host, open client with connection args
- Use dme on intro, try finding way to not release on connect
- Can I verify dolphin settings? have been changed?
- Time change default not current
- rando  world maps, include customs
- Shuffle with custom levels (no logic)
- Time custome rule
- Auto download custom levels
- Edit title screen
- implement method to read arc files : needed to change names of subfolders
- Randomize boz Heath : start 10, go down by one for each of 9 nine items
- stopmping on enemeies as move
- Add loc for getting 100 normal coins in a level?
- Ask about x% local filler
- Remove visibility of riivolution patch for next release, have it be a secret option
- Patch to skip wii safty
- Patch to relocate external save file
- verify that key combos dont overlap
- point to dumping guide in docs

## Playtest
- multiplayer
- deathlink amnesty
- do complete playthrough, add spin jump and jump logic + time logic
- Deathlink group
- Playtest on linux so the root error is apparent
- test new read manifest works on frozen and linux
- Have someone with connection issues try running in administrator mode
- test hm options
- playtest so deathlink amnesty and groups works
- try settig settings to 2
- Playtest with code loading, Whats different and if something works
- Change default savestate button
- command changing saveslot and clearcache slot
- get_time

## Bugs to fix
- overwrite level comp ?
  - Heya! So I had an issue with save states. Everything worked fine during the first bit of an AP I did, Everything continued to work fine till this morning after about an hour of game time. For some reason my save states were automatically being loaded instead of saved, and while I did have back-up save states, I did have an issue of that messing with future aspects as all my levels I completed with star coins suddenly went uncleared. The only thing that was unlocked was secret exit paths in levels I cleared with a secret exit but couldn't get that fixed afterwards. I did use the recent version posted not long ago so i'm unsure if this was an issue on my end I could have fixed or not.
  - I had a back-up save state in Worlds 3 & 9, which were the two worlds I was focusing on and I believe the issues started after beating 9-8 or 9-3? The world 3 back-up state was only a few levels behind (like 2 or 3). However after beating like one or two levels, the game started loading a state it made itself in World 4. So whenever I tried loading the World 9 or World 3 state, things ended up breaking and even one of my back-up states got messed up as the game auto-stated the same moment I save stated. Luckily it was only one of them (I usually make two states just in case) but, yeah the issues started in world 9 but carried over even into world 3 where world 9 was never even touched on that particular state.
- Can't leave vine without spin jump
  - rework climb
- i wanted to make note of some issues i encountered while playing this apworld. i've been playing on save file 1, first on accident and later i've just been sticking to it, because the game didn't have any gamebreaking problems with that and i thought this would be good to report in case the future is to make it so you can play on the other save files. it may be hard to tell where save file 1 is causing problems though, so i'm sorry if you can't make use of all this regardless:
  - oh yea one more. on occasion there was some weird enemy AI going on. a fire bro threw its fireball to the right when it was facing the left, probably just when it was about to turn to face the other way, and a few boos were able to pursue me regardless of the direction mario was facing while climbing on a pole, enabling them to move vertically pretty fast. maybe these things were just caused by lag?
  - enemy AI being weird
- ?switch doesnt disable, is permanently on
- HM5 : all hm requring castle comp
  - might be problem with patch for skipping world unlocks
- Som hm req cannon comp
- Other errors i noticed, 4-1 star coin is collectable with just carry by picking up the koopashell on the little bit of land with the red ring, once i got the propeller mushroom for what i had unlocked, 1-1 star coin 2 and 4-1 starcoin 2 can both be collected with just propeller, and 7-3 starcoin 2 can be collected with climb and propeller,  (i forgot to look if it was in logic before grabbing it, but you can also get 1-castle starcoin 3 with propeller and no p-switch) also hint movie 06 is unobtainable until the game registers 1-tower is completed, meaning it can't be collected until the second progression of world 1 is collected (not entirely sure what progress on hint movies are though, I've had some hint movies pop up and not be in logic, and still haven't been able to get hint movie 09 to show up despite being in logic, though i know the hint movies are weird to get so that might be user error)
  - the 1-1_sc2 cannot be replicated with their yaml
- you could also prevent locking yourself out of things by making the shop need you to have the currency, but not actually take it away and instead modify the prices to have some order to the actual shop items
- 6-4 sc1 logic wrong?
- 6-3 quest switch doesn't work ?
- 4-G ice flower?
- Fix inventory pow on other savefiles
- Starcoin invent not sending, of by 1, just remove the -1, verify it works
- Add command to chage which save slot to use for option
- Why doesnt launcher componenet work while running from source
- try loading code patch with riivolution
- sends everything when fades to black
- All backgrounds are dark
  - need to modify internal of the .arc file
- Issue with running with an .iso file



## Short term
- Multiplayer support
  - find other player pointers : for lives and powerups
  - Kill when in water
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
- toad rescue location
- toad house doesn't work to set, probably needs to update other location too
  - toad add1  80c807f0
  - toad add2  80c80f22
- Spin jump no logic, also no logic without normal jump
- flagpool score as location?
- Create notes in /explain more
- Make secret exit items to reunlock them
- assert early items are actually early, write test?
- Figure out how to change HM unlock condition?
- Work on UT tracker pack
  - After 0.3.0, other things are higher priority

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
- Red coin sanity
- Fix local_filler to not be early

- Nice PR: https://github.com/Silvris/Archipelago/blob/docs_viewer/worlds/docs_viewer/client.py#L23

## ER
- Create logic https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/entrance%20randomization.md**
  - design new system
    - needs named tuple
  - have each entrance or subarea be its own region
  - convert old logic to new logic
  - separate pipes, doors etc into their own category
- World
  - implement er from docs
  - send it in slot_data
- Client
  - read and convert slot_data
  - Randomize pipes, doors, other transitions
  - Starting on world map

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
- 1-C comp message shows when it shouldn't
- still sends false deathlinks
- inventory_pow desyncing
- Entering 8-A boss without ground pound freezes game
- something is making locations missing from tracker

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
- Actual deathlink messages

## Features I (Miiroun) will not implement
- Native wii support
- Randomized ?-blocks
- Coin sanity
