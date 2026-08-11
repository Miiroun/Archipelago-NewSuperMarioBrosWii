from .bases import *


class WorldBase(NSMBWWorld):
    options = {
        "randomize_abilites": True,
        "abilites_included": AbilitiesIncluded.default,
        "randomize_level_elements": True,
        "level_elements_included": LevelElementsIncluded.default,
        "randomize_enemies": RandomizeEnemies.option_add,
        "enemies_included": EnemiesIncluded.default,
        "starting_world": 1
    }


class TestWorld1(WorldBase):
    options = WorldBase.options | {
        "starting_world": 1
    }


class TestWorld2(WorldBase):
    options = WorldBase.options | {
        "starting_world": 2
    }


class TestWorld3(WorldBase):
    options = WorldBase.options | {
        "starting_world": 3
    }


class TestWorld4(WorldBase):
    options = WorldBase.options | {
        "starting_world": 4
    }


class TestWorld5(WorldBase):
    options = WorldBase.options | {
        "starting_world": 5
    }


class TestWorld6(WorldBase):
    options = WorldBase.options | {
        "starting_world": 6
    }


class TestWorld7(WorldBase):
    options = WorldBase.options | {
        "starting_world": 7
    }


class TestWorld8(WorldBase):
    options = WorldBase.options | {
        "starting_world": 8
    }

