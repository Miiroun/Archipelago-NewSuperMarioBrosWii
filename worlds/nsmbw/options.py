from Options import *
from .Common import *

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .world import NSMBWworld

class AlternativeGoal(Choice):
    """
    Which goal to have
    Bowser : beat 8-C
    Starcoin : have starcoin = requirement
    Hintmovie : have all hintmovie locations
    """
    display_name = "Alternative Goal"
    option_bowser = 0
    option_starcoins = 1
    option_hintmovies = 2

    default = option_bowser


class TrapChance(Range):
    """
    The percentage ratio of fillers that will be traps.
    """

    display_name = "Trap Chance"

    range_start = 0
    range_end = 100
    default = 15


class StarcoinSanity(Toggle):
    """
    If enabled will include 231 star coins as locations and items.
    If disabled will still create the star coins as ap items but place them in their vanilla locations.
    """
    display_name = "Starcoin Sanity"
    default = True

class StarCoinCollectImmediately(Toggle):
    """
    If enabled will send checks for star coins directly when collected,
    otherwise will send them on level completion.
    Does NOT impact logic, you will still be expected to complete a level before its star coins are in logic.
    """
    display_name = "Star Coin Collect immediately"
    default = True



class RandomizeAbilities(Toggle):
    """
    If ability randomizer should be enabled. (former movement rando)
    If enabled will shuffle all abilities in Abilities Included into the item pool
    They will need to be unlocked to be used.
    """

class AbilitiesIncluded(ItemSet):
    """
    Which abilities are shuffled into the item pool.
    Requires Randomize Abilities to be enabled.
    Consider not enabling run on your first attempt since it slows you down significantly.
    More abilities exists as secret options as they have smaller issues.
    They are: Spin jump and Climb
    """
    valid_keys = set(ABILITIES) - {ITEM.ABILITIES.ButtonUp.ButtonRight.value, ITEM.ABILITIES.ButtonLeft.value,
                                   ITEM.ABILITIES.ButtonDown.value, ITEM.ABILITIES.ButtonUp.value,
                                   ITEM.ABILITIES.Jump.value}
    default = valid_keys - {ITEM.ABILITIES.SpinJump.value,ITEM.ABILITIES.Climb.value} #  ITEM.ABILITIES.Run.value,


class RandomizeLevelElements(Toggle):
    """
    Whether level elements (also called level gimmicks) should be shuffled into the item pool.
    Uses the list from LevelElementsIncluded
    """

class LevelElementsIncluded(ItemSet):
    """
    Which level elements are shuffled into the item pool.
    Requires Randomize Level Elements to be enabled.
    The only valid none default option is pipe, which still is required for most world starts.
    """
    valid_keys = set(LEVEL_ELEMENTS) - {ITEM.LEVELELEMENTS.QuestSwitch.value}
    default = valid_keys - {ITEM.LEVELELEMENTS.Pipe.value}


class RandomizeEnemies(Choice):
    """

    """

    option_off = 0
    option_add = 1
    option_remove = 2
    visibility = Visibility.none


class EnemiesIncluded(ItemSet):
    """

    """
    valid_keys = set(ENEMIES)
    default = valid_keys
    visibility = Visibility.none



class RandomizePowerups(Choice):
    __doc__ = f"""
    Will randomize {POWERUP_UNLOCK}. Notably Star counts as an ability.
    They will require the archipelago item to pick its super 
    on_except_mushroom: (recommended) Will randomize all powerups except Super Mushroom. 
    on_progressive: Treats all powerups as Super Mushroom if the item Super Mushroom is not received.
    """
    display_name = "Randomize Power-ups"
    option_off = 0
    option_on_except_mushroom = 1
    option_on_progressive = 2
    option_on = 3
    default = option_on_except_mushroom

class RandomizeTime(Range):
    """
    Will make your starting time be separated into discreet section and you will start with one.
    E.g. if 5 then you will start with 100 mario seconds and each time item will give you 100 more,
    if 2 then start with 250 mario seconds and one time that unlocks 250 more.
    Select O if you want to disable this option.
    """
    display_name  = "Randomize Time, BETA (logic sometimes problematic)"

    range_start = 0
    range_end = 25
    #range_end = 10
    #range_end = 20
    default = 0
    #default = 5

    visibility = Visibility.none

class RandomizeBossHealth(Toggle):
    """
    If enabled all kopalings will start out with having 10 health.
    This number is reduced by 1 for each Boss Health item you receive
    """
    default = False

class HintMovieSanity(Toggle):
    """
    Hint movies in peach castles are locations, adds 65 locations.
    You will need to receive starcoin items and complete levels to buy them.
    """
    display_name = "Include Hint Movies"
    default = False

class HintMovieShopPriceLogic(Choice):
    """
    This option changes how logic for hint movies is decided.
    free (recommended)            : Hint movies does not cost starcoin items, just needs levels to be unlocked.
    ordered                       : Logic assumes you buy the movies in order, doing otherwise messes with logic (and can very rarely make you seed unbeatable).
    all                           : Logic assumes you have all star coins before a movie is in logic. This causes them to be very late spheres.
    progressive (not implemented) : Groups hintmovies together and requires all in that group to be bought before unlocking next group.
    """
    display_name = "Hint Movie Shop Price Logic"
    option_free = 0
    option_ordered = 1
    option_all = 2
    option_progressive = 3

    default = option_free

class StarCoinShopMultiplier(Range):
    """
    A multiplier for what a star coin is worth when buying from the hint movie store.
    """
    display_name = "Starcoin shop multiplier"
    range_start = 1
    range_end = 10
    default = 3


class LevelCompletion(Toggle):
    """
    All level clears are locations.
    Adds 231 locations.
    (Strongly recommended to enabled).
    """
    display_name = "Include Level Completion"
    default = True


class ShortcutSanity(Choice):
    """
    Enabled:Turns all secret exit and some normal exits into locations and unlockable items.
        Exits still needs to be unlocked as vanilla to be able to be used.
    Disabled : Lock disable non-necessary shortcuts, no ap location / items will be created.
    Dont_lock : Like disabled but most shortcuts (excluding cannons) will behave as vanilla.
    """
    display_name = "Include Shortcuts"
    option_disabled = 0
    option_enabled = 1
    option_dont_lock = 2

    default = option_enabled


class OneupsSanity(Toggle):
    """

    """
    visibility = Visibility.none


class NintyNineCoins(Toggle):
    """

    """
    visibility = Visibility.none


class RedCoinRing(Toggle):
    """

    """
    visibility = Visibility.none


class RouletBlock(Toggle):
    """

    """
    visibility = Visibility.none


class TopOffFlagpole(Toggle):
    """

    """
    visibility = Visibility.none


class KillEnemies(Toggle):
    """

    """
    visibility = Visibility.none


class LogicDifficulty(Choice):
    """
    If hard will make locations that require glitches to be in logic,
    recommended to normal.
    Easy                 : Logic should mostly account for "vanilla" solutions, trivial platforming.
    Normal (Recommended) : Still easy platforming, but some creative solutions will be in logic.
    Hard                 : Logic expects you to do very hard skips
    """
    display_name = "Logic Difficulty"

    option_easy     = 1
    option_normal   = 3
    option_hard     = 5
    #option_extrem = 7
    default = option_normal
    #visibility  = Option.visibility.none

class LogicOutsidePowerups(Toggle):
    """
    If on then solutions involving bringing powerups from outside the level will be considered in logic.
    """
    display_name = "Logic Outside Power-ups"
    default = True

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
    Gaussian    : The unlocking will be a gaussian distribution with mean = 80 SC and standard deviation = 40 SC
    Unlocked    : Not locked
    """
    display_name = "World 9 Unlock Condition"
    option_linear = 2
    option_gaussian = 3
    option_unlocked = 4

    #default = option_gaussian
    default = option_unlocked
    visibility = Visibility.none


class IncludeNumberInventoryItems(Range):
    """
    A location that gets collected when you collect a powerup to your inventory, e.g. from a toad house or beating overworld enemy.
    These locations are very grindy, do not increase above 100, or set to random on your first playthrough.
    Recommend value less than 40
    """
    display_name = "Include Inventory Items"
    range_start = 0
    range_end = 999
    default = 10

class MakeWorldCompPriority(Toggle):
    """
    Makes half world completion and world completion priority locations -> they will have a good item.
    Causes generation failures ~0.5% if enabled.
    """
    display_name = "Make World Completion Priority"
    default = False
    #visibility = Visibility.complex_ui

class BowserCastleStarUnlock(Range):
    """
    Requires at least x star coins to unlock final level or goal.
    Recommended to have bellow ~ 200 to not get fill errors
    """

    display_name = "Bowser Castle Unlock Star"
    range_start = 0
    range_end = 231

    default = 100

class BowserCastleWorldUnlock(Range):
    """
    Requirement of beating at least x of worlds to unlock final level.
    """

    display_name = "Bowser Castle Unlock World"
    range_start = 0
    range_end = 7

    default = 2


class DeathLinkGroup(FreeText):
    """
    Death Link only applies to players with an identical Group name.
    Games that don't support the Group option count as having an empty group name.
    """
    display_name = "Death Link Group"
    rich_text_doc = True
    default = ""

class DeathLinkAmnesty(Range):
    """
    How many deaths it takes to send a deathlink.
    Keep at 1 for every death to send.
    """
    display_name = "Death Link Amnesty"
    range_start = 1
    range_end = 100

    default = 5

class DeathLinkGrace(Range):
    """
    How many deathlinks it takes to receive a death.
    Keep at 1 for every death to be received.
    """
    range_start = 1
    range_end = 25

    default = 1



class AmountSupportReceived(Range):
    """
    Sets the amount of 1ups and powerups send to inventory when receiving their corresponding items.
    If set to -1 it will randomize between 1 and 10 each time you get an item
    """
    display_name = "Amount Support items received from ap-items"
    range_start = -1
    range_end = 100

    default = 5

class FillerItems(OptionCounter):
    """
    elect which filler items and in which ration to be generated.
    """
    display_name = "Filler Items"
    valid_keys = set(FILLER)
    min = 0
    default = dict(Counter(FILLER * 10)) # this is a really ineffective way of doing this, since we create a temp list 10 times the length of FILLER

class TrapItems(OptionCounter):
    """
    Select which trap items and in which ration to be generated.
    """
    display_name = "Trap Items"
    valid_keys = set(TRAPS)
    min = 0
    default = dict(Counter(TRAPS * 10)) # this is a really ineffective way of doing this, since we create a temp list 10 times the length of TRAPS

class PercentageFillerForcedLocal(Range):
    """
    Forces approximately x% of filler to be (early) local items
    """
    display_name = " (in dev, doesnt work) Percentage Filler Forced Local Only"
    range_start = 0
    range_end = 100

    default = 0
    visibility = Visibility.none

class SaveStateSlot(Range):
    """
    Which save state slot the client should use to auto save too
    """
    display_name = "Save Slot"
    range_start = 1
    range_end = 8
    default = 7

class ModifierMultiplierPercentage(Range):
    """
    Modifiers are temporary buffs / debuffs gained from filler / traps.
    The length of all modifiers are multiplied by this percentage.
    Modifiers still clears on death.
    """
    display_name = "Modifier time Multiplier Percentage"
    range_start = 1
    range_end = 1000
    default = 100


class EnemyShuffle(Toggle):
    """

    """
    visibility = Visibility.none


class UseRiivolution(Toggle):
    """
    Creates a riivolution patch when connecting the client to the server.
    If disabled the client will instead rely on memory patching.
    Required to:
     - Use other riivolution based options.
     - Not having the client autoload save states.
     - See custom randomizer graphics (log and starcoin model)

    """
    display_name = "Use Riivolution"
    default = True


class LevelShuffleRiivolution(Toggle):
    """
    Shuffles the level order.
    Requires use_riivolution to be enabled.
    """
    display_name = "Level Shuffle Riivolution"
    default = False


class MusicShuffleRiivolution(Toggle):
    """
    WARNING: Causes caches on some seeds, may need manual removal.
    Shuffles the background music and sound effects.
    Requires use_riivolution to be enabled.
    """
    display_name = "Music Shuffle Riivolution"
    default = False


class BackgroundShuffleRiivolution(Toggle):
    """
    Shuffles the level backgrounds.
    Requires use_riivolution to be enabled.
    """
    visibility = Visibility.none


class PalletShuffleRiivolution(Toggle):
    """

    """
    visibility = Visibility.none


class TileSheetShuffleRiivolution(Toggle):
    """

    """
    visibility = Visibility.none


class ImportantEarlyItems(Toggle):
    """
    Marks some important items as early, resulting in a more fun playthrough.
    """
    default = True


@dataclass
class NSMBWOptions(PerGameCommonOptions):
    level_completion : LevelCompletion
    shortcuts_sanity : ShortcutSanity
    hint_movie_sanity : HintMovieSanity
    starcoin_sanity: StarcoinSanity
    include_inventory_powerups : IncludeNumberInventoryItems
    oneups_sanity : OneupsSanity
    nintynine_coin_sanity : NintyNineCoins
    red_coin_ring : RedCoinRing
    roulet_block : RouletBlock
    kill_enemies : KillEnemies
    top_off_flag_pole : TopOffFlagpole


    randomize_powerups : RandomizePowerups
    randomize_abilites : RandomizeAbilities
    abilites_included : AbilitiesIncluded
    randomize_level_elements : RandomizeLevelElements
    level_elements_included : LevelElementsIncluded
    randomize_enemies : RandomizeEnemies
    enemies_included : EnemiesIncluded
    randomize_time : RandomizeTime
    randomize_boss_health : RandomizeBossHealth

    alternative_goal : AlternativeGoal
    logic_difficulty: LogicDifficulty
    logic_outside_powerup : LogicOutsidePowerups
    starting_world: StartingWorld
    world9_unlock_condition : World9UnlockCondition
    hint_movie_shop_price_logic : HintMovieShopPriceLogic
    starcoin_shop_multiplier : StarCoinShopMultiplier
    make_world_comp_priority : MakeWorldCompPriority
    make_important_early_items : ImportantEarlyItems

    amount_support_received : AmountSupportReceived
    filler_items : FillerItems
    trap_items : TrapItems
    trap_chance: TrapChance
    percentage_filler_forced_local : PercentageFillerForcedLocal


    bowser_star_unlock : BowserCastleStarUnlock
    bowser_world_unlock : BowserCastleWorldUnlock

    death_link : DeathLink
    death_link_group : DeathLinkGroup
    death_link_amnesty : DeathLinkAmnesty
    death_link_grace : DeathLinkGrace
    starcoin_collect_immediately : StarCoinCollectImmediately

    save_state_slot : SaveStateSlot
    modifier_multiplier_percentage : ModifierMultiplierPercentage

    enemy_shuffle : EnemyShuffle
    use_riivolution : UseRiivolution
    level_shuffle_riivolution : LevelShuffleRiivolution
    music_shuffle_riivolution : MusicShuffleRiivolution
    background_shuffle_riivolution : BackgroundShuffleRiivolution
    pallet_shuffle_riivolution : PalletShuffleRiivolution
    tile_sheet_shuffle_riivolution : TileSheetShuffleRiivolution

    # default, needed to add
    start_inventory_from_pool : StartInventoryPool


# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
    OptionGroup(
        "Locations",
        [
            ShortcutSanity,
            LevelCompletion,
            HintMovieSanity,
            StarcoinSanity,
            IncludeNumberInventoryItems,
            MakeWorldCompPriority,
        ],
    ),
    OptionGroup(
        "Items",
        [
            RandomizePowerups,
            RandomizeAbilities,
            AbilitiesIncluded,
            RandomizeLevelElements,
            LevelElementsIncluded,
            RandomizeEnemies,
            EnemiesIncluded,
            RandomizeTime,
            RandomizeBossHealth,
        ],
    ),
    OptionGroup(
        "Clear condition",
        [
            AlternativeGoal,
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
            HintMovieShopPriceLogic,
        ]
    ),
    OptionGroup(
        "Filler and Traps",
        [
            FillerItems,
            TrapItems,
            TrapChance,
            AmountSupportReceived,
            ModifierMultiplierPercentage,
            PercentageFillerForcedLocal,
        ]
    ),
    OptionGroup(
        "Riivolution",
        [
            UseRiivolution,
            LevelShuffleRiivolution,
            MusicShuffleRiivolution,
            BackgroundShuffleRiivolution,
            PalletShuffleRiivolution,
            TileSheetShuffleRiivolution,
        ],
    ),
    OptionGroup(
        "DeathLink",
        [
            DeathLink,
            DeathLinkGroup,
            DeathLinkAmnesty,
            DeathLinkGrace,
        ],
    ),
            OptionGroup(
        "Other",
        [
            StarCoinCollectImmediately,
            SaveStateSlot,
            StarCoinShopMultiplier,
            ImportantEarlyItems,
        ],
    ),
]

option_presets = {}

def adjust_options(world : "NSMBWworld"): # cannot type check because circular imports : NSMBWworld
    if world.options.level_completion.value + world.options.starcoin_sanity.value <= 0 and len(world.multiworld.player_ids) == 1:
        raise OptionError(f"(NSMBW generation error) Turn on at least one of level_completion or starcoin_sanity when generation alone")

    # This section tests if to many location options are turned off and tries to compensate for it.
    req_start_loc = -10
    req_start_loc_max = 10
    if (world.options.hint_movie_sanity.value == False):
        #print(f"(NSMBW generation error) Turning off hint_movie_sanity can cause fill errors with a low amount of num_starting_locations.")
        req_start_loc += 5
    if (world.options.level_completion.value == False):
            #print(f"(NSMBW generation error) Turning off level_completion can cause fill errors with a low amount of num_starting_locations.")
            req_start_loc += 30
            req_start_loc_max += 15
    if (world.options.starcoin_sanity.value == False):
        #print(f"(NSMBW generation error) Turning off randomize coin can cause fill errors with a low amount of num_starting_locations.")
        req_start_loc += 15
    if (world.options.shortcuts_sanity.value == ShortcutSanity.option_disabled):
        #print(f"(NSMBW generation error) Turning off shortcuts_sanity can cause fill errors with a low amount of num_starting_locations.")
        req_start_loc += 5
    if 0 <= req_start_loc:
        print(f"(NSMBW generation error) Low amount of locations detected in nsmbw, this can cause fill errors if generate alone")
        #print(f"(NSMBW generation error) Generation determined that you have to low num_starting_locations, requires at least {req_start_loc} for a stable generation.")
        #world.options.include_starting_locations.value = min(req_start_loc, req_start_loc_max)

    if world.options.include_inventory_powerups.value >= 200:
        print(f"(NSMBW generation error) You have include_inventory_powerups set to {world.options.include_inventory_powerups.value} which is >= 200"
              f"consider lowering this to get a more enjoyable experience.")

    # this tries to prevent num loc > num items
    if ((loc := world.options.shortcuts_sanity.value * 12 + world.options.level_completion.value * 71 +
                world.options.hint_movie_sanity.value * 65 + world.options.include_inventory_powerups.value) #world comp, madatory  + 17
         <= 10+
        (itm :=  world.options.randomize_time.value
         +( world.options.randomize_powerups.value >=1) *len(POWERUP_UNLOCK))):
        raise OptionError(f"(NSMBW generation error) You need to turn on more locations for NSBMW for it to be able to generate"
                          f"you have approximate {loc} locations, {itm} items, margin {itm-loc}")

    if (Utils.get_settings()["nsmbw_settings"].allow_gen_impactful_settings == False) and (len(world.multiworld.player_ids) >= 2):
        if world.options.include_inventory_powerups.value > 100:
            raise OptionError(f"(NSMBW generation error) You have more than 100 inventory powerup locations which is many and is locked by settings,"
                                  f"if you still wish to use this, enable allow_gen_impactful_settings in your host.yaml")
        if world.options.hint_movie_shop_price_logic.value == HintMovieShopPriceLogic.option_ordered:
            raise OptionError("(NSMBW generation error) Option ordered for HintMovieShopPriceLogic can rarely create unbeatable seeds and therefor needs to enable allow_gen_impactful_settings in your host.yaml ")

        if world.options.logic_difficulty == LogicDifficulty.option_hard:
            raise OptionError("(NSMBW generation error) Logic difficulty set to hard without enabling allow_gen_impactful_settings in host.yaml")

    MAX_ALLOWED_BOWSER_SC = 231-7
    if world.options.bowser_star_unlock.value > MAX_ALLOWED_BOWSER_SC:
        world.options.bowser_star_unlock.value = MAX_ALLOWED_BOWSER_SC
        print(f"(NSMBW generation error) Generation fails when star req for reaching bowser is > {MAX_ALLOWED_BOWSER_SC}, amount forcefully lowered")


    if world.options.trap_chance.value != 100:
        if len(list(Counter(world.options.filler_items.value).elements())) == 0:
            print("(NSMBW generation error) You need to have at least one filler item.")
            world.options.filler_items.value = world.options.filler_items.default


    if world.options.trap_chance.value != 0:
        if len(list(Counter(world.options.trap_items.value).elements())) == 0:
            print("(NSMBW generation error) You need to have at least one trap item.")
            world.options.trap_items.value = world.options.trap_items.default

    if world.options.percentage_filler_forced_local.value != 0:
        world.options.percentage_filler_forced_local.value = 0
        print("percentage_filler_forced_local is in dev and doesnt work")

    if world.options.hint_movie_shop_price_logic.value == HintMovieShopPriceLogic.option_progressive:
        print(f"(NSMBW generation error) Option progressive for hint_movie_shop_price_logic is not implemented, setting to default instead.") # raise OptionError
        world.options.hint_movie_shop_price_logic.value = HintMovieShopPriceLogic.default


    if (world.options.level_shuffle_riivolution.value + world.options.music_shuffle_riivolution.value
            > 0 and world.options.use_riivolution.value == False):
        raise OptionError(f"(NSMBW generation error) Cannot use an option that require riivolution patch without it being enabled")

    if world.options.alternative_goal.value == AlternativeGoal.option_hintmovies:
        if not world.options.hint_movie_sanity:
            raise OptionError(f"(NSMBW generation error) hint_movie_sanity needs to be enabled for alternative goal hint_movies")