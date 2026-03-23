from typing import ClassVar
from dataclasses import fields

from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import ItemClassification
from worlds.LauncherComponents import Component, components, icon_paths, launch as launch_component, Type

from .forager_constants import GAME_NAME, CLIENT_NAME
from .forager_items import create_world_items, ForagerItem
from .forager_rules import create_region_access_rules, create_location_access_rules
from .forager_webworld import ForagerWebWorld
from .helper_functions import load_tables, load_json_tables
from .forager_regions import load_regions, create_locations
from .forager_options import ForagerOptions


# Define the client launch state function and add it to the AP Launcher
def launch_client():
    from .Client import launch
    launch_component(launch, name=CLIENT_NAME)
components.append(Component(CLIENT_NAME, func=launch_client, component_type=Type.CLIENT))


class ForagerWorld(World):
    game = GAME_NAME
    item_name_to_id: ClassVar[dict[str, int]]
    item_name_groups: ClassVar[dict[str, set[str]]]
    item_class_sets: ClassVar[dict[str, dict[str, str]]]

    location_name_to_id: ClassVar[dict[str, int]]
    location_name_groups: ClassVar[dict[str, set[str]]]
    json_tables: dict[str, dict] = load_json_tables()

    item_name_to_id, item_name_groups, item_class_sets, location_name_to_id, location_name_groups = (
        load_tables(json_tables["items"], json_tables["locations"]))

    options: ForagerOptions
    options_dataclass = ForagerOptions

    web = ForagerWebWorld()
    required_level_count: int

    ut_can_gen_without_yaml = True  # class var that tells UT that it can gen using slot data instead of player yamls

    def __init__(self, multiworld, player):
        super().__init__(multiworld, player)
        self.required_level_count = 0

    def generate_early(self) -> None:
        """Used for evaluating any OptionErrors we see fit, updating some option values based on invalid combos, etc."""

        # Load UT's data from slot data to avoid incorrect logic being presented to the player
        if hasattr(self.multiworld, "re_gen_passthrough"):
            slot_data = self.multiworld.re_gen_passthrough[self.game]
            for key, value in slot_data.items():
                try:
                    getattr(self.options, key).value = value
                except AttributeError:
                    # As there might be slot_data keys that were added that are not options, just ignore the error.
                    pass

        if self.options.game_mode.value == self.options.game_mode.option_default:
            self.required_level_count = self.options.required_level.value

        self.multiworld.early_items[self.player].update({"Industry": 1})


    def create_regions(self):
        """Loads both the regions and the locations"""
        load_regions(self)
        create_locations(self)


    def set_rules(self):
        """Attach the various rules for both locations and regions"""
        create_region_access_rules(self)
        create_location_access_rules(self)


    def create_items(self):
        """Creates the various items required based on the user's options"""
        create_world_items(self)


    def create_item(self, name):
        for item_type in self.item_class_sets.keys():
            if name in self.item_class_sets[item_type].keys():
                cat_name: str = self.item_class_sets[item_type][name]
                return ForagerItem(name, ItemClassification(str(item_type).lower()), self.item_name_to_id[name], self.player)

        raise Exception(f"Forager world is unable to find an item named: {name}")


    def fill_slot_data(self):
        slot_data: dict = {}

        # This gets all the names of the options from both the world's option class and the inherited class as sets
        # Since this world's options inherit from PerGameCommonOptions, there will be duplicates.
        child_local_fields = set({f.name for f in fields(ForagerOptions)})
        parent_fields = set({f.name for f in fields(PerGameCommonOptions)})

        # Subtract the elements to find the options only unique to this world, then sort them to avoid any
        #   deterministic issues.
        only_in_child = sorted(list(child_local_fields - parent_fields))

        # Output the value of each based on the option type.
        for child_option in only_in_child:
            slot_data[child_option] = getattr(self.options, child_option).value
        return slot_data