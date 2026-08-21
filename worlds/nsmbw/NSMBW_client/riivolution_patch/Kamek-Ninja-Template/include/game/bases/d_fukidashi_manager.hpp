#pragma once

#include <game/bases/d_lytbase.hpp>
#include <game/sLib/s_State.hpp>

class dfukidashiInfo_c {
public:
    virtual ~dfukidashiInfo_c();

    LytBase_c mLayout;
    sFStateMgr_c<dfukidashiInfo_c, sStateMethodUsr_FI_c> mStateMgr;
    mVec3_c *mPlayerPos;
    mVec3_c mPosOffset;
    float m_1e8;
    float m_1eC;
    int mControllerType;

    nw4r::lyt::Pane *mRootPane;
    u32 m_1f8;
    nw4r::lyt::Picture *mpPicturePanes[6];
    nw4r::lyt::TextBox *mpTextBoxPanes[2];

    int mPlayer;
    int mObjectType;
    u32 m_224;
    u32 m_228;
    int mSomeAnimID;
    u32 m_230;
    int mBasedOnObjectType;
    bool mLayoutLoaded;
    bool mVisible;
    u8 mPad[2];

    static float
        c_MARIO_NORMAL_OFFSET_X,    c_MARIO_NORMAL_OFFSET_Y,
        c_MARIO_SUPER_OFFSET_X,     c_MARIO_SUPER_OFFSET_Y,
        c_MARIO_FIRE_OFFSET_X,      c_MARIO_FIRE_OFFSET_Y,
        c_MARIO_MAME_OFFSET_X,      c_MARIO_MAME_OFFSET_Y,
        c_MARIO_PROPEL_OFFSET_X,    c_MARIO_PROPEL_OFFSET_Y,
        c_MARIO_PENGUIN_OFFSET_X,   c_MARIO_PENGUIN_OFFSET_Y,
        c_MARIO_ICE_OFFSET_X,       c_MARIO_ICE_OFFSET_Y,
        c_LUIGI_NORMAL_OFFSET_X,    c_LUIGI_NORMAL_OFFSET_Y,
        c_LUIGI_SUPER_OFFSET_X,     c_LUIGI_SUPER_OFFSET_Y,
        c_LUIGI_FIRE_OFFSET_X,      c_LUIGI_FIRE_OFFSET_Y,
        c_LUIGI_MAME_OFFSET_X,      c_LUIGI_MAME_OFFSET_Y,
        c_LUIGI_PROPEL_OFFSET_X,    c_LUIGI_PROPEL_OFFSET_Y,
        c_LUIGI_PENGUIN_OFFSET_X,   c_LUIGI_PENGUIN_OFFSET_Y,
        c_LUIGI_ICE_OFFSET_X,       c_LUIGI_ICE_OFFSET_Y,
        c_KINOPIO_NORMAL_OFFSET_X,  c_KINOPIO_NORMAL_OFFSET_Y,
        c_KINOPIO_SUPER_OFFSET_X,   c_KINOPIO_SUPER_OFFSET_Y,
        c_KINOPIO_FIRE_OFFSET_X,    c_KINOPIO_FIRE_OFFSET_Y,
        c_KINOPIO_MAME_OFFSET_X,    c_KINOPIO_MAME_OFFSET_Y,
        c_KINOPIO_PROPEL_OFFSET_X,  c_KINOPIO_PROPEL_OFFSET_Y,
        c_KINOPIO_PENGUIN_OFFSET_X, c_KINOPIO_PENGUIN_OFFSET_Y,
        c_KINOPIO_ICE_OFFSET_X,     c_KINOPIO_ICE_OFFSET_Y;
};

class dfukidashiManager_c {
public:
    char pad[0x381];
    dfukidashiInfo_c mInfos[4];

    static dfukidashiManager_c *m_instance;
};
