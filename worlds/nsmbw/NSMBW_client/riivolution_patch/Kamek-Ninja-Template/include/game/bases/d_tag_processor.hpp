#pragma once
#include <game/bases/d_message.hpp>

class TagProcessor_c {
public:
    TagProcessor_c();
    ~TagProcessor_c();

    int MsgIDSet(MsgRes_c *, unsigned long, unsigned long);

    u8 mPad[0xc0];
    u8 mFontIndex;
    u8 mPad2[4];
    u8 mIconFontID; // @unofficial
    u8 mPad3[2];
};