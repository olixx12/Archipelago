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
    ThirdGroup = "Levels 11-15"
    FourthGroup = "Levels 16-20"
    FifthGroup = "Levels 21-25"
    SixthGroup = "Levels 26-30"
    SeventhGroup = "Levels 31-35"
    EighthGroup = "Levels 36-45"
    NinthGroup = "Levels 46-65"


class ForagerRegionData(NamedTuple):
    """Gives the flexibility to add multiple types of region requirements in the future, such as required gold, xp, etc."""
    parent_region: str
    items_required: dict[str, int] = None


class ForagerLocation(Location):
    game: str = GAME_NAME

    def __init__(self, player: int, name: str = '', address: Optional[int] = None, parent: Optional[Region] = None):
        super().__init__(player, name, address, parent)

# Defines the region and any access related requirements
region_access: dict[str, ForagerRegionData] = {
    "Royal Clothing": ForagerRegionData("Menu", {"Foraging" : 1, "Sewing" : 1, "Craftsmanship" : 1, "Prospecting" : 1, "Progressive Backpack" : 2}),
    "Steel": ForagerRegionData("Menu", {"Industry" : 1, "Progressive Backpack" : 1}),
    "Royal Steel": ForagerRegionData("Steel", {"Craftsmanship" : 1,"Prospecting" : 1, "Deposit" : 1, "Progressive Backpack" : 2}),
    "Electronics": ForagerRegionData("Royal Steel", {"Manufacturing" : 1, "Progressive Backpack" : 3}),
    "Void Steel": ForagerRegionData("Electronics", {"Transmutation" : 1, "Spirituality" : 1, "Storage" : 1}),
    "Cosmic Steel": ForagerRegionData("Void Steel", {"Astrology" : 1}),
    "Nuclear": ForagerRegionData("Void Steel", {"Physics" : 1}),

    "Grass": ForagerRegionData("Menu"),
    "Desert": ForagerRegionData("Grass",{"desert" : 1}),
    "Winter": ForagerRegionData("Desert",{"grave" : 1}),
    "Graveyard": ForagerRegionData("Winter", {"winter" : 1}),
    "Fire": ForagerRegionData("Graveyard", {"fire" : 1}),

    str(LevelGroups.FirstGroup): ForagerRegionData("Menu"),
    str(LevelGroups.SecondGroup): ForagerRegionData(str(LevelGroups.FirstGroup), {"Progressive Pickaxe" : 1, "Magic" : 1}),
    str(LevelGroups.ThirdGroup): ForagerRegionData(str(LevelGroups.SecondGroup), {"Industry" : 1, "Combat" : 1}),
    str(LevelGroups.FourthGroup): ForagerRegionData(str(LevelGroups.ThirdGroup), {"Progressive Pickaxe" : 2, "Progressive Book" : 1}),
    str(LevelGroups.FifthGroup): ForagerRegionData(str(LevelGroups.FourthGroup), {"Capitalism" : 1}),
    str(LevelGroups.SixthGroup): ForagerRegionData(str(LevelGroups.FifthGroup), {"Progressive Book" : 3}),
    str(LevelGroups.SeventhGroup): ForagerRegionData(str(LevelGroups.SixthGroup), {"Progressive Pickaxe" : 3}),
    str(LevelGroups.EighthGroup): ForagerRegionData(str(LevelGroups.SeventhGroup), {"Optics" : 1}),
    str(LevelGroups.NinthGroup): ForagerRegionData(str(LevelGroups.EighthGroup), {"Logistics" : 1})
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
            case i if 10 < i <= 15:
                group_to_use: str = str(LevelGroups.ThirdGroup)
            case i if 15 < i <= 20:
                group_to_use: str = str(LevelGroups.FourthGroup)
            case i if 20 < i <= 25:
                group_to_use: str = str(LevelGroups.FifthGroup)
            case i if 25 < i <= 30:
                group_to_use: str = str(LevelGroups.SixthGroup)
            case i if 30 < i <= 35:
                group_to_use: str = str(LevelGroups.SeventhGroup)
            case i if 35 < i <= 45:
                group_to_use: str = str(LevelGroups.EighthGroup)
            case i if 45 < i <= 65:
                group_to_use: str = str(LevelGroups.NinthGroup)

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
