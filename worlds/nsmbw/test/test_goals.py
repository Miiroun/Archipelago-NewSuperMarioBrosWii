from .bases import *

class TestGoalBowser(NSMBWTestBase):
    options = {
        "alternative_goal": AlternativeGoal.option_bowser,
    }


class TestGoalStarCoins(NSMBWTestBase):
    options = {
        "alternative_goal": AlternativeGoal.option_starcoins,
    }

class TestGoalHintMovies(NSMBWTestBase):
    options = {
        "alternative_goal": AlternativeGoal.option_hintmovies,
        "hint_movie_sanity" : True,
    }
