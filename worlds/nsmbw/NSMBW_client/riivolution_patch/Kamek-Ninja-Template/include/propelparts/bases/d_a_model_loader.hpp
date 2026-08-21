#pragma once
#include <game/bases/d_actor.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>

// The real model loader
class daModelLoader_c : public dActor_c {
public:
    enum SOFT_LIGHT_TYPE_e {
        SOFT_LIGHT_PLAYER,
        SOFT_LIGHT_ENEMY,
        SOFT_LIGHT_MAP,
        SOFT_LIGHT_MAPOBJ,
        SOFT_LIGHT_BOSS,
        SOFT_LIGHT_ITEM
    };

    enum ANM_VALID_FLAG_e {
        ANM_CHR_VALID = BIT_FLAG(0),
        ANM_CLR_VALID = BIT_FLAG(1),
        ANM_PAT_VALID = BIT_FLAG(2),
        ANM_SRT_VALID = BIT_FLAG(3),
        ANM_VIS_VALID = BIT_FLAG(4)
    };

    virtual int create();
    virtual int execute();
    virtual int draw();

    dHeapAllocator_c mAllocator;
    nw4r::g3d::ResFile mRes;
    m3d::mdl_c mModel;

    m3d::anmChr_c mAnmChr;
    m3d::anmMatClr_c mAnmClr;
    m3d::anmTexPat_c mAnmPat;
    m3d::anmTexSrt_c mAnmSrt;
    m3d::anmVis_c mAnmVis;

    int mBankNo;
    int mBrresNo;
    SOFT_LIGHT_TYPE_e mSoftLightType;
    m3d::playMode_e mPlaymode;
    u8 mValidAnms;
    float mAnmRate;
    float mModelScale;
};