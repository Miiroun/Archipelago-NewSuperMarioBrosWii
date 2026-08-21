#pragma once

#include <types.h>
#include <game/mLib/m_vec.hpp>

class dActor_c;
class dBc_c;
class dRide_ctr_c;

class dRc_c {
public:
    dRc_c();
    virtual ~dRc_c();

    void set(dActor_c *actor, u8 lineKind);
    void setRide(dRide_ctr_c *);

    void clrLink();
    void chkLink();

    dActor_c *mpOwner;
    mVec3_c *mpOwnerPos;
    dRc_c *mpNext;
    dRide_ctr_c *mpRide[2];
    dBc_c *mpBc;
    float m_1c[4];
    short mRotation;
    u8 mLineKind;
    u8 mRideType;
    u8 mFlags;
    u8 m_31;
    u8 mLayer;
};

class dRide_ctr_c {
public:
    dRide_ctr_c();
    virtual ~dRide_ctr_c();

    virtual void calc();
    virtual void revisePos();
    virtual void _vf14();

    void entry();

    dActor_c* mpOwner;

    dRide_ctr_c* mpNext;
    dRide_ctr_c* mpPrev;

    dRc_c* mpLinkedRc;

    mVec2_c mRight;
    mVec2_c mLeft;
    mVec2_c mLength;
    mVec2_c mLastLeft;

    float mLineLength;
    float mLeftYDelta;

    u32 mFlags;
    s16 mRotation;
    u8 mType; // 0 = dRideRoll_c, 2 = dRide2Point_c, 4 = dRideCircle_c

    bool m_43;
    bool mLinked;

    u8 mChainlinkMode;
    bool m_46;
    u8 mSubType;
    u8 m_48; // unused?
    u8 m_49; // unused?
    u8 mLayer;
    u8 m_4b; // unused?

    static dRide_ctr_c* mEntryN;
    static dRide_ctr_c* mEntryB;
};

class dRideRoll_c : public dRide_ctr_c {
public:
    dRideRoll_c();
    virtual ~dRideRoll_c();

    virtual void calc();

    void set(dActor_c*, float, float, float, float, float, short, u8, mVec3_c*);
    void set(dActor_c*, mVec2_c, float, float, float, short, u8, mVec3_c*);

    mVec3_c mCenterOffset;
    mVec3_c mSize;
};

class dRide2Point_c : public dRide_ctr_c {
public:
    dRide2Point_c();
    virtual ~dRide2Point_c();

    virtual void calc();

    mVec2_c mLeft;
    mVec2_c mRight; 
};

class dRideCircle_c : public dRide_ctr_c {
public:
    dRideCircle_c();
    virtual ~dRideCircle_c();

    virtual void calc();
    virtual void revisePos();
    virtual void _vf14();

    mVec2_c mCenterOffset;
    mVec2_c mLeftOffset;
    mVec2_c mTopMaybe;
    float mRadius;

    s32 mRightAngleOffset;
    s32 mLeftAngleOffset;
    s16 mPrevRotation;

    bool m_72; // ??
    bool m_73; // ??
};
