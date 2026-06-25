from enum import StrEnum


game_name = "NSMBW"

LEVELS_PER_WORLD = [8, 8, 8, 9, 8, 9, 9, 10, 8]


class ITEM:
    class POWERUP(StrEnum):
        Super_Mushroom = "Super Mushroom"
        Fire_Flower = "Fire Flower"
        Mini_Mushroom = "Mini Mushroom"
        Propeller_Mushroom = "Propeller Mushroom"
        Penguin_Suit = "Penguin Suit"
        Ice_Flower = "Ice Flower"

    class MOVEMENT(StrEnum):
        GroundPound = "Ground pound"
        WallJump = "Wall jump"
        Crouch = "Crouch"
        Yoshi = "Yoshi"
        Swim = "Swim"
        PSwitch = "p-switch"
        RedSwitch = "!-switch"
        Star = "Star"
        Climb = "Climb"
        Carry = "Carry"
        Door = "Door"
        QuestSwitch = "?-switch"
        SpinJump = "Spin jump"
        Pipe = "Pipe"
        Jump = "Jump"
        Run = "Run"
        ButtonLeft = "Button left"
        ButtonRight = "Button right"
        ButtonUp = "Button up"
        ButtonDown = "Button down"
        CheckPoint = "Check point"

    class TRAPS(StrEnum):
        LoosePowerupTrap = "Loose powerup trap"
        GoombaTrap = "Goomba trap"
        DeathTrap = "Death trap"
        TimeTrap = "Time trap"
        RobberyTrap = "Robbery trap"
        ShrinkTrap = "Shrink trap"
        LiteratureTrap = "Literature trap"
        ThrowTrap = "Throw trap"
        ReverseControlTrap = "Reverse Control trap"
        MovementLockTrap   = "Movement lock trap"
        SlowTrap    = "Slow Trap"

    class FILLER(StrEnum):
        FillInventory = "fill inventory"
        OneUps = "1-ups"
        CoinOne     = "Coin x01"
        CoinTen     = "Coin x10"
        CoinFifty   = "Coin x50"
        PowerUp = "Random Power-up"
        SuperSpeed = "Super Speed"

    StarCoin = "Starcoin"
    Time = "Time left"
    GlitchedLogic = "glitched logic"



POWERUP_UNLOCK = list([c.value for c in ITEM.POWERUP])
MOVEMENT_UNLOCKS = list([c.value for c in ITEM.MOVEMENT])

TRAPS = list([c.value for c in ITEM.TRAPS])
FILLER = list([c.value for c in ITEM.FILLER])


SUPPORTED_VERSIONS = ["E2"]

PLAYER_COUNT = 1

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

def name_base(world_num : int, level_num : int) -> str:
    assert_valid_level(world_num, level_num)
    return f"{world_num}-{mod_level_name(world_num,level_num)}"

def assert_valid_level(world_num : int, level_num : int) -> None:
    from worlds.nsmbw.locations import LEVELS_PER_WORLD
    assert 1 <= world_num <= 9
    assert 1 <= level_num <= LEVELS_PER_WORLD[world_num-1], f"Level {level_num} is not valid for world {world_num}"

def name_level(world_num : int, level_num : int) -> str:
    return f"{name_base(world_num,level_num)} clear"

def name_starcoin(world_num : int, level_num : int, scnum : int) -> str:
    return f"{name_base(world_num,level_num)} sc{scnum}"

def name_secret(world_num : int, level_num : int) -> str:
    return f"{name_base(world_num,level_num)} Secret exit"

def name_world_clear(world_num : int) ->  str:
    assert 1 <= world_num <= 8, f"world_num {world_num} is not valid"
    return f"World{world_num} clear"
def name_tower_clear(world_num : int) -> str:
    assert 1 <= world_num <= 8
    return f"World{world_num} 1/2 clear" #f"Tower{world_num}_clear" #

def name_hintmovie(i:int) -> str:
    from worlds.nsmbw.NSMBW_client.NSMBWInterface import HINTMOVIE_COUNT
    assert 1 <= i <= HINTMOVIE_COUNT
    return f"Hintmovie{i:02}"

def name_inventory(i : int) -> str:
    assert 1 <= i <= 999, f" i: {i} is too large"
    return f"Inventory powerup {i:03}"

def name_world_unlock(world_num : int):
    assert 1 <= world_num <= 9
    return f"World{world_num} progressive"

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