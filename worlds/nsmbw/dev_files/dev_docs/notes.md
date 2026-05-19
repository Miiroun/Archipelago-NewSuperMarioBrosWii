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
- Have test on WSL (Windows subsystem linux) and at-least boots

# Fill errors
- Are cause my magical deamons
- Free starting locations tends to alleviate issues, with current setup it clears 10_000 generations of fuzzer without fail if it can add starting locations when some options are turned off.
