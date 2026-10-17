# TODO 
# Super Short term
- remove background off tracker items


## Playtest
- bowser_level_unlock 
- roulette and red coin : more
- PercentageFillerForcedLocal
- world unlock logic change for 8-2, 7-T
- Test remaining 7-C rando
- 8-Castle is correctly locked in new system
- require second world unlock to unlock 7-6 and 8-7
- Secret exits are properly level randoed
- Secret exits have their logic properlly
- multiplayer : 
  - second player dont collect starcoin immediately
  - The extra lives filler does NOT work properly with multiple people; I was player 2, and my lives were set to 94 and 88 at two separate points when the filler was only supposed to give 5 extra lives. I do wonder if this is only visual, though, cause a couple levels later, my lives would always revert down to a smaller number
- Level patch 8-A


## Bugs to fix
- Go to next world after beating airship
- Does secret exit apply its rules correct
- sometimes freeze after paus menu
- bowser lock in client 


fuzzing error
- Could not access required locations for accessibility check
- starcoin_requirement_world_unlock breaks fuzzer
- same with bowser lock options

## Before release
- React : blocks
- fix all bugs
- do all playtest
- verify UT 0.3.5 is latest
- mark as prerelease ? 

## Short term
- Add enemy ambush and toad rescue
- Do playthrough, document completion times for time logic
- Inventory pow doesn't work on other save files
- toad rescue location
- toad house doesn't work to set, probably needs to update other location too
  - toad add1  80c807f0
  - toad add2  80c80f22
- Make secret exit items to reunlock them
- Figure out how to change HM unlock condition?
- To-do:  prompt to watch hint movie
- Need spin to get off vine and yoshi
- look up hint movie prossessing in ghidra
- shuffle coin and battle levels with normals
- add 1ups as locations to world : needs option : keep secret until logic
- Look in regi for sand storm and meteor : see if is just an easy flag to change?
- look for doStateChange
  - can improve climb and swim
- Fix inventory pow on other savefiles
- Can't leave vine without spin jump
  - rework climb
- why does global mutation fuzzer hook fail at settings??
- Rework timer modifier option
- on_progressive should req that powerup and super mushrom are both received while on should depend on outside powerups
- implement method to read arc files : needed to change names of subfolders
- Another actual logic check is you can get 4-4 starcoin 1 with just penguin suit and swim, swimming at the pipe at the right angle and spamming swim allows you to bypass the the need to hit the p-switch
- Sprite table start 	8030a340	8031ab4c
- Rando enemies: option if remove or add them
- Rework modifiers slightly so that they don't cause issues any more
- What happens when resync state with level comp off
- Edit data of pa0_jyotyu to change its color 
  - or download versions and create patch files
  - https://discord.com/channels/673369321522593794/1295786310694342691/1295786310694342691
- Shuffle sprite table? How much will explode?
- Publish can't move left patch in nsmbw dc
- Improve how swim locks
  - Improve error messages
- Write to GameFlag_e?
  - enable debug things etc
- Add local multiplayer to docs
- Match server state it might be nice to have this automatically done after every death/level complettion/etc if possible
- Make early items an option
- !MANUAL BACKGROUND RENAME WORKS!
- Edit star coin level icon : new image
  - gameScene.arc
- Rework swim?
- do complete playthrough, add spin jump and jump logic + time logic
- put HM descriptions in client
- fix climb, ?switch
- make switches progressive with new patch?
- yoshi req spin to get free from
- 6-5 swim does not work on moving water
- fix wall slide patch, make it smarter
- improve peach castle starcoin patch
- get swim to be handled in game
- Level shuffle crashes hint movies
  - it is due to starting locations not being registered
- freez when clear toad house
  - on some music shuffle seeds
- Level clear = unlockable item??
  - each level would need to be unlocked separately  
- music shuffle feels weird and unintuitive : not looping etc, some jingles still included?
- Pop-up in game after beating 8-A
  - can I steal somene from in game or does it need custom code?
- Create built in map tracker
- Dolphin debug to find whitch function responsible path unlocks
- CAN get out of logic with seperete worlds, levels unlocked: e.g 3-G 
- Ask in NSMBW dc how difficult adding UI elements is.
- Rename raw rules to rule_data?
- Work on FINAL MOVMENETS : so REACT can start on block logic ? 
- if on all levels unlocked does secret exits always open


## Logic
- oneups_sanity (and which levels)
- nintynine_coin_sanity (and amount)
- red_coin_ring (and which levels)
- roulet_block (and which levels)
- blocks_sanity (and id for each block in each level)


## Broken versions
# EU 1
- Movement

# EU 2
- Filler on other save files, in level check failing?

# US 1
- Movement broken
  - Water
  - Spin
  - Crouch
  - Walljump (slide)


## FUZZER erros
-  world_comp_priority : false
-  starcoin_requirement_world_unlock : {} 
These 2 yaml restraints fixes most of fuzzing errors, especially `starcoin_requirement_world_unlock` is bad in fuzzing


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
- patch not need watching hint movies
- brick rando: look at EN_OBJ_HATENA_BLOCK, daEnBlockMain_c
- Make penguin progressive?
- Hint movies does not work on other save files?
- Add support for other savefile
- transition movments to riivolution
- "progresive world"
  - this is kind of a completely unrelated thought, but i was thinking what if there was a version of the ap where instead of unlocking worlds randomly you always unlocked them in order? idk how interesting it would be, but the idea essentially is that you would have to beat every castle / airship stage and beat each world type of thing
  - yeah, like youd always start in world 1, then go to 2 and maybe you also have to  beat the castle before moving on
  - i think the idea is alot more interesting in the context of level rando
  - "difficult scale level rando"
- control level rando:
  - keep levels in same world
  - scale by difficulty
- Nsmbw: checkpoint item unique for each level?



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
- Hint movies that requires all level completion don't work in game : vertify still problem
- game randomly freezes : inconsistent experience
- goomba patch errors when level doesn't goomba: rough write
- HM5 : all hm requring castle comp
  - might be problem with patch for skipping world unlocks
- Som hm req cannon comp
- Peach castle is weird when hint movies appear / not
- Slotlock does not work
- Hint movies and level shuffle cannot coexist
- After i beat the mushroom house it just freezes me there
- I understand for the ones that are just jingles, but a lot of others like the world map themes wouldn't loop if they were put in a level


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
  - item that removes the world map vines in world 5
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
  - color / flip scrren : as trap?
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
- Skipp playing hint movies when buying them
- Update world map - file
- AP-images for toad houses
- SMW like powerup storage


## Long term
- Get rid of keyboard
- Fix so work with multiple dolphin instances
- Add support for other mods: pipe rando, mkwcat 8player, newer (needs logic), etc
- Actual deathlink messages
- Shuffle with custom levels (no logic)
- Unlock other charactes (no gameplay) with player 1 change character fix
- Difficullty patch levels : make levels harder, similar to other mods, if settings enabled for this
- Have character be randomized and unlockable
- Chance for level to be replaced by backwards version
 think about abstracting apworld so can support mods?
  - ask mods if newer would be ok?
  - what to have diffrent worlds with diffrent game names : that just changes game name + file name + common and raw_rules + maybe modifiy client



## Features I (Miiroun) will not implement
- Native wii support
