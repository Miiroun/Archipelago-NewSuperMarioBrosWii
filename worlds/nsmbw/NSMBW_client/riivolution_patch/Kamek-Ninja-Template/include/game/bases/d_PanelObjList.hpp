#pragma once

#include <types.h>
#include <game/mLib/m_vec.hpp>

class dPanelObjList_c {
public:
    dPanelObjList_c();
    ~dPanelObjList_c();

	void setPos(float x, float y, float z);

    u8 getUnkFlag();

    void setScaleFoot(float scale);

    void setScaleAngle(float scale, short angle);

    float getScale();

    dPanelObjList_c *mpPrev, *mpNext;
    u16 mTileNumber;
    u8 mType;
    u8 mIsChange;
    mVec3_c mPos;
    float mScale;
    s16 mAngle;
    u8 mParts;
    u32 m_20;
};