import os
from logging import Logger
from time import sleep
from typing import Any
import dolphin_memory_engine  # type: ignore
import subprocess

import psutil

import Utils
import logging
logger = logging.getLogger("Client")


# game constants
GC_GAME_ID_ADDRESS = 0x80000000

# from mkdd
DME_DOLPHIN_PROCESS_NAME_ENV_VARIABLE = "DME_DOLPHIN_PROCESS_NAME"
if Utils.get_settings()["nsmbw_settings"].dolphin_process_name:
    os.environ[DME_DOLPHIN_PROCESS_NAME_ENV_VARIABLE] = Utils.get_settings()["nsmbw_settings"].dolphin_process_name
elif DME_DOLPHIN_PROCESS_NAME_ENV_VARIABLE in os.environ:
    del os.environ[DME_DOLPHIN_PROCESS_NAME_ENV_VARIABLE]

class DolphinException(Exception):
    pass


class DolphinClient:
    dolphin: dolphin_memory_engine  # type: ignore
    logger: Logger

    def __init__(self, logger: Logger):
        self.dolphin = dolphin_memory_engine
        self.logger = logger

    def is_connected(self):
        try:
            self.__assert_connected()
            return True
        except Exception as e:
            print(e)
            return False

    def connect(self):
        if not self.dolphin.is_hooked():
            self.dolphin.hook()
            sleep(0.01)
        if (not self.is_connected()) or (not self.dolphin.is_hooked()):
            error_mess = ("""
Dolphin Connection error, verify the following in this order:
      1) The game is running in the dolphin emulator.
      2) You dont have multiple instances of dolphin open (except your ONE game library).
      3) Assert Memory Override (MEM1 and MEM2) is disabled. Dolphin -> Settings -> Advanced -> Emulated Memory Size Override.
      4) Test running the client in administer mode.
      5) You have not renamed the dolphin exe and are not running on a fork.
      6) Your dolphin emulator is recent (newer than 2026.1)
      7) Enable MMU in Dolphin -> Settings -> Advanced -> Enable MMU.
      8) Reset you dolphin settings Dolphin -> Settings -> Advanced -> Reset All Settings.
      9) Post your error in the NSMBW discord, with a screenshot and your log file.
                          """)
            logger.info(error_mess)
            raise DolphinException("Could not connect to Dolphin")

    def disconnect(self):
        if self.dolphin.is_hooked():
            self.dolphin.un_hook()

    def __assert_connected(self):
        """Custom assert function that returns a DolphinException instead of a generic RuntimeError if the connection is lost"""
        try:
            self.dolphin.assert_hooked()
            # For some reason the dolphin_memory_engine.is_hooked() function doesn't recognize when the game is closed, checking if memory is available will assert the connection is alive
            self.dolphin.read_bytes(GC_GAME_ID_ADDRESS, 1)
        except RuntimeError as e:
            #self.disconnect()
            print(e)
            raise DolphinException(e)

    def verify_target_address(self, target_address: int, read_size: int):
        """Ensures that the target address is within the valid range for GC memory"""
        if target_address < 0x80000000 or target_address + read_size > 0x81800000:
            raise DolphinException(
                f"{target_address:x} -> {target_address + read_size:x} is not a valid for GC memory"
            )

    def read_pointer(self, pointer: int, offset: int, byte_count: int) -> Any:
        self.__assert_connected()

        address = None
        try:
            address = self.dolphin.follow_pointers(pointer, [0])
        except RuntimeError:
            return None

        if not self.dolphin.is_hooked():
            raise DolphinException("Dolphin no longer connected")

        address += offset
        return self.read_address(address, byte_count)

    def read_address(self, address: int, bytes_to_read: int) -> bytes:
        self.__assert_connected()
        self.verify_target_address(address, bytes_to_read)
        result = self.dolphin.read_bytes(address, bytes_to_read)
        return result

    def write_pointer(self, pointer: int, offset: int, data: Any):
        self.__assert_connected()
        address = None
        try:
            address = self.dolphin.follow_pointers(pointer, [0])
        except RuntimeError:
            return None

        if not self.dolphin.is_hooked():
            raise DolphinException("Dolphin no longer connected")

        address += offset
        return self.write_address(address, data)

    def write_address(self, address: int, data: Any):
        self.__assert_connected()
        result = self.dolphin.write_bytes(address, data)
        return result

    #nsbmw adition



def assert_no_running_dolphin() -> bool:
    """verifies no existing instances of dolphin are running."""
    if get_num_dolphin_instances() > 0:
        return False
    return True


def get_num_dolphin_instances() -> int:
    try:
        count = 0
        for process in psutil.process_iter():
            if process.name().casefold().startswith("dolphin"):
                count += 1
        return count
    except Exception as e:
        print("Failed to get number of dolphin instances")
        print(e)
        return 0
    
