#pragma once
#include <game/bases/d_a_en_kuribo.hpp>

class daEnKuribon_c : public daEnKuribo_c {
public:
    // dActor_c overrides
    virtual bool isSpinLiftUpEnable();
    virtual void setSpinLiftUpActor(dActor_c *carryingActor);

    // dEn_c overrides
    virtual void Normal_VsEnHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsPlHitCheck(dCc_c *self, dCc_c *other);
    virtual void Normal_VsYoshiHitCheck(dCc_c *self, dCc_c *other);

    virtual void initializeState_DieOther();
    virtual void executeState_DieOther();
    virtual void finalizeState_DieOther();

    // daEnKuriboBase_c overrides
    virtual void initializeState_Walk();

    virtual void calcModel();
    virtual void reactFumiProc(dActor_c* player);

    virtual void createBodyModel();

    virtual void initialize();

    virtual void setWalkAnm();
    virtual void playWalkAnm();

    void updateCarryCc();
    void setDeathInfo_Carry(dActor_c *killedBy);
    void checkTimer();
    void playKickSound(int playerNo);

    // States
    STATE_FUNC_DECLARE(daEnKuribon_c, Dizzy);
	STATE_FUNC_DECLARE(daEnKuribon_c, Carry);
    STATE_FUNC_DECLARE(daEnKuribon_c, Throw);
    STATE_FUNC_DECLARE(daEnKuribon_c, Kick);
    STATE_FUNC_DECLARE(daEnKuribon_c, Recover);

    int mFlipTimer;
    int mCarryID;
    mVec3_c mCarryPos;
    float mCcOffsetX;
    float mCcOffsetY;
    float mCcWidth;
    float mCcHeight;

    static const float smc_WALK_SPEED;
    static const float smc_THROW_SPEED_X;
    static const float smc_KICK_SPEED_X;
    static const float smc_KICK_SPEED_Y;
};

extern const s16 l_kuribon_carry_angleY[];