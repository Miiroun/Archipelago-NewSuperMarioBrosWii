#pragma once
#include <game/bases/d_actor_state.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>
#include <game/sLib/s_State.hpp>
#include <game/mLib/m_effect.hpp>

class daBombProjectile_c : public dActorMultiState_c {
public:
    // fBase_c overrides
    virtual int create();
    virtual int execute();
    virtual int draw();

    // dBaseActor_c overrides
    virtual void finalUpdate();

    // dActor_c overrides
    virtual bool setEatSpitOut(dActor_c *eatingActor);

    void explodeTiles();
    dActor_c *getParent();
    bool getPlayerDirection();

    STATE_FUNC_DECLARE(daBombProjectile_c, ThrowWait);
    STATE_FUNC_DECLARE(daBombProjectile_c, EatWait);
    STATE_FUNC_DECLARE(daBombProjectile_c, Throw);
    STATE_FUNC_DECLARE(daBombProjectile_c, Explode);

    dHeapAllocator_c mAllocator;

    nw4r::g3d::ResFile mRes;
    nw4r::g3d::ResMdl mResMdl;
    m3d::mdl_c mModel;
    nw4r::g3d::ResAnmClr mResClr;
    m3d::anmMatClr_c mAnmClr;

    mEf::levelEffect_c mIgniteEffect;

    fBaseID_e mOwnerID;

    bool mReadyToThrow;
    bool mShouldExplode;
    bool mPlayerBomb;
    int mExplosionTimer;

    mVec3_c mRootPos;
};