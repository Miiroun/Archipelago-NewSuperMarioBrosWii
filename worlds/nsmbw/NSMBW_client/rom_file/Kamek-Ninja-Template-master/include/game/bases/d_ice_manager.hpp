#pragma once

#include <game/bases/d_actor.hpp>

struct dIceInfo {
    ~dIceInfo();
    
    u32 mFlags;
    mVec3_c mPos;
    mVec3_c mScale;
    float mPad[8];
};

class dIceMng_c {
public:
    dIceMng_c(dActor_c *owner);
    ~dIceMng_c();

    bool createIce(dIceInfo*, int);
    void setIceStatus(int, int, int);

    u8 mPad1[0xc];
    int m_0c;
    u8 mPad2[0x8];
    int m_18;
    u8 mPad3[0x14];
    int mPlrNo;
    u8 mPad4[0x38];
};