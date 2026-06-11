from .bases import RummyTestBase
from ..Common import *

class TestBasicLogic(RummyTestBase):
    options = {

    }

    # A test is a function whose name starts with "test".
    def test_can_beat(self) -> None:
        self.assertTrue(self.world.get_location(get_merge_name(1)).can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location("Victory").can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location(get_merge_name(COPYS_OF_CARDS*MAX_NUMBERS*MAX_COLORS)).can_reach(self.multiworld.state))
