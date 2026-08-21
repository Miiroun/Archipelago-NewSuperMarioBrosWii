#pragma once
#include <game/bases/d_a_en_kuribo_base.hpp>

class daEnPataKuribo_c : public daEnKuriboBase_c {
public:
    // fBase_c overrides
    virtual ~daEnPataKuribo_c();

    // dBaseActor_c overrides
    virtual void finalUpdate();

    // dEn_c overrides
    virtual bool hitCallback_Ice(dCc_c *self, dCc_c *other);

    virtual void fumidamageSE(const mVec3_c &pos, int);

    virtual bool createIceActor();

    virtual void returnState_Ice();

    virtual void beginFunsui();
    virtual void endFunsui();
    virtual BOOL isFunsui() const;

    // daEnKuriboBase_c overrides
    virtual void calcModel();
    virtual void reactFumiProc(dActor_c* player);

    virtual void reactSpinFumiProc(dActor_c* player);

    virtual void createOtherModel();
    virtual void drawModel();

    virtual void initialize();
    virtual void setTurnByEnemyHit();
    virtual void setTurnByPlayerHit(dActor_c* player);

    virtual void setWalkSpeed();

    virtual void playWalkAnm();
    virtual void walkEffect();

    virtual bool isWakidashi() const;
    virtual bool isDamageInvalid();
    virtual bool isBgmSync() const;

    STATE_FUNC_DECLARE(daEnKuriboBase_c, Pata_Walk);
    STATE_FUNC_DECLARE(daEnKuriboBase_c, Pata_Turn);

    nw4r::g3d::ResFile mWingRes;
    m3d::mdl_c mWingModel;
    m3d::anmChr_c mWingAnm;

    u16 mTurnTimer, mJumpTimer;
    u32 m_8dc;
    bool mHasWings;
    u32 m_8e4;
};