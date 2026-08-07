from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld
from .Common import *

from .options import option_groups, option_presets


class NSMBWWebWorld(WebWorld):
    game = game_name

    theme = "grassFlowers"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up New Super Mario Bros Wii for MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Miiroun"],
    )


    # We add these tutorials to our WebWorld by overriding the "tutorials" field.
    tutorials = [setup_en]

    # If we have option groups and/or option presets, we need to specify these here as well.
    option_groups = option_groups
    options_presets = option_presets

    rich_text_options_doc = True

if __name__ == "__main__":
    webworld = NSMBWWebWorld()
