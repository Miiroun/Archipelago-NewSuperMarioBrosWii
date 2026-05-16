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
    Percentage chance that any given filler item will be replaced with traps.
    """

    display_name = "Trap Chance"

    range_start = 0
    range_end = 100
    default = 30


class RandomizeStarCoins(Toggle):
    """
    If enabled will include 231 star coins as checks and star coins will be received as items.
    If disabled will still create the star coins as ap items but place them in their vanilla locations.
    """
    display_name = "Randomize Star Coins"
    default = True


class RandomizeMovment(Choice):
    """
    WARNING! logic not implemented.
    Will disable some of mario's moves until items checks are sent to reunlock them.
    """
    display_name = "Randomize Moves"

    option_off = 0
    option_on = 2

    default = option_off
    #visibility  = Option.visibility.none

class DontRandoMovement(OptionSet):
    """
    Put movement items here if you want to play with movement except curtain once like spin
    """

    display_name = "Dont Rando these Movements"
    default = {"run", "button_left"}


class RandomizePowerups(Choice):
    """
    Will make power ups not unlockable until items check are sent to reunlock them.
    """
    display_name = "Randomize Powerups"
    option_off = 0
    option_on_except_mushroom = 1
    option_on_progressive = 2
    option_on = 3
    default = option_on_except_mushroom

class IncludeHintMovies(Toggle):
    """
    Makes the hint movies in peach castles into locations, adds 65 locations.
    If remove this then compensate with starter locations to keep #locations > #items.
    """
    display_name = "Include Hint Movies"
    default = True
    #visibility = Option.visibility.complex_ui

class IncludeLevelCompletion(Toggle):
    """
    This makes completing a level into a location, adds 231 locations.
    """
    display_name = "Include Level Completion"
    default = True

class IncludeShortcuts(Toggle):
    """
    If true makes shortcuts like cannons and 7-6 and 8-7 turn into locations.
    Even if option is off will still disable shortcuts.
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
    If hard will make locations that require glitches to be in logic,
    recommended to normal.
    """
    display_name = "Logic Difficulty"
    option_normal = 0
    option_difficult = 1
    default = option_normal
    #visibility  = Option.visibility.none

class StartingWorld(Choice):
    """
    Select the world you want to start with, or keep it at random.
    """
    display_name = "Starting World"
    option_world1 = 1
    option_world2 = 2
    option_world3 = 3
    option_world4 = 4
    option_world5 = 5
    option_world6 = 6
    option_world7 = 7
    option_world8 = 8
    default = "random"

class AmountStartingItems(Range):
    """
    Gives you an amount of free locations that are automatically checked.
    This option is here to create a few free checks that helps with restrictive start errors.
    Put to at least ~25 if you disable both check hint movies and check level completion otherwise you can keep it at 0.
    """

    display_name = "Amount Starting Items"
    range_start = 0
    range_end = 100
    default = 0

class NumberInventoryItems(Range):
    """
    A location that gets collected when you collect a powerup to your inventory, e.g. from a toad house or beating overworld enemy.
    """
    display_name = "Number Inventory Items"
    range_start = 0
    range_end = 999
    default = 40

class BowserCastleStarUnlock(Range):
    """
    This setting applies requirements of at least x star coins to unlock final level
    Recommended to have bellow ~ 200 to not get fill errors
    """

    display_name = "Bowser Castle Unlock Star"
    range_start = 0
    range_end = 231

    default = 100

class BowserCastleWorldUnlock(Range):
    """
    This setting applies requirements to unlock final level
    Set this to amount of worlds needed to beat the game
    """

    display_name = "Bowser Castle Unlock World"
    range_start = 0
    range_end = 7

    default = 4

class DeathLink(Toggle):
    """
    Enable death-link as default, can be toggled in client.
    """
    display_name = "Death Link"
    default = True

class AmountSupportReceived(Range):
    """
    This setting will set the amount of 1ups and powerups send to inventory when receiving their corresponding items.
    """
    display_name = "Amount Support items received from ap-items"
    range_start = 1
    range_end = 100

    default = 5

class FillerItems(OptionSet):
    """
    Select which filler items you want to have be possible to generate.
    """
    display_name = "Filler Items"
    from .Utils import FILLER
    default = set(FILLER)

class TrapItems(OptionSet):
    """
    Select which filler items you want to have be possible to generate.
    """
    display_name = "Trap Items"
    from .Utils import TRAPS
    default = set(TRAPS)


# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class NSMBWOptions(PerGameCommonOptions):
    include_level_completion : IncludeLevelCompletion
    include_shortcuts : IncludeShortcuts
    include_hintmovies : IncludeHintMovies
    randomize_coins: RandomizeStarCoins

    randomize_movement : RandomizeMovment
    dont_rando_move : DontRandoMovement
    randomize_powerups : RandomizePowerups

    trap_chance: TrapChance
    logic_difficulty: LogicDifficulty
    starting_world: StartingWorld
    num_starting_locations : AmountStartingItems
    death_link : DeathLink
    enable_superpowers : EnableSuperPowers
    amount_support_received : AmountSupportReceived
    num_inventory_powerups : NumberInventoryItems
    filler_items : FillerItems
    trap_items : TrapItems

    bowser_star_unlock : BowserCastleStarUnlock
    bowser_world_unlock : BowserCastleWorldUnlock


# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
    OptionGroup(
        "Locations ",
        [
            IncludeShortcuts,
            IncludeLevelCompletion,
            IncludeHintMovies,
            RandomizeStarCoins,
            NumberInventoryItems,
            AmountStartingItems,
        ],
    ),
    OptionGroup(
        "Items",
        [
            RandomizePowerups,
            RandomizeMovment,
            DontRandoMovement
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
            DeathLink,
            LogicDifficulty,
            EnableSuperPowers,
            FillerItems,
            TrapItems,
            TrapChance,
            AmountSupportReceived,
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
#        "num_starting_locations" : 10,
#        "death_link" : False,
#    }
}


def adjust_options(world):

    if (world.options.include_hintmovies.value == False) and (world.options.include_level_completion.value == False):
        if world.options.num_starting_locations.value <= 20:
            pass
            #world.options.num_starting_locations.value = 20
            #print("If you disable hint movies and level completion have at least 20 free starting locations")
        #raise OptionError("IncludeHintMovies or IncludeLevelCompletion to have enough locations")
    #if world.options.randomize_coins == False:
    #    raise OptionError("RandomizeStarCoins is not implemented to be turned off")
    if world.options.bowser_star_unlock.value >200:
        world.options.bowser_star_unlock.value = 200
        print("Generation fails when star req for reaching bowser is > 200")

    from .items import MOVEMENT_UNLOCKS
    movement_set = set(MOVEMENT_UNLOCKS)
    if len(world.options.dont_rando_move.value - movement_set) > 0:
        print(f"Texts {world.options.dont_rando_move.value - movement_set} is not a valid movement.")
        world.options.dont_rando_move.value &= movement_set

    from .items import FILLER
    filler_set = set(FILLER)
    if len(world.options.filler_items.value - filler_set) > 0:
        print(f"Texts {world.options.filler_items.value - filler_set} are not a valid filler item.")
        world.options.filler_items.value &= filler_set

    from .items import TRAPS
    trap_set = set(TRAPS)
    if len(world.options.trap_items.value - trap_set) > 0:
        print(f"Texts {world.options.trap_items.value - trap_set} are not a valid trap item.")
        world.options.filler_items.value &= trap_set