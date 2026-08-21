#pragma once

#include <types.h>
#include <game/mLib/m_vec.hpp>
#include <lib/egg/core/eggHeap.h>

class dGameKeyCore_c {
public:
    /// @unofficial
    enum EXTENSION_TYPE_e {
        EXTENSION_NONE = 0, ///< No Wii remote extension is connected.
        EXTENSION_NUNCHUK, ///< The nunchuck controller is connected.
        EXTENSION_UNKNOWN = 3, ///< It has not been checked yet whether an extension is connected.
    };

    u32 getAccVerticalAngleX();

    void *m_00; // vtable
    int mIndex;
    EXTENSION_TYPE_e mAttachedExtension;
    u32 mHoldButtons, mPrevHoldButtons; ///< The buttons currently held down.
    u32 mDownButtons, mPrevDownButtons; ///< The buttons currently pressed down.
    u32 mTriggeredButtons; ///< The buttons newly pressed down.
    u8 mPad[0x14];
    mVec3_c mAcc, mPrevAcc;
    mVec2_c mAccVertX, mPrevAccVertX;
    mVec2_c mAccVertY, mPrevAccVertY;
    mVec2_c mAccVertZ;
    mVec2_c mAngle, mPrevAngle;
    float mMoveDist, mPrevMoveDist;
    bool mIsShaking;
    u8 m_8d;
    u16 mTiltAmount;
    s8 mShakeTimers[3];
    u8 m_93;
};

class dGameKey_c {
public:
    virtual ~dGameKey_c();

    void read();

    short getAccVerticalAngleX(int plNo) {
        return mRemocon[plNo]->getAccVerticalAngleX() / 65536;
    }

    // [These two functions must have different types to match]
    bool checkButtonsDown(s32 i) {
        return mRemocon[i]->mDownButtons != 0;
    }

    bool checkShaking(u32 i) {
        return mRemocon[i]->mIsShaking != 0;
    }

    static void createInstance(EGG::Heap *heap);

    dGameKeyCore_c *mRemocon[4];

    static dGameKey_c *m_instance;
};
