from .bases import RummyTestBase


class TestBasicLogic(RummyTestBase):
    options = {

    }

    # A test is a function whose name starts with "test".
    def test_can_beat(self) -> None:
        self.assertFalse(self.world.get_location("Victory").can_reach(self.multiworld.state))
