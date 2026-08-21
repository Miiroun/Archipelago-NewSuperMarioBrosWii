#pragma once

#include <game/bases/d_enemy.hpp>

class daEnPairObjParent_c : public dEn_c {
public:
    STATE_FUNC_DECLARE(daEnPairObjParent_c, Vanish);

    float mOffsetPos;

    u8 mPad[121];

    u8 mVertical;
};