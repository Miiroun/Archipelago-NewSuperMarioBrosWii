from .bases import *

class TestUnlocksOn(NSMBWTestBase):
    options = {
        "randomize_abilites" : True,
        "abilites_included" : AbilitiesIncluded.default, #valid_keys
        "randomize_level_elements" : True,
        "level_elements_included" : LevelElementsIncluded.default, #valid_keys
        "randomize_enemies" : RandomizeEnemies.option_off,
        "enemies_included" : {},
        "starting_world" : 1,
        "world_comp_priority": False
    }

class TestUnlocksOnEnemyRemove(NSMBWTestBase):
    options = {
        "randomize_abilites" : False,
        "abilites_included" : {},
        "randomize_level_elements" : False,
        "level_elements_included" : {},
        "randomize_enemies" : RandomizeEnemies.option_remove,
        "enemies_included" : EnemiesIncluded.valid_keys,
        "starting_world" : 1,
        "world_comp_priority": False
    }

class TestUnlocksIncludeOff(NSMBWTestBase):
    options = {
        "randomize_abilites" : False,
        "abilites_included" : {},
        "randomize_level_elements" : False,
        "level_elements_included" : {},
        "randomize_enemies" : RandomizeEnemies.option_add,
        "enemies_included" :  EnemiesIncluded.valid_keys,
        "starting_world": 1,
        "world_comp_priority" : False
    }


class TestUnlocksRandoOff(NSMBWTestBase):
    options = {
         "randomize_abilites" : False,
        "abilites_included" : {},
        "randomize_level_elements" : False,
        "level_elements_included" : {},
        "randomize_enemies" : RandomizeEnemies.option_off,
        "enemies_included" : EnemiesIncluded.valid_keys,
        "starting_world": 1,
        "world_comp_priority": False
    }

class TestUnlocksOff(NSMBWTestBase):
    options = {
        "randomize_abilites" : False,
        "abilites_included" : {},
        "randomize_level_elements" : False,
        "level_elements_included" : {},
        "randomize_enemies" : RandomizeEnemies.option_off,
        "enemies_included" :  {},
        "starting_world": 1,
        "world_comp_priority": False
    }
