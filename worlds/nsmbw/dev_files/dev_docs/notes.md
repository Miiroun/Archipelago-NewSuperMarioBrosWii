## This document notes stuff about implementation
# Movement rando
- cannon pipes: requires down button but not pipe item
- climb : Sneak ledges, fence causes freez / crash so are removed from rando for now


# Common bugs in code
- Forgot location_name_to_id when trying to send check : really difficult to test


# How to make release
- Playtest
- Run generic unit test
- Run fuzzer with at least 1000 iterations on none seeded yaml
- Build
- Git-Hub release
- Publish in nsmbw thread
- forward to apworld-news

# General weirdness
- Why sometimes invisible world map

# Tips to devs
- Have 2 branches when working on new big feature, so can put out smaller bugfixes until its finished.

# Playtesting
- Only developed on Windows
- Have test on WSL (Windows subsystem linux) and it at least boots

# Fill errors
- Are cause my magical deamons
- Free starting locations tends to alleviate issues, with current setup it clears 10_000 generations of fuzzer without fail if it can add starting locations when some options are turned off.


# Why not riivolution patch build from kamek?
- Because I dont have the skill and understanding of how it / c++ works
- and I want to simplify setup with only one set, and I think I need some form of external memory monitoring


# Resources
NSMBW modding resources
- https://docs.google.com/document/d/1-KQhmawgy0da8ijdzL6d7zrlMRBX3_UOm-oShqFvuYc/edit?tab=t.0#heading=h.ed97jvl7oamz
- https://github.com/N-I-N-0/New-Super-Mario-Lost-Worlds/tree/master/Docs
- https://www.learncpp.com/
- https://docs.google.com/document/d/1y2jUmJn7aoXo1FohaU6gx1vJ8cVc1tg1FEjbgNf4tUY/edit?tab=t.0#heading=h.lwtjl3l9zcq
- https://www.youtube.com/watch?app=desktop&v=IOyQhK2OCs0

Ghidra setup
- https://discord.com/channels/673369321522593794/673706884557176832/1477052416598999240

LM explanation for multiple dolphin
- Multiple Dolphin support:  In your dolphin folder, copy the dolphin.exe and rename it to something else, like Dolphin2.exe Once thats done open Luigis Mansion Client, regardless of whether Dolphin is open or not, and type /change_dolphin_process_name Dolphin2.exe to force DME to use that for LM Client from now on (Alternatively in host.yml, there is now a new option under luigismansion_options that is called dolphin_process_name that you can just change directly, see screenshot)  You will then get a popup that the client MUST be closed otherwise this will not connect to the right dolphin instance (only the client, do not need to close the launcher)  Upon re-opening the client it will now try and connect to Dolphin2.exe instead

Helpfull websites
- https://www.calculator.net/hex-calculator.html
- https://gregstoll.com/~gregstoll/floattohex/
  - NSMBW uses Single-precision floats
- https://fenixfox-studios.com/manual/powerpc/index.html
- https://fenixfox-studios.com/manual/powerpc/registers.html

