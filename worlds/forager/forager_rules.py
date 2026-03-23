from types import MappingProxyType
from typing import TYPE_CHECKING

from BaseClasses import Entrance, CollectionState, Location

from .forager_regions import ForagerRegionData, region_access, LevelGroups
from .forager_items import (LEATHER_ITEMS, ROYAL_CLOTHING_ITEMS, PLASTIC_ITEMS, ROYAL_STEEL_ITEMS,
    VOID_STEEL_ITEMS, COSMIC_STEEL_ITEMS, NUCLEAR_ITEMS)
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
    if region_data.items_required:
        add_rule(main_ent, lambda state: state.has_all(region_data.items_required, world.player))


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
            if "Leather" in item_req:
                add_rule(tool_loc, (lambda state: can_make_leather(state, world.player)))
            elif "Plastic" in item_req:
                add_rule(tool_loc, (lambda state: can_make_plastic(state, world.player)))
            else:
                add_rule(tool_loc, (lambda state, loc_item=item_req: state.has(loc_item, world.player)))

    # Create logic rules to lock the Levels behind
    for lvl_group in LevelGroups:
        if len(world.get_region(str(lvl_group)).entrances) > 0:
            for reg_entrace in world.get_region(str(lvl_group)).entrances:
                match lvl_group:
                    case LevelGroups.SecondGroup: # Levels 6-10
                        add_rule(reg_entrace, lambda state: can_make_leather(state, world.player))
                        continue

                    case LevelGroups.ThirdGroup: # Levels 11-20
                        add_rule(reg_entrace, lambda state, prog_pick=MappingProxyType({"Progressive Pickaxe": 2}):
                            state.has_all_counts(prog_pick, world.player) and (can_make_royal_steel(state, world.player)
                                or can_make_royal_clothing(state, world.player)))
                        continue

                    case LevelGroups.FourthGroup: # Levels 21-30
                        add_rule(reg_entrace, lambda state, prog_pick=MappingProxyType({"Progressive Pickaxe": 3}):
                            state.has_all_counts(prog_pick, world.player) and (can_make_royal_steel(state, world.player)
                                or can_make_royal_clothing(state, world.player)))
                        continue

                    case LevelGroups.FifthGroup: # Levels 31-40
                        add_rule(reg_entrace, lambda state, req_items=MappingProxyType({"Progressive Pickaxe": 4,
                            "Progressive Book": 2}): state.has_all_counts(req_items, world.player) and
                            can_reach_void(state, world.player))
                        continue

                    case LevelGroups.SixthGroup: # Levels 41-50
                        add_rule(reg_entrace, lambda state, req_items=MappingProxyType({"Progressive Pickaxe": 5,
                            "Progressive Book": 4}): state.has_all_counts(req_items, world.player) and
                            can_make_void_steel(state, world.player))
                        continue

                    case LevelGroups.SeventhGroup: # Levels 51-60
                        add_rule(reg_entrace, lambda state, req_items=MappingProxyType({"Progressive Pickaxe": 6,
                            "Progressive Book": 6}): state.has_all_counts(req_items, world.player) and
                            can_make_cosmic_steel(state, world.player))
                        continue

                    case LevelGroups.EighthGroup: # Levels 61-65
                        add_rule(reg_entrace, lambda state, req_items=MappingProxyType({"Progressive Pickaxe": 7,
                            "Progressive Book": 8}): state.has_all_counts(req_items, world.player) and
                            can_make_nuclear(state, world.player))
                        continue

                    case _:
                        continue


    # Add rules to the events that ensures you can only logically get the next tier if you have the previous upgrade item.
    for tier_num in range(3, 9):
        tier_loc: Location = world.get_location(f"Tier {tier_num}")
        add_rule(tier_loc, lambda state, num=tier_num-1: state.has(f"Upgrade {num}", world.player))


def deny_item_placements(world: "ForagerWorld"):
    #TODO Currently un-used, leaving just in case, even as a debug.
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
    return state.has_all(LEATHER_ITEMS, player)

def can_make_royal_clothing(state : CollectionState, player : int):
    return can_make_leather(state, player) and state.has_all(["Craftsmanship", "Prospecting"], player)

def can_make_royal_steel(state : CollectionState, player : int):
    return state.has_all(["Industry", "Craftsmanship", "Prospecting"], player)

def can_make_plastic(state : CollectionState, player : int):
    return can_make_royal_clothing(state, player) and state.has_all(["Drilling", "Manufacturing"], player)

def can_reach_void(state : CollectionState, player : int):
    #TODO : Star Fragments not considered rn
    return can_make_royal_steel(state,player) and state.has_all(["Summoning", "Combat"], player)

def can_make_void_steel(state: CollectionState, player: int):
    return can_reach_void(state,player) and state.has_all(["Transmutation", "Spirituality"], player) and (
        state.has("Progressive Sword", player, 6))

def can_make_cosmic_steel(state: CollectionState, player: int):
    return can_reach_void(state, player) and state.has("Astrology", player)

def can_make_nuclear(state: CollectionState, player: int):
    return can_reach_void(state, player) and state.has("Physics", player)