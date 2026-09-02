from .NSMBWInterface import *
from ..options import AlternativeGoal
from ..Common import *
from .. import locations

import os
import tempfile
import time
import traceback

import Utils
from ..raw_rules import LevelRules
from ..settings import NSMBWSettings

if TYPE_CHECKING:
    from .NSMBWContext import NSMBWContext


tracker_loaded = False

try:
    #raise ModuleNotFoundError("")
    from worlds.tracker.TrackerClient import TrackerCommandProcessor as SuperClientCommandProcessor, UT_VERSION

    tracker_loaded = True
    print("Tracker is loaded")
except ModuleNotFoundError:
    from CommonClient import ClientCommandProcessor as SuperClientCommandProcessor
    print("Tracker was not found so is not loaded")
logger = logging.getLogger("Client")



class NSMBWCommandProcessor(SuperClientCommandProcessor):
    ctx: "NSMBWContext"

    def __init__(self, ctx: "NSMBWContext"):
        super().__init__(ctx)

    def _cmd_status(self):
        """Display the current dolphin connection status."""
        from .NSMBWContext import status_messages
        logger.info(f"Connection status: {status_messages[self.ctx.connection_state]}")

    def _cmd_toggle_deathlink(self):
        """Toggle deathlink from client. Overrides default setting."""
        Utils.async_start(
            self.ctx.update_death_link(not self.ctx.death_link_enabled),
            name="Update Deathlink",
        )
        message = (
            f"Deathlink {'enabled' if self.ctx.death_link_enabled else 'disabled'}"
        )
        logger.info(message)

    def _cmd_deathlink_group(self, key: str = ""):
        """Update the deathlink group """
        Utils.async_start(self.ctx.update_death_link_group(key))
        logger.info(f"Updated deathlink group to '{key}' ")

    def _cmd_deathlink_amnesty(self, amount):
        """Set the value of deathlink_amnesty"""
        value = int(amount)
        self.ctx.death_link_amnesty_cap = value
        logger.info(f"Deathlink amnesty set to {self.ctx.death_link_amnesty_cap}")

    def _cmd_deathlink_grace(self, amount):
        """Set the value of deathlink_grace"""
        value = int(amount)
        self.ctx.death_link_grace_cap = value
        logger.info(f"Deathlink grace set to {self.ctx.death_link_grace_cap}")

    def _cmd_debug_deathlink(self):
        """Gives some debug info if deathlink isn't working correctly.
        If you have trouble with deathlink run this and post it in the nsmbw chanel in the archipelago discord"""
        if self.ctx.username is None:
            logger.info(f"Connect to AP-server before running debug_deathlink")
            return
        logger.info(f"""Debug info about deathlink 
                    dl enabled  : {self.ctx.death_link_enabled} 
                    dl group    : '{self.ctx.death_link_group}' 
                    dl group in slot data: '{self.ctx.slot_data['death_link_group']}' 
                    current tags: {self.ctx.tags} 
                    Amnesty     : {self.ctx.death_link_amnesty_count}/{self.ctx.death_link_amnesty_cap}
                    Grace       : {self.ctx.death_link_grace_count}/{self.ctx.death_link_grace_cap}""")

        if (f"DeathLink{self.ctx.death_link_group}" in self.ctx.tags) ^ (self.ctx.death_link_enabled):  # xor ?
            logger.info(f"there is a missmatch between group and tags, please report this")

    def _cmd_start(self):
        """
        starts game
        """
        if self.ctx.username is None:
            logger.info(f"Connect before auto start")
            return
        if self.ctx.slot_data["use_riivolution"]:
            Utils.async_start(self.ctx.patch_and_run_game(True))

        else:
            Utils.async_start(self.ctx.run_game(True))

    def _cmd_reapply_checks(self):
        """
        Do this command if some checks haven't been applied because of wrong cache.
        """
        self.ctx.locations_handled = []
        self.ctx.prossesed_inventory_powerup_locations = 0
        self.ctx.handled_num = 0
        self.ctx.prev_sent_locations = set()

    if Utils.get_settings()["nsmbw_settings"].debug_mode:
        def _cmd_clear(self, key: str = ""):
            """
            A cheat command useful for developing.
            """
            # Utils.async_start(self.ctx.unlock_everything())
            if key == "":
                self.ctx.unlock_everything()
            elif len(key.split("-")) == 2:
                world_num, level_num = base_bijection(key.upper())
                self.ctx.game_interface.set_level_stats(int(world_num), int(level_num), b'\x37')
            else:
                logger.info(r"Error in key for /dev")

        def _cmd_set_pow(self, pow: str):
            """
            Cheat command that sets your powerup
            """
            try:
                pow = int(pow)
            except Exception:
                pass

            if type(pow) != int:
                if pow in POWERUP_UNLOCK:
                    pow = POWERUP_UNLOCK.index(pow) + 1

            for player_num in range(PLAYER_COUNT):
                self.ctx.game_interface.set_powerupstate(int_to_bytes(pow, 1), player_num)

        def _cmd_add_mod(self, type_, time_):
            """ Adds type, """
            from .NSMBWContext import Modifier, modifier_type_litteral
            # assert type_ in TRAPS, "all mod are traps, for now"
            self.ctx.modifiers.append(Modifier(type_, float(time_)))

        def _cmd_clear_mod(self):
            """Clears current type"""
            self.ctx.current_mod_end_time = 0

    def _cmd_get_mod(self):
        """Prints out current type and time left"""
        if self.ctx.current_mod != "":
            logger.info(
                f"Modifier {self.ctx.current_mod} with time left {self.ctx.current_mod_end_time - time.time()}.")
        else:
            if not Utils.get_settings()["nsmbw_settings"].debug_mode:
                logger.info(f"No type active")
            else:
                logger.info(
                    f"No type active, mod '{self.ctx.current_mod} time left {self.ctx.current_mod_end_time - time.time()}")
                logger.info(f"Mod list {self.ctx.modifiers}")

    def _cmd_refresh_mod(self):
        """clear activ and future modifiers, also clears once that have been permanently activated from incorrect use of save-states"""
        from .NSMBWContext import Modifier, modifier_type_litteral

        self.ctx.current_mod_end_time = 0
        self.ctx.modifiers = list(
            Modifier(name, 0.001) for name in get_args(modifier_type_litteral)) + self.ctx.modifiers

        for _ in self.ctx.modifiers:
            self.ctx.handle_modifiers()
            sleep(0.01)

        logger.info(f"Successfully refreshed all modifiers")

    def _cmd_save(self):
        """
        Save data of client memeory to a local save file.
        """
        Utils.async_start(self.ctx.handle_save())
        # self.ctx.handle_save()

    def _cmd_load(self):
        """
        Load save file for client memory.
        """
        Utils.async_start(self.ctx.handle_load())
        self.ctx.update_memory_to_server_on_load()

        # self.ctx.handle_load()

    def _cmd_starcoins(self):
        """
        Returns the amount of star coin items sent to client.
        """
        logger.info(
            f"Star coin count: {self.ctx.starcoin_count} out of {self.ctx.slot_data['bowser_star_unlock']} for unlocking bowser")

    def _cmd_worlds_unlocked(self):
        """
        Prints how many times you have recived each progresive world
        """
        mess = "Worlds unlocked\n"
        for world_num in range(1, 9 + 1):
            mess += f"World{world_num} has been received {self.ctx.unlocked_worlds[world_num - 1]} times \n"
        logger.info(mess)

    def _cmd_completed_worlds(self):
        """
        Returns the amount of worlds that are considered completed.
        """
        completed_worlds = sum(
            [(name_world_clear(world_num) in self.ctx.completed_levels) for world_num in range(1, 7 + 1)])
        logger.info(f"You have completed {completed_worlds} / {self.ctx.slot_data['bowser_world_unlock']} worlds.")

    def _cmd_goal(self):
        """
        Prints your goal condition
        """
        if self.ctx.username is None:
            logger.info(f"Not connecterd")
            return
        match self.ctx.slot_data["alternative_goal"]:
            case AlternativeGoal.option_bowser:
                logger.info(f"Your goal is bowser.")
            case AlternativeGoal.option_starcoins:
                logger.info(f"Your goal is starcoins.")
            case AlternativeGoal.option_hintmovies:
                logger.info(f"Your goal is hint movies.")
            case AlternativeGoal.option_all_levels:
                logger.info(f"Your goal is all levels.")
            case _:
                raise NotImplementedError
    def _cmd_kill(self):
        """
        A command that kills mario. Useful if you get soft-locked.
        """
        Utils.async_start(self.ctx.game_interface.kill_player())
        self.ctx.is_pending_death_link_reset = True

    def _cmd_refresh(self):
        """
        Refreshes the JIT cashe (by save and load savestate). Usefull if something like moves are not updating.
        """
        self.ctx.game_interface.should_clear += 1
        self.ctx.game_interface.clear_cache()

    def _cmd_reconnect_dolphin(self):
        """
        A command to try and rehook dolphin
        """
        self.ctx.game_interface.dolphin_client.connect()
        time.sleep(0.01)

    def _cmd_unlocks(self):
        """
        Gives you a list of which movement you have and have not unlocked
        """
        # NSMBWOptions.dont_rando_move
        logger.info("Unlocks info")
        if self.ctx.username is None:
            logger.info("Connect to server before running /unlocks")
        else:
            if self.ctx.slot_data["randomize_abilites"] == True:
                abilites_included = set(self.ctx.slot_data["abilites_included"])
                logger.info(f"Ablities")
                logger.info(f"You currently have: {set(self.ctx.unlocks) & abilites_included}")
                logger.info(f"And you are missing: {abilites_included - set(self.ctx.unlocks)}")
                logger.info(f"With the following excluded: {set(ABILITIES) - abilites_included}")
            else:
                logger.info("You dont have ability rando enabled.")
            if self.ctx.slot_data["randomize_level_elements"] == True:
                elements_included = set(self.ctx.slot_data["level_elements_included"])
                logger.info("Level Elements")
                logger.info(f"You currently have: {set(self.ctx.unlocks) & elements_included}")
                logger.info(f"And you are missing: {elements_included - set(self.ctx.unlocks)}")
                logger.info(f"With the following excluded: {set(ABILITIES) - elements_included}")
            else:
                logger.info("You dont have level element rando enabled.")

            if self.ctx.slot_data["randomize_enemies"] == True:
                enemies_included = set(self.ctx.slot_data["enemies_included"])
                logger.info("Enemies")
                logger.info(f"You currently have: {set(self.ctx.unlocks) & enemies_included}")
                logger.info(f"And you are missing: {enemies_included - set(self.ctx.unlocks)}")
                logger.info(f"With the following excluded: {set(ENEMIES) - enemies_included}")
            else:
                logger.info("You dont have enemy rando enabled.")

            if self.ctx.slot_data["randomize_powerups"] == True:
                logger.info("Powerups:")
                txt = ""
                for pow in range(POWERUP_COUNT):
                    if self.ctx.unlocked_powerups[pow] != 0:
                        txt += f"{POWERUP_UNLOCK[pow]} is unlocked\n"
                    else:
                        txt += f"{POWERUP_UNLOCK[pow]} is locked\n"
                logger.info(txt)
            else:
                logger.info(f"You do not have powerups enabled")

    def _cmd_change_collection_level(self, value):
        """
        Set this to specify how client should respond to a location being remotely collected.
        0 = ignore, 1= update if not important (castle / final level), 2= update even if important ( for same slot coop).
        Changes the collection level setting in host.yaml, is constant for all multiworld.
        """
        assert value in ["0", "1", "2"], "Allowed values are 0, 1 or 2"
        Utils.get_settings()["nsmbw_settings"]["collect_level"] = value

    def _cmd_toggle_auto_start(self):
        """
        Toggles the auto open setting in host.yaml, is constant for all multiworld.
        """
        Utils.get_settings()["nsmbw_settings"]["auto_start"] ^= True
        logger.info(f"Auto clear open: {Utils.get_settings()['nsmbw_settings']['auto_start']}")

    def _cmd_toggle_auto_start_riivolution(self):
        """
        Toggles the auto open setting in host.yaml, is constant for all multiworld.
        """
        Utils.get_settings()["nsmbw_settings"]["auto_start_riivolution"] ^= True
        logger.info(f"Auto open: {Utils.get_settings()['nsmbw_settings']['auto_start_riivolution']}")

    def _cmd_toggle_auto_load(self):
        """
        Toggles the auto load setting in host.yaml, is constant for all multiworld.
        """
        Utils.get_settings()["nsmbw_settings"]["auto_load"] ^= True
        logger.info(f"Auto load: {Utils.get_settings()['nsmbw_settings']['auto_load']}")

    def _cmd_toggle_auto_save(self):
        """
        Toggles the auto save setting in host.yaml, is constant for all multiworld.
        """
        Utils.get_settings()["nsmbw_settings"]["auto_save"] ^= True
        logger.info(f"Auto save: {Utils.get_settings()['nsmbw_settings']['auto_save']}")

    def _cmd_toggle_auto_close(self):
        """
        Toggles the auto close setting in host.yaml, is constant for all multiworld.
        """
        Utils.get_settings()["nsmbw_settings"]["auto_close"] ^= True
        logger.info(f"Auto close: {Utils.get_settings()['nsmbw_settings']['auto_close']}")

    def _cmd_auto_clear_cache(self):
        """Toggles wherethere to automatically clear cache. If you turn it of you will have to manually do it (by loading a savestate) for deathlink, movementrando and more to work. This is not saved betwen sestions"""
        self.ctx.game_interface.auto_clear_cache ^= True
        logger.info(f"Auto clear cache: {self.ctx.game_interface.auto_clear_cache}")

    def _cmd_reprompt_gamefile(self):
        """Repromt for selecting game file"""
        NSMBWSettings.GameFilePath.browse(Utils.get_settings()["nsmbw_settings"].game_file_path)

    def _cmd_force_hook(self) -> None:
        """Force restart the Dolphin hook process (unhook + fresh re-hook), runs 30 times"""
        # this command is inspired by  https://github.com/toent/Archipelago-MKWii/blob/main/worlds/mkwii/MKWii%20Client/mkwii_client.py#L107
        Utils.async_start(self.ctx.game_interface.force_hook())

    def _cmd_match_server_state(self):
        """Syncs your in game completion to the archipelago multiservers completed locations"""
        if Utils.get_settings()["nsmbw_settings"].collect_level == 0:
            logger.info(
                f"For this command to work you need to chage you collect_level setting, you can do this with /change_collection_level")
        self.ctx.update_memory_to_server_on_load()

    def _cmd_clear_inventory(self):
        """Clears your inventory of powerups (except 5).
        Useful if you want to grind inventory_powerups but have a full inventory"""
        for pow_num in range(1, POWERUP_COUNT + 2):
            current_pow = bytes_to_int(self.ctx.game_interface.get_inventory_items(pow_num))
            set_pow = int_to_bytes(min(current_pow, 5), 1)
            self.ctx.game_interface.set_inventory_items(set_pow, pow_num)

        logger.info(f"Successfully cleared your inventory of powerups")

    def _cmd_change_save_state_slot(self, slot):
        """Changes the save state slot used for saving data."""
        num = int(slot)
        assert 1 <= num <= 8
        self.ctx.save_slot = num

    def _cmd_change_clear_cache_slot(self, slot):
        """Changes the save state slot used for clrearing the JIT cache."""
        num = int(slot)
        assert 1 <= num <= 8
        Utils.get_settings()["nsmbw_settings"].clear_cache_save_slot = num

    def _cmd_rm_tmp(self):
        """Delete all files used for creating the patch files (including all created patches, but not save data) and other temporary files."""

        nsmbw_dir = Path(tempfile.gettempdir()) / "nsmbw"
        if nsmbw_dir.exists():
            shutil.rmtree(nsmbw_dir)

        Riivolution = Path(Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder)

        files = os.listdir(Riivolution)
        for file in files:
            if file.startswith("nsmbw_ap_"):
                shutil.rmtree(Riivolution / file)

        files = os.listdir(Riivolution / "riivolution")
        for file in files:
            if file.startswith("nsmbw_ap_"):
                os.remove(Riivolution / "riivolution" / file)

        logger.info(f"Successfully deleated all temporary files.")

    def _cmd_get_time(self):
        """Prints how much time you have recived"""
        if self.ctx.username is None:
            logger.info("Connect to server before running /get_time")
        elif self.ctx.slot_data["randomize_time"] != 0:
            logger.info(
                f" You have unlocked {self.ctx.time}/{self.ctx.slot_data['randomize_time']}, which is {self.ctx.time / self.ctx.slot_data['randomize_time'] * 500} mario seconds")
        else:
            logger.info("Time rando is disabled")

    def _cmd_boss_health(self):
        """Prints how much boss health you have recived"""
        if self.ctx.username is None:
            logger.info("Connect to server before running /get_time")
        elif self.ctx.slot_data["boss_health"] != 0:
            logger.info(
                f" You have unlocked {self.ctx.boss_health}/{9} items which means a boss takes {10 - self.ctx.boss_health} hits to kill")
        else:
            logger.info("Boss health rando is disabled")

    def _cmd_coins(self):
        if self.ctx.game_interface.memory_addresses is None:
            logger.info("Connect to server before running /coins")
            return

        current_coins = self.ctx.game_interface.get_coin_count()
        coins = current_coins + self.ctx.coin_overflow

        LEVEL = self.ctx.game_interface.get_world_level_num_in_level()
        if LEVEL == (0,0):
            logger.info(f"Not in a level")
            return

        req = LevelRules[name_base(*LEVEL)].amount_coins

        logger.info(f"You have collected {coins} out of {req}")

    # if Utils.get_settings()["nsmbw_settings"].debug_mode:
    def _cmd_get_level_rando(self, name):
        """Prints where a location has been rando to"""
        world_num, level_num = base_bijection(name)
        randod_world_num1, randod_level_num1 = locations.pos_to_level_name(
            self.ctx.slot_data["shuffled_level_order"][locations.level_name_to_pos(world_num, level_num)])
        logger.info(f"{name_base(randod_world_num1, randod_level_num1)}")

    def _cmd_get_level_rando_reversed(self, name):
        """Prints where a location has been rando from"""
        world_num, level_num = base_bijection(name)
        _index = self.ctx.slot_data["shuffled_level_order"].index(locations.level_name_to_pos(world_num, level_num))
        randod_level = locations.pos_to_level_name(_index)
        logger.info(f"{name_base(*randod_level)}")

    def _cmd_print_slot_data(self):
        """Prints all slot data, useful for debuging"""
        logger.info(f"SLOT DATA")
        logger.info(self.ctx.slot_data)

    def _cmd_print_settings(self):
        """Prints your settings, useful for debuging"""
        logger.info(f"SETTINGS")
        set_obj = Utils.get_settings()["nsmbw_settings"]
        data = ""
        for attr in set_obj:
            data += f"{attr}: {set_obj[attr]}"
        #data = dict(set_obj)
        logger.info(data)

    def _cmd_print_item_prossess_data(self):
        if self.ctx.username is not None:
            logger.info(f"""
            Filler                  : {self.ctx.filler}
            Traps                   : {self.ctx.traps}
            power-up grace          : {self.ctx.powerup_grace}
            unlocked_secret_exits   : {self.ctx.unlocked_secret_exits}
            """)
        else:
            logger.info(f"Not conencted to dolphin")

    def _cmd_print_other_data(self):
        if self.ctx.username is not None:
            logger.info(f"completed_levels: {self.ctx.completed_levels}")
        else:
            logger.info(f"Not conencted to dolphin")

    def _cmd_versions(self):
        """Prints out a few diffrent versions that is useful to know"""
        logger.info(
            f"OS                        : {sys.platform}\n"
            f"NSMBWAP Client version    : {self.ctx.manifest_version}\n"
            f"NSMBWAP generated version : {self.ctx.slot_data['NSMBW_Version'] if self.ctx.username is not None else 'not connected'}\n"
            f"UT version                : {UT_VERSION if tracker_loaded else 'Not loaded'}\n"
            f"AP version                : {Utils.__version__}\n"
            f"Server version            : {self.ctx.server_version}\n"
            f"Generator version         : {self.ctx.generator_version}\n"
            f"Game version              : {self.ctx.game_interface.current_game if self.ctx.game_interface.memory_addresses is not None else 'Dolphin not connected'}\n"
            f"Game revision             : {self.ctx.game_interface.game_rev if self.ctx.game_interface.memory_addresses is not None else 'Dolphin not connected'}\n"
        )

    def _cmd_get_error(self):
        """Prints latest stacktrace"""
        logger.info(f"Prints latest stacktrace")
        logger.info(traceback.format_exc())

    def _cmd_debug(self):
        """Runs most debug commands, please post results in the NSMBW discord thread in the archipelago discord server."""
        logger.info(
            f"Runs most debug commands, post the results in the NSMBW discord thread in the archipelago discord server.")

        logger.info("---- Do basic basic refresh ----")
        self._cmd_save()
        if self.ctx.game_interface.memory_addresses is not None:
            self.ctx.game_interface.connect_to_game()
        self._cmd_refresh()
        self._cmd_refresh_mod()
        self._cmd_match_server_state()
        # self._cmd_reapply_checks() # send invent pow, dont run

        logger.info("---- Info regarding setup ----")
        self._cmd_help()
        self._cmd_versions()
        self._cmd_debug_deathlink()
        self._cmd_status()
        self._cmd_print_slot_data()
        self._cmd_print_settings()
        self._cmd_print_other_data()

        logger.info("---- Info regarding items ----")
        self._cmd_received()
        self._cmd_missing()
        self._cmd_unlocks()
        self._cmd_starcoins()
        self._cmd_worlds_unlocked()
        self._cmd_completed_worlds()
        self._cmd_get_time()
        self._cmd_print_item_prossess_data()

        logger.info("---- Info regarding errors ----")
        if tracker_loaded:
            self._cmd_faris_asked()

        self._cmd_get_error()
