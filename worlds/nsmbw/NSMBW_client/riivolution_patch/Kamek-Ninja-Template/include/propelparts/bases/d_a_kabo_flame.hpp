#pragma once
#include <game/bases/d_actor_state.hpp>
#include <game/mLib/m_effect.hpp>

class daKaboFlame_c : public dActorMultiState_c {
public:
    // fBase_c overrides
    virtual int create();
    virtual int execute();
    virtual int doDelete();

    void extinguish();

    STATE_FUNC_DECLARE(daKaboFlame_c, Burn);

    int mTimer;

    mEf::levelEffect_c mFlameEffect;
    mEf::levelEffect_c mFlameEffect2;
};