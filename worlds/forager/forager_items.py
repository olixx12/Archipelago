from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification as IC

from .forager_constants import GAME_NAME

if TYPE_CHECKING:
    from worlds.forager import ForagerWorld

LEATHER_ITEMS: dict[str,int] = {"Foraging" : 1, "Sewing" : 1, "Progressive Backpack" : 1}
ROYAL_CLOTHING_ITEMS: dict[str,int] = LEATHER_ITEMS | {"Craftsmanship" : 1, "Prospecting" : 1, "Progressive Backpack" : 2} 
PLASTIC_ITEMS: dict[str,int] = ROYAL_CLOTHING_ITEMS | {"Drilling" : 1, "Manufacturing" : 1, "Progressive Backpack" : 3, "Progressive Shovel" : 2}
STEEL_ITEMS: dict[str,int] = {"Industry" : 1,"Progressive Backpack" : 1}
ROYAL_STEEL_ITEMS: dict[str,int] = STEEL_ITEMS | {"Craftsmanship" : 1, "Prospecting" : 1, "Progressive Backpack" : 2}
ELECTRONICS_ITEMS: dict[str,int] = ROYAL_STEEL_ITEMS | {"Manufacturing" : 1, "Progressive Backpack" : 3}
VOID_ITEMS: dict[str,int] = ROYAL_STEEL_ITEMS | {"Summoning" : 1, "Combat" : 1, "Storage" : 1}
VOID_STEEL_ITEMS: dict[str,int] = VOID_ITEMS | {"Transmutation" : 1, "Spirituality" : 1, "Progressive Sword" : 6}
COSMIC_STEEL_ITEMS: dict[str,int] = VOID_STEEL_ITEMS | {"Astrology" : 1}
NUCLEAR_ITEMS: dict[str,int] = COSMIC_STEEL_ITEMS | {"Physics" : 1}

DIG_ARCHEOLOGY: dict[str,int] = {"Progressive Shovel" : 3, "Prospecting" : 1}


class ForagerItem(Item):
    game: str = GAME_NAME

    def __init__(self, name: str, classification: IC, code: int, player: int):
        super().__init__(name, classification, code, player)


def create_world_items(world: "ForagerWorld"):
    item_pool: list[Item] = []

    # Create the required amount of Progression Items
    for prog_name, prog_category in world.item_class_sets["Progression"].items():
        if prog_category in ["Seals", "Relics"]:
            continue

        json_data: dict = world.json_tables["items"][prog_category][prog_name]
        if json_data.get("count", ""):
            for tool_count in range(json_data["count"]):
                item_pool.append(ForagerItem(prog_name, IC.progression, json_data["id"], world.player))
        else:
            item_pool.append(ForagerItem(prog_name, IC.progression, json_data["id"], world.player))

    # Create the extra useful items that the player can use, such as QOL skills with 90 weight
    # or Create filler items with 10 weight
    locations_left_to_fill: int = len(world.multiworld.get_unfilled_locations(world.player)) - len(item_pool)
    for loc_to_fill in range(locations_left_to_fill):
        item_type: str = world.random.choices(["Useful", "Filler"], [90, 10], k=1)[0]
        random_type_item: str = world.random.choice(list(world.item_class_sets[item_type].keys()))
        cat_name: str = world.item_class_sets[item_type][random_type_item]
        item_pool.append(ForagerItem(random_type_item, IC.useful if item_type == "Useful" else IC.filler,
            world.json_tables["items"][cat_name][random_type_item]["id"], world.player))

    world.multiworld.itempool += item_pool