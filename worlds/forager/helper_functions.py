import json
from importlib import resources
from importlib.abc import Traversable


def load_json_tables() -> dict:
    """
    Load all JSON files from the data folder into memory
    """
    data: dict[str, dict] = {}
    data_folder: Traversable = resources.files(__name__).joinpath("data")

    for file_path in data_folder.iterdir():
        if (file_path.is_file() and file_path.name.lower().endswith('.json') and
            not file_path.name.lower().startswith("backup_")):
            data[file_path.name.replace(".json", "")] = json.loads(file_path.read_text('utf-8'))
    return data


def load_tables(item_json: dict, location_json: dict) -> tuple:
    # Loading item table dicts
    item_name_to_id: dict[str, int] = {}
    item_categories: dict[str, set[str]] = {} # Adds the item group for hinting by group name, etc.
    item_class_sets: dict[str, dict[str, str]] = {} # Adds each item classification as its own set

    for category_name, category in item_json.items():
        item_categories.setdefault(category_name, set())
        for item_name, item_data in category.items():
            item_class_sets.setdefault(item_data["classification"], {}).update({item_name: category_name})
            item_categories[category_name].add(item_name)  # Adds the item name in the "Tools" item_group
            item_name_to_id[item_name] = item_data["id"]

    # Loading location table dicts
    location_name_to_id: dict[str, int] = {}
    location_categories: dict[str, set[str]] = {} # Adds the location group for hinting by group name, etc.
    for category_name, category in location_json.items():
        location_categories.setdefault(category_name, set())

        if category_name == "Level":
            for i in range(2,category["last_id"] - category["first_id"] + 2):
                location_name_to_id[f"Level {i}"] = (category["first_id"]+i) - 2
                location_categories[category_name].add(f"Level {i}")
        else:
            for location, loc_id in category.items():
                location_name_to_id[location] = loc_id["id"]
                location_categories[category_name].add(location)

    return item_name_to_id, item_categories, item_class_sets, location_name_to_id, location_categories