# TODO 
## Release TODO
- bug fixes to work out
- documentation to update
- option descriptio
- lots of play testing to do.

## Super super short term
Write desciptions for options

Mention riivolution, keybindings and dolphin default program in setup guide : shorten and simplify? so people dont skipp

DC
- option + setting review

FIX generation and client bugs
test
- gravity

- Secret exit items
  - update docs / options

Faster timer countdown speed
kmWrite32(0x800e3ab8, 0x3403fe90);  // 92 -> 368
origin? works? : replace time trap with this

Send yaml for help


Change starting world : ask for help in discord

Edit star coin level icon : new image

try Gen a patch file for sc model : if much smaller use it

WANT TO FIX WORLD 9 FOR NEXT VERSION : SEPARATE PER LEVEL SEEMS HARD BUT COULD MAYBE CREATE AN EASY PATCH THAT JUST UNLOCKS ALL BY DEFAULT
DONT WANT IT THIS BROKEN FOR NEXT VERSION
playtest : disable_world9_sc_req
- remove option for player to decide


Look spoiler log with topology_present


Clean up dev files : remove from repo?
- Clean up git ripo

patch function that checks if level is unlocked

bool dWmConnect_c::GetConnect at 800f3380 might allow me to not override tower completion and have all levels unlocked from start

why all hm in logic?

fix carry shell patch

remove star from inventory is bugged

## Super short term
- Add riivolution info to docs
- Dolphin wsl
- Beat some levels on vanilla save file 1 to verify no wrong sends are happening
- Reword timer modifier option
- on_progressive should req that powerup and super mushrom are both received while on should depend on outside powerups
- Time change default not current
- implement method to read arc files : needed to change names of subfolders
- verify that key combos dont overlap
- Another actual logic check is you can get 4-4 starcoin 1 with just penguin suit and swim, swimming at the pipe at the right angle and spamming swim allows you to bypass the the need to hit the p-switch
- Thats good to know, i just found another check i can get with wall jump or propeller in 7-ghosthouse that isn't in logic because i don't have ?-switch
- Can find value hardcoded for level timer? Add memwatch for func that changes it
  - Can make > vanilla?, would be nice
- Sprite table start 	8030a340	8031ab4c
- Rando enemies: option if remove or add them
- Rework modifiers slightly so that they don't cause issues any more
- What happens when resync state with level comp off
- Separate auto start: auto save, auto close
- detect if unsupported dolphin settings are used
- Review option creator pr
- Try manually renaming a tileset
- Try opening vanilla tileset with puzzle
- Edit data of pa0_jyotyu to change its color 
  - or download versions and create patch files
  - https://discord.com/channels/673369321522593794/1295786310694342691/1295786310694342691
-  btw srarcoin 1 in 1-3 is entireely possible with only mushroom by triple jumping, though it is a harder one so I see why it isn't in logic
- Shuffle sprite table? How much will explode?
- Publish can't move left patch in nsmbw dc
- remove optimiz form modifires : so doesnt causes issue at cost of performance
- have option to rando towers and airshipps in their own pool
- Rework modifiers so issue doesn't happen
- Add assert if save slots overlap
- option to shuffle only towers within themselves
- Rework setup guide with auto launch disabled : if turned off riivolution, move to game info
- have randomize time increase speed instead of setting clock??
- Auto close dolphin doesn't work on Linux
- Add if game over : resync state to docs
- Save on disconnect
- Don't send loc on savefile 1
- Improve dolphin error more
  - Give debug tips in list
  - Print as list
- Shuffle in coin and battle stages into main levels
- Improve how swim locks
  - Improve error messages
- Write to GameFlag_e?
  - enable debug things etc
- Don't allow lives and powerups to be maxed out
- Add local multiplayer to docs
- Match server state it might be nice to have this automatically done after every death/level complettion/etc if possible
- Make early items an option
- !MANUAL BACKGROUND RENAME WORKS!



## Playtest
- multiplayer
- do complete playthrough, add spin jump and jump logic + time logic
- Deathlink group
- Playtest on linux so the root error is apparent
- test new read manifest works on frozen and linux
- test hm options
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
- Does time rando work??
- reprompt_gamefile
- Ydotool
- patch not need watching hint movies
- Shortcuts
- Location scout hm
- q-switch
- Try skip wii strap patch : see if works to not have bug
  - does not work on US rev2, atleast
- Playtest secret exits
- Cap inven pow at 96
- Test speed trap
- Playtest jit clear replacement
- Work more on map pack:
  - download images from wiki
  - Create own illustations of unlocks for itemtracker
- filename of new extracter
- p and q switch patch
- goomba lock doesnt work
- button_down and button_up and pipe logic
- Star invent not sending, of by 1, just remove the -1, verify it works
- start with all hm hinterd
- level shuffle has proper logic
- inventory star removal


## Bugs to fix
- Can't leave vine without spin jump
  - rework climb
- i wanted to make note of some issues i encountered while playing this apworld. i've been playing on save file 1, first on accident and later i've just been sticking to it, because the game didn't have any gamebreaking problems with that and i thought this would be good to report in case the future is to make it so you can play on the other save files. it may be hard to tell where save file 1 is causing problems though, so i'm sorry if you can't make use of all this regardless:
  - oh yea one more. on occasion there was some weird enemy AI going on. a fire bro threw its fireball to the right when it was facing the left, probably just when it was about to turn to face the other way, and a few boos were able to pursue me regardless of the direction mario was facing while climbing on a pole, enabling them to move vertically pretty fast. maybe these things were just caused by lag?
  - enemy AI being weird
- ?switch doesnt disable, is permanently on
- HM5 : all hm requring castle comp
  - might be problem with patch for skipping world unlocks
- Som hm req cannon comp
- Fix inventory pow on other savefiles
- Add command to chage which save slot to use for option
- Why doesnt launcher componenet work while running from source
- try loading code patch with riivolution
- sends everything when fades to black
- All backgrounds are dark
  - need to modify internal of the .arc file
- 9-3 & 9-8 doesn't auto send stat coin on collect
- This isn't a priority so you can focus on it later, but here's an error that was produced after running the command ```Traceback (most recent call last):   File "MultiServer.py", line 1350, in __call__   File "C:\ProgramData\Archipelago\custom_worlds\tracker.apworld\tracker\TrackerClient.py", line 250, in _cmd_explain     explain(self.ctx, lookup_name)     ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^   File "C:\ProgramData\Archipelago\custom_worlds\tracker.apworld\tracker\TrackerClient.py", line 1512, in explain     dest_id = current_world.location_name_to_id[dest_name]               ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^ KeyError: '9-1'```
  - Do I not add event locations to world 9??
- Still disconnect error
- force_hook : assert connected
- exit course sometimes send death
- 2-2sc1 & sc2
- 1-C sc3
- World 9 not properly reset when dying
  - Looks like after a death in 9-3 exclusively the default state of World 9 is stored I've died in other World 9 levels without the World being set like this
  - Entering the level was possible while the circle was solid black, and the clear/sc checks were sent out properly when the level was completed 
  - However, the world state was not reset (level clear saw the same situation as the screenshot), and I switched worlds and came back to be able to do other levels
- Is tracker 0.3.3 broken? for 0.2.1 5-1 ??
- Loose powerup should put to super if small
- 9-3 bugged, sends location
- star works if gotten from menu



## Short term
- fix UT-autotab : actually works? : needs to just update on switch and not death
- Hint movies does not work on other save files?
- Dereference player  pointer
- Add support for other savefile
- Add enemy ambush and toad rescue
- I have issue with fuzzing with hooks: UT 
- Do playthrough, document completion times for time logic
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
- request channel in ap-dc
- change starting world 
- AFTER JIT clear have proven to work : make post in AP-mod thread about it
- To-do:  prompt to watch hint movie
- Need spin to get off vine and yoshi
- look up hint movie prossessing in ghidra
- shuffle coin and battle levels with normals
- add 1ups as locations to world : needs option : keep secret until logic
- Look in regi for sand storm and meteor : see if is just an easy flag to change?
- look for doStateChange
  - can improve climb and swim
- 



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
- Suggestion: make local_items take an amount
- Ask AP-world dev for x% of filler should be local option
  - Ask about x% local filler
- locations for simple things ? 100 coins, top of flagpole, 100 lives, 100 inventory pow, etc ?
- P-switch as locations
- 8005e4c0 holds trigger A function, might be able to hijack to send death nice?
- Kamek patch to detect if ap is connected
- Hm option: cumulative but order is sorted after hm unlock order
- Is there a way in game to see how many worlds you need to complete if you set the yaml to be random? If not, I would like to suggest some way to notify the player how many they need, maybe in peach's castle or something?
- Don't know how possible it would be, but could there potentially be a starcoin counter on the overworld ui under the level/lives to keep track of how many are collected?
- Change hint movie names to indicate prog, trap, useful
- Multiplayer have separate pow restrictions


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
- NO idea why, but the big urchins in World 4-3 SC3 Room are producing an insane amount of bubbles and lagging the game lmao
- I got stuck in world 8 once, normally I'd farm enemy encounters for the mushrooms, however, the lava bubble was a strange case 
  - because the first encounter for it was fine, you can beat it no problem. But the second encounter is impossible without climb


Summery poll
- Stabilty
- QOL
- Locations/ items
- Non ap rando

  
## Features
- Save toad / kill world enemy = hint/check
- CHEATS / Useful extra features
  - Double jump
  - Auto collect checkpoint
  - Start with powerup
  - Moon jump
  - Each level connection seperate item
  - Double jump
    - https://discord.com/channels/673369321522593794/1396386889052983307/1396386889052983307
- Finding toad in level gives hint
- Unlocks : future planed movement
  - "climb_rocky_wall, tilting platforms (motion control), "canon pipes" "Bounc mushroom", "triple_jump", "cloud" (State_CloudMove),
  - "noteblock" (daEnWhiteBlock_c::makesBounce_maybe),  "Spring" (jumpDai), red coins - ring, stopmping on enemeies
  - "pow", "hold_rope" (3-G) (Hang action?),  "Bone ride", "Snake blocks", "climb_fence" (checkNetPunch makes spin forever)
  - spring

- TRAPS
  - Sandstorm
  - Darkness
  - Meteor
  - Stun / freez trap : mario → ice block
  - Spawn enemies
  - Auto scroll
  - Speed up / slow down game clock
  - Ice physics
  - Trap to put game in thrown state
- FILLER 
  - Gain this levels check point
  - Get toad house (beginning of world) : toad house is in MJ..game.. files, should be easy tm
  - Insta kill all enemies
  - screen clear gp : give player x amount
  - spawn random objects
- Features from gecko
  - Speed trap
  - fall damage trap
- Make penguin progressive
- LOCATIONS
  - 100 coins  : store # amount coin enter, add a watch for when it loops around
  - 1 ups : just look at if player life increase: not from coin
  - red ring : easy if can find adress
  - ?block / specific coin : difficult
  - Roulette block
  - Yoshi eat fruit
  - Discover each room
  - Killing each enemy type
  - Top of flagpole
- ITEMS
  - Enemy remove : should work same as checkpoint
  - Enemy add (trap item): readds enemy, works as above
  - Tilting plattform

REWORK
- P&Q switch work as checkpoint
- need to reformat rule?
  - dict with named dataclass ?
    - { "1-1" : Level(clear, sc1, sc2, sc3, secret = True, 1ups= true, 100coins = true, red ring = true)

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
- Shuffle with custom levels (no logic)
- Unlock other charactes (no gameplay) with player 1 change character fix
- Difficullty patch levels : make levels harder, similar to other mods, if settings enabled for this
- Have character be randomized and unlockable
- Chance for level to be replaced by backwards version



## Features I (Miiroun) will not implement
- Native wii support
- Randomized ?-blocks
- Coin sanity
