#pragma once
#include <game/bases/d_a_en_kuribo.hpp>

class daEnKaboKuribo_c : public daEnKuribo_c {
public:
    // dEn_c overrides
    virtual void Normal_VsPlHitCheck(dCc_c *self, dCc_c *other);

    virtual bool hitCallback_HipAttk(dCc_c *self, dCc_c *other);

    virtual void FumiScoreSet(dActor_c *actor);

    // daEnKuriboBase_c overrides
    virtual void executeState_Walk();

    virtual void createBodyModel();

    virtual void initialize();

    virtual void playWalkAnm();
    virtual void setWalkAnm();

    virtual bool isBgmSync() const;

    void setFlameAnm();

    STATE_FUNC_DECLARE(daEnKaboKuribo_c, Attack);

    bool mNoPumpkin;
    int mAttackTimer;
    m3d::anmVis_c mAnmVis;
    m3d::anmChr_c mAnmChrFlame;
    m3d::anmChrBlend_c mAnmChrBlend;

    mEf::levelEffect_c mBreakEffect;
};