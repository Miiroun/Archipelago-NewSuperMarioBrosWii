from __future__ import annotations

from typing import TYPE_CHECKING, List

from rule_builder.rules import *
from rule_builder.options import OptionFilter
from .options import RandomizeMovment, RandomizePowerups


if TYPE_CHECKING:
    from .world import NSMBWworld

DEPRIO_HM = [2,4,5,13,28,38,39,46,47,53,57,62,65]
def specific_hintmovie_requierments(world: NSMBWworld) -> List:
    # info about these harvested from https://gamefaqs.gamespot.com/wii/960544-new-super-mario-bros-wii/faqs/58584
    rule_completed_everything = Has("Starcoin", count=231)  & Has("Victory")# dont want to implement complex, just deprioritize
    requierments = [
        #starcoin cost, level requierment, generic requierment
        [3, (1,1), True_()],   #01
        [5, (1,1), rule_completed_everything],  # 02 #find every normal goal in world1-9
        [3, (1,2), Has("Starcoin", count=5)],  # 03
        [3, (1,3), rule_completed_everything],  # 04 #find every normal goal in world1-9
        [5, (1,3), Has("World1_level8_cleared")],  # 05
        [5, (1,7), Has("Starcoin", count=10)],  # 06
        [5, (1,5), Has("Starcoin", count=30)],  # 07
        [0, (2,1), Has("Starcoin", count=15)],  # 08
        [3, (2,1), Has("Starcoin", count=1)],  # 09
        [0, (2,2), Has("Starcoin", count=95)],  # 10
        [3, (2,2), Has("Starcoin", count=150)],  # 11
        [5, (2,3), Has("Starcoin", count=1)]  ,# 12
        [5, (2,4), rule_completed_everything] , # 13 #find every normal adn secret goal in world1-9
        [5, (2,5), Has("World2_level8_cleared")],  # 14
        [5, (2,5), Has("Starcoin", count=215)],  # 15
        [10, (2,6), Has("Starcoin", count=25)],  # 16
        [0, (3,1), Has("Starcoin", count=65)] , # 17
        [3, (3,1), Has("Starcoin", count=35)] , # 18
        [5, (3,2), Has("Starcoin", count=165)] , # 19
        [5, (3,2), Has("Starcoin", count=190)]  ,# 20
        [0, (3,3), Has("Starcoin", count=140)] , # 21
        [3, (3,3), Has("World3_level8_cleared")],  # 22
        [5, (3,3), Has("Starcoin", count=195)] , # 23
        [5, (3,6), Has("Starcoin", count=140)],  # 24
        [5, (3,5), Has("Starcoin", count=130)] , # 25
        [3, (4,1), Has("Starcoin", count=45)]  ,# 26
        [5, (4,2), Has("Starcoin", count=175)] , # 27
        [3, (4,2), rule_completed_everything],  # 28 # everything
        [0, (4,3), Has("Starcoin", count=125)],  # 29
        [5, (4,3), Has("World4_level8_cleared")],  # 30
        [10, (4,7), Has("Starcoin", count=70)],  # 31
        [0, (4,4), Has("Starcoin", count=50)],  # 32
        [5, (4,6), Has("Starcoin", count=69)],  # 33
        [3, (4,8), Has("Starcoin", count=145)],  # 34
        [5, (5,1), Has("Starcoin", count=105)],  # 35
        [3, (5,3), Has("Starcoin", count=55)],  # 36
        [0, (5,6), Has("Starcoin", count=75)],  # 37
        [5, (5,6), Has("World8_level8_cleared")],  # 38
        [3, (5,8), Has("World5_level8_cleared")],  # 39
        [3, (6,1), Has("Starcoin", count=80)],  # 40
        [0, (6,2), Has("Starcoin", count=135)],  # 41
        [0, (6,3), Has("Starcoin", count=85)] , # 42
        [5, (6,3), Has("Starcoin", count=205)],  # 43
        [5, (6,5), Has("Starcoin", count=90)] , # 44
        [10, (6,6), Has("Starcoin", count=100)] , # 45
        [5, (6,8), Has("World9_level6_cleared")],  # 46
        [5, (7,1), Has("World9_level7_cleared")],  # 47
        [0, (7,3), Has("Starcoin", count=170)],  # 48
        [0, (7,8), Has("Starcoin", count=160)],  # 49
        [3, (7,7), Has("Starcoin", count=120)],  # 50
        [3, (7,4), Has("Starcoin", count=231)],  # 51
        [0, (7,9), Has("Starcoin", count=115)],  # 52
        [3, (8,2), Has("World8_level8_cleared")],  # 53 #beat world 8 castle
        [5, (8,3), Has("Starcoin", count=180)],  # 54
        [0, (8,8), Has("Starcoin", count=110)],  # 55
        [5, (8,10), Has("Starcoin", count=155)],  # 56
        [5, (8,9), rule_completed_everything],  # 57 #all secret goals
        [5, (9,1), Has("Starcoin", count=225)],  # 58
        [5, (9,2), Has("Starcoin", count=220)],  # 59
        [5, (9,3), Has("Starcoin", count=185)],  # 60
        [5, (9,3), Has("Starcoin", count=210)],  # 61
        [0, (9,4), rule_completed_everything],  # 62 #all normal goals
        [5, (9,5), Has("Starcoin", count=230)],  # 63
        [0, (9,6), Has("Starcoin", count=200)],  # 64
        [3, (9,7), rule_completed_everything]  # 65 # complete everything!!!!!!!!!!!!!!!!1
    ]
    return requierments


def specific_level_requierments(world: NSMBWworld) -> tuple:
    # Logic done by:
    # REACT : powerups, all levels

    # this is option filters, turn options to true if not enabled
    filter_mov_on = OptionFilter(RandomizeMovment, RandomizeMovment.option_on)
    filter_move_off = OptionFilter(RandomizeMovment, RandomizeMovment.option_off)
    filter_mov = [filter_move_off] # [filter_mov_on,filter_mov_on_spin]

    filter_pow_on = OptionFilter(RandomizePowerups, RandomizePowerups.option_on)
    filter_pow_on_prog = OptionFilter(RandomizePowerups, RandomizePowerups.option_on_progressive)
    filter_pow_on_no_mus = OptionFilter(RandomizePowerups, RandomizePowerups.option_on_except_mushroom)
    filter_pow_off = OptionFilter(RandomizePowerups, RandomizePowerups.option_off)
    filter_pow = [filter_pow_off] #[filter_pow_on,filter_pow_on_prog,filter_pow_on_no_mus]


    # create rules that are true if their option filters are off or if have its item
    button_right = Has("button_right") | filter_mov
    button_left = Has("button_left") | filter_mov
    button_up = Has("button_up") | filter_mov
    button_down = Has("button_down") | filter_mov
    jump = Has(f"jump")  | filter_mov
    run = Has(f"run") | filter_mov

    ground_pound = (Has(f"ground_pound")  & button_down)| filter_mov
    wall_jump = (Has(f"wall_jump")  & jump)| filter_mov
    carry = Has("carry") | filter_mov
    climb = (Has("climb") & button_up)| filter_mov
    spin_jump = Has("spin_jump") | filter_mov
    swim = Has(f"swim") | filter_mov
    crouch = (Has(f"crouch") & button_down)| filter_mov

    question_switch = Has("?-switch") | filter_mov
    p_switch = Has(f"p-switch") | filter_mov
    red_block = Has(f"!-switch")  | filter_mov

    yoshi = Has(f"Yoshi")  | filter_mov
    star = Has(f"Star") | filter_mov

    door = (Has("door") & button_up) | filter_mov
    pipe = Has("pipe") | filter_mov





    # powerups
    mushroom = Has(f"Super_Mushroom") | filter_pow | filter_pow_on_no_mus
    progressive_pow_filler = mushroom | [filter_pow_on, filter_pow_on_no_mus]

    propeller = (Has(f"Propeller_Mushroom") & progressive_pow_filler & spin_jump) | filter_pow
    ice_peng = ((Has(f"Ice_Flower") | Has(f"Penguin_Suit")) & progressive_pow_filler) | filter_pow
    mini = (Has(f"Mini_Mushroom") & progressive_pow_filler) | filter_pow
    fire = (Has(f"Fire_Flower") & progressive_pow_filler) | filter_pow


    # Complex rules ( made of previous)
    pow = ground_pound | carry
    break_blocks = mushroom | propeller | ice_peng | mini | fire
    normal_move = button_right & (spin_jump | jump)

    bowser_world_clear_list  = list([f"World{world_num}_level{level_num}_cleared" for world_num, level_num in [(1,8), (2,8), (3,8), (4,9), (5,8), (6,9), (7,9)] ])
    bowser_clear_rule = Has("Starcoin", count=world.options.bowser_star_unlock.value) & HasFromListUnique(*bowser_world_clear_list, count=world.options.bowser_world_unlock.value)

    hard_rules = [ # normal compleation rules
        [  # world 1
            [normal_move, [propeller | mini | star, wall_jump | propeller, propeller]],  # -1
            [normal_move, [True_(), True_(), mushroom]],  # -2
            [normal_move, [True_(), mushroom | yoshi | mini, mushroom], True_()],  # -3
            [normal_move, [True_(), yoshi | propeller | mini, ice_peng]],  # -4
            [normal_move, [True_(), True_(), True_()]],  # -5
            [normal_move, [True_(), True_(), True_()]],  # -6
            [normal_move & door, [True_(), True_(), True_()]],  # -7 1-T
            [normal_move & door, [True_(), True_(), propeller | p_switch]],  # -8 1-C
        ],
        [  # world 2
            [normal_move, [True_(), True_(), True_()]],  # -1
            [normal_move, [True_(), True_(), mini]],  # -2
            [normal_move, [True_(), True_(), True_()]],  # -3
            [normal_move, [True_(), propeller, propeller | mini], True_()],  # -4
            [normal_move, [True_(), True_(), True_()]],  # -5
            [normal_move, [True_(), True_(), True_()], True_()],  # -6
            [normal_move & door, [True_(), True_(), True_()]],  # -7 2-T
            [ normal_move & (ice_peng | p_switch) & door, [True_(), mushroom, propeller | p_switch]],  # -8 2-C
        ],
        [  # world 3
            [normal_move, [ice_peng, True_(), ice_peng]],  # -1
            [normal_move, [True_(), True_(), True_()]],  # -2
            [normal_move, [True_(), True_(), True_()]],  # -3
            [normal_move & red_block, [True_(), True_(), True_()]],  # -4
            [normal_move, [True_(), red_block, red_block], True_()],  # -5
            [normal_move, [True_(), True_(), True_()],True_()],  #-6    # 3-Ghosthous
            [normal_move & door, [True_(), True_(), True_()]],  # -7
            [normal_move & door, [True_(), True_(), True_()]],  # -8
        ],
        [  # world 4
            [normal_move, [True_(), ice_peng | propeller | mini, True_()]],  # -1
            [normal_move, [True_(), True_(), True_()]],  # -2
            [normal_move, [True_(), True_(), mini]],  # -3
            [normal_move & (ice_peng | mini | propeller), [True_(), True_(), True_()]],  # -4
            [normal_move, [True_(), True_(), True_()]],  # -5
            [normal_move, [True_(), True_(), True_()], True_()],  # -6
            [normal_move &  (ice_peng | p_switch)& door, [True_(), ice_peng | p_switch, True_()],True_()],  # -7 4-G
            [normal_move& door, [True_(), True_(), True_()]],  # -8 4-C
            [normal_move, [True_(), True_(), True_()]],  # -9 4-A

        ],
        [  # world 5
            [normal_move, [mushroom, True_(), True_()]],  # -1
            [normal_move, [True_(), True_(), True_()]],  # -2
            [normal_move, [True_(), True_(), True_()]],  # -3
            [normal_move, [True_(), True_(), True_()]],  # -4
            [normal_move, [True_(), True_(), True_()]],  # -5
            [normal_move, [True_(), True_(), True_()],True_()],  # -6 #5-Ghosthouse
            [normal_move& door, [True_(), True_(), mushroom]],  # -7 5-T
            [normal_move& door, [True_(), True_(), True_()]],  # -8 5-C
        ],
        [  # world 6
            [normal_move, [True_(), True_(), True_()]],  # -1
            [normal_move, [True_(), True_(), mushroom | p_switch]],  # -2
            [normal_move, [True_(), True_(), mushroom]],  # -3
            [normal_move, [True_(), yoshi | propeller | mini, True_()]],  # -4
            [normal_move, [True_(), True_(), True_()], True_()],  # -5
            [normal_move, [True_(), True_(), True_()],True_()],  # -6
            [normal_move & wall_jump & jump & door & button_down, [True_(), True_(), True_()]],  # -7 6-T
            [normal_move& door, [mushroom, True_(), True_()]],  # -8 6-C
            [normal_move, [True_(), True_(), True_()]],  # -9 6-A

        ],
        [  # world 7
            [normal_move, [True_(), True_(), True_()]],  # -1
            [normal_move, [True_(), True_(), True_()]],  # -2
            [normal_move, [True_(), True_(), True_()]],  # -3
            [normal_move, [True_(), True_(), True_()]],  # -4
            [normal_move, [True_(), True_(), True_()]],  # -5
            [normal_move, [True_(), True_(), True_()], True_()],  # -6
            [normal_move, [True_(), True_(), True_()], True_()],  # -7
            [normal_move & door, [True_(), True_(), True_()]],  # -8 8-T
            [normal_move & door, [mushroom, True_(), True_()]],  # -9 7-C
            [normal_move & ground_pound, [True_(), True_(), propeller | mini]],  # -10 8-A

        ],
        [  # world 8
            [normal_move, [True_(), True_(), True_()]],  # -1
            [normal_move, [True_(), True_(), True_()]],  # -2
            [normal_move, [True_(), True_(), True_()]],  # -3
            [normal_move, [True_(), True_(), True_()]],  # -4
            [normal_move, [True_(), True_(), True_()]],  # -5
            [normal_move, [True_(), True_(), True_()]],  # -6
            [normal_move, [True_(), True_(), True_()]],  # -7
            [normal_move & door, [True_(), True_(), True_()]],  # -8 8-T
            [normal_move & bowser_clear_rule & door, [True_(), True_(), True_()]],  # -9 8-C
            [normal_move & ground_pound, [True_(), True_(), propeller | mini]],  # -10 8-A

        ],
        [  # world 9
            [normal_move, [True_(), True_(), True_()]],  # -1
            [normal_move, [True_(), True_(), True_()]],  # -2
            [normal_move, [True_(), True_(), True_()]],  # -3
            [normal_move, [True_(), True_(), ice_peng]],  # -4
            [normal_move, [True_(), True_(), ice_peng | propeller]],  # -5
            [normal_move, [True_(), True_(), True_()]],  # -6
            [normal_move, [True_(), True_(), True_()]],  # -7
            [normal_move, [True_(), True_(), True_()]],  # -8
        ],
    ]

    #
    easy_rules = [ # difficult logic
        [  # world 1
            [True_(), [True_(), True_(), True_()]],  # -1
            [True_(), [True_(), True_(), True_()]],  # -2
            [True_(), [True_(), True_(), True_()],True_()],  # -3
            [True_(), [True_(), True_(), True_()]],  # -4
            [True_(), [True_(), True_(), True_()]],  # -5
            [True_(), [True_(), True_(), True_()]],  # -6
            [True_(), [True_(), True_(), True_()]],  # -7 1-T
            [True_(), [True_(), True_(), True_()]],  # -8 1-C
        ],
        [  # world 2
            [True_(), [True_(), True_(), True_()]],  # -1
            [True_(), [True_(), True_(), True_()]],  # -2
            [True_(), [True_(), True_(), True_()]],  # -3
            [True_(), [True_(), True_(), True_()], True_()],  # -4
            [True_(), [True_(), True_(), True_()]],  # -5
            [True_(), [True_(), True_(), True_()],True_()],  # -6
            [True_(), [True_(), True_(), True_()]],  # -7 1-T
            [True_(), [True_(), True_(), True_()]],  # -8 1-C
        ],
        [  # world 3
            [True_(), [True_(), True_(), True_()]],  # -1
            [True_(), [True_(), True_(), True_()]],  # -2
            [True_(), [True_(), True_(), True_()]],  # -3
            [True_(), [True_(), True_(), True_()]],  # -4
            [True_(), [True_(), True_(), True_()], True_()],  # -5
            [True_(), [True_(), True_(), True_()],True_()],  # -6
            [True_(), [True_(), True_(), True_()]],  # -7 1-T
            [True_(), [True_(), True_(), True_()]],  # -8 1-C
        ],
        [  # world 4
            [True_(), [True_(), True_(), True_()]],  # -1
            [True_(), [True_(), True_(), True_()]],  # -2
            [True_(), [True_(), True_(), True_()]],  # -3
            [True_(), [True_(), True_(), True_()]],  # -4
            [True_(), [True_(), True_(), True_()]],  # -5
            [True_(), [True_(), True_(), True_()], True_()],  # -6
            [True_(), [True_(), True_(), True_()],True_()],  # -7 1-T
            [True_(), [True_(), True_(), True_()]],  # -8 1-C
            [True_(), [True_(), True_(), True_()]],  # -9 Airship

        ],
        [  # world 5
            [True_(), [True_(), True_(), True_()]],  # -1
            [True_(), [True_(), True_(), True_()]],  # -2
            [True_(), [True_(), True_(), True_()]],  # -3
            [True_(), [True_(), True_(), True_()]],  # -4
            [True_(), [True_(), True_(), True_()]],  # -5
            [True_(), [True_(), True_(), True_()],True_()],  # -6
            [True_(), [True_(), True_(), True_()]],  # -7 1-T
            [True_(), [True_(), True_(), True_()]],  # -8 1-C
        ],
        [  # world 6
            [True_(), [True_(), True_(), True_()]],  # -1
            [True_(), [True_(), True_(), True_()]],  # -2
            [True_(), [True_(), True_(), True_()]],  # -3
            [True_(), [True_(), True_(), True_()]],  # -4
            [True_(), [True_(), True_(), True_()], True_()],  # -5
            [True_(), [True_(), True_(), True_()],True_()],  # -6
            [True_(), [True_(), True_(), True_()]],  # -7 1-T
            [True_(), [True_(), True_(), True_()]],  # -8 1-C
            [True_(), [True_(), True_(), True_()]],  # -9 Airship

        ],
        [  # world 7
            [True_(), [True_(), True_(), True_()]],  # -1
            [True_(), [True_(), True_(), True_()]],  # -2
            [True_(), [True_(), True_(), True_()]],  # -3
            [True_(), [True_(), True_(), True_()]],  # -4
            [True_(), [True_(), True_(), True_()]],  # -5
            [True_(), [True_(), True_(), True_()], True_()],  # -6
            [True_(), [True_(), True_(), True_()], True_()],  # -7 Ghosthous
            [True_(), [True_(), True_(), True_()]],  # -8 1-T
            [True_(), [True_(), True_(), True_()]],  # -9 1-C
        ],
        [  # world 8
            [True_(), [True_(), True_(), True_()]],  # -1
            [True_(), [True_(), True_(), True_()]],  # -2
            [True_(), [True_(), True_(), True_()]],  # -3
            [True_(), [True_(), True_(), True_()]],  # -4
            [True_(), [True_(), True_(), True_()]],  # -5
            [True_(), [True_(), True_(), True_()]],  # -6
            [True_(), [True_(), True_(), True_()]],  # -7
            [True_(), [True_(), True_(), True_()]],  # -8 1-T
            [True_(), [True_(), True_(), True_()]],  # -9 1-C
            [True_(), [True_(), True_(), True_()]],  # -10 Airship

        ],
        [  # world 9
            [True_(), [True_(), True_(), True_()]],  # -1
            [True_(), [True_(), True_(), True_()]],  # -2
            [True_(), [True_(), True_(), True_()]],  # -3
            [True_(), [True_(), True_(), True_()]],  # -4
            [True_(), [True_(), True_(), True_()]],  # -5
            [True_(), [True_(), True_(), True_()]],  # -6
            [True_(), [True_(), True_(), True_()]],  # -7
            [True_(), [True_(), True_(), True_()]],  # -8
        ],
    ]


    return easy_rules, hard_rules

def get_levlel_connections():
    connections = []
    connections += [
        [ # world 1
            [], #-1
            [1],#-2
            [2],#-3
            [7],#-4
            [4],#-5
            [4],#-6
            [3],# -Tower
            [6,7] # -Caslte
        ],
        [  # world 2
            [],  # -1
            [],  # -2
            [1,2],  # -3
            [7],  # -4
            [4],  # -5
            [4],  # -6
            [3],  # -Tower
            [5,6]  # -Caslte
        ],
        [  # world 3
            [],  # -1
            [1],  # -2
            [2],  # -3
            [7],  # -4
            [4],  # -5
            [2],  # -6
            [2],  # -Tower
            [5]  # -Caslte
        ],
        [  # world 4
            [],  # -1
            [1],  # -2
            [1],  # -3
            [7],  # -4
            [6],  # -5
            [4],  # -6
            [2,3],  # -Tower
            [5],  # -Caslte
            [8] #airship
        ],
        [  # world 5
            [],  # -1
            [1],  # -2
            [1],  # -3
            [7],  # -4
            [4],  # -5
            [5],  # -6
            [2,3],  # -Tower
            [5,6]  # -Caslte
        ],
        [  # world 6
            [],  # -1
            [1],  # -2
            [1],  # -3
            [2],  # -4
            [7],  # -5
            [5],  # -6
            [4],  # -Tower
            [6],  # -Caslte
            [8] # - airship
        ],
        [  # world 7
            [],  # -1
            [1],  # -2
            [2],  # -3
            [8],  # -4
            [4],  # -5
            [5],  # -6
            [6], # - 7
            [3],  # -Tower
            [6]  # -Caslte
        ],
        [  # world 8
            [],  # -1
            [1],  # -2
            [2],  # -3
            [8],  # -4
            [4],  # -5
            [5],  # -6
            [2], # -7
            [3],  # -Tower
            [10],  # -Caslte
            [6] #- airship
        ],
        [  # world 9
            [],  # -1
            [],  # -2
            [],  # -3
            [],  # -4
            [],  # -5
            [],  # -6
            [],  # -7
            []  # -8
        ]

    ]


    return connections