from enum import StrEnum
from typing import TYPE_CHECKING, NamedTuple, Optional

from BaseClasses import Region, Location

from .forager_constants import GAME_NAME
from .forager_items import ForagerItem

if TYPE_CHECKING:
    from worlds.forager import ForagerWorld


class LevelGroups(StrEnum):
    FirstGroup = "Levels 2-5"
    SecondGroup = "Levels 6-10"
    ThirdGroup = "Levels 11-20"
    FourthGroup = "Levels 21-30"
    FifthGroup = "Levels 31-40"
    SixthGroup = "Levels 41-50"
    SeventhGroup = "Levels 51-60"
    EighthGroup = "Levels 61-65"


class ForagerRegionData(NamedTuple):
    """Gives the flexibility to add multiple types of region requirements in the future, such as required gold, xp, etc."""
    parent_region: str
    items_required: list[str] = None


class ForagerLocation(Location):
    game: str = GAME_NAME

    def __init__(self, player: int, name: str = '', address: Optional[int] = None, parent: Optional[Region] = None):
        super().__init__(player, name, address, parent)

# Defines the region and any access related requirements
region_access: dict[str, ForagerRegionData] = {
    "Royal Clothing": ForagerRegionData("Menu", ["Foraging", "Sewing", "Craftsmanship", "Prospecting"]),
    "Steel": ForagerRegionData("Menu", ["Industry"]),
    "Royal Steel": ForagerRegionData("Steel", ["Craftsmanship","Prospecting", "Deposit"]),
    "Electronics": ForagerRegionData("Royal Steel", ["Manufacturing"]),
    "Void Steel": ForagerRegionData("Electronics", ["Transmutation", "Spirituality"]),
    "Cosmic Steel": ForagerRegionData("Void Steel", ["Astrology"]),
    "Nuclear": ForagerRegionData("Void Steel", ["Physics"]),

    "Grass": ForagerRegionData("Menu"),
    "Desert": ForagerRegionData("Grass",),
    "Winter": ForagerRegionData("Desert"),
    "Graveyard": ForagerRegionData("Winter"),
    "Fire": ForagerRegionData("Graveyard"),

    str(LevelGroups.FirstGroup): ForagerRegionData("Menu"),
    str(LevelGroups.SecondGroup): ForagerRegionData(str(LevelGroups.FirstGroup), ["Industry"]),
    str(LevelGroups.ThirdGroup): ForagerRegionData(str(LevelGroups.SecondGroup), ["Deposit"]),
    str(LevelGroups.FourthGroup): ForagerRegionData(str(LevelGroups.ThirdGroup), ["Magic"]),
    str(LevelGroups.FifthGroup): ForagerRegionData(str(LevelGroups.FourthGroup), ["Capitalism"]),
    str(LevelGroups.SixthGroup): ForagerRegionData(str(LevelGroups.FifthGroup)),
    str(LevelGroups.SeventhGroup): ForagerRegionData(str(LevelGroups.SixthGroup)),
    str(LevelGroups.EighthGroup): ForagerRegionData(str(LevelGroups.SeventhGroup)),
}

def load_regions(world: "ForagerWorld"):
    # Make Menu region
    world.multiworld.regions.append(Region("Menu", world.player, world.multiworld))

    region_list: list[str] = list(world.json_tables["regions"]) + list(world.json_tables["islands"]["Lands"].keys())
    for region_name in region_list:
        world.multiworld.regions.append(Region(region_name, world.player, world.multiworld))

    for lvl_enum in LevelGroups:
        world.multiworld.regions.append(Region(str(lvl_enum), world.player, world.multiworld))

def create_locations(world: "ForagerWorld"):
    # Create all levels first.
    first_level: int = world.json_tables["locations"]["Level"]["first_id"]
    for i in range(2, world.required_level_count + 1):
        group_to_use: str = str(LevelGroups.FirstGroup)
        match i:
            case i if 5 < i <= 10:
                group_to_use: str = str(LevelGroups.SecondGroup)
            case i if 10 < i <= 20:
                group_to_use: str = str(LevelGroups.SecondGroup)
            case i if 20 < i <= 30:
                group_to_use: str = str(LevelGroups.FourthGroup)
            case i if 30 < i <= 40:
                group_to_use: str = str(LevelGroups.FifthGroup)
            case i if 40 < i <= 50:
                group_to_use: str = str(LevelGroups.SixthGroup)
            case i if 50 < i <= 60:
                group_to_use: str = str(LevelGroups.SeventhGroup)
            case i if 60 < i <= 65:
                group_to_use: str = str(LevelGroups.EighthGroup)

        level_region: Region = world.get_region(group_to_use)
        if i == world.required_level_count:
            level_region.add_event(f"Level {i}", "Victory",
                location_type=ForagerLocation, item_type=ForagerItem)
            break
        else:
            level_region.locations.append(ForagerLocation(world.player, f"Level {i}",
                (first_level + i) - 2, level_region))

    # Create the tools, minus the rods
    tools_not_create: list[str] = ["Fire Rod", "Meteor Rod", "Thunder Rod", "Storm Rod", "Ice Rod",
        "Blizzard Rod", "Necro Rod", "Death Rod"]
    for loc_group, loc_list in world.json_tables["locations"].items():
        if loc_group == "Level" or loc_group == "Bundles":
            continue

        for loc_name, loc_data in loc_list.items():
            if loc_name in tools_not_create:
                continue

            loc_region: Region = world.get_region(str(loc_data["region"]))
            loc_region.locations.append(ForagerLocation(world.player, loc_name, loc_data["id"], loc_region))

    # Create some event items for ensuring logic handles upgrade items in order.
    grass_reg: Region = world.get_region("Grass")
    for tier_num in range(2, 9):
        grass_reg.add_event(f"Tier {tier_num}", f"Upgrade {tier_num}",
            location_type=ForagerLocation, item_type=ForagerItem)