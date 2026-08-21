// Source: https://github.com/CLF78/NSMASR-v2/blob/master/game/course/tileset/grass.h
#pragma once
#include <types.h>

#define GRASSDATA "BG_grass/grass_overrides.bin"
#define GRASSSPECVERSION 1

struct GrassBinEntry_s {
    u8 mTileNum;        // Relative tileset number
    u8 mFlowerValue:4;  // 0 = none, 1 = pink, 2 = yellow, 3 = blue, 4-5 = custom, any other value = invalid
    u8 mGrassValue:4;   // 0 = none, 1 = left edge, 2-4 = middles, 5 = right edge, any other value = invalid
};

struct GrassBin_s {
    u8 mVersion;
    u8 mNumEntries;
    u8 mFlowerStyle;  // 0 = nohara, 1 = daishizen, 2+ = custom
    u8 mGrassStyle;   // 0 = nohara, 1 = nohara again, 2+ = custom
    GrassBinEntry_s mEntries[];
};

// Helper class for extra data that needs to be saved
class dGrassBinMng_c {
public:
    dGrassBinMng_c(GrassBin_s *rawData, u8 slot);
    ~dGrassBinMng_c();

    GrassBinEntry_s *getFlowerData(u16 tileNum);

    GrassBin_s *mpData;
    u8 mTileSlot;

    static dGrassBinMng_c *m_instance;
    static dGrassBinMng_c *build(GrassBin_s *rawData, u8 slot);
};
