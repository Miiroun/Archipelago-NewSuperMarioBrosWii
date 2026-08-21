#pragma once

#include <game/bases/d_lytbase.hpp>

/// @unofficial
class dPreGameLyt_c {
public:
    enum T_PANE_e {
        T_minus_00,
        T_world_00, T_worldNum_00,
        T_pictureFont_00, T_corseNum_00,
        T_remainder_00, T_remainder_01, T_remainder_02, T_remainder_03,
        T_remainder_10, T_remainder_11, T_remainder_12, T_remainder_13,
        T_x_00, T_x_01, T_x_02, T_x_03,
        T_x_10, T_x_11, T_x_12, T_x_13,
        T_x_00_o, T_x_10_o,
        T_otasukePlay_00, T_otasukePlay_01,
        T_recommend_00,
        T_remainder_00_o, T_remainder_10_o,
        T_COUNT
    };

    enum P_PANE_e {
        P_W1_00, P_W2_00, P_W3_00, P_W4_00, P_W5_00, P_W6_00, P_W7_00, P_W8_00, P_W9_00,
        P_coin_00, P_free_00,
        P_batB_03, P_batB_02, P_batB_01, P_batB_00, P_bat_00,
        P_batB_13, P_batB_12, P_batB_11, P_batB_10, P_bat_01,
        P_batB_23, P_batB_22, P_batB_21, P_batB_20, P_bat_02,
        P_batB_33, P_batB_32, P_batB_31, P_batB_30, P_bat_03,
        P_luijiIcon_00_o, P_luijiIcon_10_o,
        P_coinStage_00,
        P_COUNT
    };

    enum N_PANE_e {
        N_mario_00, N_luiji_00, N_kinoB_01, N_kinoY_00,
        N_zankiPos_00, N_zankiPos_01, N_zankiPos_02, N_zankiPos_03, N_zanki_00,
        Null_battPos1P, Null_battPos2P, Null_battPos3P, Null_battPos4P,
        N_batt_00, N_batt_01, N_batt_02, N_batt_03, N_batt,
        N_otasukePlay_00,
        N_COUNT
    };

    LytBase_c mLayout;
    nw4r::lyt::Pane* mpRootPane;

    nw4r::lyt::TextBox *mpTextBoxes[T_COUNT];
    nw4r::lyt::Picture *mpPicturePanes[P_COUNT];
    nw4r::lyt::Pane *mpNullPanes[N_COUNT];

    bool mHasLoadedLayout;
    u8 m_2e1;
    bool mIsActive;
    bool mSuperGuideDispDone;
    int mPhase;
    u32 m_2e8;
    int mCountdown;
    int mNumPlayers;
    int mBatteryLevels[4];
    int mTimer;
};