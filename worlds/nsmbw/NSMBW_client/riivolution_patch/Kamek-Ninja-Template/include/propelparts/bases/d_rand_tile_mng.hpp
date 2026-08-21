// Source: https://github.com/CLF78/NSMASR-v2/blob/master/game/course/tileset/rand.h
#pragma once
#include <types.h>

#define RANDDATA "BG_rand/rand_overrides.bin"
#define RANDSPECVERSION 1

struct RandTileBinEntry_s {
    enum NORMAL_RAND_e {
        NORMAL_RAND_NONE,
        NORMAL_RAND_HORI,
        NORMAL_RAND_VERT,
        NORMAL_RAND_BOTH,
    };

    enum SEPCIAL_RAND_e {
        SPECIAL_RAND_NONE,
        SPECIAL_RAND_VDOUBLETOP,
        SPECIAL_RAND_VDOUBLEBOTTOM,
        SPECIAL_RAND_HDOUBLELEFT,
        SPECIAL_RAND_HDOUBLERIGHT,
    };

    u8 mTileNum;         // Tile to be randomized, relative
    u8 mNormalType;      // See enum
    u8 mSpecialType;     // See enum
    u8 mArrayLen;        // Length of tile list, due to the possibility of tiles being 00
    u32 mTileArrayOffs;  // Offset to tile list in u16 format, relative to start of file
};

struct RandTileBin_s {
    u8 mVersion;
    u8 mNumEntries;
    // 2 bytes padding
    RandTileBinEntry_s mEntries[];
    // u16 random tile arrays follow
};

class dRandTileMng_c {
public:
    dRandTileMng_c(int area);
    ~dRandTileMng_c();

    RandTileBin_s *mpRandData[4];

    static dRandTileMng_c *m_instance;
    static dRandTileMng_c *build(int area);
};