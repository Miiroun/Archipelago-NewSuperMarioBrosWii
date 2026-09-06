# TODO 
# Super Short term
- Improve performance
  - Log loop time : nothing noticeable
  - watch if clear cache more often than expected : no
  - dont run patches / unlocks each frame 
  - is it loading star coin model?
  - test if happens with riivo patch without client
- Edit world map so all levels unlocked from start
- Ask how difficult adding UI elements is.
- try editing world 1 path info manually and test it out
  - test modified pointW1
- Mention which files needs to be selected for riivolution
- matrix test for local filler

- Change error messages import keyboard to mention riivolution

Setup
- Change the tracking 3(
- 4) async -> multiworld 
- 4) Riivolution: assert: mention default 
- Edit 6) in setup guide


## Playtest
- backward combat for coin battle
- bowser_level_unlock 
- starcoin_requirement_world_unlock
- 3-4 fix and cause
- roulette and red coin : more
- PercentageFillerForcedLocal
- powerups : a lot, get help


I have a problem: need to conditionally add locations depending on level rando: however they are not set until the rules set
- I cannot move level rando earlier
- Nor can I move location creation later


## Bugs to fix
- 3-4's randod to 1-3 Secret Exit seems to not send even after completing it several times.
- 3-4 secret exit is weird, maybe because it is switched with the red block?
- FYI, in the new update if you somehow gain a power up without having mushroom unlocked (i.e. you have ice flower on you via the menu) and you take damage, you just go back to ice flower infinitely
  - powerup broken on non default powerup setting
- and there other issues, with the deathlink, sometimes it send it just by entering in a level and when I exit course in the pause menu it send it ofen too
  - deathlink sends when exit course
- hello everyone, there's an issue on the toad house, when you make the mini game for get the inventory power up it crash when I get wrong ^^"
  - toad house still crash
- bytes b'<``\x80C' at addr  80a28464 not in code b'H\x00\x00(' or origin b'A\x82\x00\x1c' for patch <worlds.nsmbw.NSMBW_client.memoryAddresses.CodePatch object at 0x00000280039622E0> with name patch_star_level
- I understand for the ones that are just jingles, but a lot of others like the world map themes wouldn't loop if they were put in a level


0x429f30 	
[32-bit BE] [NTSC] Some pointer that can be used as a way to know you aren't in a stage for FFA/Coin Battle
0x0=Menu
>0x80000000=In game

roulette blocks 
daEnRouletBlock_c::finalizeState_Wait


## Short term
- fix UT-autotab : actually works? : needs to just update on switch and not death
- Add enemy ambush and toad rescue
- I have issue with fuzzing with hooks: UT 
- Do playthrough, document completion times for time logic
- Inventory pow doesn't work on other save files
- toad rescue location
- toad house doesn't work to set, probably needs to update other location too
  - toad add1  80c807f0
  - toad add2  80c80f22
- Make secret exit items to reunlock them
- assert early items are actually early, write test?
- Figure out how to change HM unlock condition?
- AFTER JIT clear have proven to work : make post in AP-mod thread about it
- To-do:  prompt to watch hint movie
- Need spin to get off vine and yoshi
- look up hint movie prossessing in ghidra
- shuffle coin and battle levels with normals
- add 1ups as locations to world : needs option : keep secret until logic
- Look in regi for sand storm and meteor : see if is just an easy flag to change?
- look for doStateChange
  - can improve climb and swim
- Fix inventory pow on other savefiles
- Shuffle in coin and battle stages into main levels
- Can't leave vine without spin jump
  - rework climb
- bool dWmConnect_c::GetConnect at 800f3380 might allow me to not override tower completion and have all levels unlocked from start
- why does global mutation fuzzer hook fail at settings??
- Rework timer modifier option
- on_progressive should req that powerup and super mushrom are both received while on should depend on outside powerups
- implement method to read arc files : needed to change names of subfolders
- Another actual logic check is you can get 4-4 starcoin 1 with just penguin suit and swim, swimming at the pipe at the right angle and spamming swim allows you to bypass the the need to hit the p-switch
- Can find value hardcoded for level timer? Add memwatch for func that changes it
  - Can make > vanilla?, would be nice
- Sprite table start 	8030a340	8031ab4c
- Rando enemies: option if remove or add them
- Rework modifiers slightly so that they don't cause issues any more
- What happens when resync state with level comp off
- Separate auto start: auto save, auto close
- detect if unsupported dolphin settings are used
- Review option creator pr
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
- Improve how swim locks
  - Improve error messages
- Write to GameFlag_e?
  - enable debug things etc
- Don't allow lives and powerups to be maxed out
- Add local multiplayer to docs
- Match server state it might be nice to have this automatically done after every death/level complettion/etc if possible
- Make early items an option
- !MANUAL BACKGROUND RENAME WORKS!
- time rando is broken : fix for 0.3.1?
  - patch starting time doesnt work
- Edit star coin level icon : new image
  - gameScene.arc
- Rework swim?
- goomba lock doesnt work
- time brocken
- do complete playthrough, add spin jump and jump logic + time logic
- put HM descriptions in client
- fix climb, ?switch
- make switches progressive with new patch?
- yoshi req spin to get free from
- 6-5 swim does not work on moving water
- fix wall slide patch, make it smarter
- improve peach castle starcoin patch
- Make name fuzzing for commands in common client: PR.
- auto read dolphin settings for where games are stored
- get swim to be handled in game
- Level shuffle crashes hint movies
  - it is due to starting locations not being registered
- freez when clear toad house
  - on some music shuffle seeds
- Level clear = unlockable item??
  - each level would need to be unlocked separately  
- music shuffle feels weird and unintuitive : not looping etc, some jingles still included?
- Make yoshi level element : breaking change


## Logic
- oneups_sanity (and amount)
- nintynine_coin_sanity
- red_coin_ring (and which levels)
- roulet_block (and which levels)


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
- Kamek patch to detect if ap is connected
- Hm option: cumulative but order is sorted after hm unlock order
- Is there a way in game to see how many worlds you need to complete if you set the yaml to be random? If not, I would like to suggest some way to notify the player how many they need, maybe in peach's castle or something?
- Don't know how possible it would be, but could there potentially be a starcoin counter on the overworld ui under the level/lives to keep track of how many are collected?
- Change hint movie names to indicate prog, trap, useful
- Multiplayer have separate pow restrictions
- Should probably store levels completed in data storage instead of looking at level completion
- Work more on map pack:
  - download images from wiki
  - Create own illustations of unlocks for itemtracker
- patch not need watching hint movies
- brick rando: look at EN_OBJ_HATENA_BLOCK, daEnBlockMain_c
- Make penguin progressive?
- Hint movies does not work on other save files?
- Add support for other savefile


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
- Sneak freezes game
- Hint movies that requires all level completion don't work in game : vertify still problem
- game randomly freezes : inconsistent experience
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
- Level rando sometimes craches game
- HM5 : all hm requring castle comp
  - might be problem with patch for skipping world unlocks
- Som hm req cannon comp
- exit course sometimes send death
- Skip into cutsceen does work sometimes? : skips if spam click intro
- riivolution patch sometimes random crashes on startup
- when i loaded the save file it took some time to recollect the items (worlds) it had been sent
- Collect immediately sometimes broken, restart fixes it.
- Peach castle is weird when hint movies appear / not


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
  - fall damage trap
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
  - P-switch as locations
  - flagpool score as location?
- ITEMS
  - Enemy remove : should work same as checkpoint
  - Enemy add (trap item): readds enemy, works as above
  - Tilting plattform


## Game patches
- Coin worlds single player
- Skipp playing hint movies when buying them
- Update world map - file
- AP-images for toad houses
- SMW like powerup storage


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
