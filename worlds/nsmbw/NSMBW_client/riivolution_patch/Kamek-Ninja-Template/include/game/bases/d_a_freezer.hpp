#pragma once
#include <game/bases/d_actor_state.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>
#include <game/bases/d_bg_ctr.hpp>

class daFreezer_c : public dActorState_c {
public:
    dHeapAllocator_c mAllocator;
    nw4r::g3d::ResFile mResFile;
    m3d::mdl_c mModel;
    m3d::anmTexSrt_c mAnmSrt;
    u32 m_45c;
    dBg_ctr_c mBg;
    u8 mPad[16];
    u32 mFireBallState;
    u32 mSetting;
    u8 mPad2[0x818];
};