#pragma once

#include <types.h>

class dWmMapModel_c {
public:
    void playSwitchAnim(bool isRedSwitch, bool);
    bool isSwitchAnimStop();

    u8 mPad[0xbf8];
};
