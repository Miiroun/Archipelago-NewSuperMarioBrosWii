from __future__ import annotations

import random
from collections.abc import Iterable
from typing import TYPE_CHECKING, List

from worlds.rummy.Common import *


class Gameboard:

    active_cards : List[RummyCard]
    ready : bool

    def __init__(self) -> None:
        self.active_cards = []
        self.ready = True

    @staticmethod
    def create_gameboard(card_order):
        obj = Gameboard()
        obj.active_cards = card_order
        return obj

    def render(self):
        pass