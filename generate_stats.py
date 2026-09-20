from __future__ import annotations

from BaseClasses import CollectionState, MultiWorld
from Options import StartInventoryPool
from Utils import __version__, output_path
from worlds import AutoWorld
from worlds.AutoWorld import AutoWorldRegister

import argparse
import os
import random
from collections import Counter
from typing import Any

import Utils
import Options
from BaseClasses import PlandoOptions
from Utils import parse_yamls

from Generate import get_seed, get_seed_name, roll_settings, get_choice,handle_name, roll_meta_option
from settings import get_settings

from fuzz import generate_random_yaml
from Options import dump_player_options
from worlds.apworld_manager.world_manager import install_world, refresh_apworld_table, repositories


import threading
import traceback
import multiprocessing
import gc
from copy import deepcopy
import tracemalloc

import statistics
import time
import pandas


def mystery_argparse(argv: list[str] | None = None) -> argparse.Namespace:
    settings = get_settings()
    defaults = settings.generator

    parser = argparse.ArgumentParser(description="CMD Generation Interface, defaults come from host.yaml.")
    parser.add_argument('--weights_file_path', default=defaults.weights_file_path,
                        help='Path to the weights file to use for rolling game options, urls are also valid')
    parser.add_argument('--sameoptions', help='Rolls options per weights file rather than per player',
                        action='store_true')
    parser.add_argument('--player_files_path', default=defaults.player_files_path,
                        help="Input directory for player files.")
    parser.add_argument('--seed', help='Define seed number to generate.', type=int)
    parser.add_argument('--multi', default=defaults.players, type=lambda value: max(int(value), 1))
    parser.add_argument('--spoiler', type=int, default=defaults.spoiler)
    parser.add_argument('--outputpath', default=settings.general_options.output_path,
                        help="Path to output folder. Absolute or relative to cwd.")  # absolute or relative to cwd
    parser.add_argument('--allow_quantity', action="store_true", default=defaults.allow_quantity,
                        help='Allows the use of the quantity option in yamls. Default is the set value in the host.yaml.')
    parser.add_argument('--race', action='store_true', default=defaults.race)
    parser.add_argument('--meta_file_path', default=defaults.meta_file_path)
    parser.add_argument('--log_level', default=defaults.loglevel, help='Sets log level')
    parser.add_argument('--log_time', help="Add timestamps to STDOUT",
                        default=defaults.logtime, action='store_true')
    parser.add_argument("--csv_output", action="store_true",
                        help="Output rolled player options to csv (made for async multiworld).")
    parser.add_argument("--plando", default=defaults.plando_options,
                        help="List of options that can be set manually. Can be combined, for example \"bosses, items\"")
    parser.add_argument("--skip_prog_balancing", action="store_true",
                        help="Skip progression balancing step during generation.")
    parser.add_argument("--skip_output", action="store_true",
                        help="Skips generation assertion and output stages and skips multidata and spoiler output. "
                             "Intended for debugging and testing purposes.")
    parser.add_argument("--spoiler_only", action="store_true",
                        help="Skips generation assertion and multidata, outputting only a spoiler log. "
                             "Intended for debugging and testing purposes.")

    #added to remove error
    parser.add_argument("--download", default=False, action="store_true", help="download all apworlds")
    parser.add_argument("--nogui", default=False, action="store_true", help="Turns off Client GUI.")
    parser.add_argument("--fuzz", default=False, action="store_true", help="Whether to fuzz yamls.")
    parser.add_argument("-n", "--count", default="10", type=str, help="How many times each apworld should run")
    parser.add_argument("-t", "--timeout", default=999, type=float, help="A timeout after which ")

    args = parser.parse_args(argv)

    if args.skip_output and args.spoiler_only:
        parser.error("Cannot mix --skip_output and --spoiler_only")
    elif args.spoiler == 0 and args.spoiler_only:
        parser.error("Cannot use --spoiler_only when --spoiler=0. Use --skip_output or set --spoiler to a different value")

    if not os.path.isabs(args.weights_file_path):
        args.weights_file_path = os.path.join(args.player_files_path, args.weights_file_path)
    if not os.path.isabs(args.meta_file_path):
        args.meta_file_path = os.path.join(args.player_files_path, args.meta_file_path)
    args.plando = PlandoOptions.from_option_string(args.plando)

    return args

def main_generate(world_name : str, fuzz = False, *varg, **kwargs):
    yaml_func = None
    if fuzz:
        yaml = generate_random_yaml(world_name, {})
        # print(yaml)
        yaml_func = parse_yamls(yaml)
    else:
        yaml_func = parse_yamls(f"""
        name : Player
        game : {world_name}
        {world_name}:
          progression_balancing: 50
            """)

    return main_base_generate(yaml_func, *varg, **kwargs)



def main_base_generate(yaml_func, *varg, **kwargs):
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
    for doc_idx, yaml in enumerate(tuple(yaml_func)):
        if yaml is None:
            print(f"Ignoring empty yaml document #{doc_idx + 1} in ...")
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
                #print(f"P{player_id} Weights: {filename} >> "
                #             f"{get_choice('description', yaml, 'No description specified')}")
                player_files[player_id] = filename
                player_id += 1

    args.multi = max(player_id - 1, args.multi)

    if args.multi == 0:
        raise Options.OptionError
        #if player_errors:
        #    errors = "\n\n".join(player_errors)
        #    raise ValueError(f"Encountered {len(player_errors)} error(s) in player files. "
        #                     f"See logs for full tracebacks.\n\n{errors}")
        #raise ValueError(
        #    "No individual player files found and number of players is 0. "
        #    "Provide individual player files or specify the number of players via host.yaml or --multi."
        #)

    #print(f"Generating for {args.multi} player{'s' if args.multi > 1 else ''}, "
    #             f"{seed_name} Seed {seed} with plando: {args.plando}")

    if not weights_cache:
        if player_errors:
            errors = "\n\n".join(player_errors)
            raise ValueError(f"Encountered {len(player_errors)} error(s) in player files. "
                             f"See logs for full tracebacks.\n\n{errors}")
        raise Exception(f"No weights found. "
                        f"Provide a general weights file ({args.weights_file_path}) or individual player files. "
                        f"A mix is also permitted.")

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
                                print(f"Meta: Category {category_name} is not present in {path}.")
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
                #print(f"Exception reading settings in file {fname}")
                player_errors.append(
                    f"{len(player_errors) + 1}. "
                    f"File {fname} is invalid. Please fix your yaml.\n{Utils.get_all_causes(e)}"
                )
        # Exit early here to avoid throwing the same errors again later
        if player_errors:
            raise Options.OptionError
            #errors = "\n\n".join(player_errors)
            #raise ValueError(f"Encountered {len(player_errors)} error(s) in player files. "
            #                 f"See logs for full tracebacks.\n\n{errors}")

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
                print(f"Exception reading settings in file {path} document #{doc_index + 1} "
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

    multiworld.set_seed(seed, args.race, str(args.outputname) if args.outputname else None)
    multiworld.plando_options = args.plando
    multiworld.game = args.game.copy()
    multiworld.player_name = args.name.copy()
    multiworld.sprite = args.sprite.copy()
    multiworld.sprite_pool = args.sprite_pool.copy()

    multiworld.set_options(args)
    if args.csv_output:
        dump_player_options(multiworld)
    multiworld.set_item_links()
    multiworld.state = CollectionState(multiworld)

    #print('Archipelago Version %s  -  Seed: %s\n', __version__, multiworld.seed)

    #print(f"Found {len(AutoWorld.AutoWorldRegister.world_types)} World Types:")
    #longest_name = max(len(text) for text in AutoWorld.AutoWorldRegister.world_types)

    #world_classes = AutoWorld.AutoWorldRegister.world_types.values()

    #version_count = max(len(cls.world_version.as_simple_string()) for cls in world_classes)
    #item_count = len(str(max(len(cls.item_names) for cls in world_classes)))
    #location_count = len(str(max(len(cls.location_names) for cls in world_classes)))

    #for name, cls in AutoWorld.AutoWorldRegister.world_types.items():
    #    if not cls.hidden and len(cls.item_names) > 0:
    #        print(f" {name:{longest_name}}: "
    #                    f"v{cls.world_version.as_simple_string():{version_count}} | "
    #                    f"Items: {len(cls.item_names):{item_count}} | "
    #                    f"Locations: {len(cls.location_names):{location_count}}")

    #del item_count, location_count

    # This assertion method should not be necessary to run if we are not outputting any multidata.
    if not args.skip_output and not args.spoiler_only:
        AutoWorld.call_stage(multiworld, "assert_generate")

    AutoWorld.call_all(multiworld, "generate_early")

    #print('')

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

    #print('Creating MultiWorld.')
    AutoWorld.call_all(multiworld, "create_regions")

    #print('Creating Items.')
    AutoWorld.call_all(multiworld, "create_items")


    return multiworld



def download_all_apworlds():
    # code copied from apworld manager
    print("Downloading apworlds")
    repositories.load_repos_from_settings()
    repositories.refresh()

    apworlds = refresh_apworld_table()
    for apworld in apworlds:
        try:
            print(f"Downloading apworld {apworld['title']}")
            install_world(apworld)
        except Exception as e:
            print(f"Failed to install {apworld} with exception: {e}")


# needs a nogui arg and ability to time out
def get_stats_one_world(world_name : str, queue,  count=10, timeout=999, *varg, **kwargs) -> None:
    print(f"Collecting stats for {world_name}")
    start = time.time()
    loc_count = []
    for i in range(count):
        if time.time() - start > timeout:
            print(f"World {world_name} timed out after {time.time() - start} seconds, after {i}/{count} successes")
            #stat += deepcopy(loc_count)
            queue.put(deepcopy(loc_count))
            return
            #return loc_count

        try:
            args, seed = main_generate(world_name, *varg, **kwargs)
            multiworld = main_fill(args, seed)
            loc_count.append(len(multiworld.itempool))

            del multiworld
        except Exception as e:
            print(e)
        multiworld = None
        gc.collect(0)
    #stat += deepcopy(loc_count)
    queue.put(deepcopy(loc_count))
    #return deepcopy(loc_count)

def get_stats_all_worlds(count=10, *varg, **kwargs) -> pandas.DataFrame:
    print(f"Getting stats for all worlds")
    data_colum = list(f"Data{i}" for i in range(1, count+ 1))
    stats = []#+ data_colum)


    for i, world_name in enumerate(AutoWorld.AutoWorldRegister.world_types):
        if world_name in ["Archipelago", "shapez", "TUNIC", "Zillion"]:
            continue

        try:
            if i % 10 == 0:
                print(f"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

                Currently completed {i}/{len(AutoWorld.AutoWorldRegister.world_types)} worlds 

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                """)
            # threading does not isolate and multiprocessing requires reimporting entire project for each process, fixed with lasy-loading
            #stat = []
            queue = multiprocessing.Queue()
            thread= multiprocessing.Process(target=get_stats_one_world, args=(world_name, queue, * varg,), kwargs={"count":count, **kwargs})

            #thread= threading.Thread(target=get_stats_one_world, args=(world_name, stat, * varg,), kwargs={"count":count, **kwargs})


            thread.start()

            thread.join()

            stat = queue.get()
            #stat = get_stats_one_world(world_name, count=count, * varg, ** kwargs)

            #print(f"stat {stat}")

            if len(stat) == 0:
                del stat
                continue

            columns = [world_name, statistics.mean(stat), statistics.median(stat), min(stat), max(stat)] #+ stat
            #if len(columns) < 5 + count:
            #    columns += [None for _ in range(count + 5 - len(columns))]
            stats.append(deepcopy(columns))
            del stat
            del columns

            gc.collect(2)
            gc.collect(1)
            gc.collect(0)


        except Exception as e:
            if e == Options.OptionError:
                continue
            traceback.print_exc()
            print(f"World {world_name} failed with exception {e}")

    df  = pandas.DataFrame(stats, columns=["World", "Mean", "Median", "Min", "Max"]) #, dtype=["float16", "int8"]
    return df

def export_stats(stats : pandas.DataFrame) -> None:
    print(f"Exporting stats")

    print(stats.to_markdown())
    stats.to_csv(os.path.join("output", "stats.csv"), index = False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", default=False, action="store_true", help="download all apworlds")
    parser.add_argument("--nogui", default=False, action="store_true", help="Turns off Client GUI.")
    parser.add_argument("--fuzz", default=False, action="store_true", help="Whether to fuzz yamls.")
    parser.add_argument("-n", "--count", default=10, type=int, help="How many times each apworld should run")
    parser.add_argument("-t", "--timeout", default=999, type=float, help="A timeout after which ")
    #should probably addd a timeout if a function has taken to long to run

    args = parser.parse_args()

    if args.download:
        download_all_apworlds()

    count : int = 10
    try:
        count = int(args.count)
    except Exception as e:
        print(e)

    print(f"Generating with count {count}")

    stats = get_stats_all_worlds(count=count, fuzz=args.fuzz, timeout=args.timeout)

    export_stats(stats)



if __name__ == '__main__':
    #gc.set_debug(gc.DEBUG_LEAK)
    debug_mem = True
    if debug_mem:
        tracemalloc.start()


    start = time.time()

    main()

    print(f"Duration {time.time() - start} seconds")
    time.sleep(3)



    if debug_mem:
        print(tracemalloc.get_traced_memory())
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        for frame in top_stats[:10]:
            print(frame)

        #print(gc.get_objects())
