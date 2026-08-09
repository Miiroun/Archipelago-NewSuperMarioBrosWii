from .bases import *

class TestGoalBowser(NSMBWWorld):
    options = {
        "alternative_goal": AlternativeGoal.option_bowser,
    }


class TestGoalStarCoins(NSMBWWorld):
    options = {
        "alternative_goal": AlternativeGoal.option_starcoins,
    }

class TestGoalHintMovies(NSMBWWorld):
    options = {
        "alternative_goal": AlternativeGoal.option_hintmovies,
        "hint_movie_sanity" : True,
    }
