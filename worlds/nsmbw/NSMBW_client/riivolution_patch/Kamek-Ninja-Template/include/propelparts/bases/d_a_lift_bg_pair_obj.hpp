#pragma once
#include <propelparts/bases/d_a_lift_bg_base.hpp>

class daLiftBgPairObj_c : public daLiftBgBase_c {
public:
    virtual bool initMovement();
    virtual void executeMovement();

    fBase_c *findController();

    fBaseID_e mControllerID;
    mVec2_c mOrigin;

    bool mIsHidden;

    // Settings
    u8 mPairObjIdx;
};