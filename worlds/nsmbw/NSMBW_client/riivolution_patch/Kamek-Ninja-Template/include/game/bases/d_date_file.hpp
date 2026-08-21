#pragma once

#include <game/bases/d_base.hpp>
#include <game/bases/d_lytbase.hpp>
#include <game/mLib/m_effect.hpp>
#include <game/sLib/s_State.hpp>
#include <game/sLib/s_StateMethodUsr_FI.hpp>

/// @unofficial
class dDateFile_c : public dBase_c {
public:
    void setFileNum();

    enum N_PANE_e {
        N_dateFile_00, N_dateFile_01,
        N_NewFile_00, N_save,
        N_COUNT
    };

    enum W_PANE_e {
        W_select_00, W_shadow_00,
        W_COUNT
    };

    enum T_PANE_e {
        T_worldNumber_00, T_worldNumber_01,
        T_x_00, T_zanki_00,
        T_fileNumber_00, T_fileNumber_01,
        T_NewdateFile_00, T_NewdateFileS,
        T_COUNT
    };

    enum P_PANE_e {
        P_Star_00, P_Star_01, P_Star_02, P_Star_03, P_Star_04,
        P_Star_05, P_Star_06, P_Star_07, P_Star_08, P_Star_09,
        P_COUNT
    };

    enum ACTION_e {
        None,
        OnFile,
        HitFile,
        SelectCopy,
        OffFile,
        InitialSetup,
        StartSelect,
        CancelSelect,
    };

    u32 m_70;
    LytBase_c mLayout;
    mEf::levelEffect_c mStarEffects[10];
    sFStateMgr_c<dDateFile_c, sStateMethodUsr_FI_c> mStateMgr;
    int mAction;
    nw4r::lyt::Pane *mpRootPane;

    nw4r::lyt::Pane *mpNullPanes[N_COUNT];
    nw4r::lyt::Window *mpWindowPanes[W_COUNT];
    LytTextBox_c *mpTextBoxes[T_COUNT];
    nw4r::lyt::Picture *mpPicturePanes[P_COUNT];
    
    float m_E40;
    int mFileNum;
    bool mHasLoadedLayout;
    bool mIsVisible;
    bool mNewFile;
    bool mDispBalloon;
    bool mUpdateInfo;
    bool mAnimActive;
    bool mExitBalloon;
    bool mDrawStarEffects;
    bool mSkipEffectDraw;
    bool mPad[3];
};