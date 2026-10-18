from test.bases import WorldTestBase
from ..options import *
from ..Common import *
from test.param import classvar_matrix

Utils.get_settings()["nsmbw_settings"].allow_gen_impactful_settings = True

class NSMBWTestBase(WorldTestBase):
    game = game_name
