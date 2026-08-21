#pragma once
#include <game/mLib/m_allocator.hpp>
#include <game/mLib/m_vec.hpp>

class dBgActorManager_c {
public:
    struct BgObjName_t {
        ~BgObjName_t();
        
        u32 mTileNum;
        u16 mProfileId;
        u8 m_06;
        u8 m_07;
        mVec3_c mOffset;
        mVec2_c mScale;
        u32 mParam;
    };

    class BgObj_c {
    public:
        u16 mUniqueId;
        u16 mX, mY;
        u8 mLayer;
        u32 mProfileId;
    };

    virtual ~dBgActorManager_c();

    mHeapAllocator_c m_allocator;
    mVec3_c mScreenBL;
    mVec3_c mScreenTR;
    BgObj_c *mpObjects;
    int mCount;
    int mType;
};

extern dBgActorManager_c::BgObjName_t *l_pRailList;
