from dataclasses import dataclass
from Options import PerGameCommonOptions, Toggle, Range, Choice, OptionGroup


class GameMode(Choice):
    """Enable alternative game modes:
    Default - Forager's main goal is to level up to a certain level to reach goal.
    """
    display_name = "Game Mode"
    internal_name = "game_mode"
    option_default = 0
    default = 0

class RequiredLevel(Range):
    """
    Choose what level is required to beat the game.
    """
    display_name = "Required Level"
    internal_name = "required_level"
    default = 65
    range_start = 20
    range_end = 65

@dataclass
class ForagerOptions(PerGameCommonOptions):
    game_mode: GameMode
    required_level: RequiredLevel


forager_option_groups: list[OptionGroup] = [
    OptionGroup("Main Forager Options", [GameMode])
]