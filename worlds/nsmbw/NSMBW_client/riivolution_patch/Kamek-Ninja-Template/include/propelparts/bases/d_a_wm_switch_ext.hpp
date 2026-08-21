#pragma once
#include <game/bases/d_a_wm_switch.hpp>

// @unofficial
class daWmSwitchExt_c : public daWmSwitch_c {
public:
    enum TYPE_e {
        TYPE_RED_W3,

        TYPE_YELLOW,
        TYPE_RED,
        TYPE_GREEN,
        TYPE_BLUE,
    };

    void createTexPat();
    void setPressState();

    inline bool isSwitchActive(int type) { return (dInfo_c::m_instance->mWmSwitch & (1 << type)) != 0; }

    m3d::anmTexPat_c *mpAnmTexPat;
    int mSwitchType;
};