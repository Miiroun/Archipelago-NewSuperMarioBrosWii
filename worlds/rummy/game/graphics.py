from enum import Enum


class Graphic(Enum):
    EMPTY = 0

    REMOTE_ITEM = 70

    ITEMS_TEXT = 80

    CARDS = 81

    ZERO = 1000
    ONE = 1001
    TWO = 1002
    THREE = 1003
    FOUR = 1004
    FIVE = 1005
    SIX = 1006
    SEVEN = 1007
    EIGHT = 1008
    NINE = 1009

    PLUS = 1100
    MINUS = 1101
    TIMES = 1102
    DIVIDE = 1103

    LETTER_A = 2000
    LETTER_E = 2005
    LETTER_H = 2008
    LETTER_I = 2009
    LETTER_M = 2013
    LETTER_T = 2019

    EQUALS = 2050
    NO = 2060

    UNKNOWN = -1


DIGIT_TO_GRAPHIC = {
    None: Graphic.EMPTY,
    0: Graphic.ZERO,
    1: Graphic.ONE,
    2: Graphic.TWO,
    3: Graphic.THREE,
    4: Graphic.FOUR,
    5: Graphic.FIVE,
    6: Graphic.SIX,
    7: Graphic.SEVEN,
    8: Graphic.EIGHT,
    9: Graphic.NINE,
}

DIGIT_TO_GRAPHIC_ZERO_EMPTY = DIGIT_TO_GRAPHIC.copy()
DIGIT_TO_GRAPHIC_ZERO_EMPTY[0] = Graphic.EMPTY
