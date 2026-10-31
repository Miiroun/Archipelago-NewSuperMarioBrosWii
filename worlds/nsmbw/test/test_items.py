from .bases import *


class TestItems(NSMBWTestBase):
    options = {

    }

    def test_goomba_extinction(self):
        for itm in self.multiworld.itempool:
            if itm.name == ITEM.UNIQUE.GoombaExtinction:
                return
                #print(f"Found")
        raise Exception(f"GoombaExtinction not found")

        #for loc in self.multiworld.get_locations():
        #    if loc.item.name == ITEM.UNIQUE.GoombaExtinction:
        #        print("found")
        #self.multiworld.find_item(ITEM.UNIQUE.GoombaExtinction, self.player)