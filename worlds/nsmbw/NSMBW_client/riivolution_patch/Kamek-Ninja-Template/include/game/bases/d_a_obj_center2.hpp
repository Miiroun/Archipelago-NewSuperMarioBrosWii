#pragma once
#include <game/bases/d_actor_state.hpp>

class daObjCenter2_c : public dActorState_c {
public:
    u32 mRotationDelta;
    u32 mPad;
    mAng mRotationSpeed;
    mAng m_3da;
    mAng m_3dc;
    u8 m_3de;
    bool mHasPlayedCoinSound;
    u8 mRotationMode;
    bool mClockwise;
    u8 mRotationIdx;
    u8 m_3e3;
    u8 mPad2[3];
    u8 m_3e7;
};