#pragma once
#include <types.h>

class dSwitchFlagMng_c {
public:
    void set(u32 eventId, int timer, bool activateEvent, bool resetEvent, bool isTimed, bool musicInterruption);

    static inline bool dSwitchFlagMng_c::checkEvent(u8 event) {return (m_instance->mFlags & (u64)(1 << event));}

    u64 mFlags;
    u8 mPad[0x6C8];

    static dSwitchFlagMng_c* m_instance;
};