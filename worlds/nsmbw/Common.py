from __future__ import annotations

import math
from enum import StrEnum
from typing import *
from .Utils import *
from Utils import *
import Utils


game_name = "NSMBW"

LEVELS_PER_WORLD = [8, 8, 8, 9, 8, 9, 9, 10, 8]

HINTMOVIE_COUNT = 65
LEVEL_COUNT = 77


DEPRIO_HM = [2,4,5,13,28,38,39,46,47,53,57,62,65]
DEPRIO_HM += [6, 9, 27, 37, 41, 43,51, 54, 55] # broken ?


# exit_type is if secret or normal exit 1== normal, 2==secret
class SecretExit(NamedTuple):
    world : int
    level : int
    level_to : int | None
    exit_type : Literal[1,2, None]
    is_item : bool | None

    def __eq__(self, other : Any ):
        if not isinstance(other, SecretExit):
            return NotImplemented
        return (self.world == other.world) and (self.level == other.level)

SECRET_EXIT : List[SecretExit] = [
    SecretExit(1, 3, 0, 2, False), SecretExit(2, 4, 8, 2, True), SecretExit(2, 6, 0, 2, False), SecretExit(3, 4, 5, 2, True),
    SecretExit(3, 5, 0, 2, False), SecretExit(3, 6, 0, 2, False), SecretExit(4, 6, 8, 2, True), SecretExit(4, 7, 0, 2, False),
    SecretExit(5, 6, 0, 2, False), SecretExit(6, 5, 8, 2, True), SecretExit(6, 6, 0, 2, False), SecretExit(7, 5, 9, 1, True),
    SecretExit(7, 7, 5, 2, True), SecretExit(7, 8, 6, 2, True), SecretExit(8, 2, 7, 2, True), SecretExit(8, 7, 10, 1, True)]

class ITEM:
    class POWERUP(StrEnum):
        Super_Mushroom = "Super Mushroom"
        Fire_Flower = "Fire Flower"
        Mini_Mushroom = "Mini Mushroom"
        Propeller_Mushroom = "Propeller Mushroom"
        Penguin_Suit = "Penguin Suit"
        Ice_Flower = "Ice Flower"

    class ABILITIES(StrEnum):
        GroundPound = "Ground pound"
        WallJump = "Wall jump"
        Crouch = "Crouch"
        Yoshi = "Yoshi"
        Swim = "Swim"
        Star = "Star"
        Climb = "Climb"
        Carry = "Carry"
        SpinJump = "Spin jump"
        Jump = "Jump"
        Run = "Run"
        ButtonLeft      = "Button left"
        ButtonRight     = "Button right"
        ButtonUp        = "Button up"
        ButtonDown      = "Button down"

    class LEVELELEMENTS(StrEnum):
        Pipe = "Pipe"
        Door = "Door"
        PSwitch = "p-switch"
        QuestSwitch = "?-switch"
        RedSwitch = "!-switch"
        CheckPoint      = "Check point"


    class ENEMIES(StrEnum):
        Goomba   = "Goomba"

    class TRAPS(StrEnum):
        LosePowerupTrap     = "Lose powerup trap"
        GoombaTrap          = "Goomba trap"
        DeathTrap           = "Death trap"
        TimeTrap            = "Time trap"
        RobberyTrap         = "Robbery trap"
        ShrinkTrap          = "Shrink trap"
        LiteratureTrap      = "Literature trap"
        ThrowTrap           = "Throw trap"
        ReverseControlTrap  = "Reverse Control trap"
        MovementLockTrap    = "Movement lock trap"
        SlowTrap            = "Slow Trap"
        GravityTrap         = "Gravity Trap"

    class FILLER(StrEnum):
        FillInventory   = "fill inventory"
        OneUps          = "1-ups"
        CoinOne         = "Coin x01"
        CoinTen         = "Coin x10"
        CoinFifty       = "Coin x50"
        PowerUp         = "Random Power-up"
        SuperSpeed      = "Super Speed"
        #ToadHouse = "Toad House"
        LowGravity      = "Low Gravity"

    class FAKE(StrEnum):
        InventoryPow        = "InventoryPowAccessible"
        InventoryPowNoToad  = "InventoryPowAccessibleNoToad"

    StarCoin        = "Starcoin"
    Time            = "Time"
    GlitchedLogic   = "glitched logic"
    BossHealth      = "Boss Health"



POWERUP_UNLOCK = list([c.value for c in ITEM.POWERUP])
POWERUP_COUNT = len(POWERUP_UNLOCK)
ABILITIES = list([c.value for c in ITEM.ABILITIES])
LEVEL_ELEMENTS = list([c.value for c in ITEM.LEVELELEMENTS])
ENEMIES = list([c.value for c in ITEM.ENEMIES])
UNLOCKS = ABILITIES + LEVEL_ELEMENTS + ENEMIES

TRAPS = list([c.value for c in ITEM.TRAPS])
FILLER = list([c.value for c in ITEM.FILLER])


SUPPORTED_VERSIONS = ["E2"]

PLAYER_COUNT = 4

LEVELS = []
for world_num in range(1,9+1):
    for level_num in range(1, LEVELS_PER_WORLD[world_num-1]+1):
        LEVELS.append((world_num, level_num))


def mod_level_name(worldnum : int, levelnum : int) -> str:
    shift = 1 if worldnum in [7,8] else 0
    new_level = levelnum - shift
    if (worldnum, levelnum) in [(3,6),(4,6),(5,6),(7,7)]:
        return "G"
    if worldnum !=9:
        if new_level == 7:
            return "T"
        elif new_level == 8:
            return "C"
        elif new_level == 9:
            return "A"
    return str(levelnum)

def name_base(world_num : int, level_num : int, assert_=True) -> str:
    if assert_:
        assert_valid_level(world_num, level_num)
    return f"{world_num}-{mod_level_name(world_num,level_num)}"

def assert_valid_level(world_num : int, level_num : int) -> None:
    assert 1 <= world_num <= 9, f"world {world_num} is invalid"
    assert 1 <= level_num <= LEVELS_PER_WORLD[world_num-1], f"Level {level_num} is not valid for world {world_num}"

def name_level(world_num : int, level_num : int) -> str:
    return f"{name_base(world_num,level_num)} clear"

def name_starcoin(world_num : int, level_num : int, scnum : int) -> str:
    return f"{name_base(world_num,level_num)} sc{scnum}"

def name_secret(secret_exit : SecretExit) -> str:
    if secret_exit.exit_type == 2:
        return f"{name_base(secret_exit.world,secret_exit.level)} Secret exit"
    elif secret_exit.exit_type == 1:
        return f"{name_base(secret_exit.world,secret_exit.level)} Normal exit"
    else:
        raise ValueError(f"Unknown exit_type: {secret_exit.exit_type}")

def name_world_clear(world_num : int) ->  str:
    assert 1 <= world_num <= 8, f"world_num {world_num} is not valid"
    return f"World{world_num} clear"
def name_tower_clear(world_num : int) -> str:
    assert 1 <= world_num <= 8
    return f"World{world_num} 1/2 clear" #f"Tower{world_num}_clear" #

def name_hintmovie(i:int) -> str:
    assert 1 <= i <= HINTMOVIE_COUNT
    return f"Hintmovie {i:02}"

def name_inventory(i : int) -> str:
    assert 1 <= i <= 999, f" i: {i} is too large"
    return f"Inventory powerup {i:03}"

def name_world_unlock(world_num : int):
    assert 1 <= world_num <= 9
    return f"World{world_num} progressive"

def name_1ups(world_num : int, level_num : int) -> str:
    assert_valid_level(world_num,level_num)
    return f"{name_base(world_num,level_num)} 1up"


def base_bijection(name : str ) -> tuple[int, int]:
    for world_num in range(1,9+1):
        for level_num in range(1,LEVELS_PER_WORLD[world_num-1]+1):
            if name_base(world_num, level_num) == name:
                return world_num, level_num
    raise ValueError(f"Level: {name} not found")

def level_bijection(name : str ) -> tuple[int, int]:
    for world_num in range(1,9+1):
        for level_num in range(1,LEVELS_PER_WORLD[world_num-1]+1):
            if name_level(world_num, level_num) == name:
                return world_num, level_num
    raise ValueError(f"Level: {name} not found")

def sc_bijection(name : str ) -> tuple[int, int, int]:
    for world_num in range(1,9+1):
        for level_num in range(1,LEVELS_PER_WORLD[world_num-1]+1):
            for sc_num in range(1,3+1):
                if name_starcoin(world_num,level_num,sc_num) == name:
                    return world_num, level_num, sc_num
    raise ValueError(f"SC: {name} not found")

def get_name_base_of_last_level_in_world(world_num : int) -> str:
    return f"{world_num}-{mod_level_name(world_num,LEVELS_PER_WORLD[world_num-1])}"


def get_time_math(world : "NSMBWworld", time : int):
    return math.ceil( (time/500) * world.options.randomize_time.value)

LEVEL_NAMES = list([name_base(world_num, level_num) for world_num, level_num in LEVELS])
