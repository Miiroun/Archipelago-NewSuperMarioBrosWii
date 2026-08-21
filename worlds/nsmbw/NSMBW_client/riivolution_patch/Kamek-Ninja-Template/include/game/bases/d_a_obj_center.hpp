#pragma once
#include <game/bases/d_actor.hpp>

class daObjCenter_c : public dActor_c {
public:
    u16 m_392;
    mAng mOffset;
    mAng mDisplacement;
    mAng mSwingArc;
    u8 mReverse;
    u8 mCounter;
    u8 mRotationIdx;
    u8 mPad[3];
};