#pragma once

#include <game/bases/d_player_model_base.hpp>

class dYoshiMdl_c : public dPyMdlBase_c {
public:
    enum YoshiColor_e {};
    
    dYoshiMdl_c(u8 index);

    u8 mPad[0x40];
    YoshiColor_e mColor;
    u8 mPad2[0x1C8];
};