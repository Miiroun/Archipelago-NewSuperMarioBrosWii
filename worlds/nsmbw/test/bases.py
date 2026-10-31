from test.bases import WorldTestBase
from ..options import *
from ..Common import *
from test.param import classvar_matrix

if not get_settings()["nsmbw_settings"].allow_gen_impactful_settings:
    get_settings()["nsmbw_settings"].allow_gen_impactful_settings = True
    get_settings().save()

class NSMBWTestBase(WorldTestBase):
    game = game_name
