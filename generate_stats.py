from __future__ import annotations

import collections
import random
import statistics
import threading
from collections.abc import Mapping
import concurrent.futures
import logging
import os
import tempfile
import time
from concurrent.futures import thread
from dataclasses import dataclass
from typing import Any, List, Dict, NamedTuple
import zipfile
import zlib

import pandas

import Options
import worlds
from BaseClasses import CollectionState, Item, Location, LocationProgressType, MultiWorld
from Fill import FillError, balance_multiworld_progression, distribute_items_restrictive, flood_items, \
    parse_planned_blocks, distribute_planned_blocks, resolve_early_locations_for_planned
from NetUtils import convert_to_base_types
from Options import StartInventoryPool
from Utils import __version__, output_path, restricted_dumps, version_tuple
from settings import get_settings
from worlds import AutoWorld
from worlds.generic.Rules import exclusion_rules, locality_rules



import argparse
import copy
import logging
import os
import random
import string
import sys
import urllib.parse
import urllib.request
from collections import Counter
from itertools import chain
from typing import Any

import ModuleUpdate

ModuleUpdate.update()

import Utils
import Options
from BaseClasses import seeddigits, get_seed, PlandoOptions
from Utils import parse_yamls, version_tuple, __version__, tuplize_version


from Generate import main as generate_main, get_seed, mystery_argparse, get_seed_name, roll_settings, get_choice, \
    read_weights_yamls, handle_name, roll_meta_option


def main_generate(world_name : str):
    args = mystery_argparse()

    seed = get_seed(args.seed)
    random.seed(seed)
    seed_name = get_seed_name(random)


    args.multi = 1

    args.name = {}
    args.outputname = seed_name
    args.sprite = dict.fromkeys(range(1, args.multi+1), None)
    args.sprite_pool = dict.fromkeys(range(1, args.multi+1), None)

    weights_cache: dict[str, tuple[Any, ...]] = {}
    meta_weights = None


    player_id: int = 1
    player_files: dict[int, str] = {}
    player_errors: list[str] = []
    allow_quantity = args.allow_quantity

    weights_for_file = []
    for doc_idx, yaml in enumerate(tuple(parse_yamls(f"""
name : Player
game : {world_name}
{world_name}:
  progression_balancing: 50
    """))):
        if yaml is None:
            logging.warning(f"Ignoring empty yaml document #{doc_idx + 1} in ...")
        else:
            quantity = yaml.get("quantity", 1)
            if quantity <= 0:
                raise ValueError("A quantity of 0 or less is invalid. Please change it to at least 1.")
            if not allow_quantity and quantity > 1:
                raise ValueError("Quantity greater than 1 is deactivated by host settings.")

            for _ in range(quantity):
                weights_for_file.append(yaml)
    weights_cache["Player"] = tuple(weights_for_file)



    # sort dict for consistent results across platforms:
    weights_cache = {key: value for key, value in sorted(weights_cache.items(), key=lambda k: k[0].casefold())}
    for filename, yaml_data in weights_cache.items():
        if filename not in {args.meta_file_path, args.weights_file_path}:
            for yaml in yaml_data:
                logging.info(f"P{player_id} Weights: {filename} >> "
                             f"{get_choice('description', yaml, 'No description specified')}")
                player_files[player_id] = filename
                player_id += 1

    args.multi = max(player_id - 1, args.multi)

    if args.multi == 0:
        if player_errors:
            errors = "\n\n".join(player_errors)
            raise ValueError(f"Encountered {len(player_errors)} error(s) in player files. "
                             f"See logs for full tracebacks.\n\n{errors}")
        raise ValueError(
            "No individual player files found and number of players is 0. "
            "Provide individual player files or specify the number of players via host.yaml or --multi."
        )

    logging.info(f"Generating for {args.multi} player{'s' if args.multi > 1 else ''}, "
                 f"{seed_name} Seed {seed} with plando: {args.plando}")

    if not weights_cache:
        if player_errors:
            errors = "\n\n".join(player_errors)
            raise ValueError(f"Encountered {len(player_errors)} error(s) in player files. "
                             f"See logs for full tracebacks.\n\n{errors}")
        raise Exception(f"No weights found. "
                        f"Provide a general weights file ({args.weights_file_path}) or individual player files. "
                        f"A mix is also permitted.")

    from worlds.AutoWorld import AutoWorldRegister
    args.outputname = seed_name
    args.sprite = dict.fromkeys(range(1, args.multi+1), None)
    args.sprite_pool = dict.fromkeys(range(1, args.multi+1), None)
    args.name = {}

    if meta_weights:
        for category_name, category_dict in meta_weights.items():
            for key in category_dict:
                option = roll_meta_option(key, category_name, category_dict)
                if option is not None:
                    for path in weights_cache:
                        for yaml in weights_cache[path]:
                            if category_name is None:
                                for category in yaml:
                                    if category in AutoWorldRegister.world_types and \
                                            key in Options.CommonOptions.type_hints:
                                        yaml[category][key] = option
                            elif category_name not in yaml:
                                logging.warning(f"Meta: Category {category_name} is not present in {path}.")
                            elif key == "triggers":
                                if "triggers" not in yaml[category_name]:
                                    yaml[category_name][key] = []
                                for trigger in option:
                                    yaml[category_name][key].append(trigger)
                            else:
                                yaml[category_name][key] = option

    settings_cache: dict[str, tuple[argparse.Namespace, ...] | None] = {fname: None for fname in weights_cache}
    if args.sameoptions:
        for fname, yamls in weights_cache.items():
            try:
                settings_cache[fname] = tuple(roll_settings(yaml, args.plando) for yaml in yamls)
            except Exception as e:
                logging.exception(f"Exception reading settings in file {fname}")
                player_errors.append(
                    f"{len(player_errors) + 1}. "
                    f"File {fname} is invalid. Please fix your yaml.\n{Utils.get_all_causes(e)}"
                )
        # Exit early here to avoid throwing the same errors again later
        if player_errors:
            errors = "\n\n".join(player_errors)
            raise ValueError(f"Encountered {len(player_errors)} error(s) in player files. "
                             f"See logs for full tracebacks.\n\n{errors}")

    player_path_cache: dict[int, str] = {}
    for player in range(1, args.multi + 1):
        player_path_cache[player] = player_files.get(player, args.weights_file_path)
    name_counter: Counter[str] = Counter()
    args.player_options = {}

    player = 1
    while player <= args.multi:
        path = player_path_cache[player]
        if not path:
            player_errors.append(f'No weights specified for player {player}')
            player += 1
            continue

        for doc_index, yaml in enumerate(weights_cache[path]):
            name = yaml.get("name")
            try:
                # Use the cached settings object if it exists, otherwise roll settings within the try-catch
                # Invariant: settings_cache[path] and weights_cache[path] have the same length
                cached = settings_cache[path]
                settings_object: argparse.Namespace = (cached[doc_index] if cached else roll_settings(yaml, args.plando))

                for k, v in vars(settings_object).items():
                    if v is not None:
                        try:
                            getattr(args, k)[player] = v
                        except AttributeError:
                            setattr(args, k, {player: v})
                        except Exception as e:
                            raise Exception(f"Error setting {k} to {v} for player {player}") from e

                # name was not specified
                if player not in args.name:
                    if path == args.weights_file_path:
                        # weights file, so we need to make the name unique
                        args.name[player] = f"Player{player}"
                    else:
                        # use the filename
                        args.name[player] = os.path.splitext(os.path.split(path)[-1])[0]
                args.name[player] = handle_name(args.name[player], player, name_counter)

            except Exception as e:
                logging.exception(f"Exception reading settings in file {path} document #{doc_index + 1} "
                                  f"(name: {args.name.get(player, name)})")
                player_errors.append(
                    f"{len(player_errors) + 1}. "
                    f"File {path} document #{doc_index + 1} (with name: {args.name.get(player, name)}) is invalid. "
                    f"Please fix your yaml.\n{Utils.get_all_causes(e)}")

            # increment for each yaml document in the file
            player += 1

    if len(set(name.lower() for name in args.name.values())) != len(args.name):
        player_errors.append(
            f"{len(player_errors) + 1}. "
            f"Names have to be unique. Names: {Counter(name.lower() for name in args.name.values())}"
        )

    if player_errors:
        errors = "\n\n".join(player_errors)
        raise ValueError(f"Encountered {len(player_errors)} error(s) in player files. "
                         f"See logs for full tracebacks.\n\n{errors}")

    return args, seed

    return args, seed


def main_fill(args, seed=None, baked_server_options: dict[str, object] | None = None):
    # this code is copy pasted from Main.py
    if not baked_server_options:
        baked_server_options = get_settings().server_options.as_dict()
    assert isinstance(baked_server_options, dict)
    if args.outputpath:
        os.makedirs(args.outputpath, exist_ok=True)
        output_path.cached_path = args.outputpath

    start = time.perf_counter()
    # initialize the multiworld
    multiworld = MultiWorld(args.multi)

    logger = logging.getLogger()
    multiworld.set_seed(seed, args.race, str(args.outputname) if args.outputname else None)
    multiworld.plando_options = args.plando
    multiworld.game = args.game.copy()
    multiworld.player_name = args.name.copy()
    multiworld.sprite = args.sprite.copy()
    multiworld.sprite_pool = args.sprite_pool.copy()

    multiworld.set_options(args)
    if args.csv_output:
        from Options import dump_player_options
        dump_player_options(multiworld)
    multiworld.set_item_links()
    multiworld.state = CollectionState(multiworld)
    logger.info('Archipelago Version %s  -  Seed: %s\n', __version__, multiworld.seed)

    logger.info(f"Found {len(AutoWorld.AutoWorldRegister.world_types)} World Types:")
    longest_name = max(len(text) for text in AutoWorld.AutoWorldRegister.world_types)

    world_classes = AutoWorld.AutoWorldRegister.world_types.values()

    version_count = max(len(cls.world_version.as_simple_string()) for cls in world_classes)
    item_count = len(str(max(len(cls.item_names) for cls in world_classes)))
    location_count = len(str(max(len(cls.location_names) for cls in world_classes)))

    for name, cls in AutoWorld.AutoWorldRegister.world_types.items():
        if not cls.hidden and len(cls.item_names) > 0:
            logger.info(f" {name:{longest_name}}: "
                        f"v{cls.world_version.as_simple_string():{version_count}} | "
                        f"Items: {len(cls.item_names):{item_count}} | "
                        f"Locations: {len(cls.location_names):{location_count}}")

    del item_count, location_count

    # This assertion method should not be necessary to run if we are not outputting any multidata.
    if not args.skip_output and not args.spoiler_only:
        AutoWorld.call_stage(multiworld, "assert_generate")

    AutoWorld.call_all(multiworld, "generate_early")

    logger.info('')

    for player in multiworld.player_ids:
        for item_name, count in multiworld.worlds[player].options.start_inventory.value.items():
            for _ in range(count):
                multiworld.push_precollected(multiworld.create_item(item_name, player))

        for item_name, count in getattr(multiworld.worlds[player].options,
                                        "start_inventory_from_pool",
                                        StartInventoryPool({})).value.items():
            for _ in range(count):
                multiworld.push_precollected(multiworld.create_item(item_name, player))
            # remove from_pool items also from early items handling, as starting is plenty early.
            early = multiworld.early_items[player].get(item_name, 0)
            if early:
                multiworld.early_items[player][item_name] = max(0, early-count)
                remaining_count = count-early
                if remaining_count > 0:
                    local_early = multiworld.local_early_items[player].get(item_name, 0)
                    if local_early:
                        multiworld.early_items[player][item_name] = max(0, local_early - remaining_count)
                    del local_early
            del early

        # items can't be both local and non-local, prefer local
        multiworld.worlds[player].options.non_local_items.value -= multiworld.worlds[player].options.local_items.value
        multiworld.worlds[player].options.non_local_items.value -= set(multiworld.local_early_items[player])

    # Clear non-applicable local and non-local items.
    if multiworld.players == 1:
        multiworld.worlds[1].options.non_local_items.value = set()
        multiworld.worlds[1].options.local_items.value = set()

    logger.info('Creating MultiWorld.')
    AutoWorld.call_all(multiworld, "create_regions")

    logger.info('Creating Items.')
    AutoWorld.call_all(multiworld, "create_items")

    logger.info('Calculating Access Rules.')
    AutoWorld.call_all(multiworld, "set_rules")

    for player in multiworld.player_ids:
        exclusion_rules(multiworld, player, multiworld.worlds[player].options.exclude_locations.value)
        multiworld.worlds[player].options.priority_locations.value -= multiworld.worlds[player].options.exclude_locations.value
        world_excluded_locations = set()
        for location_name in multiworld.worlds[player].options.priority_locations.value:
            try:
                location = multiworld.get_location(location_name, player)
            except KeyError:
                continue

            if location.progress_type != LocationProgressType.EXCLUDED:
                location.progress_type = LocationProgressType.PRIORITY
            else:
                logger.warning(f"Unable to prioritize location \"{location_name}\" in player {player}'s world because the world excluded it.")
                world_excluded_locations.add(location_name)
        multiworld.worlds[player].options.priority_locations.value -= world_excluded_locations

    # Set local and non-local item rules.
    # This function is called so late because worlds might otherwise overwrite item_rules which are how locality works
    if multiworld.players > 1:
        locality_rules(multiworld)

    multiworld.plando_item_blocks = parse_planned_blocks(multiworld)

    AutoWorld.call_all(multiworld, "connect_entrances")
    AutoWorld.call_all(multiworld, "generate_basic")

    # remove starting inventory from pool items.
    # Because some worlds don't actually create items during create_items this has to be as late as possible.
    fallback_inventory = StartInventoryPool({})
    depletion_pool: dict[int, dict[str, int]] = {
        player: getattr(multiworld.worlds[player].options, "start_inventory_from_pool", fallback_inventory).value.copy()
        for player in multiworld.player_ids
    }
    target_per_player = {
        player: sum(target_items.values()) for player, target_items in depletion_pool.items() if target_items
    }

    if target_per_player:
        new_itempool: list[Item] = []

        # Make new itempool with start_inventory_from_pool items removed
        for item in multiworld.itempool:
            if depletion_pool[item.player].get(item.name, 0):
                depletion_pool[item.player][item.name] -= 1
            else:
                new_itempool.append(item)

        # Create filler in place of the removed items, warn if any items couldn't be found in the multiworld itempool
        for player, target in target_per_player.items():
            unfound_items = {item: count for item, count in depletion_pool[player].items() if count}

            if unfound_items:
                player_name = multiworld.get_player_name(player)
                logger.warning(f"{player_name} tried to remove items from their pool that don't exist: {unfound_items}")

            needed_items = target_per_player[player] - sum(unfound_items.values())
            new_itempool += [multiworld.worlds[player].create_filler() for _ in range(needed_items)]

        assert len(multiworld.itempool) == len(new_itempool), "Item Pool amounts should not change."
        multiworld.itempool[:] = new_itempool

    multiworld.link_items()

    if any(world.options.item_links for world in multiworld.worlds.values()):
        multiworld._all_state = None

    logger.info("Running Item Plando.")
    resolve_early_locations_for_planned(multiworld)
    distribute_planned_blocks(multiworld, [x for player in multiworld.plando_item_blocks
                                           for x in multiworld.plando_item_blocks[player]])

    logger.info('Running Pre Main Fill.')

    AutoWorld.call_all(multiworld, "pre_fill")

    return multiworld

def download_all_apworlds():
    print("Dowloading apworlds")

#@dataclass
#class Stats(NamedTuple):
#    mean : float
#    median : float
#    min : float
#    max : float

Stats = collections.namedtuple("Stats", ["mean", "meadian", "min", "max"])


# needs a nogui arg and ability to time out
def get_stats_one_world(world_name : str) -> Stats:
    print(f"Collecting stats for {world_name}")
    loc_count = []
    for _ in range(10):

        multiworld = main_fill(*main_generate(world_name))
        loc_count.append(len(multiworld.itempool))
        #loc_count.append(1)

        del multiworld

    mean = statistics.mean(loc_count)
    median = statistics.median(loc_count)
    _min = min(loc_count)
    _max = max(loc_count)
    stats = Stats(mean, median, _min, _max)

    return stats


def get_stats_all_worlds() -> pandas.DataFrame:
    print(f"Getting stats for all worlds")
    stats = pandas.DataFrame(columns=["World", "Mean", "Median", "Min", "Max"])

    for world_name in AutoWorld.AutoWorldRegister.world_types :
        if world_name in ["Archipelago"]:
            continue

        try:
            stat = get_stats_one_world( world_name)
            stats.loc[len(stats)] = [world_name, stat.mean, stat.meadian, stat.min, stat.max]
        except Exception as e:
            print(f"World {world_name} failed with exception {e}")

    return stats

def export_stats(stats : pandas.DataFrame) -> None:
    print(f"Exporting stats")

    print(stats)
    stats.to_csv(os.path.join("output", "stats.csv"), index = False)


def main(*argv, **kwargs):
    download_all_apworlds()
    stats = get_stats_all_worlds()

    export_stats(stats)



if __name__ == '__main__':
    main()