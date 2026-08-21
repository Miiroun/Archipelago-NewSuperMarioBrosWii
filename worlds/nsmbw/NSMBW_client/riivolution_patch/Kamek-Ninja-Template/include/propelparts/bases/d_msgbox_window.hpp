#pragma once

#include <game/bases/d_base.hpp>
#include <game/bases/d_lytbase.hpp>
#include <game/sLib/s_State.hpp>
#include <game/sLib/s_StateMethodUsr_FI.hpp>

// Message box window

class dMsgBoxWindow_c : public dBase_c {
public:

    enum T_PANE_e {
        T_title_00,
        T_msg_00,
        T_msgS_00,
        T_COUNT
    };

    enum P_PANE_e {
        P_button_00,
        P_COUNT
    };

    enum ANIMS_e {
        ANIM_BOX_APPEAR,
        ANIM_BOX_DISAPPEAR
    };

    dMsgBoxWindow_c();
    virtual ~dMsgBoxWindow_c();

    virtual int create();
    virtual int doDelete();
    virtual int execute();
    virtual int draw();

    void showMessage(unsigned long id, bool canCancel=true, int delay=-1, bool leavesLevel=false);
    
    sFStateMgr_c<dMsgBoxWindow_c, sStateMethodUsr_FI_c> mStateMgr;

    STATE_FUNC_DECLARE(dMsgBoxWindow_c, Wait);
    STATE_FUNC_DECLARE(dMsgBoxWindow_c, BoxAppearWait);
    STATE_FUNC_DECLARE(dMsgBoxWindow_c, ShownWait);
    STATE_FUNC_DECLARE(dMsgBoxWindow_c, BoxDisappearWait);

    LytBase_c mLayout;
    bool mIsCreated;
    bool mVisible;
    bool mCanCancel;
    int mDelay;
    bool mLeaveLevel;

    LytTextBox_c *mpTextBoxes[T_COUNT];
    nw4r::lyt::Picture *mpPicturePanes[P_COUNT];

    static dMsgBoxWindow_c *m_instance;
    static bool m_isShowing;
};