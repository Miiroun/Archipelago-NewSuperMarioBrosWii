from test.bases import WorldTestBase
from ..Common import *

from ..world import RummyWorld

class RummyTestBase(WorldTestBase):
    game = RUMMY_NAME
    world: RummyWorld

