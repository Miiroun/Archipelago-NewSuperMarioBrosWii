# TODO 
# Super Short term
- Edit world map so all levels unlocked from start
- Ask how difficult adding UI elements is.
- try editing world 1 path info manually and test it out
  - test modified pointW1
  - use other program for csv editing
- Mention which files needs to be selected for settings:
- Nsmbw: checkpoint item unique for each level?
- Rename raw rules to data / raw_data / rule_data?
- Work on FINAL MOVMENETS : so REACT can start on block logic
- Decide on way to store brick rules
- Format list of all blocks
- Spend time on ap-map pack : download images from wiki with python
- Option to exlude specific worlds
- do archipelago nameing of blocks
- fix header licence
- Ap: write my slot data and seed to meme with riivolution: verify in client
- Castles req second level half
- Mention Mac issue in setup
- change display name of riivolution options?
- make level completion an impactful setting?
- other use fuzzer hook
- improve description of RandomizePowerups
- I think it could be a good idea to have a list somewhere telling which stages aren't rando'd
- setup guide: do not have dolphin open
- clarify dolphin folder when selecting : not rom folder, should include dolphin.exe
- what about shuffling the enemy ambush stages
- Level shuffle options
- I've looked at the rest of the castles in the editor and if I am correct in what I think Is happening 1-C, 3-C, and 6-C should all be fine and the only ones that won't work are 4-C and 5-C (obviously 2-C & 8-C arent randoed for other reasons)
- Test remaining 7-C rando
- Advertise rm_tmp
- Auto run /rm_tmp if some files been removed from temp folder
- Stricter error for having dolphin open when connect
- Try included dolphin version in /versions
- Docs: progressive world
- Descriptive folder browsing
- Is enemies unlocked correct
- Docs: level shuffle limitation, trap explain
- option exclude some levels
- I think just a setting that can remove up to 5 levels is fine
- Allow manual placements of levels
- Have 2 lists during enterence rando creation: 1 for placement pool and 1 for level pool, so can seperate them
- Right. I should probably make a list of levels which we allows to be randoed to 7-C instead of a disallowed list like I implement.
- work on replace csv
  - test
  - better if could modify code
  - or do dynamic write
  - start looking from my world9 patch
- make breaking changes
- update docs !!!!!!


## Playtest
- backward combat for coin battle
- bowser_level_unlock 
- starcoin_requirement_world_unlock
- 3-4 fix and cause
- roulette and red coin : more
- PercentageFillerForcedLocal
- powerups : a lot, get help
- Having more powerups than loc should send hints
- performance from just the riivo patch : no client
- fail to reading region -> rm_tmp
- /Where_is /what_is
- 7-6 unlock
- Print big red message if dolphin valuation finds incorrect settings
- level shuffle plando
- goomba extinction
- prossesed_inventory_powerup_locations rework
- only give unlocked powerups


## Bugs to fix
- I understand for the ones that are just jingles, but a lot of others like the world map themes wouldn't loop if they were put in a level
- 8-7 exit is unlocked without normal exit item being recived
- multiplayer : second player dont collect starcoin immediately
- UT fuzzer errors 
- Np! Also any idea on how to get 6-4 first star coin without Yoshi or any power up? It’s say it is in logic (it’s the 6-2 level in my seed). I'm curious
  - logic changed, test out
- Yo, just so you know, but despite having the 2 progressives W6, W6-5 and 6-6 aren't considered in logic but 6-C is.
  - I think secret exits do not respect normal exit clear conditions
- The extra lives filler does NOT work properly with multiple people; I was player 2, and my lives were set to 94 and 88 at two separate points when the filler was only supposed to give 5 extra lives. I do wonder if this is only visual, though, cause a couple levels later, my lives would always revert down to a smaller number
- rule for 1-3 sc1
- 7-6 secret exit does not account for world unlock?
  - Should it be unlocked without 2 world 7 unlocks
  - I have some problems with the current secret exit systems: figure it out and write unit tests
- Inventory star broken
- Go to next world after beating airship


0x80792f50 : GetNumberOfCoinsCollectedInEveryLevelForModelPlayBase
extracted from castle pointer
- playtest this patch
- implement in client
- invesitgate more at 80792e1c in ghidra, figure out which func breaks




0x15e566c 	
[NTSC/PAL] Peach's Castle Star Coins Pointer [32-Bit BE]
+0x2248=[32-Bit BE] Spendable Stars Coins
- might need to edit with code patch

0x153e514 	
Spendables Star Coins in Peach's Castle [32-Bit BE]


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
- Problem with name being static for level rando : cannot shuffle names ? !
- option to turn off anoying block sanity level (5-G, 7-3, 8-1, C-1)
- make some / most of block sanity excluded
- Pop-up in game after beating 8-A
  - can I steal somene from in game or does it need custom code?



## Breaking changes
- remove the 7-6 and 8-7 normal exits
- i think the both health item should be changed to something like decrease boss health
- Make yoshi level element
- option rename
  - mostly riivolution but others too
- Level shuffle rename from -> to level



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
  - p-switch
  - Crouch
  - Walljump (slide)


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
- transition movments to riivolution
- "progresive world"
  - this is kind of a completely unrelated thought, but i was thinking what if there was a version of the ap where instead of unlocking worlds randomly you always unlocked them in order? idk how interesting it would be, but the idea essentially is that you would have to beat every castle / airship stage and beat each world type of thing
  - yeah, like youd always start in world 1, then go to 2 and maybe you also have to  beat the castle before moving on
  - i think the idea is alot more interesting in the context of level rando
  - "difficult scale level rando"
- control level rando:
  - keep levels in same world
  - scale by difficulty


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
- Slot.lock does not work
- Hint movies and level shuffle cannot coexist
- After i beat the mushroom house it just freezes me there


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
 think about abstracting apworld so can support mods?
  - create my own build system?
    - run build all diffrent mod versions
    - also run kamek
  - ask mods if newer would be ok?
  - what to have diffrent worlds with diffrent game names : that just changes game name + file name + common and raw_rules + maybe modifiy client



## Features I (Miiroun) will not implement
- Native wii support
