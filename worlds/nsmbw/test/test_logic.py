from .bases import NSMBWWorld

class TestLogic(NSMBWWorld):
    options = {
    #    "difficulty": "easy",
    #    "final_boss_hp": 4000,
    }

    def test_sword_chests(self) -> None:
        """Test locations that require a sword"""
        #    locations = ["Chest1", "Chest2"]
        #    items = [["Sword"]]
        # This tests that the provided locations aren't accessible without the provided items, but can be accessed once
        # the items are obtained.
        # This will also check that any locations not provided don't have the same dependency requirement.
        # Optionally, passing only_check_listed=True to the method will only check the locations provided.
        #    self.assertAccessDependency(locations, items)