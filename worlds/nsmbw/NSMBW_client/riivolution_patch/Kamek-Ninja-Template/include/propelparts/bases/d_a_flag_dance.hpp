#pragma once
#include <game/bases/d_actor.hpp>

class daFlagDance_c : public dActor_c {
public:
    // fBase_c overrides
    virtual int create();
    virtual int execute();

    u8 mDanceType;
};