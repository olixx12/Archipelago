from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .forager_constants import GAME_NAME
from .forager_options import forager_option_groups

class ForagerWebWorld(WebWorld):
    game = GAME_NAME
    # Your game pages will have a visual theme (affecting e.g. the background image).
    # You can choose between dirt, grass, grassFlowers, ice, jungle, ocean, partyTime, and stone.
    theme = "grassFlowers"
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        f"A guide to setting up {GAME_NAME} for MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Olixx12", "SomeJakeGuy"],
    )

    tutorials = [setup_en]
    option_groups = forager_option_groups
    #options_presets = game_options_presets
