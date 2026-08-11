from .bases import *


for world_num in range(1, 8+1):
    class TestWorldNum(NSMBWWorld):
        options = {
            "randomize_abilites" : True,
            "abilites_included" : AbilitiesIncluded.default,
            "randomize_level_elements" : True,
            "level_elements_included" : LevelElementsIncluded.default,
            "randomize_enemies" : RandomizeEnemies.option_add,
            "enemies_included" : EnemiesIncluded.default,
            "starting_world" : world_num
        }