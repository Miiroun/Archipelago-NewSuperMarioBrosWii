#pragma once

#include <lib/egg/core/eggHeap.h>
#include <nw4r/ut.h>

class dFontMng_c {
public:
    static bool create(EGG::Heap *heap);
    static void *getResFontData(const char *name);
    static u8 getResFontIndex(const char *name);
    static nw4r::ut::Font *getFont(int index);

    nw4r::ut::ResFont mResFonts[4];
    dDvd::loader_c mFontLoaders[4];
    nw4r::ut::BinaryFileHeader *mpFontFiles[4];
};

extern const dFontMng_c l_dFontMng_obj;