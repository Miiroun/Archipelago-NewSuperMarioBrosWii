#include <types.h>

class PauseManager_c {
public:
    void* vtable;

    u32 mPtmfIndex;
    u32 mSelection;  // 0 for Continue, 1 for Quit
    u32 mPlayerNum;  // player who pressed pause

    u32 m_10; // never read, only stored as 0 once?
    u32 mCancelMenuSelection; // 0 for Cancel, 1 for OK

    u8 mFlags; // &1 = in pause menu, &2 = pausing disabled, &4 = ??
    bool mButtonAnimPlaying;
    bool mExitingMenu;
    bool mWillDisplay;
    bool m_1c; // stuff with otasukeInfo i think
    bool mDisablePause; // use this to disable pausing at will, since dScStage_c turns off flag 2 every frame
    // 2 bytes padding

    static PauseManager_c* m_instance;
    static bool m_Pause;
    static bool m_Created;
    static bool m_OtasukeAfter;
};