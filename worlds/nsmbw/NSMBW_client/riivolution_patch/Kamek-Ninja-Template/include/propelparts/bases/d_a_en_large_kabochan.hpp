#pragma once
#include <game/bases/d_a_en_kuribo.hpp>

class daEnLargeKabochan_c : public daEnKuribo_c {
public:
    // dEn_c overrides
    virtual bool hitCallback_HipAttk(dCc_c *self, dCc_c *other);

    virtual bool hitCallback_Fire(dCc_c *self, dCc_c *other);

    virtual void setDeathSound_HipAttk();

    virtual void initializeState_DieOther();

    virtual void hipatkEffect(const mVec3_c &pos);

    virtual bool createIceActor();

    virtual void fumiSE(dActor_c *actor);
    virtual void spinfumiSE(dActor_c *actor);

    // daEnKuriboBase_c overrides
    virtual void reactFumiProc(dActor_c* player);
    virtual void reactSpinFumiProc(dActor_c* player);
    virtual void reactYoshiFumiProc(dActor_c* yoshi);

    virtual void createBodyModel();

    virtual void initialize();

    virtual void setWalkSpeed();
    virtual void playWalkAnm();
    virtual void setWalkAnm();

    virtual bool isBgmSync() const;

    u8 mCracked;
    u8 mFireHitCount;
    m3d::anmMatClr_c mAnmClr;

    mEf::levelEffect_c mBreakEffect;

    static const float smc_WALK_SPEED;
    static const float smc_WALK_SPEED_CRACK;
    static const float smc_WALK_SPEED_CRACK2;
};