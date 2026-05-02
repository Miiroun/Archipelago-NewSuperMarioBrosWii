# New Super Mario Bros Wii Randomizer Setup Guide

## Required Software
- [Archipelago V0.6.7](https://github.com/ArchipelagoMW/Archipelago/releases/latest)
- [NSMBW World](https://github.com/Miiroun/Archipelago-NewSuperMarioBrosWii/releases/latest)
- [Dolphin emulator](https://dolphin-emu.org/download/)
- A legally acquired copy of a New Super Mario Bros Wii (tested on US rev 2, all other versions will have bugs) (both .iso and .wbfs works)
- (Optionally) [Universal Tracker](https://github.com/FarisTheAncient/Archipelago/releases)


## Setup
- Download and install archipelago (needs at least v0.6.7) and Dolphin.
- Download the ap-world file from [NSMBW World](https://github.com/Miiroun/Archipelago-NewSuperMarioBrosWii/releases/latest), doubleclick it and it's installed.
- Then create a player yaml file from the option creator in the launcher. Note that the ap client is bundled with launcher.
- Inside the client press CONNECT (when you are on the world map in game) and then enter your player name (from the yaml).
- If you care about your dolphin savefiles then back them up.

## How to play
- Open the AP launcher and find NSMBW Client, open it.
- This should prompt you for your game file. (You can change it from host.yaml).
- Clear save file 2 (you can make a copy of it if you care about it).
- When game booted select savefile 2.
- Make savestates in emulator, saving the game doesn't currently work.
- After you have entered the world map press CONNECT in the client.
- See the quirks section in en_NSMBW.md for quirks with the implementation.


## Tracker 
You can optionally use the built-in universal tracker extension to track available locations.
Simply download [universal tracker](https://github.com/FarisTheAncient/Archipelago/releases?q=Tracker) and put it into your custom worlds folder (or double click it).
Make sure you have your <player>.yaml file still in the /players/ directory for the tracker to work. It is automatically booted up if you have it in your custom worlds folder and is integrated into the client.
It might prompt you for an external pop tracker pack, this can simply be ignored as that pack is still in development.
