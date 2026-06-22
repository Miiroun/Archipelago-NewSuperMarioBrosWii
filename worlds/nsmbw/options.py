from Options import *
from .Common import *

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

class StarCoinCollectImmediately(Toggle):
    """
    BETA
    If enabled will send checks for star coins directly when collected,
    otherwise will send them on level completion
    """
    display_name = "Star Coin Collect immediately"
    default = False

    #visibility = Option.visibility.none


class RandomizeMovement(Choice):
    """
    Will disable some of mario's moves until items checks are sent to reunlock them.
    """
    display_name = "Randomize Moves"

    option_off = 0
    option_on = 2

    default = option_off
    #visibility  = Option.visibility.none

class DontRandoMovement(ItemSet):
    """
    Put movement items here if you want to play with movement except certain once.
    Turning on the default moves here can and will cause issue, they are experimental
    """

    display_name = "Dont Rando these Movements"
    valid_keys = set(MOVEMENT_UNLOCKS)
    default = {ITEM.MOVEMENT.ButtonLeft.value, ITEM.MOVEMENT.Run.value}


class RandomizePowerups(Choice):
    """
    Will make power ups not unlockable until items check are sent to reunlock them.
    """
    display_name = "Randomize Power-ups"
    option_off = 0
    option_on_except_mushroom = 1
    option_on_progressive = 2
    option_on = 3
    default = option_on_except_mushroom

class RandomizeTime(Range):
    """
    Will make your starting time be separated into discreet section. Select O if you want to disable this option.
    """

    range_start = 0
    range_end = 10
    #range_end = 20
    default = 0
    #default = 5

    #visibility = Option.visibility.complex_ui

class IncludeHintMovies(Toggle):
    """
    Makes the hint movies in peach castles into locations, adds 65 locations.
    If remove this then compensate with starter locations to keep #locations > #items.
    """
    display_name = "Include Hint Movies"
    default = True

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

class LogicOutsidePowerups(Choice):
    """
    Sett this to allow if you want solution involving bringing powerups from outside the level to be in logic.
    """
    display_name = "Logic Outside Power-ups"
    option_disallow = 0
    option_allow = 1
    default = option_allow

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

class World9UnlockCondition(Choice):
    """
    BETA
    Select in which way world 9 levels will be unlocked
    Linear      : 9-1 req 20 SC, 9-2 req e0 SC, etc.
    Gaussian    : The unlocking will be a gaussian distribution with mean = 80 SC and standard deviation = 40
    """
    display_name = "World 9 Unlock Condition"
    option_linear = 2
    option_gaussian = 3

    default = option_gaussian

class IncludeStartingItems(Range):
    """
    Gives you an amount of free locations that are automatically checked.
    This option is here to create a few free checks that helps with restrictive start errors.
    Put to at least ~25 if you disable both check hint movies and check level completion and have IncludeNumberInventoryItems = 0
    otherwise you can keep it at 0.
    """

    display_name = "Include Starting Items"
    range_start = 0
    range_end = 100
    default = 0

class IncludeNumberInventoryItems(Range):
    """
    A location that gets collected when you collect a powerup to your inventory, e.g. from a toad house or beating overworld enemy.
    """
    display_name = "Include Inventory Items"
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

    default = 2

class DeathLink(DeathLink):
    """
    Enable death-link as default, can be toggled in client.
    """
    display_name = "Death Link"
    default = False

class DeathLinkGroup(FreeText):
    """Death Link only applies to players with an identical Group name.
    Games that don't support the Group option count as having an empty group name."""
    display_name = "Death Link Group"
    rich_text_doc = True
    default = ""


class AmountSupportReceived(Range):
    """
    This setting will set the amount of 1ups and powerups send to inventory when receiving their corresponding items.
    """
    display_name = "Amount Support items received from ap-items"
    range_start = 1
    range_end = 100

    default = 5

class FillerItems(ItemSet):
    """
    Select which filler items you want to have be possible to generate.
    """
    display_name = "Filler Items"
    valid_keys = set(FILLER)
    default = set(FILLER)

class TrapItems(ItemSet):
    """
    Select which filler items you want to have be possible to generate.
    """
    display_name = "Trap Items"
    valid_keys = set(TRAPS)
    default = set(TRAPS)

class SaveStateSlot(Range):
    """
    Which save state slot the client should use to auto save too
    """
    display_name = "Save Slot"
    range_start = 1
    range_end = 7
    default = 7

class ModifierMultiplierPercentage(Range):
    """
    A percentage which to multiply the modifier time with.
    Will still clear on death.
    """
    display_name = "Modifier Multiplier Percentage"
    range_start = 1
    range_end = 1000
    default = 100

# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class NSMBWOptions(PerGameCommonOptions):
    include_level_completion : IncludeLevelCompletion
    include_shortcuts : IncludeShortcuts
    include_hintmovies : IncludeHintMovies
    randomize_starcoins: RandomizeStarCoins
    include_inventory_powerups : IncludeNumberInventoryItems
    include_starting_locations : IncludeStartingItems


    randomize_movement : RandomizeMovement
    dont_rando_move : DontRandoMovement
    randomize_powerups : RandomizePowerups
    randomize_time : RandomizeTime

    logic_difficulty: LogicDifficulty
    logic_outside_powerup : LogicOutsidePowerups
    starting_world: StartingWorld
    world9_unlock_condition : World9UnlockCondition

    amount_support_received : AmountSupportReceived
    filler_items : FillerItems
    trap_items : TrapItems
    trap_chance: TrapChance


    bowser_star_unlock : BowserCastleStarUnlock
    bowser_world_unlock : BowserCastleWorldUnlock

    death_link : DeathLink
    death_link_group : DeathLinkGroup
    starcoin_collect_immediately : StarCoinCollectImmediately

    save_state_slot : SaveStateSlot
    modifier_multiplier_percentage : ModifierMultiplierPercentage

# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
    OptionGroup(
        "Locations ",
        [
            IncludeShortcuts,
            IncludeLevelCompletion,
            IncludeHintMovies,
            RandomizeStarCoins,
            IncludeNumberInventoryItems,
            IncludeStartingItems,
        ],
    ),
    OptionGroup(
        "Items",
        [
            RandomizePowerups,
            RandomizeMovement,
            DontRandoMovement,
            RandomizeTime,
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
        "Logic",
        [
            LogicDifficulty,
            LogicOutsidePowerups,
            World9UnlockCondition,
            StartingWorld,
        ]
    ),
    OptionGroup(
        "Filler and traps",
        [
            FillerItems,
            TrapItems,
            TrapChance,
            AmountSupportReceived,
        ]
    ),
    OptionGroup(
        "Other",
        [
            DeathLink,
            DeathLinkGroup,
            StarCoinCollectImmediately,
            SaveStateSlot,
            ModifierMultiplierPercentage
        ],
    ),
]

option_presets = {
    "standard/recomeneded": {
        "include_level_completion": IncludeLevelCompletion.default,
        "include_shortcuts": IncludeShortcuts.default,
        "include_hintmovies": IncludeHintMovies.default,
        "randomize_starcoins": RandomizeStarCoins.default,

        "randomize_movement": RandomizeMovement.default,
        "dont_rando_move": DontRandoMovement.default,
        "randomize_powerups": RandomizePowerups.default,
        "randomize_time": RandomizeTime.default,
        "starting_world": StartingWorld.default,
        "include_inventory_powerups": IncludeNumberInventoryItems.default,
        "include_starting_locations": IncludeStartingItems.default,
        "logic_difficulty" : LogicDifficulty.default,
        "death_link": DeathLink.default,


        "bowser_star_unlock": BowserCastleStarUnlock.default,
        "bowser_world_unlock": BowserCastleWorldUnlock.default
    },
    "Minimal": {
        "include_level_completion": IncludeLevelCompletion.option_false,
        "include_shortcuts": IncludeShortcuts.option_false,
        "include_hintmovies": IncludeHintMovies.option_false,
        "randomize_starcoins": RandomizeStarCoins.option_false,
        "starting_world": 1,
        "include_inventory_powerups": 0,
        "include_starting_locations": 0,

        "randomize_movement": RandomizeMovement.option_off,
        "dont_rando_move": set(MOVEMENT_UNLOCKS),
        "randomize_powerups": RandomizePowerups.option_off,
        "randomize_time": 0,

        "bowser_star_unlock": 0,
        "bowser_world_unlock": 0,
        "logic_difficulty" : LogicDifficulty.option_normal,
        "death_link": DeathLink.option_false,
    },
    "Maximal": {
        "include_level_completion": IncludeLevelCompletion.option_true,
        "include_shortcuts": IncludeShortcuts.option_true,
        "include_hintmovies": IncludeHintMovies.option_true,
        "randomize_starcoins": RandomizeStarCoins.option_true,
        "starting_world": "random",
        "include_inventory_powerups" : 999,
        "include_starting_locations" : 0,

        "randomize_movement": RandomizeMovement.option_on,
        "dont_rando_move": set(),
        "randomize_powerups": RandomizePowerups.option_on,
        "randomize_time": 5,

        "bowser_star_unlock": 231, #231
        "bowser_world_unlock": 7,
        "logic_difficulty" : LogicDifficulty.option_difficult,
        "death_link": DeathLink.option_true,
    }


}


def adjust_options(world):
    # This section tests if to many location options are turned off and tries to compensate for it.
    req_start_loc = -10
    req_start_loc_max = 10
    if (world.options.include_hintmovies.value == False):
        #print(f"(NSMBW generation error) Turning off include_hintmovies can cause fill errors with a low amount of num_starting_locations.")
        req_start_loc += 5
    if (world.options.include_level_completion.value == False):
            #print(f"(NSMBW generation error) Turning off include_level_completion can cause fill errors with a low amount of num_starting_locations.")
            req_start_loc += 30
            req_start_loc_max += 15
    if (world.options.randomize_starcoins.value == False):
        #print(f"(NSMBW generation error) Turning off randomize coin can cause fill errors with a low amount of num_starting_locations.")
        req_start_loc += 15
    if (world.options.include_shortcuts.value == False):
        #print(f"(NSMBW generation error) Turning off include_shortcuts can cause fill errors with a low amount of num_starting_locations.")
        req_start_loc += 5

    if world.options.include_starting_locations.value <= req_start_loc:
        print(f"Low amount of locations detected in nsmbw, this can cause fill errors if generate alone")
        #print(f"(NSMBW generation error) Generation determined that you have to low num_starting_locations, requires at least {req_start_loc} for a stable generation.")
        #world.options.include_starting_locations.value = min(req_start_loc, req_start_loc_max)


    MAX_ALLOWED_BOWSER_SC = 200
    if world.options.bowser_star_unlock.value > MAX_ALLOWED_BOWSER_SC:
        world.options.bowser_star_unlock.value = MAX_ALLOWED_BOWSER_SC
        print(f"(NSMBW generation error) Generation fails when star req for reaching bowser is > {MAX_ALLOWED_BOWSER_SC}")

    movement_set = set(MOVEMENT_UNLOCKS)
    if len(world.options.dont_rando_move.value - movement_set) > 0:
        print(f"(NSMBW generation error) Texts {world.options.dont_rando_move.value - movement_set} is not a valid movement.")
        world.options.dont_rando_move.value &= movement_set


    filler_set = set(FILLER)
    if len(world.options.filler_items.value - filler_set) > 0:
        print(f"(NSMBW generation error) Texts {world.options.filler_items.value - filler_set} are not a valid filler item.")
        world.options.filler_items.value &= filler_set
    if world.options.trap_chance.value != 100:
        if len(world.options.filler_items.value) == 0:
            print("(NSMBW generation error) You need to have at least one filler item.")
            world.options.filler_items.value = filler_set


    trap_set = set(TRAPS)
    if len(world.options.trap_items.value - trap_set) > 0:
        print(f"(NSMBW generation error) Texts {world.options.trap_items.value - trap_set} are not a valid trap item.")
        world.options.filler_items.value &= trap_set
    if world.options.trap_chance.value != 0:
        if len(world.options.trap_items.value) == 0:
            print("(NSMBW generation error) You need to have at least one trap item.")
            world.options.trap_items.value = trap_set
