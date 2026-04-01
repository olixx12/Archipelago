from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification as IC

from .forager_constants import GAME_NAME

if TYPE_CHECKING:
    from worlds.forager import ForagerWorld

LEATHER_ITEMS: list[str] = ["Foraging", "Sewing"]
ROYAL_CLOTHING_ITEMS: list[str] = LEATHER_ITEMS + ["Craftsmanship", "Prospecting"]
PLASTIC_ITEMS: list[str] = ROYAL_CLOTHING_ITEMS + ["Drilling", "Manufacturing"]
ROYAL_STEEL_ITEMS: list[str] = ["Industry", "Craftsmanship", "Prospecting"]
VOID_ITEMS: list[str] = ROYAL_STEEL_ITEMS + ["Summoning", "Combat"]
VOID_STEEL_ITEMS: list[str] = VOID_ITEMS + ["Transmutation", "Spirituality"]
COSMIC_STEEL_ITEMS: list[str] = VOID_ITEMS + ["Astrology"]
NUCLEAR_ITEMS: list[str] = VOID_ITEMS + ["Physics"]


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