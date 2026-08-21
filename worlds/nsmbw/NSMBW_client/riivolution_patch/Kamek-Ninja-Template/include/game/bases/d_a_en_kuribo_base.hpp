#pragma once

#include <game/bases/d_enemy.hpp>
#include <game/bases/d_heap_allocator.hpp>
#include <game/bases/d_res_mng.hpp>
#include <game/bases/d_effect.hpp>

class daEnKuriboBase_c : public dEn_c {
public:
    // fBase_c overrides
    virtual int create();
    virtual int doDelete();
    virtual int execute();
    virtual int draw();

    virtual ~daEnKuriboBase_c();

    // dBaseActor_c overrides
    virtual void finalUpdate();

    // dEn_c overrides
    virtual void Normal_VsEnHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsPlHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsYoshiHitCheck(dCc_c *self, dCc_c *other);

    virtual void initializeState_DieOther();
    virtual void executeState_DieOther();
    virtual void finalizeState_DieOther();

    virtual void fumidamageSE(const mVec3_c &pos, int);
    virtual bool setDamage(dActor_c *actor);

    virtual void beginFunsui();
    virtual void endFunsui();
    virtual BOOL isFunsui() const;

    // New virtuals
    STATE_VIRTUAL_FUNC_DECLARE(daEnKuriboBase_c, Walk);
    STATE_VIRTUAL_FUNC_DECLARE(daEnKuriboBase_c, Turn);
    STATE_VIRTUAL_FUNC_DECLARE(daEnKuriboBase_c, TrplnJump);

    virtual void calcModel();
    virtual void reactFumiProc(dActor_c* player);
    virtual void reactMameFumiProc(dActor_c* player);
    virtual void reactSpinFumiProc(dActor_c* player);
    virtual void reactYoshiFumiProc(dActor_c* yoshi);

    virtual void createModel();
    virtual void createBodyModel();
    virtual void createOtherModel();
    virtual void drawModel();

    virtual void initialize();
    virtual void setTurnByEnemyHit();
    virtual void setTurnByPlayerHit(dActor_c* player);

    virtual void setWalkSpeed();
    virtual void setWalkAnm();
    virtual void playWalkAnm();
    virtual void walkEffect();

    virtual bool isWakidashi() const;
    virtual bool isDamageInvalid();
    virtual bool isBgmSync() const;

    bool isOnEnLiftRemoconTrpln(); ///< @unofficial

    dHeapAllocator_c mAllocator;

    nw4r::g3d::ResFile mRes;
    m3d::mdl_c mModel;
    m3d::anmChr_c mAnmChr;
    nw4r::g3d::ResAnmTexPat mResPat;
    m3d::anmTexPat_c mAnmTexPat;

    float mZOffset;
    u32 mIsFrozen;
    float mSavedSpeed;

    mEf::levelEffect_c mLevelEffect;
    mEf::levelOneEffect_c mLevelOneEffect;

    u16 mCheckZoneBoundParam;
};
