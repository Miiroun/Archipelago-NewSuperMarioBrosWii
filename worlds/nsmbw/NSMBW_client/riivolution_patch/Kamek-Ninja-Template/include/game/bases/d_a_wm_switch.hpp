#pragma once
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_info.hpp>
#include <game/bases/d_wm_demo_actor.hpp>
#include <game/mLib/m_3d/anm_chr.hpp>
#include <game/mLib/m_3d/anm_tex_pat.hpp>
#include <game/mLib/m_3d/smdl.hpp>

// @unofficial
class daWmSwitch_c : public dWmDemoActor_c {
public:
    int create();
    int doDelete();
    int execute();
    int draw();

    u32 mMapNodeIdx;
    dHeapAllocator_c mAllocator;
    m3d::smdl_c mModel;
    m3d::anmChr_c mAnmChr;
    m3d::anmTexSrt_c mAnmTexSrt;

    bool mIsPressed;
};