from dataclasses import dataclass

import settings
from Options import *
from settings import Bool


# In this file, we define the options the player can pick.
# The most common types of options are Toggle, Range and Choice.

# Options will be in the game's template yaml.
# They will be represented by checkboxes, sliders etc. on the game's options page on the website.
# (Note: Options can also be made invisible from either of these places by overriding Option.visibility.
#  APQuest doesn't have an example of this, but this can be used for secret / hidden / advanced options.)

# For further reading on options, you can also read the Options API Document:
# https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/options%20api.md


# The first type of Option we'll discuss is the Toggle.
# A toggle is an option that can either be on or off. This will be represented by a checkbox on the website.
# The default for a toggle is "off".
# If you want a toggle to be on by default, you can use the "DefaultOnToggle" class instead of the "Toggle" class.


class TrapChance(Range):
    """
    Percentage chance that any given Confetti Cannon will be replaced by a Math Trap.
    """

    display_name = "Trap Chance"

    range_start = 0
    range_end = 100
    default = 0


class RandomizeStarCoins(Toggle):
    """
    If enabled will include starcoins as checks
    """
    display_name = "Randomize Star Coins"
    default = True

class LogicDifficulty(Choice):
    """
    If hard will make checks that require trecet skill to be in logic,
    recommended to normal
    """
    display_name = "Logic Difficulty"
    option_normal = 0
    option_difficult = 1
    default = option_normal

class StartingWorld(Range):
    """
    Selects you starting world,
    recommended to select randomly
    """
    display_name = "Starting World"

    range_start = 1
    range_end = 8
    default = 1

# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class NSMBWOptions(PerGameCommonOptions):
    trap_chance: TrapChance
    randomize_coins: RandomizeStarCoins
    logic_difficulty: LogicDifficulty
    starting_world: StartingWorld


# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
    OptionGroup(
        "Gameplay Options",
        [
            TrapChance,
            RandomizeStarCoins,
            LogicDifficulty,
            StartingWorld,
         ],

    ),
]

# Finally, we can define some option presets if we want the player to be able to quickly choose a specific "mode".
option_presets = {
    "boring": {
        "trap_chance": 0,
        "randomize_coins": True,
        "logic_difficulty": LogicDifficulty.option_normal,
        "starting_world": 1,
    }
}

class NSMBWSettings(settings.Group):
    pass
    #class Rom_path(settings.FilePath):
    #    desciption = "ROM Path"
    #    location = ""
    #rom_path : Rom_path = None