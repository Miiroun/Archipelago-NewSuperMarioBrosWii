# TODO 
## Super super short term
Mention riivolution, keybindings and dolphin default program in setup guide : shorten and simplify? so people dont skipp
Ask in dc for better option names
Test if loading code actully moves around memory
Playtest multiplayer
Do we need to load to clear or does it on save too?
Check point similar
  func 80a92888 for red coin ring
  func 80aa7470 sneak block
  func 80a9cc70 poky
  func 80a5d2d0 daEnLiftRotHalf_c
  80a88920 chep chep
search : onCreate and create, only lables

How solve issue where to load game on start or connect if use riivolution or not
- need to update docs
Test AP map visual editor
- does new auto riivo work ? move old start to on open

Rework movements to enable abilites
- then have sub cateagorys for include movments and include level elements?

use wiithon for arc unpacking??
- maybe switch to it instead of dolphin tools


does send filler work correct right now?

why doesnt /explain 9-1 work?

DC
- option + setting review
- Where should the project continue?


I've been making a list of hint movie unlocks for y'all, I'm about half way through the list, hint movie 9 unlocks only after you beat all levels in worlds 1-8, which also means for it to work 8-7 has to be shown as complete on the map, i remember when i was doing the archipelago 8-7  never completed as a shortcut to the airship, it won't count unless every level in the first 8 worlds is blue

FIX generation and client bugs
test
- sc model
- gravity
- load 1 background

fix assert no doublicate dolphins

- Secret exit items
  - update docs

#809c6120 return : works for p switch

wii-lib currently breaks frozen

add goomba lock as option

## Super short term
- multiplayer
  - Separate powerup unlocks?
- Rename:
  - movement to abilities?
  - dontrandomoves to default moves?
  - include option to sanity?
- update docs
- button_down and button_up and pipe logic
- create an function to  and bytes
- Rando game tile sheet, enemy sheet (or sprite table ?), music etc. Easiest done through riivolution
- Try redumping my copy of nsmbw : test which guide / method best to link to
- Ask for help in dc for names
- Work on preventing sending of locations on title screen
- 8-2 secret exit requires more logic
- Ask for help in dc for names
- Secret exit items in client !!!
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
- test if loading code actually fails the client
- run /dev x2 and then see which hm aren't showing up : add to dont rando
- Dolphin wsl
- Beat some levels on vanilla save file 1 to verify no wrong sends are happening
- Reword timer modifier option
- on_progressive should req that powerup and super mushrom are both received while on should depend on outside powerups
- Put disclaimer that collect SC immediately doesn't impact logic
- Add setting to which save file to continuously save/load from
- Docs mention no changes dolphin setting or keybind
- If unlocked set red switch to on
- Hm in peach castle is not correct amount on free, should remove req of having sc
- Remove req for cost of having X HM on other settings
- Add key binds to docs
- Location scout hm: give as hint, as an option
  - Could maybe change name of hm based on if priority / useful / filler
- Use dme on intro, try finding way to not release on connect
- Can I verify dolphin settings? have been changed?
- Time change default not current
- implement method to read arc files : needed to change names of subfolders
- verify that key combos dont overlap
- point to dumping guide in docs
- Another actual logic check is you can get 4-4 starcoin 1 with just penguin suit and swim, swimming at the pipe at the right angle and spamming swim allows you to bypass the the need to hit the p-switch
- Thats good to know, i just found another check i can get with wall jump or propeller in 7-ghosthouse that isn't in logic because i don't have ?-switch
- Add better way of explaining rules
  - Does this solve issue?
- load last save state directly? : should be able to
- Pause dolphin, increment slowly: find bites in black : verify issue there not menu generally
- Can find value hardcoded for level timer? Add memwatch for func that changes it
  - Can make > vanilla?, would be nice
- Ask react for help invent pow
- Color pallet rando? : would be realy fun and possible?
- Maybe separate movement, rename to abilities and level_elements: move over pow, ?switch, flagpole
- Look at flagpole patch in ghirdra
- Sprite table start 	8030a340	8031ab4c
- Rando enemies: option if remove or add them
- Try detecting dolphin settings C:\Users\Anton\AppData\Roaming\Dolphin Emulator\Config
- Rework modifiers slightly so that they don't cause issues any more
- Chance for level to be replaced by backwards version
- Can i somehow trigger something with hitting ?-blocks?
- Make sure works with no patch
- Add test not on save file 1 before sending locations
- Test manually renaming just 1 file
- Make don't rando move invisible
- Remove option page link that doesn't exist
- What happens when resync state with level comp off
- Can create level patches if desire with bsdiff4, would be easy if needed
  - if want to change logic etc
- riivolution level shuffle is backwards
  - fixed?
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
- Publish can't move left patch in nsmbw dc
- Double jump
  - https://discord.com/channels/673369321522593794/1396386889052983307/1396386889052983307
- reuse code for check point for other level elements
- remove optimiz form modifires : so doesnt causes issue at cost of performance
- have option to rando towers and airshipps in their own pool
- If you are using Dolphin Emulator, you need to enable MMU in Config > Advanced (this can only be done while a game is not running).  Next up, the retail game does not display the exception handler by default (most modding bases do). To show it, press , , , , , , , , ,  on Player 1's Wii Remote. Alternatively, Dolphin's log will print out the exception info, so long as both OSReport log types are enabled.
- Hook into main loop, load institution
- exception handler // Disable the button sequence kmWrite32(0x802D7528, 0x48000060);
- Hook up kamek patch that can clear jit: load instru from memory: # r17+r18=address of instruction you want to remove from cache dcbf r17,r18  sync icbi r17,r18 isync
  - Probably dont want geco code solution since that difficult to do automatically
- Mention common issues if not loading save states
- Mention dolphin default program in common errors
- Find other way to invaliditet dolphin cache
- Test mem1 and 2 issue
- Should be able to at least relatively easily create kamek patch that can kill mario from externally modified memory
- Add test with / out exits
- Rework modifiers so issue doesn't happen
- Add assert if save slots overlap
- Ask react if should rando run
- Option to have world 9 levels not be blocked
- Faq jit savestate
- Try moving mem1, see if causes issues
- Change docs for linux : no need for root if xdotools or ydotools
- option to shuffle only towers within themselves
- Try: Ensure that "Enable CPU Overclock" and "Emulated Memory Size Override" are both off in your Dolphin settings
- Use single adress to mark if have applied patch
- Use the code software
- Create nice title screen
- Install blender plugin for brres
- Link to setup guide in release
- Trap to put game in thrown state
- Ask how kamek 2 loaders work
- Download keyboard like LM??
  - https://github.com/BootsinSoots/Archipelago/blob/a65d00434f58781d0286387eeb2575d80ee59791/worlds/luigismansion/iso_helper/LM_Rom.py#L148
- Auto open riivolution as separate setting 🤔, need to verify game not running
- Rework setup guide with auto launch disabled : if turned off riivolution, move to game info
## Multiple Dolphin support:  In your dolphin folder, copy the dolphin.exe and rename it to something else, like Dolphin2.exe Once thats done open Luigis Mansion Client, regardless of whether Dolphin is open or not, and type /change_dolphin_process_name Dolphin2.exe to force DME to use that for LM Client from now on (Alternatively in host.yml, there is now a new option under luigismansion_options that is called dolphin_process_name that you can just change directly, see screenshot)  You will then get a popup that the client MUST be closed otherwise this will not connect to the right dolphin instance (only the client, do not need to close the launcher)  Upon re-opening the client it will now try and connect to Dolphin2.exe instead
Hi if you are having hook loop connection issues, you can be because of these things:  1. A not PAL rom (eu rom) 2. Multiple instances of dolphin being open, even library windows count, make sure to have just one. 3. One of the two is running as administrator, they either need to run both as administrator or both not as administrator. 4. Your dolphin version is too old 5.3+ should work, but i recommend any of the 25XX versions or above. (If on linux make sure you use the *flatpak* version others will not work.) 5. For some people setting having their dolphin fallback region to anything but EU/PAL also causes connection issues
Send yaml for help
Update world 9  : use help
Look in regi for sand storm and meteor : see if is just an easy flag to change?


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
- Can I get off Yoshi without spin?
- reprompt_gamefile
- Ydotool
- patch not need watching hint movies
- Shortcuts
- Location scout hm
- Try sending !-switch
- Title screen replacement
- q-switch
- Try skip wii strap patch : see if works to not have bug
- Playtest secret exits



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
- This isn't a priority so you can focus on it later, but here's an error that was produced after running the command ```Traceback (most recent call last):   File "MultiServer.py", line 1350, in __call__   File "C:\ProgramData\Archipelago\custom_worlds\tracker.apworld\tracker\TrackerClient.py", line 250, in _cmd_explain     explain(self.ctx, lookup_name)     ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^   File "C:\ProgramData\Archipelago\custom_worlds\tracker.apworld\tracker\TrackerClient.py", line 1512, in explain     dest_id = current_world.location_name_to_id[dest_name]               ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^ KeyError: '9-1'```
  - Do I not add event locations to world 9??
- Still disconnect error
- force_hook : assert connected
- exit course sometimes send death
- Hm 5 probably not a problem
- 2-2sc1 & sc2
- 1-C sc3
- World 9 not properly reset when dying
  - Looks like after a death in 9-3 exclusively the default state of World 9 is stored I've died in other World 9 levels without the World being set like this
  - Entering the level was possible while the circle was solid black, and the clear/sc checks were sent out properly when the level was completed 
  - However, the world state was not reset (level clear saw the same situation as the screenshot), and I switched worlds and came back to be able to do other levels
- Is tracker 0.3.3 broken? for 0.2.1 5-1 ??

## DISCORD POLL TOPICS:
- usefull / prog Items : tilt plattform, double jump
- filler / trap Items : gravity
- achivement locations : 1ups, 99 coins
- genreal rando : enemy shuffle
- overhall : enterence
- re factor : death -> kamek patch, no save states
- Custumize : settings / options / cmd
- Stability : weird bug fixes, write tests, lots more playtest
- onboarding : improve guide, make video
- Cosmetic : background, tileset, color
- Quality of life patches : skip cutseence, not have to watch hm
- In game text chat
- Multiplayer support
- UT map pack

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
- request channel in ap-dc



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
- LOCATIONS
  - 100 coins  : store # amount coin enter, add a watch for when it loops around
  - 1 ups : just look at if player life increase: not from coin
  - red ring : easy if can find adress
  - ?block / specific coin : difficult
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


## Features I (Miiroun) will not implement
- Native wii support
- Randomized ?-blocks
- Coin sanity
