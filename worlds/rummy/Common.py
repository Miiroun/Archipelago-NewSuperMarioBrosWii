from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from worlds.rummy import RummyWorld

RUMMY_NAME = "AP-Rummy"

RUMMY_REGION = "rummy"

MAX_COLORS = 4
MAX_NUMBERS = 13
card_for_item = 5


class TRAPS(StrEnum):
    SHUFFLE = "Shuffle"
    PROGRESS = "Progress TRAP"

def get_merge_name(num : int) -> str:
    return f"Merge {num : 04}"

class RummyCard(object):
    color : str
    symbol : str

    def __init__(self, color, symbol) -> None:
        assert color in COLORS
        assert symbol in SYMBOLS
        self.color = str(color)
        self.symbol = str(symbol)

    def to_item(self, world):
        return world.create_item(self.get_name())

    def get_name(self) -> str:
        return f"CARD: {self.color}-{self.symbol}"

COLORS = ["RED", "GREEN", "BLUE", "YELLOW"]

SYMBOLS = list([str(i) for i in range(1,MAX_NUMBERS+1)])


def name_color_item(color : str) -> str:
    assert color in COLORS
    return f"Color: {color}"
def name_symbol_item(symbol : str) -> str:
    assert symbol in SYMBOLS
    return f"Symbol: {symbol}"

class MOVES(StrEnum):
    STRAIT = "progressive strait"
    MELD = "progressive meld"

class ITEMS(StrEnum):
    CARDS = "progressive card"

def enum_to_list(enum) -> list:
    return [e.value for e in enum]
