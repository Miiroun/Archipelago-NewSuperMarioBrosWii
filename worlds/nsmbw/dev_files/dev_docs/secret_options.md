# Secret options
Strong warning, these are secret for a reason.
Do not use them if you want a stable playthrough.<!-- TOC -->
* [Secret options](#secret-options)
  * [`nintynine_coin_sanity : true`](#nintynine_coin_sanity--true)
  * [`oneups_sanity : true`](#oneups_sanity--true)
  * [`red_coin_ring`](#red_coin_ring)
  * [`roulet_block`](#roulet_block)
  * [`pallet_shuffle_riivolution : true`](#pallet_shuffle_riivolution--true)
  * [`block_sanity : true`](#block_sanity--true)
  * [`entrance_randomizer : on`](#entrance_randomizer--on)
  * [Legacy Linux save-state hotkeys](#legacy-linux-save-state-hotkeys)
  * [How to play (`use_riivolution` disabled)](#how-to-play-use_riivolution-disabled)
<!-- TOC -->


## `nintynine_coin_sanity : true`
Sends a location when you get 99 coins in level. 
WARNING, NO LOGIC.


## `oneups_sanity : true`
Sends a location when you collect a one up in a level.
WARNING, NO LOGIC.


## `red_coin_ring`
WARNING, NO LOGIC.


## `roulet_block`
WARNING, NO LOGIC.


## `pallet_shuffle_riivolution : true`
Shuffles the color pallet of the game.
Looks good but takes about 15 minutes to actually patch the game.


## `block_sanity : true`
Creates turn all coin blocks and powerup blocks into locations: ~ 1000
They have yet to be mapped, if you encounter any not map please report them


## `entrance_randomizer : on`
Will apply the mkwcats pipe randomizer together with archiepelago
WANNING: No logic
Likes to crash a lot
Does not work with exiting levels
Does not properly reset when exit levels

## Legacy Linux save-state hotkeys

Use Riivolution to clear the JIT cache. These legacy settings are for advanced troubleshooting.

In `host.yaml`, set `nsmbw_settings.keypress_library` to:

- `0`: bundled Python `keyboard` library; requires the client to run as root on Linux.
- `1`: `xdotool`; your desktop may ask you to allow input control.
- `2`: `ydotool`; requires `ydotoold` to be running. Follow its
  [setup instructions](https://github.com/ReimuNotMoe/ydotool#runtime).

Restart the client after changing this setting.


## How to play (`use_riivolution` disabled)
0) Change these dolphin options
   - `Options → Configuration → Interface → Hotkeys Require Window Focus` to `Off`
   - `Options → Hotkey Settings → Save and Load State`. Make sure saving (e.g. shift + F8 or @(Shift+F8)) and loading (e.g. F8) save states from slot 7 and 8 are their default values.
   - If you care about your dolphin savefiles then back them up.
1) Open the AP launcher (restart if it was open before) and find NSMBW Client, open it.
2) This should prompt you for your game file. (You can repromt it by removing the nsmbw_settings in host.yaml, do NOT edit it manually).
   - If you want the game to auto start
3) Clear save file 2 (you can make a copy of it if you care about it). Then select the now empty savefile 2 to play on.
4) After you have entered the world map press `CONNECT` in the client, and enter your slot name and password.
5) Open the in game world-select menu and move to the world you have unlocked.
6) See the quirks section in [en_NSMBW.md](../../docs/en_NSMBW.md#known-quirks--bugs--help-with-debug) for quirks with the implementation.
   - If your on Linux, read [legacy-linux-save-state-hotkeys](#legacy-linux-save-state-hotkeys).
7) Make save-states to save the game and run `/save` often.
   - Don't use the in game save feature and make a new save state after every level clear.
   - To close the game run `/exit`