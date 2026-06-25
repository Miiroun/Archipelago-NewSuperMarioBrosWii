"""
This hook implements a hashing function for almost any kind of object and uses this hash function to hash global values
before and after generation, reporting cases where the hash of a global value has changed.

WARNING: This hook is a work-in-progress and is not production-ready.

WARNING: This hook can be slow to start if many worlds are loaded, as it will attempt to hash every global and classvar
of each world class and the module the world class is in.
"""

from types import ModuleType
from typing import Container, ClassVar

from BaseClasses import MultiWorld, Region, Entrance, Item, Location
from worlds.AutoWorld import World

from fuzz import BaseHook, GenOutcome


def hash_by_vars(obj, seen_object_ids):
    try:
        v = vars(obj)
    except TypeError:
        return id(obj)

    if v:
        keys2 = frozenset(k for k in v.keys() if not k.startswith("__"))
        keys_hash = hash(keys2)
        values_hash = hash(tuple(hash_anything(v2, seen_object_ids) for k, v2 in v.items() if k in keys2))
        return hash((keys_hash, values_hash))
    else:
        return id(v)


def hash_anything(obj, hash_memodict: dict[int, int] = None):
    """Hash function that can hash basically anything."""
    obj_id = id(obj)
    if obj_id in hash_memodict:
        return hash_memodict[obj_id]
    else:
        # Put object ID in for now, in-case there is recursion within obj.
        hash_memodict[obj_id] = obj_id

    # Recurse through world modules and classes.
    if (package := getattr(obj, "__package__", "")) and package.startswith("worlds.") and isinstance(obj, ModuleType):
        h = hash_by_vars(obj, hash_memodict)
        hash_memodict[obj_id] = h
        return h
    elif (module := getattr(obj, "__module__", "")) and module.startswith("worlds.") and isinstance(obj, type):
        h = hash_by_vars(obj, hash_memodict)
        hash_memodict[obj_id] = h
        return h
    elif isinstance(obj, (MultiWorld, World, Region, Entrance, Item, Location)):
        # If we somehow get a reference to one of these, they are supposed to change over a generation, and we want to
        # avoid hashing any part of them.
        # Though worlds shouldn't really be putting any of these into module globals or class vars, so raising an
        # exception here could be a valid alternative.
        h = id(obj)
        hash_memodict[obj_id] = h
        return h

    try:
        h = hash(obj)
        hash_memodict[obj_id] = h
        return h
    # Secret of Evermore has some `Tag` class that raises AttributeError when attempting to hash it.
    except (TypeError, AttributeError):
        # While tuples are immutable, they can contain mutable objects.
        if isinstance(obj, (list, tuple)):
            h = hash(tuple(hash_anything(v, hash_memodict) for v in obj))
            hash_memodict[obj_id] = h
            return h
        elif isinstance(obj, dict):
            # Keys must be hashable already.
            keys_hash = hash(frozenset(obj.keys()))
            values_hash = hash(tuple(hash_anything(v, hash_memodict) for v in obj.values()))
            h = hash((keys_hash, values_hash))
            hash_memodict[obj_id] = h
            return h
        elif isinstance(obj, set):
            # The set elements must be hashable already.
            h = hash(frozenset(obj))
            hash_memodict[obj_id] = h
            return h

        h = hash_by_vars(obj, hash_memodict)
        hash_memodict[obj_id] = h
        return h


class HookMutationFailureException(Exception):
    pass


class Hook(BaseHook):
    module_global_hashes: dict[str, dict[str, int]]
    class_var_hashes: dict[str, dict[str, int]]
    failures: Container[str] = ()

    game_module_exclusions: ClassVar[dict[str, set[str]]] = {
        # It is initialised once in stage_generate_early, if it is empty, because it reads and parses a large file.
        "shapez": {"shapesanity_simple"},

        # Technically a failure of what this hook tests. KH2 modifies this global variable for each slot, but only uses
        # the modified value within the same function that modifies KH2REGIONS. Additionally, this function clears the
        # parts of KH2REGIONS that vary by slot at the start of each section within the function.
        # This is particularly fragile code, but it currently (2026-02-23) does not cause any issues.
        "Kingdom Hearts 2": {"KH2REGIONS"},

        # A Utils.KeyedDefaultDict[str, FrozenSet[Technology]] that starts off empty, its keys and values are populated
        # only as it is accessed. Key-value pairs do not get set manually, so there is currently no potential to replace
        # existing values of keys.
        "Factorio": {"required_technologies"},

        # room_to_region starts empty, and is only populated as PhysicalRegion instances are processed through .make().
        # The data put into room_to_region is always the same for a particular PhysicalRegion. The danger is that
        # .make() is only called for the relevant regions of each world.
        # "Rain World": {"room_to_region"},

        # https://github.com/ArchipelagoMW/Archipelago/pull/5944
        "Kingdom Hearts": {"VANILLA_ABILITY_AP_COSTS"},
        # https://github.com/ArchipelagoMW/Archipelago/pull/5947
        "Pokemon Red and Blue": {"item_groups"},
    }
    game_class_var_exclusions: ClassVar[dict[str, set[str]]] = {
        # This is initialised by the enemizer_path property once, from host yaml settings.
        "A Link to the Past": {"_enemizer_path"},
    }
    # This classvar does nothing, and is purely for notetaking.
    to_investigate_module_globals: ClassVar[dict[str, set[str]]] = {
        # room_to_region starts empty, and is only populated as PhysicalRegion instances are processed through .make().
        "Rain World": {"room_to_region"},
    }

    def setup_worker(self, args):
        super().setup_worker(args)
        self.module_global_hashes = {}
        self.class_var_hashes = {}
        from worlds import AutoWorld
        import importlib

        hash_memodict = {}
        for game, world_type in AutoWorld.AutoWorldRegister.world_types.items():
            # Replace globals in the world's module.
            world_module = importlib.import_module(world_type.__module__)
            module_global_hashes = {}
            self.module_global_hashes[game] = module_global_hashes
            exclusions = self.game_module_exclusions.get(game, ())
            for k, v in vars(world_module).copy().items():
                if k.startswith("__") or k in exclusions:
                    continue
                module_global_hashes[k] = hash_anything(v, hash_memodict)
            # Replace class attributes on the World class.
            class_var_hashes = {}
            self.class_var_hashes[game] = class_var_hashes
            exclusions = self.game_class_var_exclusions.get(game, ())
            for k, v in world_type.__dict__.copy().items():
                if k.startswith("__") or k == "_AutoWorldRegister__settings" or k in exclusions:
                    continue
                class_var_hashes[k] = hash_anything(v, hash_memodict)

    def before_generate(self, args):
        super().before_generate(args)
        self.failures = []

    def after_generate(self, mw, output_path):
        super().after_generate(mw, output_path)

        if mw is None:
            # Some other error has occurred.
            return

        from worlds import AutoWorld
        import importlib

        games_in_multiworld = {world.game for world in mw.worlds.values()}

        failures = []
        hash_memodict = {}
        for game, world_type in AutoWorld.AutoWorldRegister.world_types.items():
            if game not in games_in_multiworld:
                continue
            # Check globals in the world's module.
            world_module = importlib.import_module(world_type.__module__)
            module_global_hashes = self.module_global_hashes[game]
            for k, v in vars(world_module).copy().items():
                if k not in module_global_hashes:
                    continue
                old_hash = module_global_hashes[k]
                new_hash = hash_anything(v, hash_memodict)
                if new_hash != old_hash:
                    failures.append(f"Hash comparison failed for {game} world module global {k}")
            # Check class attributes on the World class.
            class_var_hashes = self.class_var_hashes[game]
            for k, v in world_type.__dict__.copy().items():
                if k not in class_var_hashes:
                    continue
                old_hash = class_var_hashes[k]
                new_hash = hash_anything(v, hash_memodict)
                if new_hash != old_hash:
                    failures.append(f"Hash comparison failed for {game} world class attribute {k}")
        self.failures = failures

    def reclassify_outcome(self, outcome, raised):
        if self.failures:
            return GenOutcome.Failure, HookMutationFailureException(self.failures)
        elif outcome != GenOutcome.Success:
            # Ignore other errors.
            return GenOutcome.OptionError, None
        else:
            return super().reclassify_outcome(outcome, raised)



