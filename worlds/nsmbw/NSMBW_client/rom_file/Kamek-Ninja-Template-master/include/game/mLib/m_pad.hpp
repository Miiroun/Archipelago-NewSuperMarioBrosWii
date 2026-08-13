#pragma once

#include <egg/core/eggController.h>

namespace mPad {

    enum CH_e {
        MPAD_CH_0,
        MPAD_CH_1,
        MPAD_CH_2,
        MPAD_CH_3
    };

    #define PAD_CHAN_COUNT 4

    extern EGG::CoreController* g_core[PAD_CHAN_COUNT];

    extern EGG::CoreControllerMgr* g_padMg;

    extern CH_e g_currentCoreID;

    extern EGG::CoreController* g_currentCore;

    extern bool g_IsConnected[PAD_CHAN_COUNT];

    extern u32 g_PadFrame;

    void create();
    void beginPad();
    void endPad();
    int getBatteryLevel_ch(CH_e chan); // @unofficial
    void setCurrentChannel(CH_e chan);
    void clearWPADInfo(CH_e chan);
    int getWPADInfoAsync(CH_e chan);
} // namespace mPad