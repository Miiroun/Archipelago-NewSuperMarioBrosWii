from enum import StrEnum

game_name = "NSMBW"


class ITEM:
    class POWERUP(StrEnum):
        Super_Mushroom = "Super_Mushroom"
        Fire_Flower = "Fire_Flower"
        Mini_Mushroom = "Mini_Mushroom"
        Propeller_Mushroom = "Propeller_Mushroom"
        Penguin_Suit = "Penguin_Suit"
        Ice_Flower = "Ice_Flower"
    class MOVEMENT(StrEnum):
        GroundPound = "ground_pound"
        WallJump = "wall_jump"
        Crouch = "crouch"
        Yoshi = "yoshi"
        Swim = "swim"
        PSwitch = "p-switch"
        RedSwitch = "!-switch"
        Star = "star"
        Climb = "climb"
        Carry = "carry"
        Door = "door"
        QuestSwitch = "?-switch"
        SpinJump = "spin_jump"
        Pipe = "pipe"
        Jump = "jump"
        Run = "run"
        ButtonLeft = "button_left"
        ButtonRight = "button_right"
        ButtonUp = "button_up"
        ButtonDown = "button_down"

    StarCoin = "Starcoin"
    Time = "Time_left"
    GlitchedLogic = "glitched_logic"



POWERUP_UNLOCK = list([c.value for c in ITEM.POWERUP])
MOVEMENT_UNLOCKS = list([c.value for c in ITEM.MOVEMENT])

TRAPS = ["Loose_powerup_trap", "Goomba_trap", "Death_trap"] #, "Time_trap",
FILLER = ["fill_inventory", "1ups"]


SUPPORTED_VERSIONS = ["E2"]

PLAYER_COUNT = 1

def mod_level_name(worldnum : int, levelnum : int) -> str:
    shift = 1 if worldnum in [7,8] else 0
    new_level = levelnum - shift
    if (worldnum, levelnum) in [(3,6),(5,6),(7,7)]:
        return "G"
    if worldnum !=9:
        if new_level == 7:
            return "T"
        elif new_level == 8:
            return "C"
        elif new_level == 9:
            return "A"
    return str(levelnum)

def assert_valid_level(world_num : int, level_num : int) -> None:
    from worlds.nsmbw.locations import LEVELS_PER_WORLD
    assert 1 <= world_num <= 9
    assert 1 <= level_num <= LEVELS_PER_WORLD[world_num-1]

def name_level(world_num : int, level_num : int) -> str:
    assert_valid_level(world_num, level_num)
    return f"{world_num}-{mod_level_name(world_num,level_num)}_clear"

def name_starcoin(world_num : int, level_num : int, scnum : int) -> str:
    assert_valid_level(world_num, level_num)
    return f"{world_num}-{mod_level_name(world_num,level_num)}_sc{scnum}"

def name_secret(world_num : int, level_num : int) -> str:
    assert_valid_level(world_num, level_num)
    return f"Secret_exit{world_num}-{mod_level_name(world_num, level_num)}"

def name_hintmovie(i:int) -> str:
    from worlds.nsmbw.NSMBW_client.NSMBWInterface import HINTMOVIE_COUNT
    assert 1 <= i <= HINTMOVIE_COUNT
    return f"Hintmovie{i:02}"

def name_inventory(i : int) -> str:
    assert 1 <= i <= 999
    return f"Inventory_powerup_{i:03}"