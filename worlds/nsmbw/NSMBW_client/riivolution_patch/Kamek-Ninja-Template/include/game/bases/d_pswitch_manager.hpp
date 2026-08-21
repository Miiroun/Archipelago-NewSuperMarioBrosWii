#pragma once
#include <types.h>

class dPSwManager_c {
public:
    enum SwType_e {
        P_SWICH,
        Q_SWICH,

        // New switch types
        Y_SWICH,
        R_SWICH,
        G_SWICH,
        B_SWICH
    };
    
    dPSwManager_c();
    virtual ~dPSwManager_c();

    void initialize();
    void execute();
    void ProcMain();
    void finalize();

    u32 checkSwitch(SwType_e);
    bool checkMove();
    void onSwitch(SwType_e, int);
    void offSwitch(SwType_e);
    void setTimer(SwType_e, int);

    u32 mSwitchState;
    int mSwitchTimers[3];

    static dPSwManager_c *ms_instance;
};