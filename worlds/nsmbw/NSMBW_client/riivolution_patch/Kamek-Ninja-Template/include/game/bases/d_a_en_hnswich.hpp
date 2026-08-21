#pragma once

#include <game/bases/d_enemy.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>
#include <lib/egg/core/eggEffect.h>
#include <game/bases/d_bg_ctr.hpp>

class daEnHnswich_c : public dEn_c {
public:
    dHeapAllocator_c mAllocator;
    nw4r::g3d::ResFile mRes;
    m3d::mdl_c mModel;
    m3d::anmChr_c mAnmChr;
    m3d::anmTexSrt_c mAnmTexSrt;
    m3d::anmMatClr_c mAnmMatClr;
    EGG::Effect mEffect;
    u8 mPad[192];
    dBg_ctr_c mBg;
    u8 mPad2[84];
    int mSwitchType;
    u8 mPad3[32];
};