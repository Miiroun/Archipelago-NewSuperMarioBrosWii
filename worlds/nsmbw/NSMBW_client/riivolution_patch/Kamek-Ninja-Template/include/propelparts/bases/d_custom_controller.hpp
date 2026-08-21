#pragma once
#include <game/bases/d_remocon_manager.hpp>
#include <game/bases/d_s_stage.hpp>

typedef struct CONTROLLER_TYPE_e {
    enum Value {
        WIIMOTE,
        NUNCHUCK,
        INVALID,
        NONE,
        
        //NEW
        CLASSIC,
        GAMECUBE,
        GUITAR
    };
};

// These aren't officially a part of WPAD
#define WPAD_DEV_GAMECUBE               30 // Gamecube controller
#define WPAD_DEV_GCN_FUTURE             31 // Invalid gc device

// Created on game boot and stays in memory constantly until game shutdown

#define CCFLAG_HAS_CUSTOM           0x01
#define CCFLAG_NO_AUTOCONNECT       0x02
#define CCFLAG_HAS_AUTOCONNECT      0x04

#define CCFLAG_IS_PROCON            0x08
#define CCFLAG_NO_ACC               0x10
#define CCFLAG_NO_WIIMOTE           0x20

struct dPADInfo {
    u32 mHold, mTrig, mRelease;
    Vec2 mStick;
    Vec2 mSubstick;
    float mLTrigger, mRTrigger;
};

struct dCustomControllerInfo {
    dCustomControllerInfo() : mControllerType(CONTROLLER_TYPE_e::NONE), mFlags(0), mLastPressed(0), mPadInfo() {};

    u32 mControllerType;
    u8 mFlags;
    u32 mLastPressed;
    dPADInfo mPadInfo;
};

typedef struct GCC_TYPE_e {
    enum Value {
        INVALID = -1,
        NONE = 0,
        STANDARD = 1,
    };
};

class dCustomController_c {
public:
    dCustomController_c() : mControllers(), mIsHBMOpen(false) {};

    void mapClassicButtons(EGG::CoreController *controller, int controllerID);
    void mapGameCubeButtons(EGG::CoreController *controller, int controllerID);
    void mapGuitarButtons(EGG::CoreController *controller, int controllerID);
    void clearWiimotedata(KPADStatus *kStatus, bool disablePointer = true);

    u32 checkForGCConnection(int channel);
    void setGamecubeDevType(int channel);

    static void makeInstance();
    
    static void setPadInfo();

    static void changeRemoconMgrState(dRemoconMng_c::dConnect_c::dExtension_c *self, u32 extension);
    static void shakeController(int channel);

    dCustomControllerInfo mControllers[4];
    bool mIsHBMOpen;

    static dCustomController_c *m_instance;
    static PADStatus saPadStatus[4];
};

inline dCustomControllerInfo *getCustomController(int channel, bool accountForDemo = false) {
    if (accountForDemo) {
        if (dScStage_c::m_instance->m_replayPlay_p[channel] == nullptr) {
            return &dCustomController_c::m_instance->mControllers[channel];
        } else {
            return NULL;
        }
    }
    return &dCustomController_c::m_instance->mControllers[channel];
}