from worlds.AutoWorld import World, WebWorld
from BaseClasses import ItemClassification as IClass
from worlds.LauncherComponents import Component, components, icon_paths, launch as launch_component, Type
from .Regions import load_tables, load_regions, ForagerLocation
from.Items import ForagerItem

def launch_client():
    from .Client import launch
    launch_component(launch, name="ForagerClient")


components.append(Component("Forager Client", func=launch_client,
                            component_type=Type.CLIENT))

#Class ForagerWebWorld(Webworld): //Major
class ForagerWorld(World):
    game = "Forager"
    item_name_to_id = {}
    location_name_to_id = {}
    load_tables(item_name_to_id,location_name_to_id) #Placeholder, will probably need to be done elsewhere
    #web = ForagerWebWorld()

    def __init__(self, multiworld, player):
        super().__init__(multiworld, player)

    def create_item(self, name):
        return ForagerItem(name,IClass.progression,self.item_name_to_id[name],self.player) #Needs to have item classifications done
    
    def create_regions(self):
        regions = load_regions(self.player,self.multiworld)
        for location,address in self.location_name_to_id.items():
            regions["Menu"].locations.append(ForagerLocation(self.player,location,address, parent = regions["Menu"])) #Placeholder
        self.multiworld.regions.extend(list(regions.values()))
    
    def create_items(self):
        #Massive placeholder
        locations = len(self.location_name_to_id)
        items = 0
        for item,address in self.item_name_to_id.items():
            if(items < locations):
                self.multiworld.itempool.append(ForagerItem(item,IClass.progression,address,self.player))
                items += 1
    
    
