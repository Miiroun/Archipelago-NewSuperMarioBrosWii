import math

import Utils
from rule_builder import rules
from rule_builder.rules import *
from rule_builder.options import OptionFilter
from .options import *
from .Common import *
from .locations import shuffle_level_order, pos_to_level_name, level_name_to_pos
from .raw_rules import *
from . import raw_rules


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import NSMBWworld

if Utils.__version__ == "0.6.7":
    class AtLeast(NestedRule[TWorld], game="Archipelago"):
        """A rule that returns true when at least N child rules evaluate as true"""

        count: int | FieldResolver

        def __init__(
            self,
            count: int | FieldResolver,
            *children: Rule[TWorld],
            options: Iterable[OptionFilter] = (),
            filtered_resolution: bool = False,
        ) -> None:
            super().__init__(*children, options=options, filtered_resolution=filtered_resolution)
            self.count = count

        @override
        def _instantiate(self, world: TWorld) -> Rule.Resolved:
            count = resolve_field(self.count, world, int)
            if count == 0:
                return True_().resolve(world)

            children_to_process = [c.resolve(world) for c in self.children]
            return AtLeast.from_resolved(count, world, children_to_process)

        @classmethod
        def from_resolved(cls, count: int, world: TWorld, children_to_process: list[Rule.Resolved]) -> Rule.Resolved:
            clauses: list[Rule.Resolved] = []

            while children_to_process:
                child = children_to_process.pop(0)
                if child.always_true:
                    if count == 1:
                        return child
                    count -= 1
                    continue
                if child.always_false:
                    # falses can be ignored
                    continue

                clauses.append(child)

            if len(clauses) < count:
                return False_().resolve(world)
            if count == 1:
                # Switch to Or which has more optimized handling
                return Or.from_resolved(world, clauses)
            if count == len(clauses):
                # Switch to And which has more optimized handling
                return And.from_resolved(world, clauses)
            return AtLeast.Resolved(
                tuple(clauses),
                count=count,
                player=world.player,
                caching_enabled=getattr(world, "rule_caching_enabled", False),
            )

        @override
        def to_dict(self) -> dict[str, Any]:
            output = super().to_dict()
            count = self.count
            output["count"] = count.to_dict() if isinstance(count, FieldResolver) else count
            return output

        @override
        @classmethod
        def from_dict(cls, data: Mapping[str, Any], world_cls: "type[World]") -> Self:
            args = cls._parse_field_resolvers(data, world_cls.game)
            options = OptionFilter.multiple_from_dict(data.get("options", ()))
            children = [world_cls.rule_from_dict(c) for c in data.get("children", ())]
            return cls(
                args.pop("count"),
                *children,
                options=options,
                filtered_resolution=data.get("filtered_resolution", False),
            )

        class Resolved(NestedRule.Resolved):
            count: int

            @override
            def _evaluate(self, state: CollectionState) -> bool:
                count = self.count
                for rule in self.children:
                    if rule(state):
                        if count == 1:
                            return True
                        count -= 1
                return False

            @override
            def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
                messages: list[JSONMessagePart] = []
                if state is None:
                    messages = [
                        {"type": "text", "text": "At least "},
                        {"type": "color", "color": "cyan", "text": str(self.count)},
                        {"type": "text", "text": " of ("},
                    ]
                else:
                    satisfied_count = sum(1 if child(state) else 0 for child in self.children)
                    messages = [
                        {"type": "text", "text": "At least "},
                        {"type": "color", "color": "cyan", "text": f"{satisfied_count}/{self.count}"},
                        {"type": "text", "text": " of ("},
                    ]
                for i, child in enumerate(self.children):
                    if i > 0:
                        messages.append({"type": "text", "text": ", "})
                    messages.extend(child.explain_json(state))
                messages.append({"type": "text", "text": ")"})
                return messages

            @override
            def explain_str(self, state: CollectionState | None = None) -> str:
                clauses = ", ".join([c.explain_str(state) for c in self.children])
                if state is None:
                    return f"At least {self.count} of ({clauses})"
                satisfied_count = sum(1 if child(state) else 0 for child in self.children)
                return f"At least {satisfied_count}/{self.count} of ({clauses})"

            @override
            def __str__(self) -> str:
                clauses = ", ".join([str(c) for c in self.children])
                return f"At least {self.count} of ({clauses})"




def set_all_rules(world: "NSMBWworld") -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)
    assert world.get_region(name_base(world.options.starting_world.value, 1)).can_reach(world.multiworld.state), f"unable to reach first level in your starting world {world.options.starting_world.value}"


def set_level_entrance_rules(world: "NSMBWworld") -> None:

    connections = get_level_connections()

    for world_num, level_num in LEVELS:
        randod_world_num1, randod_level_num1 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world_num, level_num)])
        world.set_rule(world.get_entrance(f"{name_base(world_num,level_num)} internal level connection"),LevelRules[name_base(randod_world_num1, randod_level_num1)][0])

    for world_num in range(1,9+1):
        for i, org_lev_num in enumerate(connections[world_num-1]):
            for con_lev_num in org_lev_num:
                assert type(con_lev_num) == int, "should be an integer"
                randod_world_num, randod_level_num = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world_num,con_lev_num)])

                _rule = True_()
                if mod_level_name(world_num,i) == "T":
                    _rule &= rules.Has(name_world_unlock(world_num), count=2)

                if world_num == 9:
                    assert len(world.star_coin_req_per_world_9_level) == 8
                    _rule &= rules.Has(ITEM.StarCoin, count=world.star_coin_req_per_world_9_level[con_lev_num - 1])

                if world_num == 8 and con_lev_num == 9:
                    # want to change to CanReachRegion, but unshure how to put in a count for it
                    bowser_world_clear_list = list([name_base(world_num, level_num) for world_num, level_num in[(1, 8), (2, 8), (3, 8), (4, 9), (5, 8), (6, 9), (7, 9)]])
                    bowser_clear_rule = Has(ITEM.StarCoin,count=world.options.bowser_star_unlock.value) & HasFromListUnique(*bowser_world_clear_list, count=world.options.bowser_world_unlock.value)
                    _rule &= bowser_clear_rule
                if i== 0:
                    world.set_rule(world.get_entrance(f"World{world_num}->{name_base(world_num, con_lev_num)}"),_rule)
                else:
                    world.set_rule(world.get_entrance(f"{name_base(world_num, i)}->{name_base(world_num, con_lev_num)}"),_rule )
    for secret_exit in SECRET_EXIT:
        if secret_exit.is_item:
            _rule = LevelRules[name_base(secret_exit.world, secret_exit.level)][0]
            if secret_exit.world == 3 and secret_exit.level == 4:
                _rule = True_() # need to override this since otherwise we get error
            _rule &= rules.Has(name_secret(secret_exit))
            if secret_exit.exit_type == 2:
                #assert len(LevelRules[name_base(secret_exit.world, secret_exit.level)]) == 3, f"Make sure lists is of correct size for {name_base(secret_exit.world, secret_exit.level)}"
                _rule &= LevelRules[name_base(secret_exit.world, secret_exit.level)][2]

            #_rule = True_() # temp
            world.set_rule(world.get_entrance(name_secret(secret_exit)),_rule)



def set_all_entrance_rules(world: "NSMBWworld") -> None:
    #rules are set when connecting regions
    is_ut = getattr(world.multiworld, "generation_is_fake", False)
    if not is_ut:
        shuffle_level_order(world)

        if world.options.level_shuffel_riivolution.value == True:
            i = 0

            _rule = False_().resolve(world)

            unbeatable = True
            while unbeatable:
                status = shuffle_level_order(world)

                # this makes sure the first 2 levels are beatable
                randod_world_num1, randod_level_num1 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world.options.starting_world.value, 1)])
                randod_world_num2, randod_level_num2 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world.options.starting_world.value, 2)])
                #_rule = (level_rules[randod_world_num1 - 1][randod_level_num1 - 1][0] & level_rules[randod_world_num2 - 1][randod_level_num2 - 1][0]).resolve(world)
                _rule = (LevelRules[name_base(randod_world_num1, randod_level_num1)][0]).resolve(world)

                unbeatable = not _rule(world.multiworld.state) and status

                i += 1
                if i > 1_000:
                    raise Exception(f"Faild to find a reachable first location in 10_000 tries. Please try again. Or lower requirements for levels by starting with more unlocks.")

    set_level_entrance_rules(world)


def set_all_location_rules(world: "NSMBWworld") -> None:
    #regions = []
    #for i in range(1, 9):
    #    regions.append(world.get_region(f"World_{i}_1"))
    #    if i != 9:
    #        regions.append(world.get_region(f"World_{i}_2"))




    #sets basic rules for each levels star coin
    #
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1]+1):
            for sc in range(1, 3 + 1):
                # makes starcoins in logic if this level is cleared
                star_coin = world.get_location(name_starcoin(world_num, level_num, sc))
                sc_logic = LevelRules[name_base(world_num, level_num)][1][sc - 1]
                world.set_rule(star_coin, sc_logic )

    hm_req = specific_hintmovie_requierments()
    total_cost = 0
    if world.options.hint_movie_sanity:
        for hm_num in range(1,HINTMOVIE_COUNT+1):
            if hm_num in DEPRIO_HM:
                continue
            location = world.get_location(name_hintmovie(hm_num))
            #oftlogic for hm
            total_cost += hm_req[hm_num-1][0] #logic asume you have to get enought starcoins to get them in order
            match world.options.hint_movie_shop_price_logic:
                case HintMovieShopPriceLogic.option_free:
                    soft_logic = True_()
                case HintMovieShopPriceLogic.option_ordered:
                    soft_logic = rules.Has(ITEM.StarCoin, count=math.ceil(total_cost/ world.options.starcoin_shop_multiplier.value))
                case HintMovieShopPriceLogic.option_all:
                    soft_logic = rules.Has(ITEM.StarCoin, count=math.ceil(231 / world.options.starcoin_shop_multiplier.value))
                case _:
                    raise ValueError(f"option {world.options.hint_movie_shop_price_logic} is not acounted for")


            hm_rule = (soft_logic | (GlitchedRule()) & rules.Has(ITEM.StarCoin, count=math.ceil(hm_req[hm_num-1][0] / world.options.starcoin_shop_multiplier.value) ) & hm_req[hm_num-1][2] & rules.Has(name_base(hm_req[hm_num-1][1][0],hm_req[hm_num-1][1][1])))
            world.set_rule(location, hm_rule)

    if world.options.shortcuts_sanity.value == True:
        for secret_exit in SECRET_EXIT:
            world_num = secret_exit.world
            level_num = secret_exit.level
            secret_exit_loc = world.get_location(name_secret(secret_exit))
            if secret_exit.exit_type == 2:
                #assert len( LevelRules[name_base(world_num, level_num)]) == 3, f"Make sure lists is of correct size for {name_base(world_num, level_num)}"
                world.set_rule(secret_exit_loc, rules.Has(name_base(world_num, level_num)) &
                               LevelRules[name_base(world_num, level_num)][2])
            elif secret_exit.exit_type == 1:
                world.set_rule(secret_exit_loc, rules.Has(name_base(world_num, level_num)) )

    for i in range(1, world.options.include_inventory_powerups.value + 1):
        invent_pow = world.get_location(name_inventory(i))
        # hades soft logic thats ored with glitched logic, but also make sure you have climb
        #soft_logic = rules.HasFromList(*worlds_list, count=req_world_com) | Has(ITEM.GlitchedLogic) #& (rules.Has(ITEM.MOVEMENT.Climb)  | [OptionFilter(RandomizeMovement, RandomizeMovement.option_off)])

        # world is assuemed so this is just level
        world_toad      = [2, 1, 6, 4, 1, 7, 1, 0]
        world_star      = [3, 5, 0, 5, 5, 6, 6, 0]
        world_enemy     = [4, 5, 2, 1, 6, 3, 7, 3]

        soft_logic_list : Rule = []
        for world_num in range(1,8+1):
            _rule = Has(name_base(world_num, world_toad[world_num-1], assert_=False)) & raw_rules.climb & raw_rules.door
            for _ in range(4):
                soft_logic_list.append(_rule)

            _rule = Has(name_base(world_num, world_star[world_num-1], assert_=False))
            soft_logic_list.append(_rule)

            _rule =Has(name_base(world_num, world_enemy[world_num-1], assert_=False))
            for _ in range(6):
                soft_logic_list.append(_rule)

        hard_logic : Rule = rules.Or(*soft_logic_list)
        soft_logic : Rule = AtLeast(math.floor((i/ world.options.include_inventory_powerups.value) * 70), *soft_logic_list) | raw_rules.GlitchedRule()
        invent_rule : Rule = hard_logic & soft_logic
        world.set_rule(invent_pow, invent_rule)



def set_completion_condition(world: "NSMBWworld") -> None:
    victory_loc = world.get_location("Victory")
    match world.options.alternative_goal.value:
        case AlternativeGoal.option_bowser:
            reach_bowser_rule = rules.Has(name_base(8, 9))
            world.set_rule(victory_loc, reach_bowser_rule)
        case AlternativeGoal.option_starcoins:
            sc_rule = rules.Has(ITEM.StarCoin, world.options.bowser_star_unlock.value)
            world.set_rule(victory_loc, sc_rule)
        case AlternativeGoal.option_hintmovies:
            sc_rule = True_()
            for hm_num in range(1, HINTMOVIE_COUNT + 1):
                if hm_num in DEPRIO_HM:
                    continue
                sc_rule &= CanReachLocation(name_hintmovie(hm_num))
            world.set_rule(victory_loc, sc_rule)

    world.set_completion_rule(rules.Has("Victory"))
