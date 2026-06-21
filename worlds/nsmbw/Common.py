from enum import StrEnum


game_name = "NSMBW"

LEVELS_PER_WORLD = [8, 8, 8, 9, 8, 9, 9, 10, 8]


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

    class TRAPS(StrEnum):
        LoosePowerupTrap = "Loose_powerup_trap"
        GoombaTrap = "Goomba_trap"
        DeathTrap = "Death_trap"
        TimeTrap = "Time_trap"
        RobberyTrap = "Robbery_trap"
        ShrinkTrap = "Shrink_trap"
        LiteratureTrap = "Literature_trap"

    class FILLER(StrEnum):
        FillInventory = "fill_inventory"
        OneUps = "1-ups"
        CoinOne = "Coin x01"
        CoinFifty = "Coin x50"
        PowerUp = "Filler Power-up"

    StarCoin = "Starcoin"
    Time = "Time_left"
    GlitchedLogic = "glitched_logic"



POWERUP_UNLOCK = list([c.value for c in ITEM.POWERUP])
MOVEMENT_UNLOCKS = list([c.value for c in ITEM.MOVEMENT])

TRAPS = list([c.value for c in ITEM.TRAPS])
FILLER = list([c.value for c in ITEM.FILLER])


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

def name_base(world_num : int, level_num : int) -> str:
    assert_valid_level(world_num, level_num)
    return f"{world_num}-{mod_level_name(world_num,level_num)}"

def assert_valid_level(world_num : int, level_num : int) -> None:
    from worlds.nsmbw.locations import LEVELS_PER_WORLD
    assert 1 <= world_num <= 9
    assert 1 <= level_num <= LEVELS_PER_WORLD[world_num-1]

def name_level(world_num : int, level_num : int) -> str:
    return f"{name_base(world_num,level_num)}_clear"

def name_starcoin(world_num : int, level_num : int, scnum : int) -> str:
    return f"{name_base(world_num,level_num)}_sc{scnum}"

def name_secret(world_num : int, level_num : int) -> str:
    return f"Secret_exit{name_base(world_num,level_num)}"

def name_world_clear(world_num : int) ->  str:
    assert 1 <= world_num <= 8
    return f"World{world_num}_clear"
def name_tower_clear(world_num : int) -> str:
    assert 1 <= world_num <= 8
    return f"World{world_num}_tower" #f"Tower{world_num}_clear" #

def name_hintmovie(i:int) -> str:
    from worlds.nsmbw.NSMBW_client.NSMBWInterface import HINTMOVIE_COUNT
    assert 1 <= i <= HINTMOVIE_COUNT
    return f"Hintmovie{i:02}"

def name_inventory(i : int) -> str:
    assert 1 <= i <= 999
    return f"Inventory_powerup_{i:03}"

def name_world_unlock(world_num : int):
    assert 1 <= world_num <= 9
    return f"World{world_num}_progressive"

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