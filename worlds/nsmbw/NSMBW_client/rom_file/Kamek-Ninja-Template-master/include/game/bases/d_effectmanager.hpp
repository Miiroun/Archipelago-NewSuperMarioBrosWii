#pragma once

#include <game/mLib/m_vec.hpp>
#include <lib/egg/core/eggHeap.h>

class EffectManager_c {
public:
    static void create(EGG::Heap *heap1, EGG::Heap *heap2);
    static void setResource(void *breff, void *breft);
    static void SetIceBallMissshitEffect(mVec3_c *);
    static void calcGroupForWm();
    static void calcGroup();

    static bool m_firstCalc;
};
