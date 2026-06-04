from math import ceil
from random import Random
from typing import NamedTuple

from .events import Event
from .gameboard import Gameboard
from .graphics import Graphic
from .inputs import DIGIT_INPUTS_TO_DIGITS, Direction, Input
from ..Common import *

class RemotelyReceivedItem(NamedTuple):
    remote_item_id: int
    remote_location_id: int
    remote_location_player: int


class Game:
    gameboard: Gameboard

    random: Random

    queued_events: list[Event]

    auto_target_path: list[tuple[int, int]] = []

    remotely_received_items: set[tuple[int, int, int]]

    has_won : bool = False

    all_cards = list[RummyCard]
    allowed_cards : int


    def __init__(self,card_order,  random_object: Random | None = None) -> None:
        self.queued_events = []
        self.all_cards = list(map(RummyCard.from_string, card_order))
        self.gameboard = Gameboard.create_gameboard(self.all_cards)
        self.remotely_received_items = set()

        self.allowed_cards = 15

        if random_object is None:
            self.random = Random()
        else:
            self.random = random_object

    def render(self) -> tuple[tuple[Graphic, ...], ...]:
        return self.gameboard.render()




    #def attempt_interact(self) -> bool:
    #    delta_x, delta_y = self.player.facing.value
    #    entity_x, entity_y = self.player.current_x + delta_x, self.player.current_y + delta_y

    #    entity = self.gameboard.get_entity_at(entity_x, entity_y)

    #    if isinstance(entity, InteractableMixin):
    #        return entity.interact(self.player)

    #    return False


    @property
    def currently_typed_in_math_result(self) -> int | None:
        if not self.active_math_problem_input:
            return None

        number = self.active_math_problem_input[-1]
        if len(self.active_math_problem_input) == 2:
            number += self.active_math_problem_input[0] * 10

        return number

    def check_math_problem_result(self) -> None:
        if self.active_math_problem is None:
            return

        if self.currently_typed_in_math_result == self.active_math_problem.result:
            self.math_problem_success()

    def math_problem_input(self, input: int) -> None:
        if self.active_math_problem_input is None or len(self.active_math_problem_input) >= 2:
            return

        self.active_math_problem_input.append(input)
        self.check_math_problem_result()



    def input(self, input_key: Input) -> None:
        if not self.gameboard.ready:
            return

        if input_key in DIGIT_INPUTS_TO_DIGITS:
            self.math_problem_input(DIGIT_INPUTS_TO_DIGITS[input_key])
            return
        if input_key == Input.BACKSPACE:
            return

        if input_key == Input.LEFT:
            return

        if input_key == Input.UP:
            return

        if input_key == Input.RIGHT:
            return

        if input_key == Input.DOWN:
            return

        if input_key == Input.ACTION:
            return

        if input_key == Input.CONFETTI:
            return

        raise ValueError(f"Don't know input {input_key}")

    def receive_item(self, remote_item_id: int, remote_location_id: int, remote_location_player: int) -> None:
        remotely_received_item = RemotelyReceivedItem(remote_item_id, remote_location_id, remote_location_player)
        if remotely_received_item in self.remotely_received_items:
            return

        if remote_item_id == 101:
            self.allowed_cards += 5
        print(f"received item {remote_item_id} found at {remote_location_id} from {remote_location_player}")
        self.remotely_received_items.add(remotely_received_item)



    def force_clear_location(self, location_id: int) -> None:
        location = Location(location_id)
        self.gameboard.force_clear_location(location)

    def cancel_auto_move(self) -> None:
        self.auto_target_path = []

    def queue_auto_move(self, target_x: int, target_y: int) -> None:
        self.cancel_auto_move()
        path = self.gameboard.calculate_shortest_path(self.player.current_x, self.player.current_y, target_x, target_y)
        self.auto_target_path = path

    def do_auto_move(self) -> bool:
        if not self.auto_target_path:
            return False

        target_x, target_y = self.auto_target_path.pop(0)
        movement = target_x - self.player.current_x, target_y - self.player.current_y
        direction = Direction(movement)
        moved = self.attempt_player_movement(direction, cancel_auto_move=False)

        if moved:
            return True

        # We are attempting to interact with something on the path.
        # First, make the player face it.
        if self.player.facing != direction:
            self.player.facing = direction
            self.auto_target_path.insert(0, (target_x, target_y))
            return True

        # If we are facing it, attempt to interact with it.
        changed = self.attempt_interact()

        if not changed:
            self.cancel_auto_move()
            return False

        # If the interaction was successful, and this was the end of the path, stop
        # (i.e. don't try to attack the attacked enemy over and over until it's dead)
        if not self.auto_target_path:
            self.cancel_auto_move()
            return True

        # If there is more to go, keep going along the path
        self.auto_target_path.insert(0, (target_x, target_y))
        return True
