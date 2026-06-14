from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle


# values in Common.py can be thought of as options

@dataclass
class RummyOptions(PerGameCommonOptions):
    pass

option_groups = [
]

option_presets = {

}
