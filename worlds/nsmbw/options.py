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
    If enabled will include starcoins as checks and starcoins will be recived as items.
    If dissabed will still create the starcoins as ap items but place them in their vanilla locations.
    """
    display_name = "Randomize Star Coins"
    default = True


class RandomizeMovment(Choice):
    """
    WARNING! logic not implemented.
    Will disable some of marios moves until items checks are sent to reunlock them.
    """
    # should make spin a seperet option
    display_name = "Randomize Moves"

    option_off = 0
    option_on_except_spin = 1
    option_on = 2

    default = option_off
    #visibility  = Option.visibility.none

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
    display_name = "Include Level Completion"
    default = False

class IncludeShortcuts(Toggle):
    """
    If true makes shortcuts like cannoncs and 7-6 and 8-7 turn into checks.
    Even if option is off will still dissable shortcuts.
    """
    display_name = "Include Shortcuts"
    default = True

class EnableSuperPowers(Toggle):
    """
    Not currently implemented
    Adds extra powers like double jump to item pool
    """
    display_name = "Enable Super Powers"
    default = False
    visibility  = Option.visibility.none

class LogicDifficulty(Choice):
    """
    If hard will make checks that require glitches to be in logic,
    recommended to normal
    """
    display_name = "Logic Difficulty"
    option_normal = 0
    option_difficult = 1
    default = option_normal
    #visibility  = Option.visibility.none

class StartingWorld(Range):
    """
    If enabled will randomize your staring world.
    """
    display_name = "Starting World"
    range_start = 1
    range_end = 8

    default = random

class AmountStartingItems(Range):
    """
    Gives you an amount of free locations that are automatically checked.
    This option is here to create a few free checks that helps with restrictive start error.
    Put to at least ~25 if you disable both check hint movies and check level completion otherwise you can keep it at 0.
    """

    display_name = "Amount Starting Items"
    range_start = 0
    range_end = 100
    default = 0

class BowserCastleStarUnlock(Range):
    """
    This setting applies requirements of at least x star coins to unlock final level
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

class AmountSupportRecived(Range):
    """
    This setting will set the amount of 1ups and powerups send to inventory when reciving their corresponding checks.
    """
    display_name = "Amount Support items recived from ap-items"
    range_start = 1
    range_end = 100

    default = 5


# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class NSMBWOptions(PerGameCommonOptions):
    include_level_compleation : IncluedLevelCompletion
    include_shortcuts : IncludeShortcuts
    include_hintmovies : IncludeHintMovies
    randomize_coins: RandomizeStarCoins

    randomize_movement : RandomizeMovment
    randomize_powerups : RandomizePowerups

    trap_chance: TrapChance
    logic_difficulty: LogicDifficulty
    starting_world: StartingWorld
    num_startloc : AmountStartingItems
    death_link : DeathLink
    enable_superpowers : EnableSuperPowers
    amount_support_recived : AmountSupportRecived


    bowser_star_unlock : BowserCastleStarUnlock
    bowser_world_unlock : BowserCastleWorldUnlock


# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
    OptionGroup(
        "Locations ",
        [
            IncludeShortcuts,
            IncluedLevelCompletion,
            IncludeHintMovies,
            RandomizeStarCoins,
         ],
    ),
    OptionGroup(
        "Items",
        [
            RandomizeMovment,
            RandomizePowerups
        ],
    ),
    OptionGroup(
        "Clear condition",
        [
            BowserCastleStarUnlock,
            BowserCastleWorldUnlock,
        ],
    ),
    OptionGroup(
        "Other",
        [
            TrapChance,
            AmountStartingItems,
            DeathLink,
            LogicDifficulty,
            EnableSuperPowers,
            AmountSupportRecived,
        ],
    ),
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


def adjust_options(world):

    if (world.options.include_hintmovies.value == False) and (world.options.include_level_compleation.value == False):
        if world.options.num_startloc.value <= 20:
            world.options.num_startloc.value = 20
            print("If you dissable hint movies and level completion have at least 20 free starting locaitions")
        #raise OptionError("IncludeHintMovies or IncludeLevelCompletion to have enough locations")
    #if world.options.randomize_coins == False:
    #    raise OptionError("RandomizeStarCoins is not implemented to be turned off")
    if world.options.bowser_star_unlock.value >200:
        world.options.bowser_star_unlock.value = 200
        print("Generation fails when star req for reaching bowser is >200")