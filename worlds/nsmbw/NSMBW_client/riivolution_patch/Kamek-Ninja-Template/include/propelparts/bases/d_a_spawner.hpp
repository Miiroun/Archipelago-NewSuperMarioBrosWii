#pragma once
#include <game/bases/d_actor.hpp>

// Actor that spawns another actor when a target event is triggered.

class daSpawner_c : public dActor_c {
public:
    daSpawner_c() {};
    ~daSpawner_c() {};

    virtual int execute();

    u8 mEventID;
    ProfileName mChildProfileID;
    bool mHasChild;
    u32 mTimer;
    fBaseID_e mChildID;
};