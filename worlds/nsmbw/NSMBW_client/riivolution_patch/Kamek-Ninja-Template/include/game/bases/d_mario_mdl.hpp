#pragma once
#include <game/bases/d_player_model.hpp>

class dMarioMdl_c : public dPlayerMdl_c {
public:
    dMarioMdl_c(u8 index);

    void fn_800cab00(int); ///< @unofficial

    u8 mPad[0x50];
};