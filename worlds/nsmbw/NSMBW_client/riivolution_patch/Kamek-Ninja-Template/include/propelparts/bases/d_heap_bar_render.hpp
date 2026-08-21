#pragma once
#include <game/mLib/m_3d.hpp>
#include <lib/egg/core/eggHeap.h>

// Heap bar rendering

class dHeapBarRender_c {
public:
    dHeapBarRender_c() { }

    void draw();

    void setupGX();
    void endGX();

    void drawHeapBar(int freeSize, int heapSize, int index, const char *name);

    static dHeapBarRender_c m_instance;

    static const EGG::Heap *sc_heapList[];
    static const float sc_heapPosY[];
    static const u32 sc_heapColors[];
    static const u32 sc_stopColors[];
};