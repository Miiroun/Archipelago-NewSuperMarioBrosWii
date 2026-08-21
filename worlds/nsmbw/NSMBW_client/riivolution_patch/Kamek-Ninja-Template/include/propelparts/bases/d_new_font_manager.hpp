#pragma once
#include <game/bases/d_font_manager.hpp>

class dNewFontMng_c {
public:
    dNewFontMng_c();

    static int create(EGG::Heap *pHeap);

    static nw4r::ut::BinaryFileHeader *getResFontData(const char *name);
    static u8 getResFontIndex(const char *name);
    static nw4r::ut::ResFont *getFont(int index);

    nw4r::ut::ResFont *mpFonts;
    dDvd::loader_c *mpFontLoaders;
    nw4r::ut::BinaryFileHeader **mpFontDatas;

    static dNewFontMng_c *m_instance;
    static const char *FONT_NAME_TBL[];
};