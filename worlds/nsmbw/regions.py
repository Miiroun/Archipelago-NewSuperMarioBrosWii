from __future__ import annotations


from BaseClasses import Entrance, Region
from rule_builder import rules
from .Common import *
from .options import World9UnlockCondition, WorldUnlock, LevelUnlock
from .raw_rules import get_level_connections

if TYPE_CHECKING:
    from .world import NSMBWworld


def create_and_connect_regions(world: NSMBWworld) -> None:
    create_all_regions(world)
    connect_regions(world)

    #menu_region = Region("Menu", world.player, world.multiworld)
    #visualize_regions(menu_region, "visualized_regions")


def create_all_regions(world: NSMBWworld) -> None:
    # Creating a region is as simple as calling the constructor of the Region class.
    menu_region = Region("Menu", world.player, world.multiworld)
    peach_castle_region = Region("Peach castle", world.player, world.multiworld)
    inventory_region = Region("Inventory", world.player, world.multiworld)

    regions = [menu_region, peach_castle_region, inventory_region]
    for world_num in range(1,9+1):
        regions.append(Region(f"World{world_num}", world.player, world.multiworld))

    for level in LEVELS:
        if (level_randoed_bijection(world.shuffled_level_order, *level))[0] == 10:
            continue

        regions.append(Region(name_base(*level)+ " start", world.player, world.multiworld))
        regions.append(Region(name_base(*level)          , world.player, world.multiworld))

    world.multiworld.regions += regions


def connect_regions(world: NSMBWworld) -> None:
    menu_region = world.get_region("Menu")

    world.get_region(f"World1").connect(world.get_region("Peach castle"))
    menu_region.connect(world.get_region("Inventory"))

    connections = get_level_connections()
    if len(world.star_coin_req_per_world_9_level) == 0:
        world.star_coin_req_per_world_9_level = list(0 for _ in range(8))
        match world.options.world9_unlock_condition.value:
            case World9UnlockCondition.option_linear:
                for i in range(8):
                    world.star_coin_req_per_world_9_level[i] = 20*(i+1)
            case World9UnlockCondition.option_gaussian:
                for i in range(8):
                    world.star_coin_req_per_world_9_level[i] = int(round( world.random.normalvariate(80,40)))
                    if world.star_coin_req_per_world_9_level[i] <0:
                        world.star_coin_req_per_world_9_level[i] = 0
                    if world.star_coin_req_per_world_9_level[i] > 231-10: # 10 is margin
                        world.star_coin_req_per_world_9_level[i] = 231-10
            case World9UnlockCondition.option_unlocked:
                for i in range(8):
                    world.star_coin_req_per_world_9_level[i] = 0
            case _:
                raise ValueError(f"Case {world.options.world9_unlock_condition.value} is not valid")

    for world_num in range(1,10+1):
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            if (level_randoed_bijection(world.shuffled_level_order, world_num,level_num))[0] == 10:
                continue
            world.get_region(name_base(world_num, level_num) + " start").connect(world.get_region(name_base(world_num, level_num)),
                                                          f"{name_base(world_num,level_num)} internal level connection")

    for world_num in range(1,9+1):
        menu_region.connect(world.get_region(f"World{world_num}"), f"menu->World{world_num}")
        for org_lev_num, con_levels in enumerate(connections[world_num-1]):
            for con_lev_num in con_levels:
                assert type(con_lev_num) == int, "should be an integer"
                con_randod_world_num, con_randod_level_num = level_randoed(world.shuffled_level_order, world_num, con_lev_num)
                if org_lev_num != 0:
                    org_randod_world_num, org_randod_level_num = level_randoed(world.shuffled_level_order, world_num, org_lev_num)
                else:
                    org_randod_world_num, org_randod_level_num = (0,0)

                org_region : Region
                conn_name : str
                if (org_randod_level_num == 0) or (world.options.level_unlock.value == LevelUnlock.option_all_unlocked):
                    org_region = world.get_region(f"World{world_num}")
                    conn_name = f"World{world_num}->{name_base(con_randod_world_num, con_randod_level_num)}"
                    if conn_name in world.multiworld.regions.entrance_cache[world.player]:
                        continue

                elif world.options.level_unlock.value == LevelUnlock.option_vanilla:
                    org_region = world.get_region(name_base(org_randod_world_num, org_randod_level_num))
                    conn_name = f"{name_base(org_randod_world_num, org_randod_level_num)}->{name_base(con_randod_world_num, con_randod_level_num)}"
                else:
                    raise ValueError
                org_region.connect(world.get_region(name_base(con_randod_world_num, con_randod_level_num)+ " start"),conn_name)

    for secret_exit in SECRET_EXIT:
        #randoed_secret_exit : SecretExit = secret_exit_randoed_func(world.shuffled_level_order, level_randoed_bijection, secret_exit)


        if secret_exit.is_item and (secret_exit.exit_type == 2):
            #world.get_region(name_base(randoed_secret_exit.world, randoed_secret_exit.level) + " start").connect(world.get_region(name_base(randoed_secret_exit.world, randoed_secret_exit.level_to) + " start"), name_secret(secret_exit), rules.True_())

            from_level = level_randoed(world.shuffled_level_order,secret_exit.world, secret_exit.level)
            to_level = level_randoed(world.shuffled_level_order, secret_exit.world, secret_exit.level_to)
            world.get_region(name_base(*from_level) + " start").connect(world.get_region(name_base(*to_level) + " start"),name_secret(secret_exit))

