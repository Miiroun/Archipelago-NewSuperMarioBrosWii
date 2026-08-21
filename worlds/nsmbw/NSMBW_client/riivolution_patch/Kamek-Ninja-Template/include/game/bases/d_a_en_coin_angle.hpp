#pragma once

#include <game/bases/d_enemy.hpp>

/// @unofficial
class daEnCoinAngle_c : public dEn_c {
public:
    void rotateCoin();

    u8 mPad[0x5C0];
    fBaseID_e mControllerUniqueID;
};