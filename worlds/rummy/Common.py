from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from worlds.rummy import RummyWorld

RUMMY_NAME = "AP-Rummy"

RUMMY_REGION = "rummy"

MAX_COLORS = 4
MAX_NUMBERS = 13
CARD_PER_ITEM = 2
COPYS_OF_CARDS = 5
NUMBER_STARTING_CARDS = 16 // CARD_PER_ITEM
REQUIRED_CARDS_TO_START = 9
GLITCH_LOGIC_ITEM = "glitched_logic"
EXTRA_CARDS = 6 // CARD_PER_ITEM


class TRAPS(StrEnum):
    SHUFFLE = "Shuffle"
    PROGRESS = "Unmerge"

class MOVES(StrEnum):
    STRAIT = "progressive strait"
    MELD = "progressive meld"

class ITEMS(StrEnum):
    CARDS = "progressive card"

def get_merge_name(num : int) -> str:
    assert 0 < num < 10_000, f"get merge number {num} out of range"
    return f"Merge {num : 04}"

class RummyCard(object):
    color : str
    symbol : str

    def __init__(self, color : str, symbol : str) -> None:
        assert color in COLORS, f"color {color} not in {COLORS}"
        assert symbol in SYMBOLS, f"symbol {symbol} not in {SYMBOLS}"
        self.color = str(color)
        self.symbol = str(symbol)

    def to_item(self, world):
        return world.create_item(self.get_name())

    def get_name(self) -> str:
        return f"CARD: {self.color}-{self.symbol}"

    def __eq__(self, other):
        if not isinstance(other, RummyCard):
            return NotImplemented            # don't attempt to compare against unrelated types
        return self.color == other.color and self.symbol == other.symbol
    def __hash__(self):
        return hash((self.color, self.symbol))
    def __repr__(self):
        return self.get_name()
    def __str__(self):
        return self.get_name()

    @staticmethod
    def from_string(data : str) -> Any:
        split = data.split(" ")[1].split("-")
        color = split[0]
        symbol = split[1]
        return RummyCard(color, symbol)


COLORS = ["RED", "BLUE", "BLACK", "WHITE"] #, "GREEN", "YELLOW"
assert len(COLORS) == MAX_COLORS

SYMBOLS = list([str(i) for i in range(1,MAX_NUMBERS+1)])
assert len(SYMBOLS) == MAX_NUMBERS

def name_color_item(color : str) -> str:
    assert color in COLORS, f"name {color} not in {COLORS}"
    return f"Color: {color}"
def name_symbol_item(symbol : str) -> str:
    assert symbol in SYMBOLS, f"name {symbol} not in SYMBOLS"
    return f"Symbol: {symbol}"



def enum_to_list(enum) -> list:
    return [e.value for e in enum]
