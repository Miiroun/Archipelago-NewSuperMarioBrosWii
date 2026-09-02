from rule_builder.rules import *
from rule_builder.options import OptionFilter
from .options import *
from .Common import *

if TYPE_CHECKING:
    from  .world import NSMBWworld

rule_completed_everything = Has(ITEM.StarCoin, count=231)  & Has("Victory")
# dont want to implement complex, just deprioritize

@dataclasses.dataclass()
class HasSC(Rule["NSMBWworld"], game = game_name):
    amount : int | FieldResolver

    @override
    def _instantiate(self, world: "NSMBWworld") -> Rule.Resolved:
        if world.options.hint_movie_shop_price_logic.value != HintMovieShopPriceLogic.option_free:
            return Has(ITEM.StarCoin, count=resolve_field(self.amount, world, int)).resolve(world)
        else:
            return True_().resolve(world)

def specific_hintmovie_requierments() -> List:
    # info about these harvested from https://gamefaqs.gamespot.com/wii/960544-new-super-mario-bros-wii/faqs/58584

    requierments : list = [
        #starcoin cost, level requierment, generic requierment
        [3, (1,1), True_()],   #01
        [5, (1,1), rule_completed_everything],  # 02 #find every normal goal in world1-9
        [3, (1,2), HasSC(5)],  # 03
        [3, (1,3), rule_completed_everything],  # 04 #find every normal goal in world1-9
        [5, (1,3), Has(name_base(1,8))],  # 05
        [5, (1,8), HasSC(10)],  # 06
        [5, (1,5), HasSC(30)],  # 07
        [0, (2,1), HasSC(15)],  # 08
        [3, (2,1), HasSC(1)],  # 09
        [0, (2,2), HasSC(95)],  # 10
        [3, (2,2), HasSC(150)],  # 11
        [5, (2,3), rule_completed_everything]  ,# 12
        [5, (2,4), HasSC(20)] , # 13 #find every normal adn secret goal in world1-9
        [5, (2,5), Has(name_base(2,8))],  # 14
        [5, (2,5), HasSC(215)],  # 15
        [10, (2,6), HasSC(25)],  # 16
        [0, (3,1), HasSC(65)] , # 17
        [3, (3,1), HasSC(35)] , # 18
        [5, (3,2), HasSC(165)] , # 19
        [5, (3,2), HasSC(190)]  ,# 20
        [0, (3,3), HasSC(140)] , # 21
        [3, (3,3), Has(name_base(3,8))],  # 22
        [5, (3,3), HasSC(195)] , # 23
        [5, (3,6), HasSC(140)],  # 24
        [5, (3,5), HasSC(130)] , # 25
        [3, (4,1), HasSC(45)]  ,# 26
        [5, (4,2), HasSC(175)] , # 27
        [3, (4,2), rule_completed_everything],  # 28 # everything
        [0, (4,3), HasSC(125)],  # 29
        [5, (4,3), Has(name_base(4,8))],  # 30
        [10, (4,7), HasSC(70)],  # 31
        [0, (4,4), HasSC(50)],  # 32
        [5, (4,6), HasSC(69)],  # 33
        [3, (4,8), HasSC(145)],  # 34
        [5, (5,1), HasSC(105)],  # 35
        [3, (5,3), HasSC(55)],  # 36
        [0, (5,6), HasSC(75)],  # 37
        [5, (5,6), Has(name_base(8,8))],  # 38
        [3, (5,8), Has(name_base(5,8))],  # 39
        [3, (6,1), HasSC(80)],  # 40
        [0, (6,2), HasSC(135)],  # 41
        [0, (6,3), HasSC(85)] , # 42
        [5, (6,3), HasSC(205)],  # 43
        [5, (6,5), HasSC(90)] , # 44
        [10, (6,6), HasSC(100)] , # 45
        [5, (6,8), Has(name_base(9,6))],  # 46
        [5, (7,1), Has(name_base(9,7))],  # 47
        [0, (7,3), HasSC(170)],  # 48
        [0, (7,8), HasSC(160)],  # 49
        [3, (7,7), HasSC(120)],  # 50
        [3, (7,4), HasSC(231)],  # 51
        [0, (7,9), HasSC(115)],  # 52
        [3, (8,2), Has(name_base(8,8))],  # 53 #beat world 8 castle
        [5, (8,3), HasSC(180)],  # 54
        [0, (8,8), HasSC(110)],  # 55
        [5, (8,10), HasSC(155)],  # 56
        [5, (8,9), rule_completed_everything],  # 57 #all secret goals
        [5, (9,1), HasSC(225)],  # 58
        [5, (9,2), HasSC(220)],  # 59
        [5, (9,3), HasSC(185)],  # 60
        [5, (9,3), HasSC(210)],  # 61
        [0, (9,4), rule_completed_everything],  # 62 #all normal goals
        [5, (9,5), HasSC(230)],  # 63
        [0, (9,6), HasSC(200)],  # 64
        [3, (9,7), rule_completed_everything]  # 65 # complete everything!!!!!!!!!!!!!!!!1
    ]
    return requierments

def get_time_rule(world : "NSMBWworld", time : int) -> Rule[TWorld]:
    _amount_items_needed = get_time_math(world,time)
    _rule = Has(ITEM.Time, count=_amount_items_needed)
    if _amount_items_needed <= 1: # should precompute so doesnt show
        _rule = True_()

    return _rule

@dataclasses.dataclass()
class TimeRule(Rule["NSMBWworld"], game = game_name):
    """custom rule"""

    time : int | FieldResolver

    @override
    def _instantiate(self, world: "NSMBWworld") -> Rule.Resolved:
        # caching_enabled only needs to be passed in when your world inherits from CachedRuleBuilderWorld
        return get_time_rule(world, resolve_field(self.time, world, int)).resolve(world)


@dataclasses.dataclass()
class GlitchedRule(Rule["NSMBWworld"], game = game_name):

    @override
    def _instantiate(self, world: "NSMBWworld") -> Rule.Resolved:
        if getattr(world.multiworld, "generation_is_fake", False):
            return Has(ITEM.GlitchedLogic).resolve(world)
        else:
            return False_().resolve(world)




filter_pow_on = OptionFilter(RandomizePowerups, RandomizePowerups.option_on)
filter_pow_on_prog = OptionFilter(RandomizePowerups, RandomizePowerups.option_on_progressive)
filter_pow_on_no_mus = OptionFilter(RandomizePowerups, RandomizePowerups.option_on_except_mushroom)
filter_pow_off = OptionFilter(RandomizePowerups, RandomizePowerups.option_off)
filter_pow = [filter_pow_off] #[filter_pow_on,filter_pow_on_prog,filter_pow_on_no_mus]


def has_ability(name : str):
    assert name in ABILITIES
    return Has(name) | OptionFilter(RandomizeAbilities,     False)  | False_(filtered_resolution=True, options=[OptionFilter(AbilitiesIncluded,    name, operator="contains")])

def has_element(name : str):
    assert name in LEVEL_ELEMENTS
    return Has(name) | OptionFilter(RandomizeLevelElements, False)  | False_(filtered_resolution=True, options=[OptionFilter(LevelElementsIncluded,    name, operator="contains")])



# create rules that are true if their option filters are off or if have its item
button_right = has_ability(ITEM.ABILITIES.ButtonRight)
button_left = has_ability(ITEM.ABILITIES.ButtonLeft)
button_up = has_ability(ITEM.ABILITIES.ButtonUp)
button_down = has_ability(ITEM.ABILITIES.ButtonDown)
jump = has_ability(ITEM.ABILITIES.Jump)
run = has_ability(ITEM.ABILITIES.Run)

ground_pound = has_ability(ITEM.ABILITIES.GroundPound) & button_down
wall_jump = has_ability(ITEM.ABILITIES.WallJump) & jump
carry = has_ability(ITEM.ABILITIES.Carry)
climb = has_ability(ITEM.ABILITIES.Climb)
spin_jump = has_ability(ITEM.ABILITIES.SpinJump)
swim = has_ability(ITEM.ABILITIES.Swim)
crouch = has_ability(ITEM.ABILITIES.Crouch) & button_down

question_switch = has_element(ITEM.LEVELELEMENTS.QuestSwitch)
p_switch = has_element(ITEM.LEVELELEMENTS.PSwitch)
red_block = has_element(ITEM.LEVELELEMENTS.RedSwitch) & Has(name_base(3,5))

yoshi = has_ability(ITEM.ABILITIES.Yoshi)
star = has_ability(ITEM.ABILITIES.Star)

door = has_element(ITEM.LEVELELEMENTS.Door) & button_up
pipe = has_element(ITEM.LEVELELEMENTS.Pipe)



# powerups
mushroom = Has(ITEM.POWERUP.Super_Mushroom) | filter_pow | filter_pow_on_no_mus
progressive_pow_filler = mushroom | [filter_pow_on, filter_pow_on_no_mus]

propeller = (Has(ITEM.POWERUP.Propeller_Mushroom) & progressive_pow_filler & spin_jump) | filter_pow
ice = (Has(ITEM.POWERUP.Ice_Flower) & progressive_pow_filler) | filter_pow
peng = (Has(ITEM.POWERUP.Penguin_Suit) & progressive_pow_filler) | filter_pow
mini = (Has(ITEM.POWERUP.Mini_Mushroom) & progressive_pow_filler) | filter_pow
fire = (Has(ITEM.POWERUP.Fire_Flower) & progressive_pow_filler) | filter_pow

# detailed moves
carry_shell = carry
carry_block = carry & spin_jump
carry &= carry & spin_jump # this is temp, only until we changed all carry to either carry_shell or carry_block


#other rules
outside_powerups = [OptionFilter(LogicOutsidePowerups, True)] | GlitchedRule() # and with this rule
# these can be somewhat used in the wrong category if makes rules more clean / easier to read, and with these rules
logic_hard   = [OptionFilter(LogicDifficulty, LogicDifficulty.option_hard)] | GlitchedRule()
logic_normal = [OptionFilter(LogicDifficulty, LogicDifficulty.option_normal)] | logic_hard # this one probably cann't be used, but I will leave it in just in case, maybe useful if OR
#logic_easy   = [OptionFilter(LogicDifficulty, LogicDifficulty.option_easy)] | logic_normal

# more powerup stuff
ice_peng = ice | peng
fire_o = fire & outside_powerups
ice_o = ice & outside_powerups
propeller_o = propeller & outside_powerups
peng_o = peng & outside_powerups
ice_peng_o = ice_peng & outside_powerups
mini_o = mini & outside_powerups
star_o = star & outside_powerups

# Complex rules ( made of previous)
super_mario = mushroom | propeller | ice_peng | fire
max_mini = mini & run & wall_jump
oswj = run & wall_jump & (fire | ice_peng | mini)
normal_move = button_right & (jump | spin_jump) & TimeRule(100)
# button_left & button_up & button_down & jump & spin_jump & p_switch & door & pipe & TimeRule(50) #changed this to fit my current logic, can probably be cleaned up a bit

tower_rules = door & button_left


class Level(NamedTuple):
    clear : Rule
    starcoins : Tuple[Rule, Rule, Rule]
    secret_exit : Optional[Rule]  = None
    oneups : Optional[Rule]  = None
    nintynine_coins : Optional[Rule]  = None
    amount_coins : int = 99
    red_coin_ring : Optional[Rule] = None
    roulette : Optional[Rule] = None


LevelRules : Dict[str, Level]= { # normal compleation rules
    #world 1
    "1-1"  : Level(normal_move & TimeRule(90), (propeller | (mini_o & (run | logic_hard)) | (run & (carry_shell | star_o | ice_peng_o) & logic_hard), wall_jump | propeller, propeller | (logic_hard & (run | mini_o | ice_peng_o)))),  # -1
    "1-2"  : Level(normal_move & pipe & button_down , (button_up, p_switch | propeller_o, super_mario & ground_pound) ),  # -2
    "1-3"  : Level(normal_move, (yoshi | propeller_o | (logic_hard & ((mini_o & (ground_pound | run)) | (run & (super_mario | ground_pound)) | carry_block)),pipe & button_down &  (yoshi | propeller_o | (logic_hard & run & (ground_pound | super_mario))), yoshi | propeller_o | wall_jump | (logic_hard & ((mini_o & ground_pound) | carry_shell))), (yoshi | propeller_o | (logic_hard & ((oswj & outside_powerups) | (carry_shell & (super_mario | run)))) ) & pipe),  # -3
    "1-4"  : Level(pipe & button_down & button_up & normal_move & swim, (True_(), ice | peng_o | propeller_o | mini_o | logic_hard, ice | peng_o | logic_hard)),  # -4
    "1-5"  : Level(pipe & button_down & button_up & normal_move & spin_jump, (climb, True_(), True_())),  # -5
    "1-6"  : Level(pipe & button_down & button_up & normal_move, (True_(), True_(), run | (mini_o | (star_o & logic_hard)) | (propeller & (climb | outside_powerups)))),  # -6
    "1-T"  : Level(pipe & button_down & button_up & normal_move &tower_rules, (True_(), wall_jump | propeller_o, True_())),  # -7 1-T
    "1-C"  : Level(pipe & button_down & button_up & normal_move & door & TimeRule(200), (True_(), True_(), propeller_o | (wall_jump & p_switch))),  # -8 1-C

    # World 2
    "2-1"  : Level(normal_move & jump, (True_(), True_(), carry | propeller_o | mini_o)),  # -1
    "2-2"  : Level(normal_move & pipe & button_down & button_up & jump, (p_switch | (ground_pound & super_mario), climb & (carry | propeller_o | logic_hard), mini & wall_jump & (carry | ground_pound))),  # -2
    "2-3"  : Level(normal_move & pipe& button_down & button_up, (True_(), True_(), (run | propeller_o | mini_o | (star & logic_hard)) )),  # -3
    "2-4"  : Level(normal_move  & pipe & button_down & button_up& (climb | (propeller_o | (mini_o & wall_jump)) | (logic_hard & wall_jump & run & super_mario))  , (climb , propeller , (propeller | (mini_o & wall_jump)) ), propeller & (wall_jump | run) ),  # -4 # this was orignaly propeller_o for sc2, sc3 and secret exit, but locations must be accessible independent of setting, so changed it to just propeller_o
    "2-5"  : Level(pipe & button_down & button_up & normal_move, (True_(), yoshi | carry | propeller_o | (wall_jump & (mini_o | run | super_mario)) | (logic_hard & ice_peng_o), True_())),  # -5
    "2-6"  : Level(pipe & button_down & button_up & normal_move, (True_(), carry | propeller | mini_o, True_()), propeller | (mini_o & logic_hard)),  # -6
    "2-T"  : Level(pipe & button_down & button_up & normal_move & tower_rules, (True_(), True_(), True_())),  # -7 2-T
    "2-C"  : Level(pipe & button_down & button_up & normal_move & door & ((p_switch) | ((ice | peng_o) & carry) | (peng_o & crouch)), (True_(), (super_mario & wall_jump) | propeller_o, p_switch | ((ice | peng_o) & carry))),  # -8 2-C

      # world 3
    "3-1"  : Level(normal_move & pipe, ((peng & crouch) | logic_hard, True_(), (peng & crouch) | (carry & logic_hard))),  # -1
    "3-2"  : Level(normal_move, (True_(), normal_move | wall_jump | yoshi | propeller_o, True_())),  # -2
    "3-3"  : Level(normal_move & button_down & button_up, ((swim | mini_o | ((propeller_o | (peng & crouch)) & logic_hard) ) , True_(), (carry | propeller_o | (wall_jump & logic_hard)) )),  # -3
    "3-4"  : Level(pipe & button_down & button_up & normal_move & red_block, (True_(), True_(), True_()),normal_move & pipe),  # -4
    "3-5"  : Level(pipe & button_down & button_up & normal_move, (True_(), red_block, red_block), red_block),  # -5
    "3-G"  : Level(pipe & button_down & button_up & normal_move & door & (climb | (propeller_o & wall_jump) | (oswj & logic_hard & outside_powerups)), (True_(), True_(), True_()),True_()),  #-6    # 3-Ghosthouse
    "3-T"  : Level(pipe & button_down & button_up & normal_move&tower_rules, (True_(), carry_block, wall_jump | propeller_o)),  # -7 3-T
    "3-C"  : Level(pipe & button_down & button_up & normal_move & door, (True_(), True_(), True_())),  # -8 3-C

    # world 4
    "4-1"  : Level(normal_move & swim & pipe& button_down & button_up, (ice_o | peng | propeller_o | (mini_o & (run | logic_hard)) | carry, ice_o | peng | propeller_o | mini_o | (logic_hard & wall_jump & run & ground_pound), peng | ice_o | mini_o | propeller_o | logic_hard)),  # -1
    "4-2"  : Level(pipe & button_down & button_up & normal_move, (True_(), True_(), True_())),  # -2
    "4-3"  : Level(pipe & button_down & button_up & normal_move, (True_(), mini | propeller_o | (peng & crouch & (run | logic_hard)) | (swim & (super_mario | run | (star & logic_hard))), swim & mini)),  # -3
    "4-4"  : Level(pipe & button_down & button_up & normal_move & swim, ((peng | ice_o | propeller_o | mini_o) & p_switch, True_(), True_())),  # -4
    "4-5"  : Level(pipe & button_down & button_up & normal_move, (True_(), True_(), True_())),  # -5
    "4-G"  : Level(pipe & button_down & button_up & normal_move & door & (p_switch | (peng_o & crouch) | (ice_peng_o & carry_block)), (True_(), True_(), True_()), True_()),  # -6 4-G
    "4-T"  : Level(normal_move & tower_rules, (True_(), True_(), True_()), True_()),  # -7 4-T
    "4-C"  : Level(pipe & button_down & button_up & normal_move & swim, (True_(), True_(), True_())),  # -8 4-C
    "4-A"  : Level(pipe & button_down & button_up & normal_move & spin_jump &(carry | propeller_o | (logic_hard & wall_jump & (super_mario | (mini_o & ground_pound)))) & door, (True_(), (carry & ground_pound) | (logic_hard & wall_jump & (ground_pound | (carry & (ice | peng_o)) | (peng_o & crouch))), True_())),  # -9 4-A
# world 5
    "5-1"  : Level(normal_move & (climb | propeller_o) & pipe, (super_mario & ground_pound, swim | mini_o, ((swim | mini_o) & climb) | propeller_o | (logic_hard & climb & run & (carry | ground_pound)))),  # -1
    "5-2"  : Level(pipe & button_down & button_up & normal_move, (True_(), button_left | (crouch & logic_hard), (carry_block & spin_jump) | propeller_o | (max_mini & logic_hard & outside_powerups))),  # -2
    "5-3"  : Level(pipe & button_down & button_up & normal_move, (True_(), carry |((peng_o & crouch) & logic_hard), True_())),  # -3
    "5-4"  : Level(pipe & button_down & button_up & normal_move, (logic_hard | super_mario | run, logic_hard | carry | propeller_o, carry)),  # -4
    "5-5"  : Level(pipe & button_down & button_up & normal_move, (True_(), True_(), carry)),  # -5
    "5-G"  : Level(normal_move & door & ((question_switch & carry_block) | logic_hard), (True_(), True_(), True_() ), True_() ),  # -6 5-Ghosthouse
    "5-T"  : Level(pipe & button_down & button_up & normal_move& tower_rules & (carry | wall_jump | propeller_o), (True_(), True_(), super_mario)),  # -7 5-T
    "5-C"  : Level(pipe & button_down & button_up & normal_move & door & TimeRule(150), (wall_jump | propeller | (logic_hard & carry & (ice | peng_o)), True_(), True_())),  # -8 5-C
# world 6
    "6-1"  : Level(normal_move, (True_(), True_(), logic_hard | ice | peng_o | propeller_o)),  # -1
    "6-2"  : Level(normal_move & pipe& button_down & button_up & (swim | run | logic_normal), (carry_shell | (peng_o & crouch), logic_hard | ice | peng_o | propeller_o, True_())),  # -2
    "6-3"  : Level(normal_move & pipe & button_down & button_up & ((swim & question_switch) | (wall_jump & (propeller_o | (logic_hard & ice_peng_o & run)))),(True_(), True_(), (wall_jump & fire) | propeller_o | (logic_hard & ice_peng_o & run & carry))), # 6-3
    "6-4"  : Level(pipe & button_down & button_up & normal_move, ((carry | yoshi | propeller), (yoshi | propeller | ((max_mini | (oswj & logic_hard)) & outside_powerups)), (yoshi | propeller | wall_jump))),  # -4
    "6-5"  : Level(pipe & button_down & button_up & normal_move, (True_(), True_(), climb & (carry | propeller_o)), climb),  # -5
    "6-6"  : Level(pipe & button_down & button_up & normal_move & (question_switch | logic_hard), (True_(), True_(), True_()),True_()),  # -6
    "6-T"  : Level(pipe & button_down & button_up & normal_move&tower_rules, (True_(), wall_jump | propeller_o, wall_jump | propeller_o)),  # -7 6-T
    "6-C"  : Level(pipe & button_down & button_up & normal_move& door, (True_(), True_(), True_())),  # -8 6-C
    "6-A"  : Level(pipe & button_down & button_up & normal_move & spin_jump, (ground_pound  | (logic_hard & ((peng_o & crouch & wall_jump) | (carry & (ice | peng_o)))), ground_pound , ground_pound  | (logic_hard & peng_o & crouch))),  # -9 6-A
# world 7
    "7-1"  : Level(normal_move & pipe& button_down & button_up, (wall_jump | propeller_o, True_(), True_())),  # -1
    "7-2"  : Level(pipe & button_down & button_up & normal_move & (swim | (propeller_o & logic_normal)), (ground_pound | (logic_hard & swim & (ice_peng_o & carry) | (peng_o & crouch)), swim, True_())),  # -2
    "7-3"  : Level(pipe & button_down & button_up & normal_move, (True_(), climb & p_switch | (climb & propeller_o), True_()) ),  # -3
    "7-4"  : Level(pipe & button_down & button_up & normal_move, (True_(), True_(), True_())),  # -4
    "7-5"  : Level(pipe & button_down & button_up & normal_move & spin_jump, (True_(), propeller | p_switch, True_())),  # -5
    "7-6"  : Level(pipe & button_down & button_up & normal_move, (True_(), True_(), True_()), True_()),  # -6
    "7-G"  : Level(pipe & button_down & button_up & normal_move & door & question_switch, (True_(),  True_(), (climb | propeller_o | (mini_o & (carry | (wall_jump & logic_hard))))), (climb | propeller_o | (mini_o & (carry | (wall_jump & logic_hard))))),  #  7-Ghosthouse
    "7-T"  : Level(pipe & button_down & button_up & normal_move&tower_rules& door, (True_(), True_(), True_()), True_()),  # -8 7-T
    "7-C"  : Level(pipe & button_down & button_up & normal_move & door & (run | (super_mario & logic_hard)), (super_mario, True_(), wall_jump | propeller_o)),  # 7-C
# world 8
    "8-1"  : Level(normal_move & jump & run & pipe & button_up & (button_left | logic_hard) & TimeRule(150), (True_(), carry_block, True_())),  # -1
    "8-2"  : Level(normal_move & button_left & pipe & button_down & TimeRule(100), (True_(), True_(), True_()), button_left),  # -2
    "8-3"  : Level(pipe & button_down & button_up & normal_move & (run | crouch) & TimeRule(100), (True_(), True_(), True_())),  # -3
    "8-4"  : Level(pipe & button_down & button_up & normal_move & swim & question_switch & TimeRule(150), (True_(),True_(),True_())),  # -4
    "8-5"  : Level(pipe & button_down & button_up & normal_move, (True_(), carry, True_())),  # -5
    "8-6"  : Level(pipe & button_down & button_up & normal_move & climb & jump & button_up & pipe, (True_(), climb & (propeller | wall_jump), True_())),  # -6
    "8-7"  : Level(pipe & button_down & button_up & normal_move & TimeRule(200), (True_(), True_(), True_())),  # -7
    "8-T"  : Level(pipe & button_down & button_up & normal_move&tower_rules & TimeRule(200), (True_(), True_(), True_())),  # -8 8-T
    "8-C"  : Level(normal_move & door & button_down & pipe & ((propeller & crouch) | logic_hard), (True_(), True_(), True_())),  # -9 8-C
    "8-A"  : Level(pipe & button_down & normal_move & ground_pound & spin_jump , (True_(), True_(), propeller | (ground_pound & ((mini_o & (wall_jump | run)) | (logic_hard & run & carry))))),  # -10 8-A
# world 9
    "9-1"  : Level(pipe & button_down & button_up & normal_move, (logic_normal | propeller | mini_o, True_(), True_())),  # -1
    "9-2"  : Level(pipe & button_down & button_up & normal_move & (mini_o | (run & climb) | swim | (peng_o & crouch & run)) & (run | logic_hard), (True_(), swim, (carry & ((mini_o & ground_pound) | (run & climb) | swim)) | (peng_o & crouch & run))),  # -2
    "9-3"  : Level(pipe  & normal_move & (run | logic_normal), (p_switch & button_down & button_up, (run | (propeller_o & logic_hard)) & p_switch & button_up, logic_hard | run | propeller_o | mini_o)),  # -3
    "9-4"  : Level(pipe & button_down & button_up & normal_move & (run | propeller_o | mini_o | ice | peng_o), (wall_jump | propeller_o, carry | propeller_o, ice | peng_o)),  # -4
    "9-5"  : Level(pipe & button_down & button_up & normal_move & (question_switch | wall_jump | propeller_o | logic_hard), (True_(), True_(), (ice_o | peng | propeller_o))),  # -5
    "9-6"  : Level(pipe & button_down & button_up & normal_move & (run | propeller_o | mini_o), (True_(), logic_hard | propeller_o | ((run | mini_o) & wall_jump), True_())),  # -6
    "9-7"  : Level(pipe & button_down & button_up & normal_move & (run | ((mini_o | wall_jump | propeller_o) & logic_hard)), (True_(), True_(), ((run | logic_hard) & (wall_jump | propeller_o)))),  # -7
    "9-8"  : Level(pipe & button_down & button_up & normal_move, (carry | propeller | mini, True_(), True_())),  # -8
# world Coin
    "C-1" : Level(normal_move & pipe, (True_(),True_(), logic_hard | carry_shell | carry_block)),
    "C-2": Level(normal_move, (True_(), True_(), True_())),
    "C-3": Level(normal_move & door, (True_(), True_(), True_())),
    "C-4": Level(normal_move, (True_(), True_(), True_())),
    "C-5": Level(normal_move & pipe, (super_mario & ground_pound, True_(), True_())),
}


def get_level_connections() -> List[List[List[int]]]:
    connections = []
    connections += [
        [ # world 1
            [1],
            [2], #-1
            [3],#-2
            [7],#-3
            [5,6],#-4
            [8],#-5
            [8],#-6
            [4],# -Tower
            [] # -Caslte
        ],
        [  # world 2
            [1,2],
            [3],  # -1
            [3],  # -2
            [7],  # -3
            [5,6,8],  # -4
            [],  # -5
            [],  # -6
            [4],  # -Tower
            []  # -Caslte
        ],
        [  # world 3
            [1],
            [2],  # -1
            [3,6,7],  # -2
            [],  # -3
            [8],  # -4
            [],  # -5
            [],  # -6
            [4],  # -Tower
            []  # -Caslte
        ],
        [  # world 4
            [1],
            [2,3],  # -1
            [7],  # -2
            [7],  # -3
            [5],  # -4
            [6],  # -5
            [8],  # -6
            [4],  # -Tower
            [9],  # -Caslte
            [] #airship
        ],
        [  # world 5
            [1],
            [2,3],  # -1
            [7],  # -2
            [7],  # -3
            [5,6,8],  # -4
            [],  # -5
            [],  # -6
            [4],  # -Tower
            []  # -Caslte
        ],
        [  # world 6
            [1],
            [2,3],  # -1
            [4],  # -2
            [7],  # -3
            [7],  # -4
            [6],  # -5
            [8],  # -6
            [5],  # -Tower
            [9],  # -Caslte
            [] # - airship
        ],
        [  # world 7
            [1],
            [2],  # -1
            [3],  # -2
            [8],  # -3
            [5],  # -4
            [9],  # -5
            [9],  # -6
            [4], # - 7 # ghosthouse
            [7],  # -Tower
            []  # -Caslte
        ],
        [  # world 8
            [1],
            [2],  # -1
            [3],  # -2
            [8],  # -3
            [5],  # -4
            [6],  # -5
            [10],  # -6
            [], # -7
            [4],  # -Tower
            [],  # -Caslte
            [9] #- airship
        ],
        [  # world 9
            [1,2,3,4,5,6,7,8],
            [],  # -1
            [],  # -2
            [],  # -3
            [],  # -4
            [],  # -5
            [],  # -6
            [],  # -7
            []  # -8
        ]

    ]


    return connections
