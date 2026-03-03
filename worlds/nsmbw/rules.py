from __future__ import annotations

from typing import TYPE_CHECKING

import rule_builder.rules
from rule_builder import rules

if TYPE_CHECKING:
    from .world import NSMBWworld



def set_all_rules(world: NSMBWworld) -> None:
    # In order for AP to generate an item layout that is actually possible for the player to complete,
    # we need to define rules for our Entrances and Locations.
    # Note: Regions do not have rules, the Entrances connecting them do!
    # We'll do entrances first, then locations, and then finally we set our victory condition.


    # removed rules for now
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)
    pass


def set_all_entrance_rules(world: NSMBWworld) -> None:
    enterances = []
    for i in range(1, 9 + 1):
        enterances.append(world.get_entrance( f"From menu to World {i} connection"))  # rules.Has(f"World{i}_unlock")
        if i != 9:
            enterances.append(world.get_entrance(f"World {i} internal connection"))  # rules.HasAll(f"World{i}_unlock")

    for i in range(1, 9 + 1):
        world.set_rule(enterances[2*i-2], rules.Has(f"World{i}_unlock"))
        if i != 9:
            world.set_rule(enterances[2*i+1-2], rules.HasAll(f"World{i}_unlock"))

def specific_hintmovie_requierments(world: NSMBWworld) -> List:
    # info about these harvested from https://gamefaqs.gamespot.com/wii/960544-new-super-mario-bros-wii/faqs/58584
    rule_completed_everything = rules.Has("World8_level10_cleared") # dont want to implement
    requierments = [
        [3, rules.True_()],   #01
        [5, rule_completed_everything],  # 02 #find every normal goal in world1-9
        [3, rules.Has("Starcoin", count=5)],  # 03
        [3, rule_completed_everything],  # 04 #find every normal goal in world1-9
        [5, rules.Has("World1_level8_cleared")],  # 05
        [5, rules.Has("Starcoin", count=10)],  # 06
        [5, rules.Has("Starcoin", count=30)],  # 07
        [0, rules.Has("Starcoin", count=15)],  # 08
        [3, rules.Has("Starcoin", count=1)],  # 09
        [0, rules.Has("Starcoin", count=95)],  # 10
        [3, rules.Has("Starcoin", count=150)],  # 11
        [5, rules.Has("Starcoin", count=1)]  ,# 12
        [5, rule_completed_everything] , # 13 #find every normal adn secret goal in world1-9
        [5, rules.Has("World2_level8_cleared")],  # 14
        [5, rules.Has("Starcoin", count=215)],  # 15
        [10, rules.Has("Starcoin", count=25)],  # 16
        [0, rules.Has("Starcoin", count=65)] , # 17
        [3, rules.Has("Starcoin", count=35)] , # 18
        [5, rules.Has("Starcoin", count=165)] , # 19
        [5, rules.Has("Starcoin", count=190)]  ,# 20
        [0, rules.Has("Starcoin", count=140)] , # 21
        [3, rules.Has("World3_level8_cleared")],  # 22
        [5, rules.Has("Starcoin", count=195)] , # 23
        [5, rules.Has("Starcoin", count=140)],  # 24
        [5, rules.Has("Starcoin", count=130)] , # 25
        [3, rules.Has("Starcoin", count=45)]  ,# 26
        [5, rules.Has("Starcoin", count=175)] , # 27
        [3, rule_completed_everything],  # 28 # everything
        [0, rules.Has("Starcoin", count=125)],  # 29
        [5, rules.Has("World4_level8_cleared")],  # 30
        [10, rules.Has("Starcoin", count=70)],  # 31
        [0, rules.Has("Starcoin", count=50)],  # 32
        [5, rules.Has("Starcoin", count=69)],  # 33
        [3, rules.Has("Starcoin", count=145)],  # 34
        [5, rules.Has("Starcoin", count=105)],  # 35
        [3, rules.Has("Starcoin", count=55)],  # 36
        [0, rules.Has("Starcoin", count=75)],  # 37
        [5, rules.Has("World8_level8_cleared")],  # 38
        [3, rules.Has("World5_level8_cleared")],  # 39
        [3, rules.Has("Starcoin", count=80)],  # 40
        [0, rules.Has("Starcoin", count=135)],  # 41
        [0, rules.Has("Starcoin", count=85)] , # 42
        [5, rules.Has("Starcoin", count=205)],  # 43
        [5, rules.Has("Starcoin", count=90)] , # 44
        [10, rules.Has("Starcoin", count=100)] , # 45
        [5, rules.Has("World9_level6_cleared")],  # 46
        [5, rules.Has("World9_level7_cleared")],  # 47
        [0, rules.Has("Starcoin", count=170)],  # 48
        [0, rules.Has("Starcoin", count=160)],  # 49
        [3, rules.Has("Starcoin", count=120)],  # 50
        [3, rules.Has("Starcoin", count=231)],  # 51
        [0, rules.Has("Starcoin", count=115)],  # 52
        [3, rules.Has("World8_level8_cleared")],  # 53 #beat world 8 castle
        [5, rules.Has("Starcoin", count=180)],  # 54
        [0, rules.Has("Starcoin", count=110)],  # 55
        [5, rules.Has("Starcoin", count=155)],  # 56
        [5, rule_completed_everything],  # 57 #all secret goals
        [5, rules.Has("Starcoin", count=225)],  # 58
        [5, rules.Has("Starcoin", count=220)],  # 59
        [5, rules.Has("Starcoin", count=185)],  # 60
        [5, rules.Has("Starcoin", count=210)],  # 61
        [0, rule_completed_everything],  # 62 #all normal goals
        [5, rules.Has("Starcoin", count=230)],  # 63
        [0, rules.Has("Starcoin", count=200)],  # 64
        [3, rule_completed_everything]  # 65 # complete everything!!!!!!!!!!!!!!!!1
    ]
    return requierments

def specific_level_requierments(world: NSMBWworld) -> List:
    # doesnt acount for secret exit
    mushroom = rules.Has(f"powerup_state:{'Super_Mushroom'}")


    propeller = rules.Has(f"powerup_state:{'Propeller_Mushroom'}") & mushroom
    ice_peng = (rules.Has(f"powerup_state:{'Ice_Flower'}") | rules.Has(f"powerup_state:{'Penguin_Suit'}")) & mushroom
    mini = rules.Has(f"powerup_state:{'Mini_Mushroom'}") & mushroom


    p_switch = rules.Has(f"movment:{'p-switch'}") | rules.True_()
    red_block = rules.Has(f"movment:{'red-block'}") | rules.True_()
    yoshi = rules.True_()
    star = rules.True_()

    gp = rules.Has(f"movment:{'ground_pound'}")


    requierments = []
    requierments += [ # normal compleation rules
        [  # world 1
            [rules.True_(), [propeller | mini | star, rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), mushroom]],  # -2
            [rules.True_(), [rules.True_(), mushroom | yoshi | mini, mushroom]],  # -3
            [rules.True_(), [rules.True_(), yoshi | propeller | mini, ice_peng]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), propeller | p_switch]],  # -8 1-C
        ],
        [  # world 2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), mini]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), propeller, propeller | mini]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 2-T
            [ ice_peng | p_switch, [rules.True_(), mushroom, propeller | p_switch]],  # -8 2-C
        ],
        [  # world 3
            [rules.True_(), [ice_peng, rules.True_(), ice_peng]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [red_block, [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), red_block, red_block]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8
        ],
        [  # world 4
            [rules.True_(), [rules.True_(), ice_peng | propeller | mini, rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), mini]],  # -3
            [ice_peng | mini | propeller, [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [ice_peng | p_switch, [rules.True_(), ice_peng | p_switch, rules.True_()]],  # -7 4-G
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 4-C
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -9 4-A

        ],
        [  # world 5
            [rules.True_(), [mushroom, rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), mushroom]],  # -7 5-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 5-C
        ],
        [  # world 6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), mushroom | p_switch]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), mushroom]],  # -3
            [rules.True_(), [rules.True_(), yoshi | propeller | mini, rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 6-T
            [rules.True_(), [mushroom, rules.True_(), rules.True_()]],  # -8 6-C
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -9 6-A

        ],
        [  # world 7
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 7-T
            [rules.True_(), [mushroom, rules.True_(), rules.True_()]],  # -9 7-C

        ],
        [  # world 8
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 8-T
            [gp, [rules.True_(), rules.True_(), propeller | mini]],  # -9 8-A
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -10 8-C
        ],
        [  # world 9
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), ice_peng]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), ice_peng | propeller]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8
        ],
    ]

    #
    #requierments += \
    [ # difficult logic
        [  # world 1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 1-C
        ],
        [  # world 2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 1-C
        ],
        [  # world 3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 1-C
        ],
        [  # world 4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 1-C
        ],
        [  # world 5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 1-C
        ],
        [  # world 6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 1-C
        ],
        [  # world 7
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 1-C
        ],
        [  # world 8
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 1-C
        ],
        [  # world 9
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -1
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -2
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -3
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -4
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -5
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -6
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -7 1-T
            [rules.True_(), [rules.True_(), rules.True_(), rules.True_()]],  # -8 1-C
        ],
    ]
    return requierments

def set_all_location_rules(world: NSMBWworld) -> None:
    #regions = []
    #for i in range(1, 9):
    #    regions.append(world.get_region(f"World_{i}_1"))
    #    if i != 9:
    #        regions.append(world.get_region(f"World_{i}_2"))
    level_req = specific_level_requierments(world)

    #sets basic rules for each level
    #
    levels_per_world = [8, 8, 8, 9, 8, 9, 9, 10, 8]
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, levels_per_world[world_num - 1]+1):
            flagpole = world.get_location(f"World{world_num}_level{level_num}_flagpole")
            if world_num != 9:
                if level_num == 1:
                    world.set_rule(flagpole, rules.Has(f"World{world_num}_unlock", count=1) & level_req[world_num-1][level_num-1][0])
                elif level_num == 4:
                    world.set_rule(flagpole, rules.Has(f"World{world_num}_unlock", count=2) & rules.Has(f"World{world_num}_level{level_num-1}_cleared")& level_req[world_num-1][level_num-1][0])
                else:
                    # makes a level in logic if previous level is cleared
                    world.set_rule(flagpole, (rules.Has(f"World{world_num}_level{level_num-1}_cleared") & level_req[world_num-1][level_num-1][0]))
            if world_num == 9:
                world.set_rule(flagpole,rules.Has("Starcoin",count=10*level_num) & rules.Has(f"World{world_num}_unlock", count=1) & level_req[world_num-1][level_num-1][0])

            for sc in range(1, 3 + 1):
                # makes starcoins in logic if this level is cleared
                star_coin = world.get_location(f"World{world_num}_level{level_num}_SC{sc}")
                world.set_rule(star_coin,rules.Has(f"World{world_num}_level{level_num}_cleared") & level_req[world_num - 1][level_num - 1][1][sc - 1] )

    HM_COUNT = 65
    hm_req = specific_hintmovie_requierments(world)
    total_cost = 0
    for hm_num in range(1,HM_COUNT+1):
        location = world.get_location(f"Hintmovie{hm_num}")
        #oftlogic for hm
        total_cost += hm_req[hm_num-1][0] #logic asume you have to get enought starcoins to get them in order
        world.set_rule(location, (rules.Has(f"Starcoin", count=total_cost) & hm_req[hm_num-1][1] ) )


def set_completion_condition(world: NSMBWworld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    #world.multiworld.completion_condition[world.player] = Has_all(("Sword", count= "Shield"), world.player)

    # In our case, we went for the Victory event design pattern (see create_events() in locations.py).
    # So lets undo what we just did, and instead set the completion condition to:
    world.set_completion_rule(rules.Has("Victory"))

#rules to json exists