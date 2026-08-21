#pragma once
#include <game/bases/d_base.hpp>

enum UNIT_NUM_e {
    UNIT_0 = 0,
    UNIT_GRASS_L = 416, ///< Grass (left edge)
    UNIT_GRASS_C1, ///< Grass (center 1)
    UNIT_GRASS_C2, ///< Grass (center 2)
    UNIT_GRASS_C3, ///< Grass (center 3)
    UNIT_GRASS_R, ///< Grass (right edge)
    UNIT_FLOWER_1 = 432, ///< Yellow flower
    UNIT_FLOWER_2, ///< Red flower
    UNIT_FLOWER_3, ///< Blue flower
    UNIT_GRASS_FLOWER_1 = 448, ///< Grass with yellow flower
    UNIT_GRASS_FLOWER_2, ///< Grass with red flower
    UNIT_GRASS_FLOWER_3, ///< Grass with blue flower
};

#define UNIT_IS_GRASS(x) (\
    x == UNIT_GRASS_L || \
    x == UNIT_GRASS_C1 || x == UNIT_GRASS_C2 || x == UNIT_GRASS_C3 || \
    x == UNIT_GRASS_R \
)

#define UNIT_IS_FLOWER(x) (\
    x == UNIT_FLOWER_1 || \
    x == UNIT_FLOWER_2 || \
    x == UNIT_FLOWER_3 \
)

#define UNIT_IS_GRASS_FLOWER(x) (\
    x == UNIT_GRASS_FLOWER_1 || \
    x == UNIT_GRASS_FLOWER_2 || \
    x == UNIT_GRASS_FLOWER_3 \
)

struct dBGRender {
    u8 mPad[0xC00];
    u8 *mObjData;
    u8 m_c04, m_c05; // Extracted from UnitHeadData, maybe row and column?
    u16 m_c06, m_c08; // Unused??
    u16 mBlockNumber;
    u16 mCurrX, mCurrY;
    u16 mCurrTile;
    u16 mObjDataOffset, mObjType, mObjX, mObjY, mObjWidth, mObjHeight;
    u16 mTileNumberWithinBlock, mAreaID;
};

struct dBGBuffer {
    u16 mTiles[0x100];
};

class dBgUnit_c {
public:
    virtual ~dBgUnit_c();

    dBGBuffer *mAllocatedBlocks[257];
    u8 mUsedIDs[2048];
    u16 mNextID;
    // 2 bytes padding
    u32 mPa0_id, mPa1_id, mPa2_id, mPa3_id; // Only set for Nintendo tilesets and used for randomization
    u32 mLayerId, mAreaId;
    EGG::FrmHeap *mpHeap;
    bool mShouldRandomize;
    // 3 bytes padding

    u16 *GetBuffPos(u16, u16, int*, bool); // Last param is unused

    void randomiseHorzVert(dBGRender *render, u16 *tileArray, int arrayLength, int slot);
    void randomiseHorz(dBGRender *render, u16 *tileArray, int arrayLength, int slot);
    void randomiseVert(dBGRender *render, u16 *tileArray, int arrayLength, int slot);

    static dBgUnit_c *create(dBgUnit_c *unit, EGG::Heap *heap, int area, int layer);
};

struct dBgData_c {
    u32 mLayer0;
    u32 mLayer1;
    u32 mLayer2;
};


class dBgGlobal_c {
public:
    virtual ~dBgGlobal_c();
    char *getEnvironment(int, int);
    dBgUnit_c *GetBgUnitP(int, int);

    dBgData_c mData[100];

    static dBgGlobal_c *ms_pInstance;
};