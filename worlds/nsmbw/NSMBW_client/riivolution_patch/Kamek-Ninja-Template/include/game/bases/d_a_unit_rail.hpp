#pragma once
#include <game/bases/d_base_actor.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/mLib/m_3d/smdl.hpp>

class daUnitRail_c : public dBaseActor_c {
public:
    dHeapAllocator_c mAllocator;
    m3d::smdl_c mModel;
    bool mInserted;
};
