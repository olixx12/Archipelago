import json
import pkgutil

from BaseClasses import Region, MultiWorld, Entrance, Location, LocationProgressType, CollectionState, ItemClassification as IClass
from worlds.generic.Rules import add_rule

offset = 4072780000

def can_make_leather(state : CollectionState, player : int):
    return state.has_all(("Foraging","Sewing"), player)

def can_make_plastic(state : CollectionState, player : int):
    return (can_make_leather(state,player) and state.has_all(("Drilling", "Manufacturing"), player))

def can_reach_void(state : CollectionState, player : int):
    #TODO : Star Fragments not considered rn
    return (can_make_plastic(state,player) and state.has("Summoning", player))

def can_make_void_steel(state: CollectionState, player: int):
    return state.has_all(("Transmutation", "Spirituality", "Summoning"), player) and can_reach_void(state,player)

def load_regions(player : int, multiworld : MultiWorld):
    region_file = pkgutil.get_data(__name__,"data/regions.json").decode("utf-8")
    region_list = json.loads(region_file)
    regions = {name: Region(name,player,multiworld) for name in region_list}
    #TODO : Finishing Connection rules prob, putting the locations in the regions
    regions["Menu"].connect(regions["Steel"],"Steel Craftable",
                            lambda state: state.has("Industry",player))
    regions["Steel"].connect(regions["Royal Steel"],"Royal Steel Craftable",
                            lambda state: state.has_all(("Craftmanship","Prospecting"),player))
    regions["Royal Steel"].connect(regions["Electronics"],"Electronics Craftable", 
                                   lambda state : state.has("Manufacturing", player))
    regions["Electronics"].connect(regions["Void Steel"],"Void Steel Craftable", 
                                   lambda state : can_make_void_steel(state,player))
    regions["Void Steel"].connect(regions["Cosmic Steel"], "Cosmic Steel Craftable",
                                  lambda state : state.has("Astrology",player))
    regions["Void Steel"].connect(regions["Nuclear"], "Nuclear Tier", 
                                  lambda state : state.has("Physics", player))
    return regions.values()


def load_tables(item_name_to_id,location_name_to_id):
    #Loading item table
    item_file = pkgutil.get_data(__name__,"data/items.json").decode("utf-8")
    items = json.loads(item_file)
    for category_name,category in items.items():
        if category_name == "Tools":
            for tool_name,tool in category.items():
                item_name_to_id[tool_name] = tool["id"]
        else:
            item_name_to_id.update(category)
    #Loading location table
    location_file = pkgutil.get_data(__name__,"data/locations.json").decode("utf-8")
    locations = json.loads(location_file)
    for category_name,category in locations.items():
        if category_name == "Level":
            for i in range(2,category["last_id"] - category["first_id"] + 2):
                location_name_to_id[f"Level {i}"] = (category["first_id"]+i) - 2
        else:
            item_name_to_id.update(category)
    #Applying the offset to both table
    for item_name,item_id in item_name_to_id.items():
        item_name_to_id[item_name] = item_id + offset
    for location_name,location_id in location_name_to_id.items():
        item_name_to_id[location_name] = location_id + offset