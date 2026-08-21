#pragma once

#include <game/bases/d_enemy.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>
#include <game/bases/d_effect.hpp>

class daEnHeihoLarge_c : public dEn_c {
public:
    enum HEIHO_LARGE_TYPE_e {
        HEIHO_LARGE,
        HEIHO_GIANT,
        HEIHO_MEGA,
    };

    virtual int create();
    virtual int execute();
    virtual int draw();

    virtual void finalUpdate();

    virtual void Normal_VsEnHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsPlHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsYoshiHitCheck(dCc_c *self, dCc_c *other);

    virtual bool hitCallback_Shell(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_Fire(dCc_c *self, dCc_c *other);
    virtual bool hitCallback_Ice(dCc_c *self, dCc_c *other);

    virtual void setDeathInfo_Quake(int isMPGP);

    virtual void initializeState_DieFall();
    virtual void executeState_DieFall();

    virtual bool setDamage(dActor_c *actor);

    virtual void boyonBegin();

    virtual bool createIceActor();

    virtual void FumiJumpSet(dActor_c *actor);
    virtual void FumiScoreSet(dActor_c *actor);

    void setWalkSpeed();
    void updateModel();

    void reactFumiProc(dActor_c *player);
    void reactYoshiFumiProc(dActor_c *player);

    STATE_FUNC_DECLARE(daEnHeihoLarge_c, Walk);
    STATE_FUNC_DECLARE(daEnHeihoLarge_c, Turn);
    STATE_FUNC_DECLARE(daEnHeihoLarge_c, Dizzy);

    dHeapAllocator_c mAllocator;
    nw4r::g3d::ResFile mRes;
    m3d::mdl_c mModel;
    m3d::anmChr_c mAnmChr;
    m3d::anmTexPat_c mAnmTexPat;

    int mColor;

    HEIHO_LARGE_TYPE_e mLargeType;
    int mTimer;
    u8 mFireHitCount;
    float mScaleCbrt;
    mEf::levelEffect_c mDizzyEffect;
};