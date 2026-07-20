from types import MappingProxyType
from typing import TYPE_CHECKING

from BaseClasses import Entrance, CollectionState, Location

from .forager_regions import ForagerRegionData, region_access, LevelGroups
from .forager_items import (LEATHER_ITEMS, ROYAL_CLOTHING_ITEMS, PLASTIC_ITEMS, ROYAL_STEEL_ITEMS,
    VOID_ITEMS, VOID_STEEL_ITEMS, COSMIC_STEEL_ITEMS, NUCLEAR_ITEMS, STEEL_ITEMS, ELECTRONICS_ITEMS)
from worlds.generic.Rules import add_rule, add_item_rule

if TYPE_CHECKING:
    from . import ForagerWorld


def interpret_region_access(world: "ForagerWorld", region_name: str, region_data: ForagerRegionData):
    """Reads the input Region data class to then determine the various rules to apply to the given region.
    This includes parsing items required, xp, gold, etc."""
    main_ent: Entrance = world.get_region(region_data.parent_region).connect(world.get_region(region_name))

    # Make the connection bidirectional so AP can have an easier time to generate.
    world.get_region(region_name).connect(world.get_region(region_data.parent_region))

    # If the connection requires any items to access
    items = region_data.items_required
    if items:
        if("desert" in list(items.keys())):
            add_rule(main_ent,lambda state: can_reach_desert(state,world.player))
        elif("grave" in list(items.keys())):
            add_rule(main_ent,lambda state: can_reach_graveyard(state,world.player))
        elif("winter" in list(items.keys())):
            add_rule(main_ent,lambda state: can_reach_winter(state,world.player))
        elif("fire" in list(items.keys())):
            add_rule(main_ent,lambda state: can_reach_fire(state,world.player))
        else:
            add_rule(main_ent, lambda state: state.has_all_counts(items, world.player))


def create_region_access_rules(world: "ForagerWorld"):
    """Create the entrance and update the rules for each region based on the region access list"""
    for region_name, region_data in region_access.items():
        interpret_region_access(world, region_name, region_data)


def create_location_access_rules(world: "ForagerWorld"):
    # Create the victory condition
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)

    # Create the tools, minus the rods
    tools_not_create: list[str] = ["Fire Rod", "Meteor Rod", "Thunder Rod", "Storm Rod", "Ice Rod",
        "Blizzard Rod", "Necro Rod", "Death Rod"]
    for tool_name, tool_data in world.json_tables["locations"]["Tools"].items():
        if tool_name in tools_not_create or not list(tool_data["required_items"]):
            continue

        tool_loc: Location = world.get_location(tool_name)
        for item_req in list(tool_data["required_items"]):
            if "Leather" == item_req:
                add_rule(tool_loc, (lambda state: can_make_leather(state, world.player)))
            elif "Steel" == item_req:
                add_rule(tool_loc, (lambda state: can_make_steel(state,world.player)))
            elif "Royal Steel" == item_req:
                add_rule(tool_loc, (lambda state: can_make_royal_steel(state,world.player)))
            elif "Royal Clothing" == item_req:
                add_rule(tool_loc, (lambda state: can_make_royal_clothing(state,world.player)))
            elif "Plastic" == item_req:
                add_rule(tool_loc, (lambda state: can_make_plastic(state, world.player)))
            elif "Electronics" == item_req:
                add_rule(tool_loc, (lambda state: can_make_electronics(state, world.player)))
            elif "Void" == item_req:
                add_rule(tool_loc, (lambda state: can_reach_void(state,world.player)))
            elif "Void Steel" == item_req:
                add_rule(tool_loc, (lambda state: can_make_void_steel(state,world.player)))
            elif "Cosmic Steel" == item_req:
                add_rule(tool_loc, (lambda state: can_make_cosmic_steel(state,world.player)))
            elif "Nuclear" == item_req:
                add_rule(tool_loc, (lambda state: can_make_nuclear(state,world.player)))
            else:
                add_rule(tool_loc, (lambda state, loc_item=item_req: state.has(loc_item, world.player)))

def deny_item_placements(world: "ForagerWorld"):
    #TODO Currently un-used, leaving just in case, even as a debug.
    #TODO Doesn't work anymore due to stuff like backpacks being considered now.
    """Update the item rules to avoid placing that would otherwise self-lock.
    Normally this wouldn't be an issue, except that they are treated like progression unlocks.
    I.e. Royal Clothing requires everything in that tier, plus the previous tier."""
    world_loc_names: list[str] = [loc.name for loc in world.get_locations()]

    for loc_group, loc_list in world.json_tables["locations"].items():
        if loc_group == "Level" or loc_group == "Bundles":
            continue

        for loc_name, loc_data in loc_list.items():
            # Skip any locations that were previously not created.
            if not loc_name in world_loc_names:
                continue

            curr_loc: Location = world.get_location(loc_name)
            if "Leather" in list(loc_data["required_items"]):
                add_item_rule(curr_loc, lambda item: not item.name in LEATHER_ITEMS)

            match str(loc_data["region"]):
                case "Royal Clothing":
                    add_item_rule(curr_loc, lambda item: not item.name in ROYAL_CLOTHING_ITEMS)
                case "Steel":
                    add_item_rule(curr_loc, lambda item: not item.name in ["Industry"])
                case "Royal Steel":
                    add_item_rule(curr_loc, lambda item: not item.name in ROYAL_STEEL_ITEMS)
                case "Electronics":
                    add_item_rule(curr_loc, lambda item: not item.name in PLASTIC_ITEMS)
                case "Void Steel":
                    add_item_rule(curr_loc, lambda item: not item.name in VOID_STEEL_ITEMS)
                case "Cosmic Steel":
                    add_item_rule(curr_loc, lambda item: not item.name in COSMIC_STEEL_ITEMS)
                case "Nuclear":
                    add_item_rule(curr_loc, lambda item: not item.name in NUCLEAR_ITEMS)
                case _:
                    continue


def can_make_leather(state : CollectionState, player : int):
    return state.has_all_counts(LEATHER_ITEMS, player)

def can_make_royal_clothing(state : CollectionState, player : int):
    return state.has_all_counts(ROYAL_CLOTHING_ITEMS, player)

def can_make_steel(state : CollectionState, player : int):
    return state.has_all_counts(STEEL_ITEMS, player)

def can_make_royal_steel(state : CollectionState, player : int):
    return state.has_all_counts(ROYAL_STEEL_ITEMS, player)

def can_make_plastic(state : CollectionState, player : int):
    return state.has_all_counts(PLASTIC_ITEMS, player)

def can_make_electronics(state : CollectionState, player : int):
    return state.has_all_counts(ELECTRONICS_ITEMS, player)

def can_reach_void(state : CollectionState, player : int):
    return state.has_all_counts(VOID_ITEMS, player)

def can_make_void_steel(state: CollectionState, player: int):
    return state.has_all_counts(VOID_STEEL_ITEMS, player)

def can_make_cosmic_steel(state: CollectionState, player: int):
    return state.has_all_counts(COSMIC_STEEL_ITEMS, player)

def can_make_nuclear(state: CollectionState, player: int):
    return state.has_all_counts(NUCLEAR_ITEMS, player)

def can_make_banks(state: CollectionState, player: int):
    return state.has_all(["Industry","Banking"],player)

def can_sell_items(state: CollectionState, player: int):
    return state.has("Capitalism",player) or (state.has("Trade",player) and can_make_leather(state,player))

def can_reach_desert(state : CollectionState, player: int):
    return can_make_banks(state,player) or (can_sell_items(state,player) and state.has_any(["Colonization","Progressive Wallet"],player))

def can_reach_graveyard(state : CollectionState, player: int):
    return ((can_make_banks(state,player) and state.has_any_count({"Colonization" : 1, "Treasury" : 1, "Progressive Wallet" : 2},player)) or
            (can_sell_items(state,player) and state.has_all(["Geology", "Progressive Pickaxe", "Colonization"],player)))

def can_reach_winter(state: CollectionState, player: int):
    return can_sell_items(state,player) and state.has_all_counts({"Colonization" : 1, "Geology" : 1, "Mining" : 1, "Progressive Pickaxe" : 2, "Progressive Wallet" : 2},player)

def can_reach_fire(state: CollectionState, player: int):
    return (can_sell_items(state,player) and 
            state.has_all_counts({"Colonization" : 1,"Geology" : 1, "Mining" : 1, "Prospecting" : 1, "Deposit" : 1, "Progressive Pickaxe" : 3, "Progressive Wallet" : 2},player))