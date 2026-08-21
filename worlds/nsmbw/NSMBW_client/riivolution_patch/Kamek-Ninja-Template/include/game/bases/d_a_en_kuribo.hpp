#pragma once
#include <game/bases/d_a_en_kuribo_base.hpp>

class daEnKuribo_c : public daEnKuriboBase_c {
public:
    // fBase_c overrides
    virtual int doDelete();

    virtual ~daEnKuribo_c();

    // dBaseActor_c overrides
    virtual void finalUpdate();

    // dEn_c overrides
    virtual bool hitCallback_HipAttk(dCc_c *self, dCc_c *other);

    virtual void fumidamageSE(const mVec3_c &pos, int);

    virtual bool createIceActor();

    virtual void beginFunsui();
    virtual void endFunsui();
    virtual BOOL isFunsui() const;

    // daEnKuriboBase_c overrides
    virtual void reactSpinFumiProc(dActor_c* player);
    virtual void reactYoshiFumiProc(dActor_c* yoshi);

    virtual void createOtherModel();
    virtual void drawModel();

    virtual void initialize();
    virtual void setTurnByEnemyHit();

    virtual void setWalkSpeed();
    virtual void playWalkAnm();
    virtual void walkEffect();

    virtual bool isWakidashi() const;
    virtual bool isDamageInvalid();
    virtual bool isBgmSync() const;

    STATE_FUNC_DECLARE(daEnKuriboBase_c, Born_Split1);
    STATE_FUNC_DECLARE(daEnKuriboBase_c, Born_Split2);
    STATE_FUNC_DECLARE(daEnKuriboBase_c, BlockAppear);
    STATE_FUNC_DECLARE(daEnKuriboBase_c, Down);
    STATE_FUNC_DECLARE(daEnKuriboBase_c, Auto_Walk);
    STATE_FUNC_DECLARE(daEnKuriboBase_c, Dokan_Down);
    STATE_FUNC_DECLARE(daEnKuriboBase_c, EatOut_Ready);

    u32 mTumbleSensor[3];

    mVec2_c mTargetPos;

    u8 mTumbleState;
    bool mKeepMovingUp;

    u16 mAutoWalkDirection;
    u32 m_18;
};