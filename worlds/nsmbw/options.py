import settings
from Options import *


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
    Traps are not currently implemented
    Percentage chance that any given filler item will be replaced with traps.
    """

    display_name = "Trap Chance"

    range_start = 0
    range_end = 100
    default = 0


class RandomizeStarCoins(Toggle):
    """
    Dissabling is not yet implented
    If enabled will include starcoins as checks and starcoins will be recived as items
    """
    display_name = "Randomize Star Coins"
    default = True


class RandomizeMovment(Choice):
    """
    Will disable some of marios moves until items checks are sent to reunlock them.
    """
    # should make spin a seperet option
    display_name = "Randomize Moves"

    option_off = 0
    option_on_except_spin = 1
    option_on = 2

    default = option_off

class RandomizePowerups(Choice):
    """
    Will make power ups not unlockable until items check are sent to reunlock them.
    """
    # should make mushroom a seperet option
    display_name = "Randomize Powerups"
    option_off = 0
    option_on_except_mushroom = 1
    option_on_progressive = 2
    option_on = 3
    default = option_on_progressive

class IncludeHintMovies(Toggle):
    """
    Makes the hint movies in peach castles into locations
    If remove this then compensate with starter locations to keep #locations > #items
    """
    display_name = "Include Hint Movies"
    default = True

class IncluedLevelCompletion(Toggle):
    """
    This makes completing a level a check
    """
    display_name = "Inclue Level Completion"
    default = False


class EnableSuperPowers(Toggle):
    """
    Not currently implemented
    Adds extra powers like double jump to item pool
    """
    display_name = "Enable Super Powers"
    default = False

class LogicDifficulty(Choice):
    """
    If hard will make checks that require glitches to be in logic,
    recommended to normal
    """
    display_name = "Logic Difficulty"
    option_normal = 0
    option_difficult = 1
    default = option_normal

class StartingWorld(Toggle):
    """
    A toggle if you should start with world 1 or random
    """
    display_name = "Starting World"

    default = True

class AmountStartingItems(Range):
    """
    This option is here to create a few free checks that helps with restrictive start error.
    Put to at least ~ if you disable both check hintmovies and check level completion
    """

    display_name = "Amount Starting Items"
    range_start = 0
    range_end = 100
    default = 0

class BowserCastleStarUnlock(Range):
    """
    This setting applies requirements of at least x starcoins to unlock final level
    Recommended to have bellow ~ 200 to not get fill errors
    """

    display_name = "Bowser Castle Unlock Star"
    range_start = 0
    range_end = 271

    default = 0

class BowserCastleWorldUnlock(Range):
    """
    This setting applies requirements to unlock final level
    Set this to amount of worlds needed to beat the game
    """

    display_name = "Bowser Castle Unlock World"
    range_start = 0
    range_end = 7

    default = 0

class DeathLink(Toggle):
    """
    Enable death-link as default, can be toggled in client.
    """
    display_name = "Death Link"
    default = False


# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class NSMBWOptions(PerGameCommonOptions):
    trap_chance: TrapChance
    randomize_coins: RandomizeStarCoins
    logic_difficulty: LogicDifficulty
    starting_world: StartingWorld
    include_hintmovies : IncludeHintMovies
    randomize_movement : RandomizeMovment
    randomize_powerups : RandomizePowerups
    num_startloc : AmountStartingItems
    death_link : DeathLink
    bowser_star_unlock : BowserCastleStarUnlock
    bowser_world_unlock : BowserCastleWorldUnlock
    include_level_compleation : IncluedLevelCompletion

# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
#    OptionGroup(
#        "Gameplay Options",
#        [
#            TrapChance,
#            RandomizeStarCoins,
#            LogicDifficulty,
#            StartingWorld,
#            RandomizeLevelCompletion,
#            RandomizeMovment,
#            RandomizePowerups,
#            IncludeHintMovies,
#            AmountStartingItems,
#            DeathLink,
#            BowserCastleStarUnlock,
#            BowserCastleWorldUnlock,
#         ],
#
#    ),
]

# Finally, we can define some option presets if we want the player to be able to quickly choose a specific "mode".
option_presets = {
#    "standard": {
#        "trap_chance": 0,
#        "randomize_coins": True,
#        "logic_difficulty": LogicDifficulty.option_normal,
#        "starting_world": True,
#        "randomize_level_completion" : False,
#        "randomize_movement" : False,
#        "randomize_powerups" : 2,
#        "include_hintmovies": True,
#        "num_startloc" : 10,
#        "death_link" : False,
#    }
}
