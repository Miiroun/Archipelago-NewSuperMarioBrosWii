import asyncio
from enum import Enum
from logging import Logger
from typing import Dict, Optional

from dolphin_interface_client import *
from worlds.nsmbw.items import ITEM_NAME_TO_ID
from worlds.oot.Messages import int_to_bytes


class ConnectionState(Enum):
    DISCONNECTED = 0
    IN_GAME = 1
    IN_MENU = 2
    MULTIPLE_DOLPHIN_INSTANCES = 3
    SCOUTS_SENT = 4
    IN_WORLDMAP = 5

_SUPPORTED_VERSIONS = ["US"]
from memoryAddresses import GAMES

# game constants
HUD_MESSAGE_DURATION = 7.0
HUD_MAX_MESSAGE_SIZE = 194

STARCOIN_COUNT = 65
LEVEL_COUNT = 77
POWERUP_COUNT = 7
ITEM_ID_TO_NAME = {v: k for k, v in ITEM_NAME_TO_ID.items()}

ROM_FILE_NAME = r"New Super Mario Bros. Wii (USA) (En,Fr,Es) (Rev 2).wbfs"


class NSMBWInterface():
    """Interface sitting in front of the DolphinClient to provide higher level functions for interacting with Metroid Prime"""

    dolphin_client: DolphinClient
    connection_status: str
    logger: Logger
    _previous_message_size: int = 0
    game_id_error: Optional[str] = None
    game_rev_error: int
    current_game: Optional[str] = ""
    relay_trackers: Optional[Dict[Any, Any]]
    
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.dolphin_client = DolphinClient(logger)
    


    def connect_to_game(self):
        """Initializes the connection to dolphin and verifies it is connected to Metroid Prime"""
        try:
            self.dolphin_client.connect()
            game_id = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS, 6)
            
            print("gameeid:",game_id) # remove later

            try:
                game_rev: Optional[int] = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS + 7, 1)[0]
            except:
                game_rev = None
            # The first read of the address will be null if the client is faster than the emulator
            self.current_game = None
            for version in _SUPPORTED_VERSIONS:
                if (
                    game_id == GAMES[version]["game_id"]
                    and game_rev == GAMES[version]["game_rev"]
                ):
                    self.current_game = version
                    break
            if (
                self.current_game is None
                and self.game_id_error != game_id
                and game_id != b"\x00\x00\x00\x00\x00\x00"
            ):
                self.logger.info(
                    f"Connected to the wrong game ({game_id}, rev {game_rev}), please connect to rigtb game version"
                )
                self.game_id_error = game_id
                if game_rev:
                    self.game_rev_error = game_rev
            if self.current_game:
                self.logger.info("NSMBW Disc Version: " + self.current_game)
        except DolphinException:
            pass

    def disconnect_from_game(self):
        self.dolphin_client.disconnect()
        self.logger.info("Disconnected from Dolphin Emulator")

    def get_connection_state(self):
        try:
            connected = self.dolphin_client.is_connected()
            if not connected or self.current_game is None:
                return ConnectionState.DISCONNECTED
            elif self.is_in_level():
                return ConnectionState.IN_GAME
            elif self.is_in_worldmap():
                return ConnectionState.IN_WORLDMAP
            else:
                return ConnectionState.IN_MENU
        except DolphinException:
            return ConnectionState.DISCONNECTED
    def is_in_level(self) -> bool:
        """Check if the player is in the actual game rather than the main menu"""

        return self.get_player_status() == b'\x00'

    def is_in_worldmap(self) -> bool:
        return self.get_player_status() == b'\x02'

    def reset_relay_tracker_cache(self):
        self.relay_trackers = None

    def update_relay_tracker_cache(self):
        #metroid had lots of code here that i dont understand
        pass


    def send_hud_message(self, message: str) -> bool:
        message = f"&just=center;{message}"
        if not self.current_game:
            return False

        if self.current_game == "jpn":
            message = f"&push;&font=C29C51F1;{message}&pop;"
        current_value = self.dolphin_client.read_address(
            GAMES[self.current_game]["HUD_TRIGGER_ADDRESS"], 1
        )
        if current_value == b"\x01":
            return False
        self._save_message_to_memory(message)
        self.dolphin_client.write_address(
            GAMES[self.current_game]["HUD_TRIGGER_ADDRESS"], b"\x01"
        )
        return True

    def _save_message_to_memory(self, message: str):
        encoded_message = message.encode("utf-16_be")[:HUD_MAX_MESSAGE_SIZE]

        if len(encoded_message) == self._previous_message_size:
            encoded_message += b"\x00 "  # Add a space to the end of the message to force the game to update the message if it is the same size

        self._previous_message_size = len(encoded_message)

        encoded_message += (
            b"\x00\x00"  # Game expects a null terminator at the end of the message
        )

        if len(encoded_message) & 3:
            # Ensure the size is a multiple of 4
            num_to_align = (len(encoded_message) | 3) - len(encoded_message) + 1
            encoded_message += b"\x00" * num_to_align

        assert self.current_game
        self.dolphin_client.write_address(
            GAMES[self.current_game]["HUD_MESSAGE_ADDRESS"], encoded_message
        )
    
    #my code-------------------------------------------------

    # just created
    def get_sc(self):
        address = GAMES[self.current_game]["SC_current_level"]
        return self.dolphin_client.read_address(address,4*3)
    def starcoin_stockage(self):
        address = GAMES[self.current_game]["SC_stockage"]
        return self.dolphin_client.read_address(address,1)
    def get_level_world(self):
        address = GAMES[self.current_game]["level_world"]
        return self.dolphin_client.read_address(address,4)
    def get_level_stats(self, level_num):
        address = GAMES[self.current_game]["level_stat"] + level_num * 4
        return self.dolphin_client.read_address(address,4)
    def get_inventory_items(self, type_num):
        address = GAMES[self.current_game]["inventory_items"] + type_num
        return self.dolphin_client.read_address(address,1)
    def get_world_level(self):
        address = GAMES[self.current_game]["world_level"]
        return self.dolphin_client.read_address(address,1)
    def get_level_level(self):
        address = GAMES[self.current_game]["level_level"]
        return self.dolphin_client.read_address(address,1)
    def get_hm_stats(self, hm_num):
        address = GAMES[self.current_game]["HM_stats"] +hm_num
        return self.dolphin_client.read_address(address,1)
    def get_worldstats_selectmenu(self):
        address = GAMES[self.current_game]["Worldstats_selectmenu"]
        return self.dolphin_client.read_address(address,1)
    def get_powerupstate(self):
        #address1 = GAMES[self.current_game]["powerup_state1"]
        address2 = GAMES[self.current_game]["powerup_state2"]
        #powerup_state1 = self.dolphin_client.read_address(address1,1)
        powerup_state2 = self.dolphin_client.read_address(address2,1)
        #assert powerup_state1 == powerup_state2, "Powerup states do not match, please report diffrense"
        return powerup_state2
    def get_player_status(self):
        address = GAMES[self.current_game]["player_status"]
        return self.dolphin_client.read_address(address,1)


    def set_worldstats(self,world_num : int, status : bytes):
        address = GAMES[self.current_game]["Worldstats_selectmenu"] + (world_num-1)
        self.dolphin_client.write_address(address, status)
    def set_powerupstate(self, powerup_state : bytes):
        #address1 = GAMES[self.current_game]["powerup_state1"]
        address2 = GAMES[self.current_game]["powerup_state2"]
        #self.dolphin_client.write_address(address1, powerup_state) # proberbly unnessesary
        self.dolphin_client.write_address(address2, powerup_state)
    def set_sc_count(self, coint_num : int):
        address = GAMES[self.current_game]["sc_count"]
        self.dolphin_client.write_address(address, int_to_bytes(coint_num,1))
    def set_inventory_items(self, value, type_num):
        address = GAMES[self.current_game]["inventory_items"] + type_num
        self.dolphin_client.write_address(address, value)
    def set_level_stats(self, level_num, data):
        address = GAMES[self.current_game]["level_stat"] + level_num * 4
        self.dolphin_client.write_address(address,data)

    def update_inventory_items(self, type_num):
        address = GAMES[self.current_game]["inventory_items"]
        amount = self.get_inventory_items(type_num)
        self.set_inventory_items(amount+b'x\01', type_num)



    async def kill_player(self):
        death_addres = 0x800555DC
        self.dolphin_client.write_address(death_addres, b'\60\x00\x00\x00')
        await asyncio.sleep(0.01)
        self.dolphin_client.write_address(death_addres, b'\x48\x00\x00\x28')


