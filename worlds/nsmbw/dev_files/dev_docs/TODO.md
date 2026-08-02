# TODO 
Mention riivolution, keybindings and dolphin default program in setup guide : shorten and simplify? so people dont skipp
Finish shortcut sanity
Ask in dc for better option names
Try skip wii strap patch : see if works to not have bug
Title screen replacement
Find way to still auto start on start up if not selected riivolution
Test if loading code actully moves around memory

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
- Work on preventing sending of locations on title screen
- 8-2 secret exit requires more logic
- Hm are broken 6, 9, 55 ...
- Ask for help in dc for names
- Secret exit items in client !!!
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
- run /dev x2 and then see which hm aren't showing up : add to dont rando
- Dolphin wsl
- Beat some levels on vanilla save file 1 to verify no wrong sends are happening
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
- Use dme on intro, try finding way to not release on connect
- Can I verify dolphin settings? have been changed?
- Time change default not current
- rando  world maps, include customs
- Shuffle with custom levels (no logic)
- Edit title screen
- implement method to read arc files : needed to change names of subfolders
- stopmping on enemeies as move
- Ask about x% local filler
- Remove visibility of riivolution patch for next release, have it be a secret option
- Patch to skip wii safty
- verify that key combos dont overlap
- point to dumping guide in docs
- Another actual logic check is you can get 4-4 starcoin 1 with just penguin suit and swim, swimming at the pipe at the right angle and spamming swim allows you to bypass the the need to hit the p-switch
- Thats good to know, i just found another check i can get with wall jump or propeller in 7-ghosthouse that isn't in logic because i don't have ?-switch
- Add better way of explaining rules
- ``` Skip Wii Remote Strap Screen PAL <memory offset="0x803286C0" value="8015D0A0"/> <memory offset="0x803286CC" value="8015D010"/> <memory offset="0x803286D8" value="8015CFC0"/> ``` by CLF78
  - Does this solve issue?
- load last save state directly? : should be able to
- Pause dolphin, increment slowly: find bites in black : verify issue there not menu generally
- name: LivesLimitChange     type: patch     addr_pal: 0x80427C00     data: '000003E7' #default is 0x63 = 99    - name: LivesCharacterLimitChange     type: patch     addr_pal: 0x80159A50     data: '3882ab38' #default is 3882ab34 -> 2
- Can find value hardcoded for level timer? Add memwatch for func that changes it
  - Can make > vanilla?, would be nice
- Ask react for help invent pow
- Color pallet rando? : would be realy fun and possible?
- Maybe separate movement, rename to abilities and level_elements: move over pow, ?switch, flagpole
- Look at flagpole patch in ghirdra
- Pin message about other nsmbw randos
  - maybe create a dc pin .md
- Custom title screen? 
  - relativly easy, high reward change
- Sprite table start 	8030a340	8031ab4c
- Rando enemies: option if remove or add them
- Redirect save should be safe: yep its this line ``` <savegame external="/save/{$__gameid}{$__region}" clone="false" /> ``` this one should be fixed
  - done ?
- Try detecting dolphin settings C:\Users\Anton\AppData\Roaming\Dolphin Emulator\Config
- Rework modifiers slightly so that they don't cause issues any more
- Chance for level to be replaced by backwards version
- P-switch as locations
- Can i somehow trigger something with hitting ?-blocks?
- Make sure works with no patch
- Make debug mode a setting instead of on frozzen
- Add test not on save file 1 before sending locations
- Test manually renaming just 1 file
- Make don't rando move invisible
- Remove option page link that doesn't exist
- What happens when resync state with level comp off
- Can create level patches if desire with bsdiff4, would be easy if needed
  - if want to change logic etc
- riivolution level shuffle is backwards
  - fixed?
- starcoin_count double init
- Emulated memory override ? 
- Does glitch logic not work??
  - add test
- Separate auto start: auto save, auto close
- detect if unsupported dolphin settings are used
- Review option creator pr
- Set up way to test patcher without booting client
- Try manually renaming a tileset
- Try opening vanilla tileset with puzzle
- Edit data of pa0_jyotyu to change its color 
  - or download versions and create patch files
  - https://discord.com/channels/673369321522593794/1295786310694342691/1295786310694342691
-  btw srarcoin 1 in 1-3 is entireely possible with only mushroom by triple jumping, though it is a harder one so I see why it isn't in logic
- Shuffle sprite table? How much will explode?
- ```yaml - name: DisableGameOverItemClear   type: nop_insn   area_pal: 0x80789038 ```
  - done ?
- Publish can't move left patch in nsmbw dc
- Location scout hm
- Double jump
  - https://discord.com/channels/673369321522593794/1396386889052983307/1396386889052983307
- verify dolphin settings
  - C:\Users\Anton\AppData\Roaming\Dolphin Emulator\Config : 
    - Dolphin.ini
      - HotkeysRequireFocus = False
    - Hotkeys.ini
      Load State/Load State Slot 1 = F1
      Load State/Load State Slot 2 = F2
      Load State/Load State Slot 3 = F3
      Load State/Load State Slot 4 = F4
      Load State/Load State Slot 5 = F5
      Load State/Load State Slot 6 = F6
      Load State/Load State Slot 7 = F7
      Load State/Load State Slot 8 = F8
      Save State/Save State Slot 1 = @(Shift+F1)
      Save State/Save State Slot 2 = @(Shift+F2)
      Save State/Save State Slot 3 = @(Shift+F3)
      Save State/Save State Slot 4 = @(Shift+F4)
      Save State/Save State Slot 5 = @(Shift+F5)
      Save State/Save State Slot 6 = @(Shift+F6)
      Save State/Save State Slot 7 = @(Shift+F7)
      Save State/Save State Slot 8 = @(Shift+`F8`)
- reuse code for check point for other level elements
- remove optimiz form modifires : so doesnt causes issue at cost of performance

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
- load prev save state when loading riivolution directly instead of loading it after entering
  - test so works
- Boss health
- DisableGameOverItemClear
- Time custome rule
- allow_gen_difficult_settings
- Setting for being in debug mode instead of if frozen
- star coin multiplyer for hm


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
- 9-3 & 9-8 doesn't auto send stat coin on collect


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
- Auto download custom levels to shuffle with
  - can use some backwards levels
- Add loc for getting 100 normal coins in a level?
- Unlock enemies as items?
  - Can I block them like checkpoint?
  - options
    - start all item remove them
    - start none, trap item add enemy types
  - do this for other level parts like seesaw?


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
