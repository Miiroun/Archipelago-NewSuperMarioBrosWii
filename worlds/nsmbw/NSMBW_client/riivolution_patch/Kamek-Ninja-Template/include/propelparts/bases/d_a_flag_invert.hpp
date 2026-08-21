#pragma once
#include <game/bases/d_actor.hpp>

class daFlagInvert_c : public dActor_c {
public:
    // fBase_c overrides
    virtual int execute();

    bool mPreviousFlagState;
};